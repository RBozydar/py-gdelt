.PHONY: help fmt lint typecheck test coverage doc-coverage ci verify install clean commit bump-version changelog integration integration-schema-drift

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies with uv
	uv sync --all-extras

fmt:  ## Format code with ruff
	uvx ruff format src/py_gdelt
	uvx ruff check src/py_gdelt --fix

lint:  ## Lint code with ruff (no auto-fix)
	uvx ruff check .
	uvx ruff format --check .

typecheck:  ## Type check with mypy
	uv run mypy src/py_gdelt

test:  ## Run tests with pytest
	uv run pytest tests/

coverage:  ## Run tests with coverage report
	uv run pytest -m "not integration" --cov=src/py_gdelt --cov-report=html --cov-report=term tests/
	@echo "HTML coverage report: htmlcov/index.html"

doc-coverage:  ## Check documentation coverage
	uv run interrogate -vv src/py_gdelt
	uv run pydoclint --style=google src/py_gdelt

ci:  ## Run all CI checks (lint, typecheck, coverage)
	@echo "=== Running Linting ==="
	$(MAKE) lint
	@echo "\n=== Running Type Checking ==="
	$(MAKE) typecheck
	@echo "\n=== Running Tests with Coverage ==="
	$(MAKE) coverage
	@echo "\n=== All CI checks passed! ==="

verify: ci  ## Alias for ci target (backward compatibility)

clean:  ## Clean generated files
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

commit:  ## Interactive conventional commit (requires commitizen)
	uv run cz commit

bump-version:  ## Bump version based on commits
	uv run cz bump

changelog:  ## Generate changelog
	uv run cz changelog

integration:  ## Run all integration tests (requires network)
	uv run pytest tests/integration/ -v -m integration

integration-schema-drift:  ## Run schema drift detection tests
	uv run pytest tests/integration/test_schema_drift.py -v
