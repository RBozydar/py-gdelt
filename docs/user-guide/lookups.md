# Lookup Tables

GDELT provides lookup tables for codes and classifications.

## Available Lookups

- **CAMEO** - Event codes and descriptions
- **Themes** - Theme taxonomy
- **Countries** - Country code conversions
- **Ethnic/Religious Groups** - Group classifications

## Usage

```python
async with GDELTClient() as client:
    # CAMEO codes
    cameo = client.lookups.cameo
    event = cameo.get("14")  # PROTEST

    # Country conversions
    countries = client.lookups.countries
    iso3 = countries.fips_to_iso3("US")  # USA
```

For details, see [examples](../examples/basic.md).
