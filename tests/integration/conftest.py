"""Integration test shared fixtures and utilities."""

from importlib import import_module


def check_module_available(module_path: str) -> bool:
    """Check whether a module (or symbol within a module) is importable.

    Args:
        module_path: Dotted module path (e.g. 'codomyrmex.performance') or
                     dotted symbol path (e.g. 'codomyrmex.performance.run_benchmark').

    Returns:
        True if the module/symbol imports without error, False otherwise.
    """
    parts = module_path.rsplit(".", 1)
    try:
        mod = import_module(parts[0])
        if len(parts) == 2:
            getattr(mod, parts[1])
    except (ImportError, AttributeError):
        return False
    return True
