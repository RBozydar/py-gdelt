"""Unit tests for GDELT configuration settings.

Tests cover:
- Environment variable loading with GDELT_ prefix
- TOML file loading
- Default values
- Type validation
- Path handling
"""

import os
import tempfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from py_gdelt.config import GDELTSettings


class TestGDELTSettingsDefaults:
    """Test default values when no environment variables or config file is provided."""

    def test_default_values(self) -> None:
        """Test that all settings have sensible defaults."""
        settings = GDELTSettings()

        # BigQuery defaults
        assert settings.bigquery_project is None
        assert settings.bigquery_credentials is None

        # Cache defaults
        assert settings.cache_dir == Path.home() / ".cache" / "gdelt"
        assert settings.cache_ttl == 3600

        # HTTP defaults
        assert settings.max_retries == 3
        assert settings.timeout == 30
        assert settings.max_concurrent_requests == 10
        assert settings.max_concurrent_downloads == 10

        # Behavior defaults
        assert settings.fallback_to_bigquery is True
        assert settings.validate_codes is True

    def test_cache_dir_is_path_type(self) -> None:
        """Test that cache_dir is a Path object, not a string."""
        settings = GDELTSettings()
        assert isinstance(settings.cache_dir, Path)


class TestGDELTSettingsEnvironmentVariables:
    """Test loading settings from environment variables with GDELT_ prefix."""

    def test_load_bigquery_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading BigQuery settings from environment variables."""
        monkeypatch.setenv("GDELT_BIGQUERY_PROJECT", "my-project")
        monkeypatch.setenv("GDELT_BIGQUERY_CREDENTIALS", "/path/to/credentials.json")

        settings = GDELTSettings()

        assert settings.bigquery_project == "my-project"
        assert settings.bigquery_credentials == "/path/to/credentials.json"

    def test_load_cache_settings_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading cache settings from environment variables."""
        monkeypatch.setenv("GDELT_CACHE_DIR", "/tmp/custom-cache")
        monkeypatch.setenv("GDELT_CACHE_TTL", "7200")

        settings = GDELTSettings()

        assert settings.cache_dir == Path("/tmp/custom-cache")
        assert settings.cache_ttl == 7200

    def test_load_http_settings_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading HTTP settings from environment variables."""
        monkeypatch.setenv("GDELT_MAX_RETRIES", "5")
        monkeypatch.setenv("GDELT_TIMEOUT", "60")
        monkeypatch.setenv("GDELT_MAX_CONCURRENT_REQUESTS", "20")
        monkeypatch.setenv("GDELT_MAX_CONCURRENT_DOWNLOADS", "5")

        settings = GDELTSettings()

        assert settings.max_retries == 5
        assert settings.timeout == 60
        assert settings.max_concurrent_requests == 20
        assert settings.max_concurrent_downloads == 5

    def test_load_behavior_settings_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading behavior settings from environment variables."""
        monkeypatch.setenv("GDELT_FALLBACK_TO_BIGQUERY", "false")
        monkeypatch.setenv("GDELT_VALIDATE_CODES", "false")

        settings = GDELTSettings()

        assert settings.fallback_to_bigquery is False
        assert settings.validate_codes is False

    def test_env_prefix_is_case_insensitive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that environment variable prefix is case-insensitive."""
        # Pydantic-settings should handle case-insensitive env vars
        monkeypatch.setenv("gdelt_timeout", "45")

        settings = GDELTSettings()

        assert settings.timeout == 45


class TestGDELTSettingsTOMLConfig:
    """Test loading settings from TOML configuration file."""

    def test_load_from_toml_file(self, tmp_path: Path) -> None:
        """Test loading settings from a TOML configuration file."""
        config_file = tmp_path / "gdelt.toml"
        config_content = """
[gdelt]
bigquery_project = "toml-project"
bigquery_credentials = "/toml/path/creds.json"
cache_dir = "/tmp/toml-cache"
cache_ttl = 1800
max_retries = 10
timeout = 120
max_concurrent_requests = 5
max_concurrent_downloads = 3
fallback_to_bigquery = false
validate_codes = false
"""
        config_file.write_text(config_content)

        settings = GDELTSettings(config_path=config_file)

        assert settings.bigquery_project == "toml-project"
        assert settings.bigquery_credentials == "/toml/path/creds.json"
        assert settings.cache_dir == Path("/tmp/toml-cache")
        assert settings.cache_ttl == 1800
        assert settings.max_retries == 10
        assert settings.timeout == 120
        assert settings.max_concurrent_requests == 5
        assert settings.max_concurrent_downloads == 3
        assert settings.fallback_to_bigquery is False
        assert settings.validate_codes is False

    def test_env_overrides_toml(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that environment variables override TOML configuration."""
        config_file = tmp_path / "gdelt.toml"
        config_content = """
[gdelt]
timeout = 60
max_retries = 5
"""
        config_file.write_text(config_content)

        # Environment variable should override TOML
        monkeypatch.setenv("GDELT_TIMEOUT", "90")

        settings = GDELTSettings(config_path=config_file)

        assert settings.timeout == 90  # From env
        assert settings.max_retries == 5  # From TOML

    def test_nonexistent_config_file_uses_defaults(self) -> None:
        """Test that nonexistent config file path falls back to defaults."""
        settings = GDELTSettings(config_path=Path("/nonexistent/path/config.toml"))

        # Should use defaults
        assert settings.timeout == 30
        assert settings.max_retries == 3

    def test_none_config_path_uses_defaults(self) -> None:
        """Test that None config_path uses defaults."""
        settings = GDELTSettings(config_path=None)

        assert settings.timeout == 30
        assert settings.max_retries == 3


class TestGDELTSettingsValidation:
    """Test Pydantic validation of settings."""

    def test_invalid_timeout_type(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that invalid type for timeout raises ValidationError."""
        monkeypatch.setenv("GDELT_TIMEOUT", "not-a-number")

        with pytest.raises(ValidationError) as exc_info:
            GDELTSettings()

        # Check that the error is about timeout field
        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "timeout" for error in errors)

    def test_invalid_boolean_type(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that invalid boolean value raises ValidationError."""
        monkeypatch.setenv("GDELT_FALLBACK_TO_BIGQUERY", "maybe")

        with pytest.raises(ValidationError) as exc_info:
            GDELTSettings()

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "fallback_to_bigquery" for error in errors)

    def test_negative_timeout_allowed(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that negative values are allowed (Pydantic doesn't restrict by default)."""
        # Note: We're not adding validation constraints in the basic implementation
        # but this test documents the behavior
        monkeypatch.setenv("GDELT_TIMEOUT", "-1")

        settings = GDELTSettings()
        assert settings.timeout == -1

    def test_path_conversion(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that string paths are converted to Path objects."""
        monkeypatch.setenv("GDELT_CACHE_DIR", "/custom/path")

        settings = GDELTSettings()

        assert isinstance(settings.cache_dir, Path)
        assert settings.cache_dir == Path("/custom/path")


class TestGDELTSettingsExports:
    """Test module exports."""

    def test_all_export_exists(self) -> None:
        """Test that __all__ is defined in the module."""
        from py_gdelt import config

        assert hasattr(config, "__all__")
        assert "GDELTSettings" in config.__all__

    def test_settings_is_importable(self) -> None:
        """Test that GDELTSettings can be imported from the module."""
        from py_gdelt.config import GDELTSettings as ImportedSettings

        # Should be able to instantiate
        settings = ImportedSettings()
        assert isinstance(settings, ImportedSettings)


class TestGDELTSettingsDocstrings:
    """Test that proper documentation exists."""

    def test_class_has_docstring(self) -> None:
        """Test that GDELTSettings has a docstring."""
        assert GDELTSettings.__doc__ is not None
        assert len(GDELTSettings.__doc__.strip()) > 0

    def test_module_has_docstring(self) -> None:
        """Test that config module has a docstring."""
        from py_gdelt import config

        assert config.__doc__ is not None
        assert len(config.__doc__.strip()) > 0
