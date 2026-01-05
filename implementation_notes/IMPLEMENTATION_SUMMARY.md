# FileSource Implementation Summary

## Overview

Implemented `FileSource` class for downloading and extracting GDELT data files from `data.gdeltproject.org`. This is a core component of the py-gdelt library that provides direct access to GDELT's raw data files.

## Files Created

### Core Implementation
- **`src/py_gdelt/sources/__init__.py`** - Sources package initialization
- **`src/py_gdelt/sources/files.py`** - Complete FileSource implementation (591 lines)
- **`src/py_gdelt/sources/README.md`** - Comprehensive documentation

### Tests
- **`tests/test_sources_files.py`** - Full test suite (565 lines)
  - 25+ test cases covering all functionality
  - Uses pytest-asyncio and respx for async HTTP mocking
  - Tests initialization, downloads, extraction, caching, security, and error handling

### Examples
- **`examples/download_gdelt_files.py`** - Working examples demonstrating:
  - Recent events download
  - Specific file download
  - Master file list retrieval
  - Custom concurrency limits

### Utilities
- **`test_runner.py`** - Quick verification script for basic functionality

## Key Features Implemented

### 1. **File Download & Extraction**
- Async HTTP downloads using httpx
- Automatic decompression (ZIP and GZIP)
- Semaphore-based concurrency control
- Progress tracking via async generators

### 2. **Intelligent Caching**
- Historical files (>30 days): Cached indefinitely (immutable data)
- Recent files: TTL-based caching (default 1 hour)
- Master file lists: Short TTL (5 minutes)
- File date extraction from URLs for cache decisions

### 3. **Security Features**
- **URL Validation**: Only allows `data.gdeltproject.org` and `api.gdeltproject.org`
- **HTTPS Enforcement**: Automatically upgrades HTTP to HTTPS
- **Zip Bomb Protection**:
  - Maximum decompressed size: 500MB
  - Maximum compression ratio: 100:1
  - Incremental decompression with safety checks
- **Path Safety**: Uses existing `validate_url()` from `_security.py`

### 4. **Error Handling**
- Graceful handling of 404s (expected for missing time slots)
- Proper exception hierarchy (APIError, DataError, SecurityError)
- Firewall pattern for concurrent downloads (one failure doesn't cancel others)
- Comprehensive logging at appropriate levels

### 5. **Date Range Support**
- Generates URLs for 15-minute intervals
- Supports all file types: export, mentions, gkg, ngrams
- Translation file support
- Date extraction from GDELT URL timestamps

## Architecture Decisions

### 1. **Async-First Design**
- Uses `asyncio.TaskGroup` for structured concurrency
- Semaphore-based rate limiting (configurable)
- Async context manager (`async with`) for resource management
- Proper client lifecycle management (owned vs external)

### 2. **Dependency Injection**
- Accepts optional `GDELTSettings`, `httpx.AsyncClient`, and `Cache` instances
- Creates defaults if not provided
- Follows SOLID principles (Dependency Inversion)

### 3. **Firewall Pattern**
```python
async def _safe_download_and_extract(self, url: str) -> tuple[str, bytes] | None:
    """Acts as firewall - catches exceptions to prevent sibling task cancellation."""
    try:
        data = await self.download_and_extract(url)
        return url, data
    except Exception as e:
        logger.exception("Failed to download %s", url)
        return None  # Swallow exception
```

This ensures that in `TaskGroup`, one failed download doesn't cancel others.

### 4. **Security Layers**
1. URL validation (allowed hosts only)
2. HTTPS enforcement
3. Decompression size checks (before extraction for ZIP, during for GZIP)
4. Compression ratio validation
5. Incremental decompression (prevents memory exhaustion)

## File Type Support

### GDELT v2 Files
- **export**: Events data (`.export.CSV.zip`)
- **mentions**: Event mentions (`.mentions.CSV.zip`)
- **gkg**: Global Knowledge Graph (`.gkg.csv.zip`)

### GDELT v3 Files
- **ngrams**: Web NGrams (`.webngrams.json.gz`)

### Translation Files
- Supported for all v2 file types
- Pattern: `.translation.export.CSV.zip`

## API Design

### Context Manager Pattern
```python
async with FileSource() as source:
    urls = await source.get_files_for_date_range(...)
    async for url, data in source.stream_files(urls):
        # Process data
```

### Streaming Pattern
```python
async for url, data in source.stream_files(urls, max_concurrent=10):
    # Data is automatically downloaded and extracted
    # Failed downloads are logged but don't stop iteration
```

### Individual Downloads
```python
# Raw download
data = await source.download_file(url)

# Download + extract
data = await source.download_and_extract(url)
```

## Testing Strategy

### Test Coverage
- **Initialization**: Default settings, custom settings, context managers
- **Master File List**: Success, caching, HTTP errors, network errors
- **Date Range**: All file types, translation files, invalid inputs
- **Downloads**: Success, 404 handling, server errors, caching
- **Extraction**: ZIP, GZIP, invalid archives, zip bombs
- **Streaming**: Concurrent downloads, failures, custom concurrency
- **Helpers**: HTTPS upgrade, date extraction

### Mocking Strategy
- Uses `respx` for HTTP mocking
- Uses `pytest.mark.asyncio` for async tests
- Uses temporary directories for cache testing

## Compliance with Requirements

### Asyncio & Concurrency ✓
- Uses `asyncio.TaskGroup` for structured concurrency
- Firewall pattern for independent tasks
- No blocking I/O (uses async httpx)
- Proper synchronization with `asyncio.Semaphore`
- Strong references to background tasks

### Type Hints ✓
- Complete type hints for all functions and methods
- Uses modern syntax (`Type | None` instead of `Optional[Type]`)
- `Literal` for file type constraints
- `Final` for constants

### Error Handling ✓
- No assertions in production code
- Catches `Exception`, not `BaseException`
- Specific exception types (APIError, DataError, SecurityError)
- Structured logging with proper levels

### Logging ✓
- Uses standard logging library
- Structured messages (no f-strings in logger calls)
- Appropriate levels (debug, info, warning, error)

### Input Validation ✓
- URL validation via security module
- Date range validation
- File type validation
- Pydantic models for settings

### Naming Conventions ✓
- snake_case for functions and variables
- PascalCase for classes
- UPPER_CASE for constants
- No built-in name overrides

### Immutability ✓
- Uses `Final` for constants
- No mutable default arguments
- Immutable data structures where appropriate

### Imports ✓
- All absolute imports
- Organized in three sections (stdlib, third-party, local)
- Modern typing imports

### Documentation ✓
- Google-style docstrings for all public methods
- Comprehensive README with examples
- Inline comments explaining WHY for complex logic

### Testing ✓
- Comprehensive test suite (565 lines)
- Uses pytest and pytest-asyncio
- Async fixtures and mocks
- High coverage of edge cases

## Known Limitations

1. **File Naming Quirk**: GDELT files have `.CSV` extension but use TAB delimiters (documented in README)
2. **15-minute Gaps**: Not all time slots have files, 404s are expected (handled gracefully)
3. **No Retry Logic**: Unlike endpoints, FileSource doesn't have automatic retries (could be added)
4. **Memory Usage**: Large files are decompressed into memory (could stream to disk)

## Future Enhancements

1. **Streaming to Disk**: Option to decompress directly to files for very large archives
2. **Retry Logic**: Add tenacity-based retries for transient failures
3. **Progress Callbacks**: Allow users to provide progress callbacks for long downloads
4. **Batch Size Control**: Automatic batching for very large date ranges
5. **Checksum Validation**: Verify file integrity if GDELT provides checksums

## Files Modified

No existing files were modified. All changes are new files in:
- `src/py_gdelt/sources/`
- `tests/`
- `examples/`

## Integration Points

The FileSource integrates with:
- **`GDELTSettings`** (config.py) - Configuration management
- **`Cache`** (cache.py) - Intelligent caching with TTL
- **Security utilities** (_security.py) - URL validation, decompression safety
- **Exception hierarchy** (exceptions.py) - Proper error types
- **httpx.AsyncClient** - Async HTTP client (dependency injection)

## Verification Steps

To verify the implementation:

1. **Run Tests**:
   ```bash
   pytest tests/test_sources_files.py -v
   ```

2. **Type Checking**:
   ```bash
   mypy src/py_gdelt/sources/files.py
   ```

3. **Linting**:
   ```bash
   ruff check src/py_gdelt/sources/files.py
   ```

4. **Basic Functionality**:
   ```bash
   python test_runner.py
   ```

5. **Examples**:
   ```bash
   python examples/download_gdelt_files.py list
   ```

## Summary

The FileSource implementation provides a robust, secure, and efficient way to download GDELT data files. It follows all Python best practices, uses modern async patterns, includes comprehensive security features, and is fully tested. The implementation is production-ready and integrates seamlessly with the existing py-gdelt infrastructure.
