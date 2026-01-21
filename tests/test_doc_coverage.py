"""Test that all public API exports are documented.

This test ensures that:
1. All models exported from py_gdelt.models are documented in docs/api/models.md
2. All exceptions exported from py_gdelt.exceptions are documented in docs/api/exceptions.md

This prevents documentation drift where new exports are added but not documented.
"""

from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

import py_gdelt.exceptions as exceptions_module
import py_gdelt.models as models_module


# Project root (relative to this test file)
PROJECT_ROOT = Path(__file__).parent.parent


def _get_documented_items(doc_file: Path, module_path: str) -> set[str]:
    """Extract documented items from a mkdocstrings-style markdown file.

    Looks for patterns like `::: py_gdelt.models.Event` and extracts the class name.

    Args:
        doc_file: Path to the markdown documentation file.
        module_path: Module path prefix to match (e.g., "py_gdelt.models").

    Returns:
        Set of class names that are documented in the file.
    """
    documented: set[str] = set()
    content = doc_file.read_text()
    prefix = f"::: {module_path}."

    for raw_line in content.splitlines():
        line = raw_line.strip()
        # Look for mkdocstrings reference pattern: ::: py_gdelt.models.ClassName
        if line.startswith(prefix):
            # Extract the class name using removeprefix for robustness
            class_name = line.removeprefix(prefix).strip()
            if class_name:  # Ensure we got a valid name
                documented.add(class_name)

    return documented


def _get_public_classes(module: ModuleType) -> set[str]:
    """Get all public class names from a module.

    Args:
        module: The module to inspect.

    Returns:
        Set of public class names (non-underscore prefixed types).
    """
    return {
        name
        for name in dir(module)
        if not name.startswith("_") and isinstance(getattr(module, name), type)
    }


def _get_public_exceptions(module: ModuleType) -> set[str]:
    """Get all public exception class names from a module.

    Args:
        module: The module to inspect.

    Returns:
        Set of public exception class names.
    """
    return {
        name
        for name in dir(module)
        if not name.startswith("_")
        and isinstance(getattr(module, name), type)
        and issubclass(getattr(module, name), Exception)
    }


# Test configurations for documentation coverage
DOC_COVERAGE_CONFIGS: list[tuple[ModuleType, str, str, str]] = [
    (models_module, "py_gdelt.models", "docs/api/models.md", "models"),
    (exceptions_module, "py_gdelt.exceptions", "docs/api/exceptions.md", "exceptions"),
]


@pytest.mark.parametrize(
    ("module", "module_path", "doc_path", "module_name"),
    DOC_COVERAGE_CONFIGS,
    ids=["models", "exceptions"],
)
def test_all_exports_documented(
    module: ModuleType,
    module_path: str,
    doc_path: str,
    module_name: str,
) -> None:
    """Verify all exported items are documented in the corresponding docs file."""
    # Get all exported names from __all__
    exported = set(module.__all__)

    # Get documented items from the docs file
    doc_file = PROJECT_ROOT / doc_path
    assert doc_file.exists(), f"Documentation file not found: {doc_file}"

    documented = _get_documented_items(doc_file, module_path)

    # Find any missing documentation
    undocumented = exported - documented
    extra_documented = documented - exported

    # Build helpful error messages
    errors: list[str] = []
    if undocumented:
        suggestions = "\n".join(f"  ::: {module_path}.{item}" for item in sorted(undocumented))
        errors.append(
            f"{module_name.title()} exported but NOT documented in {doc_path}:\n"
            f"  {sorted(undocumented)}\n"
            f"  Add these to {doc_path} with mkdocstrings syntax:\n"
            f"{suggestions}"
        )
    if extra_documented:
        errors.append(
            f"{module_name.title()} documented but NOT exported from {module_path}:\n"
            f"  {sorted(extra_documented)}\n"
            f"  Either add to {module_name}/__init__.py __all__ or remove from docs."
        )

    assert not errors, "\n\n".join(errors)


# Test configurations for __all__ validation
ALL_VALIDATION_CONFIGS: list[tuple[ModuleType, Any, str]] = [
    (models_module, _get_public_classes, "models"),
    (exceptions_module, _get_public_exceptions, "exceptions"),
]


@pytest.mark.parametrize(
    ("module", "get_actual_fn", "module_name"),
    ALL_VALIDATION_CONFIGS,
    ids=["models", "exceptions"],
)
def test_all_matches_actual_exports(
    module: ModuleType,
    get_actual_fn: Any,
    module_name: str,
) -> None:
    """Verify __all__ matches actual public classes/exceptions in the module."""
    # Get actual public items
    actual_public = get_actual_fn(module)
    declared_all = set(module.__all__)

    # Check for items in __all__ that don't exist as public classes
    in_all_not_public = declared_all - actual_public

    errors: list[str] = []
    if in_all_not_public:
        errors.append(
            f"Items in {module_name}.__all__ but not importable as public classes:\n"
            f"  {sorted(in_all_not_public)}"
        )

    # Note: We don't fail on public_not_in_all because some public classes
    # might intentionally not be exported (e.g., internal helpers)

    assert not errors, "\n\n".join(errors)
