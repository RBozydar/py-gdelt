# Configuration

Configure py-gdelt using environment variables, TOML files, or programmatic settings.

## Environment Variables

Set environment variables to configure default behavior:

```
# Timeouts and retries
export GDELT_TIMEOUT=60
export GDELT_MAX_RETRIES=5

# Caching
export GDELT_CACHE_DIR=/path/to/cache
export GDELT_CACHE_TTL=3600

# BigQuery
export GDELT_BIGQUERY_PROJECT=my-project
export GDELT_BIGQUERY_CREDENTIALS=/path/to/credentials.json

# Behavior
export GDELT_FALLBACK_TO_BIGQUERY=true
export GDELT_VALIDATE_CODES=true
export GDELT_MAX_CONCURRENT_DOWNLOADS=10
```

## TOML Configuration

Create a `gdelt.toml` file:

```
[gdelt]
timeout = 60
max_retries = 5
cache_dir = "/path/to/cache"
cache_ttl = 3600
fallback_to_bigquery = true
validate_codes = true
max_concurrent_downloads = 10

[gdelt.bigquery]
project = "my-project"
credentials = "/path/to/credentials.json"
```

Load it with:

```
from pathlib import Path
from py_gdelt import GDELTClient

config_path = Path("gdelt.toml")
async with GDELTClient(config_path=config_path) as client:
    ...
```

## Programmatic Settings

Use `GDELTSettings` for full control:

```
from pathlib import Path
from py_gdelt import GDELTClient, GDELTSettings

settings = GDELTSettings(
    # Timeouts and retries
    timeout=60,
    max_retries=5,

    # Caching
    cache_dir=Path.home() / ".cache" / "gdelt",
    cache_ttl=3600,

    # BigQuery
    bigquery_project="my-project",
    bigquery_credentials=Path("/path/to/credentials.json"),

    # Behavior
    fallback_to_bigquery=True,
    validate_codes=True,
    max_concurrent_downloads=10,
)

async with GDELTClient(settings=settings) as client:
    ...
```

## Configuration Options

### Timeouts

- **timeout** (int): HTTP request timeout in seconds. Default: `30`
- **connect_timeout** (int): Connection timeout in seconds. Default: `10`

### Retries

- **max_retries** (int): Maximum retry attempts. Default: `3`
- **retry_backoff** (float): Backoff multiplier for retries. Default: `2.0`

### Caching

- **cache_dir** (Path): Directory for cached files. Default: `~/.cache/gdelt`
- **cache_ttl** (int): Cache time-to-live in seconds. Default: `3600` (1 hour)
- **use_cache** (bool): Enable/disable caching. Default: `True`

### BigQuery

- **bigquery_project** (str): Google Cloud project ID. Default: `None`
- **bigquery_credentials** (Path): Path to credentials JSON. Default: `None`
- **fallback_to_bigquery** (bool): Use BigQuery when file sources fail. Default: `False`

### Performance

- **max_concurrent_downloads** (int): Max parallel file downloads. Default: `5`
- **chunk_size** (int): Download chunk size in bytes. Default: `8192`

### Validation

- **validate_codes** (bool): Validate CAMEO/country codes. Default: `False`
- **strict_mode** (bool): Raise errors on invalid codes. Default: `False`

## Priority Order

Configuration is loaded in this order (later overrides earlier):

1. Default values
1. Environment variables
1. TOML configuration file
1. Programmatic `GDELTSettings`

## BigQuery Setup

For BigQuery access:

1. Install dependencies: `pip install py-gdelt[bigquery]`
1. Create Google Cloud project
1. Enable BigQuery API
1. Create service account and download credentials
1. Set credentials path:

```
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

Or in code:

```
settings = GDELTSettings(
    bigquery_project="my-project",
    bigquery_credentials=Path("/path/to/credentials.json"),
    fallback_to_bigquery=True,
)
```

## Best Practices

- Use environment variables for sensitive data (credentials)
- Use TOML for team-shared configuration
- Use programmatic settings for runtime customization
- Enable caching in development, configure carefully in production
- Set appropriate timeouts for your network conditions
- Enable BigQuery fallback for production reliability
