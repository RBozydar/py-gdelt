# GDELT Data Sources

This package provides different sources for accessing GDELT data.

## FileSource

Downloads GDELT data files directly from `data.gdeltproject.org`.

### Features

- **Concurrent Downloads**: Semaphore-based rate limiting with configurable concurrency
- **Automatic Decompression**: Handles ZIP and GZIP files transparently
- **Intelligent Caching**:
  - Historical files (>30 days): Cached indefinitely (immutable)
  - Recent files: TTL-based (default 1 hour)
  - Master file lists: Short TTL (5 minutes)
- **Security**:
  - URL validation (only allows `data.gdeltproject.org`)
  - Zip bomb protection (500MB max, 100:1 ratio max)
  - Decompression safety checks
- **Error Handling**: Graceful handling of missing files (404s are normal in GDELT)

### Usage

#### Basic Usage

```python
import asyncio
from datetime import datetime
from py_gdelt.sources import FileSource

async def download_gdelt_data():
    async with FileSource() as source:
        # Get URLs for a date range
        urls = await source.get_files_for_date_range(
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 2),
            file_type="export"
        )

        # Download and extract files
        async for url, data in source.stream_files(urls):
            print(f"Downloaded {url}: {len(data)} bytes")
            # Process data (TAB-delimited despite .CSV extension)

asyncio.run(download_gdelt_data())
```

#### Custom Configuration

```python
from pathlib import Path
from py_gdelt.config import GDELTSettings
from py_gdelt.sources import FileSource

settings = GDELTSettings(
    cache_dir=Path("/tmp/gdelt_cache"),
    cache_ttl=7200,  # 2 hours
    max_concurrent_downloads=20,
    timeout=60
)

async with FileSource(settings=settings) as source:
    # ... use source
```

#### Using with External HTTP Client

```python
import httpx
from py_gdelt.sources import FileSource

async with httpx.AsyncClient() as client:
    source = FileSource(client=client)
    # ... use source
    # Note: client won't be closed by FileSource
```

#### Master File List

```python
async with FileSource() as source:
    # Get all available files
    urls = await source.get_master_file_list()

    # Include translation files
    urls = await source.get_master_file_list(include_translation=True)
```

#### Individual File Download

```python
async with FileSource() as source:
    # Download raw file
    data = await source.download_file(
        "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"
    )

    # Download and extract
    data = await source.download_and_extract(
        "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"
    )
```

### File Types

FileSource supports all GDELT file types:

- **export**: Events data (`.export.CSV.zip`)
- **mentions**: Event mentions (`.mentions.CSV.zip`)
- **gkg**: Global Knowledge Graph (`.gkg.csv.zip`)
- **ngrams**: Web NGrams (`.webngrams.json.gz`) from v3 API

### URL Patterns

GDELT uses the following URL patterns:

```
# Events (v2)
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.export.CSV.zip

# Mentions (v2)
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.mentions.CSV.zip

# GKG (v2)
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.gkg.csv.zip

# NGrams (v3)
http://data.gdeltproject.org/gdeltv3/webngrams/YYYYMMDDHHMMSS.webngrams.json.gz

# Translation files
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.translation.export.CSV.zip
```

### Important Notes

1. **File Naming**: Files have `.CSV` extension but use **TAB delimiters**, not commas
2. **15-minute Granularity**: Files are published every 15 minutes, but some slots may be empty
3. **404 Errors are Normal**: Not all 15-minute time slots have data, 404s are expected
4. **HTTP Only**: `data.gdeltproject.org` only supports HTTP (SSL cert mismatch with `*.storage.googleapis.com`)
5. **Historical Data**: Files older than 30 days are cached indefinitely (immutable)

### Error Handling

```python
from py_gdelt.exceptions import APIError, DataError, SecurityError

async with FileSource() as source:
    try:
        data = await source.download_and_extract(url)
    except APIError as e:
        # Network or HTTP errors (404, 503, etc.)
        print(f"API error: {e}")
    except DataError as e:
        # Invalid archive format, parsing errors
        print(f"Data error: {e}")
    except SecurityError as e:
        # Zip bomb, invalid URL, size limits exceeded
        print(f"Security error: {e}")
```

### Security Features

FileSource implements multiple security layers:

1. **URL Validation**: Only allows `data.gdeltproject.org` domain
2. **Decompression Limits**:
   - Maximum decompressed size: 500MB
   - Maximum compression ratio: 100:1
3. **Incremental Decompression**: Checks limits while decompressing (prevents memory exhaustion)

### Performance Tips

1. **Adjust Concurrency**: Increase `max_concurrent_downloads` for faster bulk downloads
2. **Cache Configuration**: Use larger cache TTL for development, smaller for production
3. **Streaming**: Use `stream_files()` for processing multiple files efficiently
4. **External Client**: Reuse `httpx.AsyncClient` across multiple FileSource instances

### Testing

The module includes comprehensive tests:

```bash
pytest tests/test_sources_files.py -v
```

Tests cover:
- Initialization and context managers
- Master file list retrieval
- Date range URL generation
- File download and caching
- ZIP/GZIP extraction
- Security protections (zip bombs, invalid URLs)
- Concurrent streaming
- Error handling

## Future Sources

- **BigQuerySource**: Access GDELT data via Google BigQuery (planned)
- **LocalSource**: Read GDELT files from local filesystem (planned)
