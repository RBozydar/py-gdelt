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
        """Test retrieving entry via __getitem__ with valid code."""
        cameo = CAMEOCodes()
        entry = cameo["01"]
        assert entry.name == "MAKE PUBLIC STATEMENT"
        entry = cameo["14"]
        assert entry.name == "PROTEST"
        entry = cameo["20"]
        assert entry.name == "USE UNCONVENTIONAL MASS VIOLENCE"

    def test_getitem_valid_three_digit_code(self) -> None:
        """Test retrieving entry for three-digit codes."""
        cameo = CAMEOCodes()
        entry = cameo["010"]
        assert entry.name == "Make statement, not specified below"
        entry = cameo["141"]
        assert entry.name == "Demonstrate or rally, not specified below"
        entry = cameo["204"]
        assert entry.name == "Use weapons of mass destruction, not specified below"

    def test_getitem_invalid_code_raises_key_error(self) -> None:
        """Test that invalid code raises KeyError."""
        cameo = CAMEOCodes()
        with pytest.raises(KeyError):
            _ = cameo["99"]

    def test_get_valid_code(self) -> None:
        """Test get() returns correct entry."""
        cameo = CAMEOCodes()
        entry = cameo.get("01")
        assert entry is not None
        assert entry.name == "MAKE PUBLIC STATEMENT"
        entry = cameo.get("14")
        assert entry is not None
        assert entry.name == "PROTEST"

    def test_get_invalid_code_returns_none(self) -> None:
        """Test get() returns None for invalid code."""
        cameo = CAMEOCodes()
        assert cameo.get("99") is None
        assert cameo.get("INVALID") is None

    def test_contains_valid_code(self) -> None:
        """Test __contains__ for valid codes."""
        cameo = CAMEOCodes()
        assert "01" in cameo
        assert "141" in cameo

    def test_contains_invalid_code(self) -> None:
        """Test __contains__ for invalid codes."""
        cameo = CAMEOCodes()
        assert "99" not in cameo
        assert "INVALID" not in cameo

    def test_search_finds_matches(self) -> None:
        """Test search finds codes by name/description."""
        cameo = CAMEOCodes()
        results = cameo.search("statement")
        assert len(results) > 0
        assert "01" in results

    def test_search_case_insensitive(self) -> None:
        """Test search is case insensitive."""
        cameo = CAMEOCodes()
        results_lower = cameo.search("statement")
        results_upper = cameo.search("STATEMENT")
        assert results_lower == results_upper

    def test_search_no_matches(self) -> None:
        """Test search returns empty list when no matches."""
        cameo = CAMEOCodes()
        results = cameo.search("NONEXISTENT_XYZ")
        assert results == []

    def test_get_goldstein_valid_code(self) -> None:
        """Test get_goldstein returns correct Goldstein entry."""
        cameo = CAMEOCodes()
        entry = cameo.get_goldstein("01")
        assert entry is not None
        assert entry.value == 0.0
        entry = cameo.get_goldstein("02")
        assert entry is not None
        assert entry.value == 1.0
        entry = cameo.get_goldstein("14")
        assert entry is not None
        assert entry.value == -5.0
        entry = cameo.get_goldstein("20")
        assert entry is not None
        assert entry.value == -10.0

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

    def test_get_goldstein_category_highly_conflictual(self) -> None:
        """Test get_goldstein_category returns highly_conflictual for scores < -5."""
        cameo = CAMEOCodes()
        assert cameo.get_goldstein_category(-10.0) == "highly_conflictual"
        assert cameo.get_goldstein_category(-7.5) == "highly_conflictual"
        assert cameo.get_goldstein_category(-5.1) == "highly_conflictual"

    def test_get_goldstein_category_moderately_conflictual(self) -> None:
        """Test get_goldstein_category returns moderately_conflictual for -5 <= score < -2."""
        cameo = CAMEOCodes()
        assert cameo.get_goldstein_category(-5.0) == "moderately_conflictual"
        assert cameo.get_goldstein_category(-3.5) == "moderately_conflictual"
        assert cameo.get_goldstein_category(-2.1) == "moderately_conflictual"

    def test_get_goldstein_category_mildly_conflictual(self) -> None:
        """Test get_goldstein_category returns mildly_conflictual for -2 <= score < 0."""
        cameo = CAMEOCodes()
        assert cameo.get_goldstein_category(-2.0) == "mildly_conflictual"
        assert cameo.get_goldstein_category(-1.0) == "mildly_conflictual"
        assert cameo.get_goldstein_category(-0.1) == "mildly_conflictual"

    def test_get_goldstein_category_cooperative(self) -> None:
        """Test get_goldstein_category returns cooperative for scores >= 0."""
        cameo = CAMEOCodes()
        assert cameo.get_goldstein_category(0.0) == "cooperative"
        assert cameo.get_goldstein_category(5.0) == "cooperative"
        assert cameo.get_goldstein_category(10.0) == "cooperative"

    def test_get_goldstein_category_boundary_values(self) -> None:
        """Test get_goldstein_category at exact boundary values."""
        cameo = CAMEOCodes()
        # Boundary at -5: -5.0 is moderately_conflictual, -5.01 is highly_conflictual
        assert cameo.get_goldstein_category(-5.0) == "moderately_conflictual"
        # Boundary at -2: -2.0 is mildly_conflictual, -2.01 is moderately_conflictual
        assert cameo.get_goldstein_category(-2.0) == "mildly_conflictual"
        # Boundary at 0: 0.0 is cooperative, -0.01 is mildly_conflictual
        assert cameo.get_goldstein_category(0.0) == "cooperative"


class TestGKGThemes:
    """Tests for GKGThemes class."""

    def test_getitem_valid_theme(self) -> None:
        """Test retrieving theme entry via __getitem__."""
        themes = GKGThemes()
        entry = themes["ENV_CLIMATECHANGE"]
        assert entry.category == "Environment"
        assert entry.description == "Climate change and global warming"

    def test_getitem_invalid_theme_raises_key_error(self) -> None:
        """Test that invalid theme raises KeyError."""
        themes = GKGThemes()
        with pytest.raises(KeyError):
            _ = themes["INVALID_THEME"]

    def test_contains_valid_theme(self) -> None:
        """Test __contains__ for valid themes."""
        themes = GKGThemes()
        assert "ENV_CLIMATECHANGE" in themes
        assert "HEALTH_PANDEMIC" in themes

    def test_contains_invalid_theme(self) -> None:
        """Test __contains__ for invalid themes."""
        themes = GKGThemes()
        assert "INVALID_THEME" not in themes

    def test_get_valid_theme(self) -> None:
        """Test get() returns correct entry."""
        themes = GKGThemes()
        entry = themes.get("ENV_CLIMATECHANGE")
        assert entry is not None
        assert entry.category == "Environment"

    def test_get_invalid_theme_returns_none(self) -> None:
        """Test get() returns None for invalid theme."""
        themes = GKGThemes()
        assert themes.get("INVALID_THEME") is None

    def test_search_returns_matching_themes(self) -> None:
        """Test search returns themes matching description substring."""
        themes = GKGThemes()
        results = themes.search("pandemic")
        assert len(results) > 0
        assert "HEALTH_PANDEMIC" in results

    def test_search_case_insensitive(self) -> None:
        """Test search is case-insensitive."""
        themes = GKGThemes()
        results_upper = themes.search("PANDEMIC")
        results_lower = themes.search("pandemic")
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

    def test_fips_to_iso3_valid_code(self) -> None:
        """Test fips_to_iso3 conversion with valid FIPS code."""
        countries = Countries()
        assert countries.fips_to_iso3("US") == "USA"
        assert countries.fips_to_iso3("UK") == "GBR"
        assert countries.fips_to_iso3("IZ") == "IRQ"

    def test_fips_to_iso3_invalid_code_returns_none(self) -> None:
        """Test fips_to_iso3 returns None for invalid FIPS code."""
        countries = Countries()
        assert countries.fips_to_iso3("XX") is None
        assert countries.fips_to_iso3("INVALID") is None

    def test_fips_to_iso2_valid_code(self) -> None:
        """Test fips_to_iso2 conversion with valid FIPS code."""
        countries = Countries()
        assert countries.fips_to_iso2("US") == "US"
        assert countries.fips_to_iso2("UK") == "GB"

    def test_fips_to_iso2_invalid_code_returns_none(self) -> None:
        """Test fips_to_iso2 returns None for invalid FIPS code."""
        countries = Countries()
        assert countries.fips_to_iso2("XX") is None

    def test_contains_valid_code(self) -> None:
        """Test __contains__ for valid FIPS codes."""
        countries = Countries()
        assert "US" in countries
        assert "us" in countries  # Case insensitive
        assert "UK" in countries

    def test_contains_invalid_code(self) -> None:
        """Test __contains__ for invalid codes."""
        countries = Countries()
        assert "XXX" not in countries

    def test_getitem_valid_code(self) -> None:
        """Test __getitem__ returns entry."""
        countries = Countries()
        entry = countries["US"]
        assert entry.name == "United States"
        assert entry.iso3 == "USA"
        assert entry.iso2 == "US"

    def test_getitem_invalid_code_raises_key_error(self) -> None:
        """Test __getitem__ raises KeyError for invalid code."""
        countries = Countries()
        with pytest.raises(KeyError):
            _ = countries["XXX"]

    def test_get_valid_code(self) -> None:
        """Test get() returns correct entry."""
        countries = Countries()
        entry = countries.get("US")
        assert entry is not None
        assert entry.name == "United States"

    def test_get_invalid_code_returns_none(self) -> None:
        """Test get() returns None for invalid code."""
        countries = Countries()
        assert countries.get("XXX") is None

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
        iso_code = countries.fips_to_iso3(fips_code)
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
        entry = lookups.cameo["01"]
        assert entry.name == "MAKE PUBLIC STATEMENT"
        # Test themes access
        assert lookups.themes.get_category("HEALTH_PANDEMIC") == "Health"
        # Test countries access
        assert lookups.countries.fips_to_iso3("US") == "USA"
