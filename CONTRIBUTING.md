# Contributing to py-gdelt

Thank you for your interest in contributing to py-gdelt! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/py-gdelt.git
   cd py-gdelt
   ```

2. **Install dependencies:**
   ```bash
   uv sync --all-extras
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install --install-hooks
   ```

## Development Workflow

### Making Changes

1. Create a new branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. Make your changes following the code standards below

3. Run all checks locally:
   ```bash
   make check  # Runs lint, typecheck, test, doc-coverage
   ```

4. Commit your changes using conventional commits (see below)

5. Push and create a pull request

### Available Make Targets

Run `make help` to see all available targets:

- `make install` - Install dependencies
- `make lint` - Run linting checks
- `make fmt` - Format code
- `make typecheck` - Run type checking
- `make test` - Run tests
- `make coverage` - Run tests with coverage report
- `make doc-coverage` - Check documentation coverage
- `make commit` - Interactive conventional commit helper
- `make bump-version` - Bump version based on commits
- `make changelog` - Generate changelog from commits
- `make clean` - Clean generated files

## Commit Message Format

This project follows [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that don't affect code meaning (white-space, formatting, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to CI configuration files and scripts
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

### Examples

```bash
feat: add GDELT event parser for GKG records
fix: correct timezone handling in date parsing
docs: update API documentation for query builder
test: add integration tests for BigQuery connector
refactor: simplify error handling in HTTP client
perf: optimize database query performance
ci: add documentation coverage enforcement
```

### Interactive Commit Helper

Use the interactive commit helper to ensure proper formatting:

```bash
make commit
```

This will guide you through creating a properly formatted commit message.

### Commit Message Rules

- Use lowercase for type and description
- Keep the header (first line) under 100 characters
- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Don't end the subject line with a period
- Separate subject from body with a blank line
- Wrap the body at 72 characters
- Use the body to explain what and why vs. how

## Code Standards

### Type Hints

All public functions and methods must have complete type hints:

```python
def fetch_events(
    start_date: datetime,
    end_date: datetime,
    *,
    limit: int | None = None
) -> list[Event]:
    """Fetch GDELT events within date range."""
    ...
```

### Docstrings

Use Google-style docstrings for all public functions, classes, and modules:

```python
def parse_event(data: dict[str, Any]) -> Event:
    """Parse raw GDELT event data into Event model.

    Args:
        data: Raw event data dictionary from GDELT API.

    Returns:
        Parsed Event instance.

    Raises:
        ValidationError: If data doesn't match expected schema.
    """
    ...
```

### Code Quality

- **Line length**: Maximum 100 characters
- **Formatting**: Ruff (automatically enforced)
- **Linting**: Ruff with strict rules
- **Type checking**: MyPy in strict mode
- **Test coverage**: Minimum 80% overall coverage
- **Documentation coverage**: Minimum 90% docstring coverage

All these checks run automatically via pre-commit hooks and CI.

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run only unit tests (fast)
uv run pytest tests/unit

# Run only integration tests
uv run pytest tests/integration
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Mark integration tests with `@pytest.mark.integration`
- Aim for high test coverage
- Use descriptive test names
- Include docstrings explaining what the test validates

Example:

```python
import pytest
from py_gdelt import EventParser


def test_parse_event_with_valid_data():
    """Test that EventParser correctly parses valid event data."""
    data = {...}
    event = EventParser.parse(data)
    assert event.id == "12345"
    assert event.date == datetime(2024, 1, 1)


@pytest.mark.integration
def test_fetch_events_from_api():
    """Test fetching events from live GDELT API."""
    ...
```

## Pull Request Process

1. **Update documentation**: If adding features, update relevant documentation
2. **Add tests**: New features and bug fixes should include tests
3. **Update changelog**: Add entry to CHANGELOG.md if using manual tracking
4. **Ensure CI passes**: All checks must pass before merge
5. **Get review**: Wait for maintainer review and address feedback
6. **Squash commits**: PRs may be squashed on merge

### PR Title Format

PR titles must follow Conventional Commits format (automatically validated):

✅ Good:
- `feat: add support for GKG v2 format`
- `fix: handle timezone conversion errors`
- `docs: improve API reference examples`

❌ Bad:
- `Feature: Add GKG support` (capitalized type)
- `Added new feature` (not following format)
- `WIP: working on it` (not descriptive)

## Versioning

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible new features
- **PATCH**: Backward-compatible bug fixes

Version bumps are automated based on conventional commits:

- `feat:` commits trigger MINOR version bump
- `fix:` commits trigger PATCH version bump
- `BREAKING CHANGE:` in footer triggers MAJOR version bump

## Maintaining Lookup Data

### Regenerating Country Codes

The `countries.json` file contains FIPS-to-ISO country code mappings used by GDELT. This data is generated from the `geonamescache` package (a dev dependency).

**When to regenerate:** The FIPS 10-4 standard was withdrawn by NIST in 2008, so the data is essentially frozen. Regeneration should only be needed if `geonamescache` fixes errors or adds new territories.

**To regenerate `countries.json`:**

```bash
uv run python -c "
from geonamescache import GeonamesCache
import json

gc = GeonamesCache()
countries = gc.get_countries()

continent_to_region = {
    'AF': 'Africa', 'AS': 'Asia', 'EU': 'Europe',
    'NA': 'North America', 'SA': 'South America',
    'OC': 'Oceania', 'AN': 'Antarctica',
}

middle_east = ['IR', 'IZ', 'IS', 'SA', 'AE', 'KU', 'BA', 'QA', 'LE', 'SY', 'JO', 'YM', 'MU']

output = {}
for iso2, data in countries.items():
    fips = data.get('fips')
    if not fips:
        continue
    region = continent_to_region.get(data.get('continentcode'), 'Other')
    if fips in middle_east:
        region = 'Middle East'
    output[fips] = {
        'iso3': data.get('iso3'),
        'iso2': data.get('iso'),
        'name': data.get('name'),
        'full_name': None,
        'region': region,
    }

output = dict(sorted(output.items()))
print(json.dumps(output, indent=2))
" > src/py_gdelt/lookups/data/countries.json
```

After regeneration, run `make ci` to verify the changes don't break any tests.

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about development
- Suggestions for improvements

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).
