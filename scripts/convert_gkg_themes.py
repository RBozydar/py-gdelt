#!/usr/bin/env python3
"""Convert GDELT GKG themes lookup file to JSON with generated descriptions.

This script processes LOOKUP-GKGTHEMES.txt and generates descriptions using:
1. CrisisLex EMTerms CSV lookup for CRISISLEX_* themes
2. World Bank name parsing for WB_* themes
3. Taxonomy parsing for TAX_* themes
4. Prefix-based mapping for ENV_, ECON_, etc.
5. Title-casing fallback for simple themes

Ambiguous themes are flagged for LLM processing.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path


GDELT_DOCS = Path("gdelt_docs")
LOOKUPS_DATA = Path("src/py_gdelt/lookups/data")

# =============================================================================
# TAX_ Category Mapping
# =============================================================================

TAX_CATEGORY_MAP: dict[str, str] = {
    "FNCACT": "Functional Actor",
    "WORLDLANGUAGES": "World Language",
    "WORLDBIRDS": "World Bird",
    "DISEASE": "Disease",
    "WORLDMAMMALS": "World Mammal",
    "TERROR": "Terrorism",
    "ETHNICITY": "Ethnicity",
    "WORLDFISH": "World Fish",
    "POLITICAL": "Political",
    "RELIGION": "Religion",
    "WORLDINSECTS": "World Insect",
    "AGRICULHARMINSECTS": "Agricultural Harmful Insect",
    "AIDGROUPS": "Aid Group",
    "WORLDREPTILES": "World Reptile",
    "WEAPONS": "Weapon",
    "WORLDARACHNIDS": "World Arachnid",
    "PLANTDISEASE": "Plant Disease",
    "MILITARY": "Military",
    "ECON": "Economic",
    "FOODSTAPLES": "Food Staple",
    "WORLDCRUSTACEANS": "World Crustacean",
    "CARTELS": "Cartel",
    "CHRONICDISEASE": "Chronic Disease",
    "WORLDMYRIAPODA": "World Myriapod",
    "SPECIAL": "Special",
    "SPECIALDEATH": "Special Death",
}

# =============================================================================
# Known Prefix Categories
# =============================================================================

# Note: Some categories have multiple prefixes (e.g., MIL_ and MILITARY_ both exist
# in the GDELT data). These map to the same category name intentionally.
PREFIX_CATEGORY_MAP: dict[str, str] = {
    "ENV": "Environment",
    "ECON": "Economy",
    "HEALTH": "Health",
    "SOC": "Social",
    "GOV": "Government",
    "TECH": "Technology",
    "MEDIA": "Media",
    "NATURAL": "Natural Disaster",
    "MANMADE": "Man-Made Disaster",
    "EPU": "Economic Policy Uncertainty",
    "UNGP": "UN Guiding Principles",
    "CRISISLEX": "CrisisLex",
    "MOVEMENT": "Movement",
    "UNREST": "Unrest",
    "REL": "Religion",
    "SELF": "Self",
    "ACT": "Action",
    "AVIATION": "Aviation",
    "ROAD": "Road",
    "RAIL": "Rail",
    "PIPELINE": "Pipeline",
    "MARITIME": "Maritime",
    "EMERG": "Emergency",
    "DISCRIMINATION": "Discrimination",
    "HUMAN": "Human Rights",
    "FOOD": "Food",
    "WATER": "Water",
    "ELECTION": "Election",
    "URBAN": "Urban",
    "INFO": "Information",
    "INTERNET": "Internet",
    "AID": "Aid",
    "GENERAL": "General",
    "WMD": "Weapons of Mass Destruction",
    # Variant prefixes mapping to same category (both forms exist in GDELT data)
    "MIL": "Military",
    "MILITARY": "Military",
    "MED": "Medical",
    "MEDICAL": "Medical",
    "CRIME": "Crime",
    "CRM": "Crime",
    "POLITICAL": "Political",
    # Additional prefixes for ambiguous themes
    "SLFID": "State-Level Fragility Indicators",
    "USPEC": "US Policy Uncertainty",
}

# =============================================================================
# Acronym Expansions
# =============================================================================

ACRONYM_MAP: dict[str, str] = {
    "MSM": "Mainstream Media",
    "NGO": "Non-Governmental Organization",
    "NGOs": "Non-Governmental Organizations",
    "UN": "United Nations",
    "EU": "European Union",
    "NATO": "NATO",
    "ISIS": "ISIS",
    "ISIL": "ISIL",
    "WMD": "Weapons of Mass Destruction",
    "ICT": "Information and Communication Technology",
    "GDP": "Gross Domestic Product",
    "HIV": "HIV",
    "AIDS": "AIDS",
    "COVID": "COVID",
    "COVID19": "COVID-19",
    "LGBTQ": "LGBTQ",
    "LGBT": "LGBT",
    "POW": "Prisoner of War",
    "IDP": "Internally Displaced Person",
    "IDPs": "Internally Displaced Persons",
    "PTSD": "PTSD",
    "CRISISLEXREC": "CrisisLex Record",
}

# =============================================================================
# Concatenated Word Splits
# =============================================================================

WORD_SPLITS: dict[str, str] = {
    "POINTSOFINTEREST": "Points of Interest",
    "CLIMATECHANGE": "Climate Change",
    "ARMEDCONFLICT": "Armed Conflict",
    "STOCKMARKET": "Stock Market",
    "HUMANRIGHTS": "Human Rights",
    "HEALTHCARE": "Health Care",
    "CIVILWAR": "Civil War",
    "SOCIALMEDIA": "Social Media",
    "CYBERSECURITY": "Cyber Security",
    "SUPPLYCHAIN": "Supply Chain",
    "EXTREMEWEATHER": "Extreme Weather",
    "MASSMEDIA": "Mass Media",
    "WORLDBANK": "World Bank",
    "GENERALCRIME": "General Crime",
    "FOODSECURITY": "Food Security",
    "WATERSECURITY": "Water Security",
    "BORDERCONTROL": "Border Control",
    "BORDERWALL": "Border Wall",
    "PRICECONTROL": "Price Control",
    "PUBLICHEALTH": "Public Health",
    "MENTALHEALTH": "Mental Health",
    "DISEASEOUTBREAK": "Disease Outbreak",
    "ECONOMICCRISIS": "Economic Crisis",
    "FINANCIALCRISIS": "Financial Crisis",
    "HOUSINGCRISIS": "Housing Crisis",
    "DEBTCRISIS": "Debt Crisis",
    "REFUGEECRISIS": "Refugee Crisis",
    "MIGRANTCRISIS": "Migrant Crisis",
    "OILPRICE": "Oil Price",
    "GOLDPRICE": "Gold Price",
    "INTERESTRATE": "Interest Rate",
    "EXCHANGERATE": "Exchange Rate",
    "TAXREFORM": "Tax Reform",
    "TRADEWAR": "Trade War",
    "TRADEDEAL": "Trade Deal",
    "NUCLEARWEAPON": "Nuclear Weapon",
    "NUCLEARPOWER": "Nuclear Power",
    "SOLARPOWER": "Solar Power",
    "WINDPOWER": "Wind Power",
    "RENEWABLEENERGY": "Renewable Energy",
    "FOSSILFUEL": "Fossil Fuel",
    "ELECTRICVEHICLE": "Electric Vehicle",
    "DEVELOPMENTAID": "Development Aid",
    "PEACEBUILDING": "Peace Building",
    "RULEOFLAW": "Rule of Law",
}

# =============================================================================
# CrisisLex Category Mapping (from EMTerms-1.0.csv)
# =============================================================================

CRISISLEX_CATEGORY_MAP: dict[str, str] = {
    "C01": "Children's Well-being and Education",
    "C02": "Needs Food",
    "C03": "Mental and Physical Well-being",
    "C04": "Logistics and Transportation",
    "C05": "Need of Shelters",
    "C06": "Water and Sanitation",
    "C07": "Safety and Security",
    "C08": "Telecommunications",
    "O01": "Weather Conditions",
    "O02": "Response Agencies at Crisis",
    "O03": "Witnesses' Accounts",
    "O04": "Impact of Crisis",
    "T01": "Caution and Advice",
    "T02": "Injured People",
    "T03": "Dead People",
    "T04": "Infrastructure Damage",
    "T05": "Money Requested or Offered",
    "T06": "Supplies Needed or Offered",
    "T07": "Services Needed or Offered",
    "T08": "Missing, Found, or Trapped People",
    "T09": "Displaced, Relocated, or Evacuated",
    "T10": "Shelter and Food",
    "T11": "Updates and Sympathy",
}


def load_crisislex_terms(filepath: Path) -> dict[str, str]:
    """Load CrisisLex EMTerms CSV and build code -> name mapping."""
    mapping: dict[str, str] = {}
    with filepath.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("Category Code", "").strip()
            name = row.get("Category Name", "").strip()
            if code and name and code not in mapping:
                mapping[code] = name
    return mapping


def expand_description(text: str) -> str:
    """Expand acronyms and split concatenated words in description.

    Args:
        text: Raw description text (may be uppercase with underscores)

    Returns:
        Expanded and properly formatted description
    """
    # First check for exact matches in word splits
    text_upper = text.upper().replace(" ", "")
    if text_upper in WORD_SPLITS:
        return WORD_SPLITS[text_upper]

    # Check for acronym expansion
    if text.upper() in ACRONYM_MAP:
        return ACRONYM_MAP[text.upper()]

    # Try to split each word
    words = text.replace("_", " ").split()
    result_words = []

    for word in words:
        word_upper = word.upper()
        if word_upper in ACRONYM_MAP:
            result_words.append(ACRONYM_MAP[word_upper])
        elif word_upper in WORD_SPLITS:
            result_words.append(WORD_SPLITS[word_upper])
        else:
            # Title case the word
            result_words.append(word.title())

    return " ".join(result_words)


def parse_crisislex(theme: str, crisislex_map: dict[str, str]) -> tuple[str, str]:
    """Parse CRISISLEX_* theme to (category, description).

    Examples:
        CRISISLEX_C07_SAFETY -> ("CrisisLex", "Safety and Security")
        CRISISLEX_T03_DEAD -> ("CrisisLex", "Dead People")
        CRISISLEX_CRISISLEXREC -> ("CrisisLex", "CrisisLex Record")
    """
    # Remove prefix
    rest = theme[len("CRISISLEX_") :]

    # Check for special cases first
    if rest.upper() in ACRONYM_MAP:
        return "CrisisLex", ACRONYM_MAP[rest.upper()]

    # Try to extract category code (C01, T03, O01, etc.)
    match = re.match(r"^([COT]\d{2})_?(.*)$", rest)
    if match:
        code = match.group(1)
        # Look up in CrisisLex mapping
        if code in crisislex_map:
            return "CrisisLex", crisislex_map[code]
        if code in CRISISLEX_CATEGORY_MAP:
            return "CrisisLex", CRISISLEX_CATEGORY_MAP[code]

    # Fallback: expand and parse the name
    description = expand_description(rest)
    return "CrisisLex", description


def parse_world_bank(theme: str) -> tuple[str, str]:
    """Parse WB_* theme to (category, description).

    Examples:
        WB_696_PUBLIC_SECTOR_MANAGEMENT -> ("World Bank", "Public Sector Management")
        WB_2432_FRAGILITY_CONFLICT_AND_VIOLENCE -> ("World Bank", "Fragility Conflict and Violence")
    """
    # Remove WB_ prefix
    rest = theme[3:]

    # Split on first underscore after the numeric ID
    match = re.match(r"^(\d+)_(.+)$", rest)
    if match:
        name = match.group(2)
        description = expand_description(name)
        return "World Bank", description

    # Fallback
    return "World Bank", expand_description(rest)


def parse_taxonomy(theme: str) -> tuple[str, str]:
    """Parse TAX_* theme to (category, description).

    Examples:
        TAX_FNCACT -> ("Taxonomy", "Functional Actor")
        TAX_FNCACT_PRESIDENT -> ("Taxonomy: Functional Actor", "President")
        TAX_FNCACT_PRIME_MINISTER -> ("Taxonomy: Functional Actor", "Prime Minister")
        TAX_WORLDLANGUAGES_RUSSIAN -> ("Taxonomy: World Language", "Russian")
        TAX_DISEASE_CANCER -> ("Taxonomy: Disease", "Cancer")
    """
    # Remove TAX_ prefix
    rest = theme[4:]
    parts = rest.split("_")

    if not parts:
        return "Taxonomy", theme

    # First part is the category
    cat_key = parts[0]
    cat_name = TAX_CATEGORY_MAP.get(cat_key, expand_description(cat_key))

    if len(parts) == 1:
        # Root category: TAX_FNCACT -> "Functional Actor"
        return "Taxonomy", cat_name

    # Remaining parts are the specific item
    item_parts = parts[1:]
    item_raw = "_".join(item_parts)
    item_name = expand_description(item_raw)

    return f"Taxonomy: {cat_name}", item_name


def parse_prefix_theme(theme: str) -> tuple[str, str]:
    """Parse theme with known prefix to (category, description).

    Examples:
        ENV_CLIMATECHANGE -> ("Environment", "Climate Change")
        ECON_INFLATION -> ("Economy", "Inflation")
        NATURAL_DISASTER_EARTHQUAKE -> ("Natural Disaster", "Earthquake")
    """
    for prefix, category in PREFIX_CATEGORY_MAP.items():
        if theme.startswith(prefix + "_"):
            rest = theme[len(prefix) + 1 :]
            description = expand_description(rest)
            return category, description

    return None, None  # type: ignore[return-value]


def parse_simple_theme(theme: str) -> tuple[str, str]:
    """Parse simple theme (no prefix) to (category, description).

    Examples:
        KILL -> ("General", "Kill")
        LEADER -> ("General", "Leader")
        ARMEDCONFLICT -> ("General", "Armed Conflict")
    """
    # Check for known word splits or acronyms first
    description = expand_description(theme)
    return "General", description


def generate_theme_entry(
    theme: str, count: int, crisislex_map: dict[str, str]
) -> dict[str, str | int | None]:
    """Generate a theme entry with category and description.

    Returns dict with keys: category, description, count
    """
    category: str
    description: str

    if theme.startswith("CRISISLEX_"):
        category, description = parse_crisislex(theme, crisislex_map)
    elif theme.startswith("WB_"):
        category, description = parse_world_bank(theme)
    elif theme.startswith("TAX_"):
        category, description = parse_taxonomy(theme)
    else:
        # Try known prefixes
        result = parse_prefix_theme(theme)
        if result[0] is not None:
            category, description = result
        else:
            # Fallback to simple parsing
            category, description = parse_simple_theme(theme)

    return {
        "category": category,
        "description": description,
        "count": count,
    }


def identify_ambiguous_themes(themes: dict[str, dict]) -> list[str]:
    """Identify themes that may need LLM review for better descriptions."""
    ambiguous = []

    # Patterns that suggest ambiguity
    ambiguous_prefixes = ["SLFID_", "USPEC_"]

    # Known valid short descriptions (acronyms we've expanded)
    valid_short = set(ACRONYM_MAP.values())

    for theme, entry in themes.items():
        # Check for ambiguous prefixes
        if any(theme.startswith(p) for p in ambiguous_prefixes):
            ambiguous.append(theme)
            continue

        # Check for very short descriptions (likely acronyms)
        desc = entry.get("description", "")
        if len(desc) <= 3 and desc.isupper() and desc not in valid_short:
            ambiguous.append(theme)
            continue

        # Check for repeated words (parsing artifacts)
        # Threshold 0.5 = flag if unique words are less than half of total words
        # e.g., "Disease Disease Disease" -> 1 unique / 3 total = 0.33 < 0.5
        # This catches cases where word splitting went wrong
        words = desc.lower().split()
        if len(words) >= 2 and len(set(words)) < len(words) * 0.5:
            ambiguous.append(theme)

    return ambiguous


def read_with_encoding_fallback(filepath: Path) -> str:
    """Read file with encoding fallback for GDELT files."""
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            return filepath.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    msg = f"Could not decode {filepath}"
    raise ValueError(msg)


def convert_gkg_themes() -> None:
    """Convert LOOKUP-GKGTHEMES.TXT to JSON with descriptions."""
    # Load CrisisLex terms if available
    crisislex_path = GDELT_DOCS / "EMTerms-1.0.csv"
    crisislex_map: dict[str, str] = {}
    if crisislex_path.exists():
        crisislex_map = load_crisislex_terms(crisislex_path)
        print(f"Loaded {len(crisislex_map)} CrisisLex categories")

    # Read themes file
    themes_path = GDELT_DOCS / "LOOKUP-GKGTHEMES.txt"
    content = read_with_encoding_fallback(themes_path)
    lines = content.strip().split("\n")

    # Parse themes
    themes: dict[str, dict] = {}
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            theme = parts[0].strip()
            count = int(parts[1].strip())
            themes[theme] = generate_theme_entry(theme, count, crisislex_map)

    print(f"Parsed {len(themes)} themes")

    # Identify ambiguous themes
    ambiguous = identify_ambiguous_themes(themes)
    print(f"Identified {len(ambiguous)} potentially ambiguous themes")

    # Write main output
    output = LOOKUPS_DATA / "gkg_themes.json"
    output.write_text(json.dumps(themes, indent=2, ensure_ascii=False))
    print(f"Wrote {len(themes)} entries to {output}")

    # Write ambiguous themes for review
    if ambiguous:
        ambiguous_output = GDELT_DOCS / "gkg_themes_ambiguous.txt"
        ambiguous_data = {t: themes[t] for t in ambiguous}
        ambiguous_output.write_text(json.dumps(ambiguous_data, indent=2, ensure_ascii=False))
        print(f"Wrote {len(ambiguous)} ambiguous themes to {ambiguous_output}")

    # Print category breakdown
    categories: dict[str, int] = {}
    for entry in themes.values():
        cat = entry.get("category", "Unknown")
        # Get top-level category
        if ":" in cat:
            cat = cat.split(":")[0]
        categories[cat] = categories.get(cat, 0) + 1

    print("\nCategory breakdown:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:15]:
        print(f"  {cat}: {count:,}")


if __name__ == "__main__":
    convert_gkg_themes()
