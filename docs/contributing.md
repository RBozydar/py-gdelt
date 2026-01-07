# Contributing

Contributions to py-gdelt are welcome!

## Development Setup

```bash
# Clone repository
git clone https://github.com/rbwasilewski/py-gdelt.git
cd py-gdelt

# Install development dependencies
pip install -e ".[dev,bigquery,pandas]"
```

## Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests (requires live API access)
pytest tests/integration/ -m integration

# With coverage
pytest --cov=py_gdelt tests/
```

## Code Quality

```bash
# Linting
ruff check .

# Type checking
mypy .

# Format code
ruff format .
```

## Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write tests for new features
- Update documentation
- Use meaningful commit messages

## Pull Requests

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Run quality checks
7. Submit pull request

## Reporting Issues

Use GitHub issues for:
- Bug reports
- Feature requests
- Documentation improvements

Include:
- Python version
- py-gdelt version
- Minimal reproduction code
- Expected vs actual behavior

## License

By contributing, you agree your contributions will be licensed under the MIT License.
