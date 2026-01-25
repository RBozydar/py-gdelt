"""
Comprehensive unit tests for the lookups module.

Tests all lookup classes (CAMEOCodes, GKGThemes, Countries, Lookups)
with focus on edge cases, error handling, and lazy loading behavior.
"""

import pytest

from py_gdelt.exceptions import InvalidCodeError
from py_gdelt.lookups import (
    CAMEOCodes,
    Countries,
    GCAMLookup,
    GKGThemes,
    ImageTags,
    ImageWebTags,
    Languages,
    Lookups,
)


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
        assert entry.description == "Climate Change"
        assert entry.count > 0

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
        """Test validate raises InvalidCodeError for invalid theme format."""
        themes = GKGThemes()
        with pytest.raises(InvalidCodeError) as exc_info:
            themes.validate("invalid-theme-format")  # lowercase with dashes
        assert exc_info.value.code == "invalid-theme-format"
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

    def test_contains_iso3_codes(self) -> None:
        """Test __contains__ supports ISO3 codes (GDELT v2 format)."""
        countries = Countries()
        # ISO3 codes should be recognized
        assert "USA" in countries
        assert "GBR" in countries
        assert "IRQ" in countries
        # Case insensitive
        assert "usa" in countries

    def test_getitem_valid_code(self) -> None:
        """Test __getitem__ returns entry."""
        countries = Countries()
        entry = countries["US"]
        assert entry.name == "United States"
        assert entry.iso3 == "USA"
        assert entry.iso2 == "US"

    def test_getitem_iso3_codes(self) -> None:
        """Test __getitem__ supports ISO3 codes (GDELT v2 format)."""
        countries = Countries()
        # ISO3 codes should work
        entry = countries["USA"]
        assert entry.name == "United States"
        assert entry.iso3 == "USA"
        # Case insensitive
        entry = countries["gbr"]
        assert entry.name == "United Kingdom"

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

    def test_get_iso3_codes(self) -> None:
        """Test get() supports ISO3 codes (GDELT v2 format)."""
        countries = Countries()
        # ISO3 codes should work
        entry = countries.get("USA")
        assert entry is not None
        assert entry.name == "United States"
        # Case insensitive
        entry = countries.get("gbr")
        assert entry is not None
        assert entry.name == "United Kingdom"

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
            lookups.validate_theme("invalid-theme")  # lowercase with dash

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


class TestCountriesNormalize:
    """Tests for Countries.normalize() method."""

    def test_normalize_fips_code(self) -> None:
        """Test normalizing valid FIPS codes returns unchanged."""
        countries = Countries()
        assert countries.normalize("US") == "US"
        assert countries.normalize("IR") == "IR"
        assert countries.normalize("UK") == "UK"

    def test_normalize_iso3_code(self) -> None:
        """Test normalizing ISO3 codes converts to FIPS."""
        countries = Countries()
        assert countries.normalize("USA") == "US"
        assert countries.normalize("IRN") == "IR"
        assert countries.normalize("GBR") == "UK"
        assert countries.normalize("DEU") == "GM"

    def test_normalize_case_insensitive(self) -> None:
        """Test normalization is case insensitive."""
        countries = Countries()
        assert countries.normalize("usa") == "US"
        assert countries.normalize("irn") == "IR"
        assert countries.normalize("Gbr") == "UK"

    def test_normalize_invalid_raises_with_suggestions(self) -> None:
        """Test invalid code raises InvalidCodeError with suggestions."""
        countries = Countries()
        with pytest.raises(InvalidCodeError) as exc_info:
            countries.normalize("IRAN")
        error = exc_info.value
        assert error.code == "IRAN"
        assert error.code_type == "country"
        assert len(error.suggestions) > 0
        assert error.help_url is not None

    def test_normalize_invalid_shows_accepted_formats(self) -> None:
        """Test error message shows accepted formats for country codes."""
        countries = Countries()
        with pytest.raises(InvalidCodeError) as exc_info:
            countries.normalize("INVALID")
        error_str = str(exc_info.value)
        assert "FIPS" in error_str
        assert "ISO3" in error_str


class TestCountriesSuggest:
    """Tests for Countries.suggest() method."""

    def test_suggest_by_name(self) -> None:
        """Test suggestions by country name."""
        countries = Countries()
        suggestions = countries.suggest("IRAN")
        assert len(suggestions) > 0
        assert any("IR" in s for s in suggestions)

    def test_suggest_by_partial_code(self) -> None:
        """Test suggestions by partial code match."""
        countries = Countries()
        suggestions = countries.suggest("US")
        assert len(suggestions) > 0

    def test_suggest_limit(self) -> None:
        """Test suggestion limit is respected."""
        countries = Countries()
        suggestions = countries.suggest("A", limit=2)
        assert len(suggestions) <= 2


class TestIranCountryCodes:
    """Specific tests for Iran (the originally reported issue)."""

    def test_iran_fips_code_exists(self) -> None:
        """Test Iran FIPS code (IR) exists in countries data."""
        countries = Countries()
        assert "IR" in countries
        entry = countries["IR"]
        assert entry.name == "Iran"
        assert entry.iso3 == "IRN"

    def test_iran_iso3_to_fips(self) -> None:
        """Test converting Iran ISO3 to FIPS."""
        countries = Countries()
        assert countries.iso_to_fips("IRN") == "IR"

    def test_iran_fips_to_iso3(self) -> None:
        """Test converting Iran FIPS to ISO3."""
        countries = Countries()
        assert countries.fips_to_iso3("IR") == "IRN"

    def test_iran_normalize_both_formats(self) -> None:
        """Test normalize accepts both IR and IRN for Iran."""
        countries = Countries()
        assert countries.normalize("IR") == "IR"
        assert countries.normalize("IRN") == "IR"


class TestGKGThemesRelaxedValidation:
    """Tests for relaxed GKG theme validation."""

    def test_validate_known_theme(self) -> None:
        """Test known themes pass validation."""
        themes = GKGThemes()
        themes.validate("ENV_CLIMATECHANGE")  # Should not raise

    def test_validate_unknown_wellformed_theme(self) -> None:
        """Test unknown but well-formed themes pass validation."""
        themes = GKGThemes()
        # These are valid patterns even if not in our limited list
        themes.validate("SOME_UNKNOWN_THEME")  # Should not raise
        themes.validate("WB_12345_SOMETHING")  # Should not raise
        themes.validate("TAX_POLICY")  # Should not raise

    def test_validate_invalid_format_raises(self) -> None:
        """Test invalid format themes raise InvalidCodeError."""
        themes = GKGThemes()
        with pytest.raises(InvalidCodeError):
            themes.validate("invalid-theme")  # lowercase and dash
        with pytest.raises(InvalidCodeError):
            themes.validate("123_STARTS_WITH_NUMBER")
        with pytest.raises(InvalidCodeError):
            themes.validate("")

    def test_validate_case_normalization(self) -> None:
        """Test validation normalizes case."""
        themes = GKGThemes()
        # Known theme in different case should work
        themes.validate("env_climatechange")  # Should not raise (normalized to upper)


class TestLanguages:
    """Tests for Languages class."""

    def test_getitem_valid_code(self) -> None:
        """Test retrieving entry via __getitem__ with valid code."""
        languages = Languages()
        entry = languages["deu"]
        assert entry.name == "German"
        assert entry.code == "deu"
        entry = languages["fra"]
        assert entry.name == "French"
        assert entry.code == "fra"

    def test_getitem_invalid_code_raises_key_error(self) -> None:
        """Test that invalid code raises KeyError."""
        languages = Languages()
        with pytest.raises(KeyError):
            _ = languages["xyz"]
        with pytest.raises(KeyError):
            _ = languages["eng"]  # Not in the dataset

    def test_getitem_case_insensitive(self) -> None:
        """Test __getitem__ is case insensitive."""
        languages = Languages()
        entry_lower = languages["deu"]
        entry_upper = languages["DEU"]
        entry_mixed = languages["Deu"]
        assert entry_lower.name == entry_upper.name == entry_mixed.name
        assert entry_lower.name == "German"

    def test_contains_valid_code(self) -> None:
        """Test __contains__ for valid codes."""
        languages = Languages()
        assert "deu" in languages
        assert "fra" in languages
        assert "spa" in languages
        assert "zho" in languages

    def test_contains_invalid_code(self) -> None:
        """Test __contains__ for invalid codes."""
        languages = Languages()
        assert "xyz" not in languages
        assert "eng" not in languages
        assert "INVALID" not in languages

    def test_get_valid_code(self) -> None:
        """Test get() returns correct LanguageEntry."""
        languages = Languages()
        entry = languages.get("deu")
        assert entry is not None
        assert entry.name == "German"
        assert entry.code == "deu"
        entry = languages.get("spa")
        assert entry is not None
        assert entry.name == "Spanish"

    def test_get_invalid_code_returns_none(self) -> None:
        """Test get() returns None for invalid code."""
        languages = Languages()
        assert languages.get("xyz") is None
        assert languages.get("eng") is None
        assert languages.get("INVALID") is None

    def test_search_by_code(self) -> None:
        """Test search() finds by code substring."""
        languages = Languages()
        results = languages.search("deu")
        assert len(results) > 0
        assert "deu" in results

    def test_search_by_name(self) -> None:
        """Test search() finds by name."""
        languages = Languages()
        results = languages.search("German")
        assert len(results) > 0
        assert "deu" in results
        results = languages.search("French")
        assert len(results) > 0
        assert "fra" in results

    def test_search_case_insensitive(self) -> None:
        """Test search is case-insensitive."""
        languages = Languages()
        results_lower = languages.search("german")
        results_upper = languages.search("GERMAN")
        results_mixed = languages.search("German")
        assert results_lower == results_upper == results_mixed
        assert "deu" in results_lower

    def test_suggest_prefix_matches(self) -> None:
        """Test suggest() with prefix."""
        languages = Languages()
        suggestions = languages.suggest("de")
        assert len(suggestions) > 0
        assert any("deu" in s for s in suggestions)

    def test_suggest_name_matches(self) -> None:
        """Test suggest() matches names."""
        languages = Languages()
        suggestions = languages.suggest("Ger")
        assert len(suggestions) > 0
        assert any("German" in s for s in suggestions)

    def test_suggest_respects_limit(self) -> None:
        """Test limit parameter."""
        languages = Languages()
        suggestions = languages.suggest("a", limit=2)
        assert len(suggestions) <= 2
        suggestions = languages.suggest("a", limit=5)
        assert len(suggestions) <= 5

    def test_validate_valid_code_no_exception(self) -> None:
        """Test validate passes."""
        languages = Languages()
        languages.validate("deu")  # Should not raise
        languages.validate("fra")  # Should not raise
        languages.validate("spa")  # Should not raise

    def test_validate_invalid_code_raises_error(self) -> None:
        """Test validate raises InvalidCodeError."""
        languages = Languages()
        with pytest.raises(InvalidCodeError) as exc_info:
            languages.validate("xyz")
        assert exc_info.value.code == "xyz"
        assert exc_info.value.code_type == "language"

    def test_validate_includes_suggestions(self) -> None:
        """Test error includes suggestions."""
        languages = Languages()
        with pytest.raises(InvalidCodeError) as exc_info:
            languages.validate("de")
        error = exc_info.value
        assert error.code == "de"
        assert len(error.suggestions) > 0

    def test_validate_includes_help_url(self) -> None:
        """Test error includes help_url."""
        languages = Languages()
        with pytest.raises(InvalidCodeError) as exc_info:
            languages.validate("INVALID")
        error = exc_info.value
        assert error.help_url is not None
        assert "LOOKUP-LANGUAGES" in error.help_url

    def test_lazy_loading(self) -> None:
        """Verify data is None before first access."""
        languages = Languages()
        # Data should be None before first access
        assert languages._data is None
        assert languages._keys_lower is None
        # Access data (trigger lazy load)
        _ = "deu" in languages
        # Now data should be loaded
        assert languages._data is not None


class TestImageWebTags:
    """Tests for ImageWebTags class."""

    def test_getitem_valid_tag(self) -> None:
        """Test retrieving entry via __getitem__ with valid web tag."""
        web_tags = ImageWebTags()
        entry = web_tags["Image"]
        assert entry.tag == "Image"
        assert entry.count == 2198300

        entry = web_tags["Photograph"]
        assert entry.tag == "Photograph"
        assert entry.count == 1027341

        entry = web_tags["Donald Trump"]
        assert entry.tag == "Donald Trump"
        assert entry.count == 502109

    def test_getitem_invalid_tag_raises_key_error(self) -> None:
        """Test that invalid web tag raises KeyError."""
        web_tags = ImageWebTags()
        with pytest.raises(KeyError):
            _ = web_tags["NonexistentWebTag"]
        with pytest.raises(KeyError):
            _ = web_tags["INVALID_TAG_XYZ"]

    def test_getitem_case_insensitive(self) -> None:
        """Test __getitem__ is case-insensitive."""
        web_tags = ImageWebTags()
        entry_lower = web_tags["image"]
        entry_upper = web_tags["IMAGE"]
        entry_mixed = web_tags["ImAgE"]
        assert entry_lower.tag == "Image"
        assert entry_upper.tag == "Image"
        assert entry_mixed.tag == "Image"
        assert entry_lower.count == entry_upper.count == entry_mixed.count

    def test_contains_valid_tag(self) -> None:
        """Test __contains__ for valid web tags."""
        web_tags = ImageWebTags()
        assert "Image" in web_tags
        assert "News" in web_tags
        assert "Donald Trump" in web_tags
        assert "Photograph" in web_tags

    def test_contains_invalid_tag(self) -> None:
        """Test __contains__ for invalid web tags."""
        web_tags = ImageWebTags()
        assert "NonexistentWebTag" not in web_tags
        assert "INVALID_TAG" not in web_tags

    def test_get_valid_tag(self) -> None:
        """Test get() returns correct entry."""
        web_tags = ImageWebTags()
        entry = web_tags.get("Image")
        assert entry is not None
        assert entry.tag == "Image"
        assert entry.count == 2198300

        entry = web_tags.get("Photograph")
        assert entry is not None
        assert entry.tag == "Photograph"
        assert entry.count == 1027341

    def test_get_invalid_tag_returns_none(self) -> None:
        """Test get() returns None for invalid web tag."""
        web_tags = ImageWebTags()
        assert web_tags.get("NonexistentWebTag") is None
        assert web_tags.get("INVALID_TAG") is None

    def test_search_finds_matches(self) -> None:
        """Test search finds matching web tags."""
        web_tags = ImageWebTags()
        results = web_tags.search("Trump")
        assert len(results) > 0
        assert "Donald Trump" in results

        results = web_tags.search("President")
        assert len(results) > 0
        assert "President" in results
        assert "President of the United States" in results

    def test_suggest_prefix_matches(self) -> None:
        """Test suggest() returns prefix matches with priority."""
        web_tags = ImageWebTags()
        suggestions = web_tags.suggest("Pres", limit=5)
        assert len(suggestions) > 0
        # Prefix matches should come first
        assert any(tag.startswith("Pres") for tag in suggestions[:3])

    def test_suggest_respects_limit(self) -> None:
        """Test suggest() respects the limit parameter."""
        web_tags = ImageWebTags()
        suggestions = web_tags.suggest("a", limit=3)
        assert len(suggestions) <= 3

        suggestions = web_tags.suggest("a", limit=10)
        assert len(suggestions) <= 10

    def test_validate_valid_tag_no_exception(self) -> None:
        """Test validate does not raise for valid web tag."""
        web_tags = ImageWebTags()
        web_tags.validate("Image")  # Should not raise
        web_tags.validate("News")  # Should not raise
        web_tags.validate("Donald Trump")  # Should not raise

    def test_validate_invalid_tag_raises_error(self) -> None:
        """Test validate raises InvalidCodeError for invalid web tag."""
        web_tags = ImageWebTags()
        with pytest.raises(InvalidCodeError) as exc_info:
            web_tags.validate("NonexistentWebTag")
        assert exc_info.value.code == "NonexistentWebTag"
        assert exc_info.value.code_type == "image_web_tag"

    def test_validate_includes_suggestions(self) -> None:
        """Test error includes suggestions for similar tags."""
        web_tags = ImageWebTags()
        with pytest.raises(InvalidCodeError) as exc_info:
            web_tags.validate("Imag")
        error = exc_info.value
        assert len(error.suggestions) > 0
        # Should suggest "Image" as it starts with "Imag"
        assert "Image" in error.suggestions

    def test_validate_includes_help_url(self) -> None:
        """Test error includes help_url."""
        web_tags = ImageWebTags()
        with pytest.raises(InvalidCodeError) as exc_info:
            web_tags.validate("InvalidTag")
        error = exc_info.value
        assert error.help_url is not None
        assert "LOOKUP-IMAGEWEBTAGS.TXT" in error.help_url

    def test_lazy_loading(self) -> None:
        """Test that data is None before first access."""
        web_tags = ImageWebTags()
        assert web_tags._data is None
        assert web_tags._keys_lower is None

        # Access should trigger lazy load
        _ = web_tags["Image"]
        assert web_tags._data is not None
        assert web_tags._keys_lower is not None


class TestImageTags:
    """Tests for ImageTags class."""

    def test_getitem_valid_tag(self) -> None:
        """Test retrieving entry via __getitem__ with valid tag."""
        tags = ImageTags()
        entry = tags["person"]
        assert entry.tag == "person"
        assert entry.count > 0

    def test_getitem_invalid_tag_raises_key_error(self) -> None:
        """Test that invalid tag raises KeyError."""
        tags = ImageTags()
        with pytest.raises(KeyError):
            _ = tags["nonexistent_tag_xyz"]

    def test_getitem_case_insensitive(self) -> None:
        """Test __getitem__ is case-insensitive."""
        tags = ImageTags()
        lower = tags["person"]
        upper = tags["PERSON"]
        assert lower == upper
        assert lower.tag == "person"

    def test_contains_valid_tag(self) -> None:
        """Test __contains__ for valid tags."""
        tags = ImageTags()
        assert "person" in tags
        assert "vehicle" in tags
        assert "sports" in tags

    def test_contains_invalid_tag(self) -> None:
        """Test __contains__ for invalid tags."""
        tags = ImageTags()
        assert "nonexistent_tag_xyz" not in tags
        assert "INVALID_TAG" not in tags

    def test_get_valid_tag(self) -> None:
        """Test get() returns correct entry."""
        tags = ImageTags()
        entry = tags.get("person")
        assert entry is not None
        assert entry.tag == "person"
        assert entry.count > 0

    def test_get_invalid_tag_returns_none(self) -> None:
        """Test get() returns None for invalid tag."""
        tags = ImageTags()
        assert tags.get("nonexistent_tag_xyz") is None
        assert tags.get("INVALID_TAG") is None

    def test_search_finds_matches(self) -> None:
        """Test search finds matching tags."""
        tags = ImageTags()
        results = tags.search("person")
        assert len(results) > 0
        assert "person" in results

    def test_search_case_insensitive(self) -> None:
        """Test search is case-insensitive."""
        tags = ImageTags()
        results_lower = tags.search("person")
        results_upper = tags.search("PERSON")
        assert results_lower == results_upper

    def test_search_no_matches(self) -> None:
        """Test search returns empty list when no matches found."""
        tags = ImageTags()
        results = tags.search("nonexistent_query_xyz_12345")
        assert results == []

    def test_suggest_prefix_matches_first(self) -> None:
        """Test prefix matches have higher priority in suggestions."""
        tags = ImageTags()
        # "person" should be first as it's a prefix match for "per"
        suggestions = tags.suggest("per", limit=5)
        assert len(suggestions) > 0
        assert "person" in suggestions
        # Prefix matches should come before contains matches

    def test_suggest_contains_matches(self) -> None:
        """Test suggest finds contains matches when no prefix matches."""
        tags = ImageTags()
        # Should find tags containing "ball" like "football player"
        suggestions = tags.suggest("oot", limit=5)
        assert len(suggestions) > 0

    def test_suggest_respects_limit(self) -> None:
        """Test suggest respects the limit parameter."""
        tags = ImageTags()
        suggestions = tags.suggest("p", limit=2)
        assert len(suggestions) <= 2

    def test_validate_valid_tag_no_exception(self) -> None:
        """Test validate does not raise for valid tag."""
        tags = ImageTags()
        tags.validate("person")  # Should not raise
        tags.validate("vehicle")  # Should not raise

    def test_validate_invalid_tag_raises_error(self) -> None:
        """Test validate raises InvalidCodeError for invalid tag."""
        tags = ImageTags()
        with pytest.raises(InvalidCodeError) as exc_info:
            tags.validate("nonexistent_tag_xyz")
        assert exc_info.value.code == "nonexistent_tag_xyz"
        assert exc_info.value.code_type == "image_tag"

    def test_validate_includes_suggestions(self) -> None:
        """Test error includes suggestions for similar tags."""
        tags = ImageTags()
        with pytest.raises(InvalidCodeError) as exc_info:
            tags.validate("perso")  # Close to "person"
        error = exc_info.value
        assert len(error.suggestions) > 0
        # Should suggest "person" as it's a prefix match
        assert "person" in error.suggestions

    def test_validate_includes_help_url(self) -> None:
        """Test error includes help_url."""
        tags = ImageTags()
        with pytest.raises(InvalidCodeError) as exc_info:
            tags.validate("nonexistent_tag_xyz")
        error = exc_info.value
        assert error.help_url is not None
        assert "LOOKUP-IMAGETAGS.TXT" in error.help_url

    def test_lazy_loading(self) -> None:
        """Verify data is None before first access."""
        tags = ImageTags()
        # Before first access, _data should be None
        assert tags._data is None
        # Access data by calling __contains__
        _ = "person" in tags
        # After access, _data should be populated
        assert tags._data is not None
        assert tags._keys_lower is not None


class TestGCAMLookup:
    """Tests for GCAMLookup class."""

    def test_getitem_valid_variable(self) -> None:
        """Test retrieving entry via __getitem__ with valid variable."""
        gcam = GCAMLookup()
        entry = gcam["c2.14"]
        assert entry.variable == "c2.14"
        assert entry.dictionary_name != ""
        assert entry.dimension_name != ""

    def test_getitem_invalid_variable_raises_key_error(self) -> None:
        """Test that invalid variable raises KeyError."""
        gcam = GCAMLookup()
        with pytest.raises(KeyError):
            _ = gcam["invalid.999"]

    def test_getitem_case_insensitive(self) -> None:
        """Test __getitem__ is case insensitive."""
        gcam = GCAMLookup()
        entry_lower = gcam["c2.14"]
        entry_upper = gcam["C2.14"]
        entry_mixed = gcam["C2.14"]
        assert entry_lower.variable == entry_upper.variable
        assert entry_lower.variable == entry_mixed.variable

    def test_contains_valid_variable(self) -> None:
        """Test __contains__ for valid variables."""
        gcam = GCAMLookup()
        assert "c2.14" in gcam
        assert "c1.1" in gcam

    def test_contains_invalid_variable(self) -> None:
        """Test __contains__ for invalid variables."""
        gcam = GCAMLookup()
        assert "invalid.999" not in gcam
        assert "NONEXISTENT" not in gcam

    def test_get_valid_variable(self) -> None:
        """Test get() returns GCAMEntry for valid variable."""
        gcam = GCAMLookup()
        entry = gcam.get("c2.14")
        assert entry is not None
        assert entry.variable == "c2.14"

    def test_get_invalid_variable_returns_none(self) -> None:
        """Test get() returns None for invalid variable."""
        gcam = GCAMLookup()
        assert gcam.get("invalid.999") is None
        assert gcam.get("NONEXISTENT") is None

    def test_search_by_dictionary_name(self) -> None:
        """Test search finds variables by dictionary name substring."""
        gcam = GCAMLookup()
        results = gcam.search("Forest Values")
        assert len(results) > 0
        # All Forest Values entries should start with "c1"
        assert all(var.startswith("c1.") for var in results)

    def test_search_by_dimension_name(self) -> None:
        """Test search finds variables by dimension name substring."""
        gcam = GCAMLookup()
        results = gcam.search("AESTHETIC")
        assert len(results) > 0
        assert "c1.1" in results

    def test_suggest_prefix_matches(self) -> None:
        """Test suggest() returns prefix matches."""
        gcam = GCAMLookup()
        suggestions = gcam.suggest("c2.1")
        assert len(suggestions) > 0
        # All suggestions should start with "c2.1"
        assert all(s.startswith("c2.1") for s in suggestions)

    def test_suggest_respects_limit(self) -> None:
        """Test suggest() respects limit parameter."""
        gcam = GCAMLookup()
        suggestions = gcam.suggest("c2", limit=3)
        assert len(suggestions) <= 3

    def test_validate_valid_variable_no_exception(self) -> None:
        """Test validate passes for valid variable."""
        gcam = GCAMLookup()
        gcam.validate("c2.14")  # Should not raise

    def test_validate_invalid_variable_raises_error(self) -> None:
        """Test validate raises InvalidCodeError for invalid variable."""
        gcam = GCAMLookup()
        with pytest.raises(InvalidCodeError) as exc_info:
            gcam.validate("invalid.999")
        assert exc_info.value.code == "invalid.999"
        assert exc_info.value.code_type == "gcam"

    def test_validate_includes_suggestions(self) -> None:
        """Test validate error includes suggestions."""
        gcam = GCAMLookup()
        with pytest.raises(InvalidCodeError) as exc_info:
            gcam.validate("c1.")  # Invalid but matches "c1.1", "c1.2", etc.
        error = exc_info.value
        assert len(error.suggestions) > 0
        # Should suggest c1.1, c1.2, etc.
        assert any(s.startswith("c1.") for s in error.suggestions)

    def test_validate_includes_help_url(self) -> None:
        """Test validate error includes help URL."""
        gcam = GCAMLookup()
        with pytest.raises(InvalidCodeError) as exc_info:
            gcam.validate("invalid.999")
        error = exc_info.value
        assert error.help_url is not None
        assert "GCAM" in error.help_url

    def test_lazy_loading(self) -> None:
        """Verify data is None before first access."""
        gcam = GCAMLookup()
        assert gcam._data is None
        # Access data
        _ = gcam["c1.1"]
        # Now data should be loaded
        assert gcam._data is not None

    def test_get_dictionary_returns_all_entries(self) -> None:
        """Test get_dictionary returns all entries with given prefix."""
        gcam = GCAMLookup()
        c2_entries = gcam.get_dictionary("c2")
        assert len(c2_entries) > 0
        # All entries should start with "c2."
        assert all(var.startswith("c2.") for var in c2_entries)
        # Verify they are GCAMEntry objects
        for entry in c2_entries.values():
            assert entry.dictionary_name != ""

    def test_get_dictionary_empty_for_invalid(self) -> None:
        """Test get_dictionary returns empty dict for invalid prefix."""
        gcam = GCAMLookup()
        result = gcam.get_dictionary("invalid_prefix")
        assert result == {}

    def test_get_dictionary_case_insensitive(self) -> None:
        """Test get_dictionary is case insensitive."""
        gcam = GCAMLookup()
        entries_lower = gcam.get_dictionary("c2")
        entries_upper = gcam.get_dictionary("C2")
        assert len(entries_lower) == len(entries_upper)
        assert set(entries_lower.keys()) == set(entries_upper.keys())

    def test_list_dictionaries(self) -> None:
        """Test list_dictionaries returns sorted list of unique prefixes."""
        gcam = GCAMLookup()
        prefixes = gcam.list_dictionaries()
        assert len(prefixes) > 0
        assert "c1" in prefixes
        assert "c2" in prefixes
        # Verify sorted
        assert prefixes == sorted(prefixes)
        # Verify unique
        assert len(prefixes) == len(set(prefixes))

    def test_list_dictionary_names(self) -> None:
        """Test list_dictionary_names returns sorted list of dictionary names."""
        gcam = GCAMLookup()
        names = gcam.list_dictionary_names()
        assert len(names) > 0
        assert "Forest Values" in names
        # Verify sorted
        assert names == sorted(names)
        # Verify unique
        assert len(names) == len(set(names))

    def test_by_language_english(self) -> None:
        """Test by_language returns English entries."""
        gcam = GCAMLookup()
        eng_entries = gcam.by_language("eng")
        assert len(eng_entries) > 0
        # All entries should have language "eng"
        assert all(entry.language == "eng" for entry in eng_entries.values())

    def test_by_language_case_insensitive(self) -> None:
        """Test by_language is case insensitive."""
        gcam = GCAMLookup()
        entries_lower = gcam.by_language("eng")
        entries_upper = gcam.by_language("ENG")
        assert len(entries_lower) == len(entries_upper)

    def test_by_language_empty_for_invalid(self) -> None:
        """Test by_language returns empty dict for invalid language."""
        gcam = GCAMLookup()
        result = gcam.by_language("invalid_lang")
        assert result == {}
