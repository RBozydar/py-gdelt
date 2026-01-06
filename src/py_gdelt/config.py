"""Configuration settings for the GDELT Python client library.

This module provides the GDELTSettings class which manages all configuration
for the GDELT client, including:
- BigQuery credentials and project settings
- HTTP client configuration (retries, timeouts, concurrency)
- Caching configuration
- Behavioral flags (validation, fallback strategies)

Settings are loaded from:
1. TOML configuration file (if provided)
2. Environment variables with GDELT_ prefix
3. Default values

Environment variables take precedence over TOML configuration.
"""

import logging
import tomllib
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


__all__ = ["GDELTSettings"]

logger = logging.getLogger(__name__)


class TOMLConfigSource(PydanticBaseSettingsSource):
    """Custom settings source for loading configuration from TOML files.

    This source loads settings from a TOML file specified by the config_path
    initialization parameter. It has lower priority than environment variables.

    Args:
        settings_cls: The settings class being initialized.
        config_path: Optional path to TOML configuration file.
    """

    def __init__(self, settings_cls: type[BaseSettings], config_path: Path | None = None) -> None:
        super().__init__(settings_cls)
        self.config_path = config_path
        self._config_data: dict[str, Any] = {}

        if config_path is not None and config_path.exists():
            try:
                with config_path.open("rb") as f:
                    data = tomllib.load(f)
                    # Extract settings from [gdelt] section if it exists
                    self._config_data = data.get("gdelt", {})
                    logger.debug(
                        "Loaded configuration from %s: %d settings",
                        config_path,
                        len(self._config_data),
                    )
            except (OSError, tomllib.TOMLDecodeError) as e:
                logger.warning("Failed to load TOML config from %s: %s", config_path, e)
        elif config_path is not None:
            logger.debug("Config file not found: %s, using defaults", config_path)

    def get_field_value(self, _field_info: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        """Get the value for a specific field from the TOML config.

        Args:
            _field_info: Field information from Pydantic (unused).
            field_name: Name of the field to retrieve.

        Returns:
            Tuple of (value, key, value_is_complex).
        """
        value = self._config_data.get(field_name)
        return value, field_name, False

    def __call__(self) -> dict[str, Any]:
        """Return the entire configuration dictionary.

        Returns:
            Dictionary of configuration values from TOML file.
        """
        return self._config_data


class GDELTSettings(BaseSettings):
    """Configuration settings for the GDELT client library.

    Settings can be configured via:
    - Environment variables with GDELT_ prefix (e.g., GDELT_TIMEOUT=60)
    - TOML configuration file passed to config_path parameter
    - Default values

    Environment variables take precedence over TOML configuration.

    Args:
        config_path: Optional path to TOML configuration file.
            If provided and exists, settings will be loaded from it.
            Environment variables will override TOML settings.
        **kwargs: Additional keyword arguments for setting field values.

    Attributes:
        model_config: Pydantic settings configuration (env prefix, case sensitivity)
        bigquery_project: Google Cloud project ID for BigQuery access
        bigquery_credentials: Path to Google Cloud credentials JSON file
        cache_dir: Directory for caching downloaded GDELT data
        cache_ttl: Cache time-to-live in seconds
        master_file_list_ttl: Master file list cache TTL in seconds
        max_retries: Maximum number of HTTP request retries
        timeout: HTTP request timeout in seconds
        max_concurrent_requests: Maximum concurrent HTTP requests
        max_concurrent_downloads: Maximum concurrent file downloads
        fallback_to_bigquery: Whether to fallback to BigQuery when APIs fail
        validate_codes: Whether to validate CAMEO/country codes

    Example:
        >>> # Using defaults
        >>> settings = GDELTSettings()

        >>> # Loading from TOML file
        >>> settings = GDELTSettings(config_path=Path("gdelt.toml"))

        >>> # Environment variables override TOML
        >>> import os
        >>> os.environ["GDELT_TIMEOUT"] = "60"
        >>> settings = GDELTSettings()
        >>> settings.timeout
        60
    """

    model_config = SettingsConfigDict(
        env_prefix="GDELT_",
        case_sensitive=False,
        extra="ignore",
    )

    # BigQuery settings (optional)
    bigquery_project: str | None = Field(
        default=None,
        description="Google Cloud project ID for BigQuery access",
    )
    bigquery_credentials: str | None = Field(
        default=None,
        description="Path to Google Cloud credentials JSON file",
    )

    # Cache settings
    cache_dir: Path = Field(
        default_factory=lambda: Path.home() / ".cache" / "gdelt",
        description="Directory for caching downloaded GDELT data",
    )
    cache_ttl: int = Field(
        default=3600,
        description="Cache time-to-live in seconds",
    )
    master_file_list_ttl: int = Field(
        default=300,
        description="Master file list cache TTL in seconds (default 5 minutes)",
    )

    # HTTP settings
    max_retries: int = Field(
        default=3,
        description="Maximum number of HTTP request retries",
    )
    timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds",
    )
    max_concurrent_requests: int = Field(
        default=10,
        description="Maximum concurrent HTTP requests",
    )
    max_concurrent_downloads: int = Field(
        default=10,
        description="Maximum concurrent file downloads",
    )

    # Behavior settings
    fallback_to_bigquery: bool = Field(
        default=True,
        description="Whether to fallback to BigQuery when APIs fail",
    )
    validate_codes: bool = Field(
        default=True,
        description="Whether to validate CAMEO/country codes",
    )

    # Class variable to store config_path during initialization
    _current_config_path: Path | None = None

    def __init__(self, config_path: Path | None = None, **kwargs: Any) -> None:
        # Store config_path temporarily on class for settings_customise_sources
        GDELTSettings._current_config_path = config_path
        try:
            # Initialize the parent BaseSettings
            super().__init__(**kwargs)
        finally:
            # Clean up class variable
            GDELTSettings._current_config_path = None

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        **_kwargs: Any,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Customize settings sources to include TOML configuration.

        The order of sources determines precedence (first source wins):
        1. Init settings (kwargs passed to __init__)
        2. Environment variables (GDELT_ prefix)
        3. TOML configuration file
        4. Default values

        Args:
            settings_cls: The settings class being customized.
            init_settings: Settings from __init__ kwargs.
            env_settings: Settings from environment variables.
            dotenv_settings: Settings from .env file (unused).
            file_secret_settings: Settings from secret files (unused).
            **_kwargs: Additional keyword arguments (unused).

        Returns:
            Tuple of settings sources in priority order.
        """
        # Get config_path from class variable set in __init__
        config_path = cls._current_config_path
        toml_source = TOMLConfigSource(settings_cls, config_path=config_path)

        # Return sources in priority order (first wins)
        return (
            init_settings,  # Highest priority: explicit kwargs
            env_settings,  # Environment variables
            toml_source,  # TOML configuration
            # Default values are handled by Pydantic automatically
        )
