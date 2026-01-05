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
*   Python >= 3.12
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


### PyTest & Coverage

**Configuration:** `pyproject.toml` → `[tool.pytest.ini_options]`, `[tool.coverage.*]`
