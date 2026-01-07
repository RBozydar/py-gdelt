"""Test that all public API exports are documented.

This test ensures that:
1. All models exported from py_gdelt.models are documented in docs/api/models.md
2. All exceptions exported from py_gdelt.exceptions are documented in docs/api/exceptions.md

This prevents documentation drift where new exports are added but not documented.
"""

from pathlib import Path

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
    documented = set()
    content = doc_file.read_text()

    for raw_line in content.splitlines():
        line = raw_line.strip()
        # Look for mkdocstrings reference pattern: ::: py_gdelt.models.ClassName
        if line.startswith(f"::: {module_path}."):
            # Extract the class name after the module path
            class_name = line.split(".")[-1]
            documented.add(class_name)

    return documented


def test_all_models_documented() -> None:
    """Verify all exported models are documented in docs/api/models.md."""
    # Get all exported model names
    exported_models = set(models_module.__all__)

    # Get documented models from the docs file
    models_doc = PROJECT_ROOT / "docs" / "api" / "models.md"
    assert models_doc.exists(), f"Documentation file not found: {models_doc}"

    documented_models = _get_documented_items(models_doc, "py_gdelt.models")

    # Find any missing documentation
    undocumented = exported_models - documented_models
    extra_documented = documented_models - exported_models

    # Build helpful error messages
    errors = []
    if undocumented:
        errors.append(
            f"Models exported but NOT documented in docs/api/models.md:\n"
            f"  {sorted(undocumented)}\n"
            f"  Add these to docs/api/models.md with mkdocstrings syntax:\n"
            + "\n".join(f"  ::: py_gdelt.models.{m}" for m in sorted(undocumented))
        )
    if extra_documented:
        errors.append(
            f"Models documented but NOT exported from py_gdelt.models:\n"
            f"  {sorted(extra_documented)}\n"
            f"  Either add to models/__init__.py __all__ or remove from docs."
        )

    assert not errors, "\n\n".join(errors)


def test_all_exceptions_documented() -> None:
    """Verify all exported exceptions are documented in docs/api/exceptions.md."""
    # Get all exported exception names
    exported_exceptions = set(exceptions_module.__all__)

    # Get documented exceptions from the docs file
    exceptions_doc = PROJECT_ROOT / "docs" / "api" / "exceptions.md"
    assert exceptions_doc.exists(), f"Documentation file not found: {exceptions_doc}"

    documented_exceptions = _get_documented_items(exceptions_doc, "py_gdelt.exceptions")

    # Find any missing documentation
    undocumented = exported_exceptions - documented_exceptions
    extra_documented = documented_exceptions - exported_exceptions

    # Build helpful error messages
    errors = []
    if undocumented:
        errors.append(
            f"Exceptions exported but NOT documented in docs/api/exceptions.md:\n"
            f"  {sorted(undocumented)}\n"
            f"  Add these to docs/api/exceptions.md with mkdocstrings syntax:\n"
            + "\n".join(f"  ::: py_gdelt.exceptions.{e}" for e in sorted(undocumented))
        )
    if extra_documented:
        errors.append(
            f"Exceptions documented but NOT exported from py_gdelt.exceptions:\n"
            f"  {sorted(extra_documented)}\n"
            f"  Either add to exceptions.py __all__ or remove from docs."
        )

    assert not errors, "\n\n".join(errors)


def test_models_all_matches_actual_exports() -> None:
    """Verify __all__ in models/__init__.py matches actual public classes."""
    # Get all public classes (non-underscore) that are actually importable
    actual_public = {
        name
        for name in dir(models_module)
        if not name.startswith("_") and isinstance(getattr(models_module, name), type)
    }

    declared_all = set(models_module.__all__)

    # Check for mismatches
    in_all_not_public = declared_all - actual_public
    public_not_in_all = actual_public - declared_all

    errors = []
    if in_all_not_public:
        errors.append(
            f"Items in __all__ but not importable as public classes:\n  {sorted(in_all_not_public)}"
        )
    if public_not_in_all:
        # This is less critical - some public classes might intentionally not be exported
        # But it's worth noting
        pass  # Don't fail on this, just the reverse

    assert not errors, "\n\n".join(errors)


def test_exceptions_all_matches_actual_exports() -> None:
    """Verify __all__ in exceptions.py matches actual exception classes."""
    # Get all public exception classes
    actual_exceptions = {
        name
        for name in dir(exceptions_module)
        if not name.startswith("_")
        and isinstance(getattr(exceptions_module, name), type)
        and issubclass(getattr(exceptions_module, name), Exception)
    }

    declared_all = set(exceptions_module.__all__)

    # Check for mismatches
    in_all_not_exception = declared_all - actual_exceptions

    errors = []
    if in_all_not_exception:
        errors.append(
            f"Items in __all__ but not actual exception classes:\n  {sorted(in_all_not_exception)}"
        )

    assert not errors, "\n\n".join(errors)
