# FileSource Quick Reference

## Installation & Import

```python
from py_gdelt.sources import FileSource
from py_gdelt.config import GDELTSettings
from datetime import datetime
```

## Basic Usage

### Download Files for Date Range

```python
async with FileSource() as source:
    urls = await source.get_files_for_date_range(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
        file_type="export",  # or "mentions", "gkg", "ngrams"
    )

    async for url, data in source.stream_files(urls):
        # data is bytes (TAB-delimited CSV)
        lines = data.decode("utf-8").splitlines()
        print(f"Downloaded {len(lines)} events")
```

### Download Single File

```python
async with FileSource() as source:
    # Download and extract
    data = await source.download_and_extract(
        "http://data.gdeltproject.org/gdeltv2/20240101000000.export.CSV.zip"
    )

    # Or just download (no extraction)
    raw_data = await source.download_file(url)
```

### Get Master File List

```python
async with FileSource() as source:
    urls = await source.get_master_file_list()
    print(f"Found {len(urls)} files")

    # Include translation files
    urls = await source.get_master_file_list(include_translation=True)
```

## Configuration

### Custom Settings

```python
from pathlib import Path

settings = GDELTSettings(
    cache_dir=Path("/tmp/gdelt"),
    cache_ttl=7200,  # 2 hours
    max_concurrent_downloads=20,
    timeout=60,
)

async with FileSource(settings=settings) as source:
    # Use source
```

### Shared HTTP Client

```python
import httpx

async with httpx.AsyncClient() as client:
    source = FileSource(client=client)
    # Client lifecycle managed externally
```

### Custom Concurrency

```python
async with FileSource() as source:
    urls = await source.get_files_for_date_range(...)

    # Override default concurrency
    async for url, data in source.stream_files(urls, max_concurrent=5):
        # Process data
```

## File Types

| Type | Description | Extension | API Version |
|------|-------------|-----------|-------------|
| `export` | Events data | `.export.CSV.zip` | v2 |
| `mentions` | Event mentions | `.mentions.CSV.zip` | v2 |
| `gkg` | Global Knowledge Graph | `.gkg.csv.zip` | v2 |
| `ngrams` | Web NGrams | `.webngrams.json.gz` | v3 |

## Error Handling

```python
from py_gdelt.exceptions import APIError, DataError, SecurityError

async with FileSource() as source:
    try:
        data = await source.download_and_extract(url)
    except APIError as e:
        # Network errors, HTTP errors (404, 503, etc.)
        print(f"API error: {e}")
    except DataError as e:
        # Invalid archive, parsing errors
        print(f"Data error: {e}")
    except SecurityError as e:
        # Zip bomb, invalid URL, size limits
        print(f"Security error: {e}")
```

## URL Patterns

### GDELT v2
```
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.export.CSV.zip
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.mentions.CSV.zip
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.gkg.csv.zip
```

### GDELT v3
```
http://data.gdeltproject.org/gdeltv3/webngrams/YYYYMMDDHHMMSS.webngrams.json.gz
```

### Translation Files
```
http://data.gdeltproject.org/gdeltv2/YYYYMMDDHHMMSS.translation.export.CSV.zip
```

## Important Notes

1. **TAB Delimiters**: Files have `.CSV` extension but use TAB delimiters, not commas
2. **15-minute Slots**: Files published every 15 minutes, but some slots may be empty (404s are normal)
3. **HTTP Only**: `data.gdeltproject.org` only supports HTTP (SSL cert mismatch)
4. **Caching**: Historical files (>30 days) cached indefinitely, recent files use TTL
5. **Security**: Only allows `data.gdeltproject.org` domain, enforces size limits

## Advanced Examples

### Process Files in Batches

```python
async with FileSource() as source:
    urls = await source.get_files_for_date_range(...)

    batch_size = 100
    for i in range(0, len(urls), batch_size):
        batch_urls = urls[i:i + batch_size]

        async for url, data in source.stream_files(batch_urls):
            # Process batch
            pass
```

### Filter by Translation Files

```python
async with FileSource() as source:
    urls = await source.get_files_for_date_range(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 2),
        file_type="export",
        include_translation=True,
    )

    # Separate regular and translation files
    regular_urls = [u for u in urls if "translation" not in u]
    trans_urls = [u for u in urls if "translation" in u]
```

### Save to Disk

```python
from pathlib import Path

output_dir = Path("gdelt_data")
output_dir.mkdir(exist_ok=True)

async with FileSource() as source:
    async for url, data in source.stream_files(urls):
        # Extract filename from URL
        filename = url.split("/")[-1].replace(".zip", "")

        # Save to disk
        (output_dir / filename).write_bytes(data)
```

## Performance Tips

1. **Increase Concurrency**: For faster bulk downloads
   ```python
   async for url, data in source.stream_files(urls, max_concurrent=20):
       ...
   ```

2. **Adjust Cache TTL**: Larger for development, smaller for production
   ```python
   settings = GDELTSettings(cache_ttl=86400)  # 24 hours
   ```

3. **Reuse Client**: Share httpx client across multiple sources
   ```python
   async with httpx.AsyncClient() as client:
       source1 = FileSource(client=client)
       source2 = FileSource(client=client)
   ```

4. **Filter Before Download**: Use master list to filter files
   ```python
   all_urls = await source.get_master_file_list()
   filtered_urls = [u for u in all_urls if "20240101" in u]
   ```

## Common Patterns

### Recent Data (Last N Hours)

```python
from datetime import datetime, timedelta

async with FileSource() as source:
    end = datetime.utcnow()
    start = end - timedelta(hours=6)

    urls = await source.get_files_for_date_range(
        start_date=start,
        end_date=end,
        file_type="export",
    )
```

### Specific Day

```python
async with FileSource() as source:
    day = datetime(2024, 1, 15)

    urls = await source.get_files_for_date_range(
        start_date=day,
        end_date=day + timedelta(days=1),
        file_type="export",
    )
```

### All File Types for Time Range

```python
from typing import Literal, get_args

async with FileSource() as source:
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 1, 1, 0)  # 1 hour

    for file_type in ["export", "mentions", "gkg"]:
        urls = await source.get_files_for_date_range(
            start_date=start,
            end_date=end,
            file_type=file_type,
        )

        print(f"{file_type}: {len(urls)} files")
```

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("py_gdelt.sources.files")
logger.setLevel(logging.DEBUG)
```

### Check Cache

```python
async with FileSource() as source:
    cache_size = source.cache.size()
    print(f"Cache size: {cache_size / (1024*1024):.2f} MB")

    # Clear old cache entries
    cleared = source.cache.clear(before=datetime(2024, 1, 1))
    print(f"Cleared {cleared} entries")
```

### Inspect URLs

```python
async with FileSource() as source:
    urls = await source.get_files_for_date_range(...)

    for url in urls[:5]:  # First 5
        date = FileSource._extract_date_from_url(url)
        print(f"{url} -> {date}")
```
