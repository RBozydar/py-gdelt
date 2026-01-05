# Installation

## Requirements

- Python 3.12 or higher
- pip (Python package manager)

## Basic Installation

Install py-gdelt using pip:

```bash
pip install py-gdelt
```

This installs the core library with support for:
- Events, Mentions, GKG endpoints (file-based)
- NGrams endpoint
- All REST APIs (DOC, GEO, Context, TV, TVAI)
- Lookup tables

## Optional Dependencies

### BigQuery Support

For BigQuery data access and automatic fallback:

```bash
pip install py-gdelt[bigquery]
```

This adds:
- `google-cloud-bigquery>=3.0`
- Ability to query GDELT BigQuery datasets
- Automatic fallback when file sources fail

### Pandas Integration

For data analysis and manipulation:

```bash
pip install py-gdelt[pandas]
```

This adds:
- `pandas>=2.0`
- DataFrame conversion utilities
- Easier data manipulation

### All Optional Dependencies

Install everything:

```bash
pip install py-gdelt[bigquery,pandas]
```

## Development Installation

For contributing to py-gdelt:

```bash
# Clone the repository
git clone https://github.com/rbwasilewski/py-gdelt.git
cd py-gdelt

# Install in editable mode with dev dependencies
pip install -e ".[dev,bigquery,pandas]"
```

Development dependencies include:
- pytest for testing
- pytest-asyncio for async tests
- pytest-cov for coverage
- pytest-timeout for test timeouts
- mypy for type checking
- ruff for linting
- respx for HTTP mocking

## Verification

Verify your installation:

```python
import py_gdelt
print(py_gdelt.__version__)

from py_gdelt import GDELTClient
print("Installation successful!")
```

## Upgrading

Upgrade to the latest version:

```bash
pip install --upgrade py-gdelt
```

## Uninstallation

Remove py-gdelt:

```bash
pip uninstall py-gdelt
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Configuration](configuration.md)
- [Examples](../examples/index.md)
