"""
Comprehensive unit tests for the lookups module.

Tests all lookup classes (CAMEOCodes, GKGThemes, Countries, Lookups)
with focus on edge cases, error handling, and lazy loading behavior.
"""

import pytest

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups import CAMEOCodes, Countries, GKGThemes, Lookups


class TestCAMEOCodes:
    """Tests for CAMEOCodes class."""

    def test_getitem_valid_code(self) -> None:
        """Test retrieving description via __getitem__ with valid code."""
        cameo = CAMEOCodes()
        assert cameo["01"] == "MAKE PUBLIC STATEMENT"
        assert cameo["14"] == "PROTEST"
        assert cameo["20"] == "USE UNCONVENTIONAL MASS VIOLENCE"

    def test_getitem_valid_three_digit_code(self) -> None:
        """Test retrieving description for three-digit codes."""
        cameo = CAMEOCodes()
        assert cameo["010"] == "MAKE STATEMENT, NOT SPECIFIED BELOW"
        assert cameo["141"] == "DEMONSTRATE OR RALLY"
        assert cameo["204"] == "USE WEAPONS OF MASS DESTRUCTION"

    def test_getitem_invalid_code_raises_key_error(self) -> None:
        """Test that invalid code raises KeyError."""
        cameo = CAMEOCodes()
        with pytest.raises(KeyError):
            _ = cameo["99"]

    def test_get_description_valid_code(self) -> None:
        """Test get_description returns correct description."""
        cameo = CAMEOCodes()
        assert cameo.get_description("01") == "MAKE PUBLIC STATEMENT"
        assert cameo.get_description("14") == "PROTEST"

    def test_get_description_invalid_code_returns_none(self) -> None:
        """Test get_description returns None for invalid code."""
        cameo = CAMEOCodes()
        assert cameo.get_description("99") is None
        assert cameo.get_description("INVALID") is None

    def test_get_goldstein_valid_code(self) -> None:
        """Test get_goldstein returns correct Goldstein scale value."""
        cameo = CAMEOCodes()
        assert cameo.get_goldstein("01") == 0.0
        assert cameo.get_goldstein("02") == 1.0
        assert cameo.get_goldstein("14") == -5.0
        assert cameo.get_goldstein("20") == -10.0

    def test_get_goldstein_invalid_code_returns_none(self) -> None:
        """Test get_goldstein returns None for invalid code."""
        cameo = CAMEOCodes()
        assert cameo.get_goldstein("99") is None

    def test_is_conflict_codes(self) -> None:
        """Test is_conflict correctly identifies conflict codes (14-20)."""
        cameo = CAMEOCodes()
        # Conflict codes
        assert cameo.is_conflict("14") is True
        assert cameo.is_conflict("140") is True
        assert cameo.is_conflict("145") is True
        assert cameo.is_conflict("20") is True
        assert cameo.is_conflict("204") is True
        # Non-conflict codes
        assert cameo.is_conflict("01") is False
        assert cameo.is_conflict("02") is False
        assert cameo.is_conflict("13") is False

    def test_is_cooperation_codes(self) -> None:
        """Test is_cooperation correctly identifies cooperation codes (01-08)."""
        cameo = CAMEOCodes()
        # Cooperation codes
        assert cameo.is_cooperation("01") is True
        assert cameo.is_cooperation("010") is True
        assert cameo.is_cooperation("02") is True
        assert cameo.is_cooperation("020") is True
        # Non-cooperation codes
        assert cameo.is_cooperation("14") is False
        assert cameo.is_cooperation("20") is False

    def test_get_quad_class_valid_codes(self) -> None:
        """Test get_quad_class returns correct quadrant (1-4)."""
        cameo = CAMEOCodes()
        # Verbal cooperation (01-05): Quad 1
        assert cameo.get_quad_class("01") == 1
        assert cameo.get_quad_class("02") == 1
        # Material cooperation (06-08): Quad 2
        assert cameo.get_quad_class("06") == 2
        assert cameo.get_quad_class("060") == 2
        # Verbal conflict (09-13): Quad 3
        assert cameo.get_quad_class("09") == 3
        assert cameo.get_quad_class("10") == 3
        # Material conflict (14-20): Quad 4
        assert cameo.get_quad_class("14") == 4
        assert cameo.get_quad_class("20") == 4

    def test_get_quad_class_invalid_code_returns_none(self) -> None:
        """Test get_quad_class returns None for invalid code."""
        cameo = CAMEOCodes()
        assert cameo.get_quad_class("99") is None

    def test_validate_valid_code_no_exception(self) -> None:
        """Test validate does not raise for valid code."""
        cameo = CAMEOCodes()
        cameo.validate("01")  # Should not raise
        cameo.validate("141")  # Should not raise

    def test_validate_invalid_code_raises_invalid_code_error(self) -> None:
        """Test validate raises InvalidCodeError for invalid code."""
        cameo = CAMEOCodes()
        with pytest.raises(InvalidCodeError) as exc_info:
            cameo.validate("99")
        assert exc_info.value.code == "99"
        assert exc_info.value.code_type == "cameo"

    def test_validate_invalid_code_error_message(self) -> None:
        """Test InvalidCodeError contains descriptive message."""
        cameo = CAMEOCodes()
        with pytest.raises(InvalidCodeError) as exc_info:
            cameo.validate("INVALID")
        assert "INVALID" in str(exc_info.value)
        assert "cameo" in str(exc_info.value)


class TestGKGThemes:
    """Tests for GKGThemes class."""

    def test_getitem_valid_theme(self) -> None:
        """Test retrieving theme metadata via __getitem__."""
        themes = GKGThemes()
        result = themes["ENV_CLIMATECHANGE"]
        assert result["category"] == "Environment"
        assert "description" in result

    def test_getitem_invalid_theme_raises_key_error(self) -> None:
        """Test that invalid theme raises KeyError."""
        themes = GKGThemes()
        with pytest.raises(KeyError):
            _ = themes["INVALID_THEME"]

    def test_search_returns_matching_themes(self) -> None:
        """Test search returns themes matching substring query."""
        themes = GKGThemes()
        results = themes.search("HEALTH")
        assert len(results) > 0
        assert all("HEALTH" in theme for theme in results)

    def test_search_case_insensitive(self) -> None:
        """Test search is case-insensitive."""
        themes = GKGThemes()
        results_upper = themes.search("HEALTH")
        results_lower = themes.search("health")
        assert results_upper == results_lower

    def test_search_no_matches_returns_empty_list(self) -> None:
        """Test search returns empty list when no matches found."""
        themes = GKGThemes()
        results = themes.search("NONEXISTENT_QUERY_XYZ")
        assert results == []

    def test_get_category_valid_theme(self) -> None:
        """Test get_category returns correct category."""
        themes = GKGThemes()
        assert themes.get_category("ENV_CLIMATECHANGE") == "Environment"
        assert themes.get_category("HEALTH_PANDEMIC") == "Health"
        assert themes.get_category("ECON_INFLATION") == "Economy"

    def test_get_category_invalid_theme_returns_none(self) -> None:
        """Test get_category returns None for invalid theme."""
        themes = GKGThemes()
        assert themes.get_category("INVALID") is None

    def test_list_by_category_returns_matching_themes(self) -> None:
        """Test list_by_category returns all themes in category."""
        themes = GKGThemes()
        env_themes = themes.list_by_category("Environment")
        assert len(env_themes) > 0
        assert "ENV_CLIMATECHANGE" in env_themes
        assert all(themes.get_category(theme) == "Environment" for theme in env_themes)

    def test_list_by_category_case_sensitive(self) -> None:
        """Test list_by_category is case-sensitive."""
        themes = GKGThemes()
        assert len(themes.list_by_category("Environment")) > 0
        assert len(themes.list_by_category("environment")) == 0

    def test_list_by_category_no_matches_returns_empty_list(self) -> None:
        """Test list_by_category returns empty list for unknown category."""
        themes = GKGThemes()
        result = themes.list_by_category("NonexistentCategory")
        assert result == []

    def test_validate_valid_theme_no_exception(self) -> None:
        """Test validate does not raise for valid theme."""
        themes = GKGThemes()
        themes.validate("ENV_CLIMATECHANGE")  # Should not raise

    def test_validate_invalid_theme_raises_invalid_code_error(self) -> None:
        """Test validate raises InvalidCodeError for invalid theme."""
        themes = GKGThemes()
        with pytest.raises(InvalidCodeError) as exc_info:
            themes.validate("INVALID_THEME")
        assert exc_info.value.code == "INVALID_THEME"
        assert exc_info.value.code_type == "theme"


class TestCountries:
    """Tests for Countries class."""

    def test_fips_to_iso_valid_code(self) -> None:
        """Test fips_to_iso conversion with valid FIPS code."""
        countries = Countries()
        assert countries.fips_to_iso("US") == "USA"
        assert countries.fips_to_iso("UK") == "GBR"
        assert countries.fips_to_iso("IZ") == "IRQ"

    def test_fips_to_iso_invalid_code_returns_none(self) -> None:
        """Test fips_to_iso returns None for invalid FIPS code."""
        countries = Countries()
        assert countries.fips_to_iso("XX") is None
        assert countries.fips_to_iso("INVALID") is None

    def test_iso_to_fips_valid_code(self) -> None:
        """Test iso_to_fips conversion with valid ISO code."""
        countries = Countries()
        assert countries.iso_to_fips("USA") == "US"
        assert countries.iso_to_fips("GBR") == "UK"
        assert countries.iso_to_fips("IRQ") == "IZ"

    def test_iso_to_fips_invalid_code_returns_none(self) -> None:
        """Test iso_to_fips returns None for invalid ISO code."""
        countries = Countries()
        assert countries.iso_to_fips("XXX") is None
        assert countries.iso_to_fips("INVALID") is None

    def test_get_name_fips_code(self) -> None:
        """Test get_name works with FIPS code."""
        countries = Countries()
        assert countries.get_name("US") == "United States"
        assert countries.get_name("IZ") == "Iraq"

    def test_get_name_iso_code(self) -> None:
        """Test get_name works with ISO code."""
        countries = Countries()
        assert countries.get_name("USA") == "United States"
        assert countries.get_name("IRQ") == "Iraq"

    def test_get_name_invalid_code_returns_none(self) -> None:
        """Test get_name returns None for invalid code."""
        countries = Countries()
        assert countries.get_name("XX") is None
        assert countries.get_name("XXX") is None

    def test_validate_valid_fips_code_no_exception(self) -> None:
        """Test validate does not raise for valid FIPS code."""
        countries = Countries()
        countries.validate("US")  # Should not raise

    def test_validate_valid_iso_code_no_exception(self) -> None:
        """Test validate does not raise for valid ISO code."""
        countries = Countries()
        countries.validate("USA")  # Should not raise

    def test_validate_invalid_code_raises_invalid_code_error(self) -> None:
        """Test validate raises InvalidCodeError for invalid code."""
        countries = Countries()
        with pytest.raises(InvalidCodeError) as exc_info:
            countries.validate("INVALID")
        assert exc_info.value.code == "INVALID"
        assert exc_info.value.code_type == "country"

    def test_roundtrip_conversion(self) -> None:
        """Test FIPS -> ISO -> FIPS roundtrip conversion."""
        countries = Countries()
        fips_code = "US"
        iso_code = countries.fips_to_iso(fips_code)
        assert iso_code is not None
        roundtrip_fips = countries.iso_to_fips(iso_code)
        assert roundtrip_fips == fips_code


class TestLookups:
    """Tests for Lookups aggregator class."""

    def test_cameo_property_returns_cameo_codes_instance(self) -> None:
        """Test cameo property returns CAMEOCodes instance."""
        lookups = Lookups()
        assert isinstance(lookups.cameo, CAMEOCodes)

    def test_themes_property_returns_gkg_themes_instance(self) -> None:
        """Test themes property returns GKGThemes instance."""
        lookups = Lookups()
        assert isinstance(lookups.themes, GKGThemes)

    def test_countries_property_returns_countries_instance(self) -> None:
        """Test countries property returns Countries instance."""
        lookups = Lookups()
        assert isinstance(lookups.countries, Countries)

    def test_lazy_loading_same_instance(self) -> None:
        """Test that lazy loading returns same instance on repeated access."""
        lookups = Lookups()
        cameo1 = lookups.cameo
        cameo2 = lookups.cameo
        assert cameo1 is cameo2

    def test_validate_cameo_delegates_to_cameo_codes(self) -> None:
        """Test validate_cameo delegates to CAMEOCodes.validate."""
        lookups = Lookups()
        lookups.validate_cameo("01")  # Should not raise
        with pytest.raises(InvalidCodeError):
            lookups.validate_cameo("99")

    def test_validate_theme_delegates_to_gkg_themes(self) -> None:
        """Test validate_theme delegates to GKGThemes.validate."""
        lookups = Lookups()
        lookups.validate_theme("ENV_CLIMATECHANGE")  # Should not raise
        with pytest.raises(InvalidCodeError):
            lookups.validate_theme("INVALID")

    def test_validate_country_delegates_to_countries(self) -> None:
        """Test validate_country delegates to Countries.validate."""
        lookups = Lookups()
        lookups.validate_country("US")  # Should not raise
        with pytest.raises(InvalidCodeError):
            lookups.validate_country("INVALID")

    def test_all_lookups_accessible_via_aggregator(self) -> None:
        """Test that all lookup functionality is accessible via Lookups."""
        lookups = Lookups()
        # Test CAMEO access
        assert lookups.cameo["01"] == "MAKE PUBLIC STATEMENT"
        # Test themes access
        assert lookups.themes.get_category("HEALTH_PANDEMIC") == "Health"
        # Test countries access
        assert lookups.countries.fips_to_iso("US") == "USA"
