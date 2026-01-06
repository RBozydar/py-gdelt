# Fix Docstring Violations Plan

## Summary
Fix 123 pydoclint violations (after ignoring DOC502) across the codebase and add pre-commit hooks for prevention.

## Current State
- **interrogate**: 99.5% (1 missing docstring in `utils/dedup.py`)
- **pydoclint**: 173 violations, 123 after ignoring DOC502
- **CI**: Already has doc-coverage job (will fail until fixed)
- **Pre-commit**: Missing pydoclint/interrogate hooks

## Violations to Fix (123 total)

| Code | Count | Fix Approach |
|------|-------|--------------|
| DOC404 | 23 | Add/fix Yields type in docstring |
| DOC301 | 19 | Merge `__init__` docstring into class docstring |
| DOC603 | 15 | Update class Attributes section |
| DOC103 | 15 | Add missing args to docstring |
| DOC101 | 14 | Add missing args to docstring |
| DOC503 | 11 | Update Raises section to match actual exceptions |
| DOC602 | 9 | Remove extra attrs from class docstring |
| DOC601 | 6 | Add missing attrs to class docstring |
| DOC201 | 5 | Fix Returns section |
| DOC403 | 4 | Fix Yields documentation |
| DOC501 | 2 | Add Raises section for actual exceptions |

## Implementation Steps

### Step 1: Configure pydoclint to ignore DOC502
Edit `pyproject.toml`:
```toml
[tool.pydoclint]
skip = ["DOC502"]  # Allow Raises sections for delegated/inherited exceptions
```

### Step 2: Fix violations by file (prioritized by violation count)

**High priority (many violations):**
1. `src/py_gdelt/sources/fetcher.py` - ~20 violations
2. `src/py_gdelt/endpoints/*.py` - ~30 violations across files
3. `src/py_gdelt/models/*.py` - ~15 violations
4. `src/py_gdelt/sources/files.py` - ~10 violations

**Medium priority:**
5. `src/py_gdelt/client.py` - ~8 violations
6. `src/py_gdelt/config.py` - ~6 violations
7. `src/py_gdelt/filters.py` - ~8 violations
8. `src/py_gdelt/lookups/*.py` - ~8 violations

**Low priority:**
9. `src/py_gdelt/cache.py` - ~3 violations
10. `src/py_gdelt/utils/*.py` - ~5 violations
11. `src/py_gdelt/parsers/*.py` - ~4 violations
12. `src/py_gdelt/exceptions.py` - ~4 violations

### Step 3: Add missing docstring
- Add docstring to function in `src/py_gdelt/utils/dedup.py` (interrogate fix)

### Step 4: Add pre-commit hooks
Add to `.pre-commit-config.yaml`:
```yaml
  - repo: local
    hooks:
      - id: interrogate
        name: interrogate
        entry: uv run interrogate -vv src/py_gdelt
        language: system
        pass_filenames: false
        types: [python]
      - id: pydoclint
        name: pydoclint
        entry: uv run pydoclint --style=google src/py_gdelt
        language: system
        pass_filenames: false
        types: [python]
```

### Step 5: Update CLAUDE.md with Docstring Guidelines

Add a new section to `CLAUDE.md` under "Code Quality Standards":

```markdown
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
   - Put all documentation in the class docstring
   - Do NOT add a separate docstring to `__init__()` (DOC301)
   - Include an `Attributes:` section listing all public attributes

2. **Arguments** - Must match function signature exactly
   - Document all parameters (except `self`/`cls`)
   - Order must match the function signature
   - Types are in signatures, not docstrings (we use type hints)

3. **Returns/Yields** - Must match return annotation
   - For generators, use `Yields:` with the yield type
   - For regular returns, use `Returns:` with the return type

4. **Raises** - Only document exceptions actually raised in the method body
   - DOC502 is ignored: you MAY document exceptions raised by called methods
   - If you document Raises, ensure it matches actual `raise` statements

#### Example (Correct)

```python
class MyClient:
    """Client for accessing the API.

    Provides methods for querying and streaming data.

    Attributes:
        base_url: The API base URL.
        timeout: Request timeout in seconds.
    """

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
- ❌ Documenting args not in the signature
- ❌ Missing args that are in the signature
- ❌ Wrong yield type in `Yields:` section
- ❌ Documenting `Raises:` for exceptions not raised in the method body
```

### Step 6: Verify
- Run `make doc-coverage` to confirm all violations fixed
- Run `make ci` to ensure full CI passes

## Files to Modify

### Configuration
- `pyproject.toml` - Add DOC502 to skip list
- `.pre-commit-config.yaml` - Add interrogate + pydoclint hooks
- `CLAUDE.md` - Add docstring guidelines section

### Source Files (docstring fixes)
- `src/py_gdelt/cache.py`
- `src/py_gdelt/client.py`
- `src/py_gdelt/config.py`
- `src/py_gdelt/exceptions.py`
- `src/py_gdelt/filters.py`
- `src/py_gdelt/endpoints/base.py`
- `src/py_gdelt/endpoints/context.py`
- `src/py_gdelt/endpoints/doc.py`
- `src/py_gdelt/endpoints/events.py`
- `src/py_gdelt/endpoints/geo.py`
- `src/py_gdelt/endpoints/gkg.py`
- `src/py_gdelt/endpoints/mentions.py`
- `src/py_gdelt/endpoints/ngrams.py`
- `src/py_gdelt/endpoints/tv.py`
- `src/py_gdelt/lookups/cameo.py`
- `src/py_gdelt/lookups/countries.py`
- `src/py_gdelt/lookups/models.py`
- `src/py_gdelt/lookups/themes.py`
- `src/py_gdelt/models/articles.py`
- `src/py_gdelt/models/common.py`
- `src/py_gdelt/models/events.py`
- `src/py_gdelt/models/gkg.py`
- `src/py_gdelt/models/ngrams.py`
- `src/py_gdelt/parsers/events.py`
- `src/py_gdelt/parsers/gkg.py`
- `src/py_gdelt/parsers/mentions.py`
- `src/py_gdelt/parsers/ngrams.py`
- `src/py_gdelt/sources/bigquery.py`
- `src/py_gdelt/sources/fetcher.py`
- `src/py_gdelt/sources/files.py`
- `src/py_gdelt/utils/dedup.py`
- `src/py_gdelt/utils/streaming.py`
