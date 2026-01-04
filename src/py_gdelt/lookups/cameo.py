"""
CAMEO code lookups for GDELT events.

This module provides the CAMEOCodes class for working with Conflict and Mediation
Event Observations (CAMEO) event codes used throughout GDELT data.
"""

import json
from importlib.resources import files
from typing import Final

from py_gdelt.exceptions import InvalidCodeError

__all__ = ["CAMEOCodes"]

# CAMEO code ranges
_COOPERATION_START: Final[int] = 1
_COOPERATION_END: Final[int] = 8
_CONFLICT_START: Final[int] = 14
_CONFLICT_END: Final[int] = 20

# Quad class boundaries
_VERBAL_COOPERATION_END: Final[int] = 5
_MATERIAL_COOPERATION_END: Final[int] = 8
_VERBAL_CONFLICT_END: Final[int] = 13
_MATERIAL_CONFLICT_END: Final[int] = 20


class CAMEOCodes:
    """
    CAMEO event code lookups with lazy loading.

    Provides methods to look up CAMEO code descriptions, Goldstein scale values,
    and classify codes as cooperation/conflict or by quad class.

    All data is loaded lazily from JSON files on first access.
    """

    def __init__(self) -> None:
        """Initialize CAMEOCodes with lazy-loaded data."""
        self._codes: dict[str, str] | None = None
        self._goldstein: dict[str, float] | None = None

    @property
    def _codes_data(self) -> dict[str, str]:
        """Lazy load CAMEO codes data."""
        if self._codes is None:
            data_path = files("py_gdelt.lookups.data").joinpath("cameo_codes.json")
            self._codes = json.loads(data_path.read_text())
        return self._codes

    @property
    def _goldstein_data(self) -> dict[str, float]:
        """Lazy load Goldstein scale data."""
        if self._goldstein is None:
            data_path = files("py_gdelt.lookups.data").joinpath("cameo_goldstein.json")
            self._goldstein = json.loads(data_path.read_text())
        return self._goldstein

    def __getitem__(self, code: str) -> str:
        """
        Get description for CAMEO code.

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            Description of the event code

        Raises:
            KeyError: If code is not found
        """
        return self._codes_data[code]

    def get_description(self, code: str) -> str | None:
        """
        Get description for CAMEO code, returning None if not found.

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            Description of the event code, or None if code not found
        """
        return self._codes_data.get(code)

    def get_goldstein(self, code: str) -> float | None:
        """
        Get Goldstein scale value for CAMEO code.

        The Goldstein scale ranges from -10 (most conflictual) to +10 (most cooperative).

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            Goldstein scale value, or None if code not found
        """
        return self._goldstein_data.get(code)

    def is_conflict(self, code: str) -> bool:
        """
        Check if CAMEO code represents conflict (codes 14-20).

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            True if code is in conflict range (14-20), False otherwise
        """
        root_code = int(code[:2])
        return _CONFLICT_START <= root_code <= _CONFLICT_END

    def is_cooperation(self, code: str) -> bool:
        """
        Check if CAMEO code represents cooperation (codes 01-08).

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            True if code is in cooperation range (01-08), False otherwise
        """
        root_code = int(code[:2])
        return _COOPERATION_START <= root_code <= _COOPERATION_END

    def get_quad_class(self, code: str) -> int | None:
        """
        Get quad class (1-4) for CAMEO code.

        Quad classes:
        - 1: Verbal cooperation (01-05)
        - 2: Material cooperation (06-08)
        - 3: Verbal conflict (09-13)
        - 4: Material conflict (14-20)

        Args:
            code: CAMEO code (e.g., "01", "141", "20")

        Returns:
            Quad class (1-4), or None if code is invalid or not found
        """
        if code not in self._codes_data:
            return None

        root_code = int(code[:2])

        if _COOPERATION_START <= root_code <= _VERBAL_COOPERATION_END:
            return 1
        if root_code <= _MATERIAL_COOPERATION_END:
            return 2
        if root_code <= _VERBAL_CONFLICT_END:
            return 3
        if root_code <= _MATERIAL_CONFLICT_END:
            return 4

        return None

    def validate(self, code: str) -> None:
        """
        Validate CAMEO code, raising exception if invalid.

        Args:
            code: CAMEO code to validate

        Raises:
            InvalidCodeError: If code is not valid
        """
        if code not in self._codes_data:
            msg = f"Invalid CAMEO code: {code!r}"
            raise InvalidCodeError(msg, code=code, code_type="cameo")
