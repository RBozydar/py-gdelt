## 1. Overview & Goals
**ALWAYS** use the @agent-python-coder to implement Python code changes.

## Quick Start for Contributors

**Before committing any changes, ALWAYS run:**
```bash
make ci  # Runs lint + typecheck + tests with coverage
```

### 1.1 Project Purpose

A comprehensive Python client library for the GDELT (Global Database of Events, Language, and Tone) project, providing unified access to all GDELT data sources with a modern, type-safe API.

### 1.2 Goals

- **Unified Interface**: Single client covering all 6 REST APIs, 3 database tables, and NGrams dataset
- **Version Normalization**: Transparent handling of GDELT v1/v2 differences with normalized output
- **Resilience**: Automatic fallback to BigQuery when APIs fail or rate limit
- **Modern Python**: 3.11+, Async-first, Pydantic models, type hints throughout
- **Streaming**: Generator-based iteration for large datasets with memory efficiency
- **Developer Experience**: Clear errors, progress indicators, comprehensive lookups


## Development Setup

### Prerequisites
*   Python >= 3.11
*   `uv` 


### Testing
This project uses `pytest` with strict coverage requirements.
```bash
# Run tests
make test

# Run tests with coverage report
make coverage

# Run all CI checks (lint + typecheck + coverage)
make ci
```

## Code Quality Standards

This project enforces strict code quality standards to ensure consistency and maintainability.
**NEVER bypass any rules linting rules without explicit approval from the user.**

### Ruff (Linting & Formatting)

**Configuration:** `pyproject.toml` → `[tool.ruff]`

**Commands:**
```bash
# Format code (auto-fix)
make fmt

# Lint without auto-fix
make lint

# Or directly with ruff
uvx ruff check .
uvx ruff format .
```

#### Linting Philosophy

All ignored linting rules are categorized and documented in `pyproject.toml`:

**Rule Categories:**

1. **PERMANENT** (5 rules) - Justified by project architecture
   - ARG002, S608, PLR0913, UP046, UP047
   - UP046/UP047 ignored for Python 3.11 compatibility (no PEP 695 syntax)
   - These violations are intentional and correct for this codebase

2. **INTENTIONAL STYLE** (2 rules) - Keep ignored
   - PLR2004 (38 violations) - HTTP codes, column counts are self-documenting
   - TRY003 (35 violations) - Descriptive exception messages preferred

**Process:**

1. **Adding new ignores:** Requires PR approval, category assignment, and documentation
2. **Quarterly review:** Re-evaluate all ignores every Q1/Q2/Q3/Q4


### MyPy (Type Checking)

**Configuration:** `pyproject.toml` → `[tool.mypy]`

*   **Strict mode:** Enabled for production code (all strict checks active)
*   **Pydantic plugin:** Enabled for proper Pydantic model validation
*   **Incremental caching:** `.mypy_cache/` for fast re-checks
*   **Target:** Python 3.12+


**Commands:**
```bash
# Type check production code only (recommended)
make typecheck

# Or directly with mypy
uv run mypy deep_research
```


### Docstrings (pydoclint + interrogate)

**Configuration:** `pyproject.toml` → `[tool.pydoclint]`, `[tool.interrogate]`

**Style:** Google-style docstrings

**Commands:**
```bash
# Check docstring coverage and quality
make doc-coverage
```

#### Docstring Rules

1. **Class docstrings** - Document the class, not `__init__`
   - Put all documentation in the class docstring (description, Args, Attributes, Examples)
   - Do NOT add a separate docstring to `__init__()` (DOC301 violation)
   - Include an `Attributes:` section only for public class/instance attributes (not private `_foo`)

2. **Arguments** - Must match function signature exactly
   - Document all parameters (except `self`/`cls`)
   - Order must match the function signature
   - Types are in signatures, not docstrings (we use type hints)

3. **Returns/Yields** - Must match return annotation
   - For generators/iterators, use `Yields:` with the yield type: `Yields:\n    TypeName: Description`
   - For regular returns, use `Returns:` with the return type
   - If method returns Iterator but uses `yield`, use `Yields:` not `Returns:`

4. **Raises** - Only document exceptions actually raised in the method body
   - `skip-checking-raises = true` is configured, so you MAY document exceptions raised by called methods
   - But be accurate about what the method itself raises

#### Example (Correct)

```python
class MyClient:
    """Client for accessing the API.

    Provides methods for querying and streaming data.

    Args:
        base_url: The API base URL.
        timeout: Request timeout in seconds.

    Attributes:
        BASE_URL: Default API endpoint URL.
    """

    BASE_URL: str = "https://api.example.com"

    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self.base_url = base_url
        self.timeout = timeout

    def fetch(self, query: str, limit: int = 100) -> list[dict[str, Any]]:
        """Fetch data from the API.

        Args:
            query: The search query string.
            limit: Maximum number of results to return.

        Returns:
            List of result dictionaries.

        Raises:
            APIError: If the API request fails.
        """
        ...

    def stream(self, query: str) -> Iterator[dict[str, Any]]:
        """Stream results from the API.

        Args:
            query: The search query string.

        Yields:
            dict[str, Any]: Individual result dictionaries.
        """
        ...
```

#### Common Mistakes to Avoid

- ❌ Adding docstring to `__init__()` - use class docstring instead
- ❌ Documenting private attributes (`_foo`) in Attributes section
- ❌ Documenting args not in the signature
- ❌ Missing args that are in the signature
- ❌ Wrong yield type in `Yields:` section (must match Iterator/Generator type param)
- ❌ Using `Returns:` for methods that yield (use `Yields:` instead)


### PyTest & Coverage

**Configuration:** `pyproject.toml` → `[tool.pytest.ini_options]`, `[tool.coverage.*]`


### Multi-Version Python Testing

The CI pipeline tests against multiple Python versions to ensure broad compatibility:

**Supported Versions:** Python 3.11, 3.12, 3.13, 3.14

**CI Matrix:** `.github/workflows/ci.yml` → `test.strategy.matrix.python-version`

**Compatibility Guidelines:**
- **No PEP 695 syntax** - Use `Generic[T]` instead of `class Foo[T]:` for Python 3.11 compatibility
- **Use `from __future__ import annotations`** - Enables modern type syntax on older Python versions
- All dependencies must support Python 3.11+

**Testing locally on a specific version:**
```bash
# Test on Python 3.11
uv sync --all-extras --python 3.11 && uv run --python 3.11 pytest tests/

# Test on Python 3.14
uv sync --all-extras --python 3.14 && uv run --python 3.14 pytest tests/
```
