"""
Lazy loading utilities for Codomyrmex modules.

This module provides lazy loading capabilities to improve startup time
by deferring module imports until they are actually needed.
"""

import sys
import importlib
from typing import Any, Dict, Optional, Callable
from functools import wraps


class LazyLoader:
    """
    A lazy loader that defers module imports until they are actually accessed.

    This helps improve startup time by avoiding importing heavy modules
    until they are actually needed.
    """

    def __init__(self, module_name: str, package: Optional[str] = None):
        """
        Initialize the lazy loader.

        Args:
            module_name: The name of the module to load lazily
            package: The package name if module_name is relative
        """
        self.module_name = module_name
        self.package = package
        self._module: Optional[Any] = None
        self._loading = False

    def __getattr__(self, name: str) -> Any:
        """Load the module and return the requested attribute."""
        if self._module is None and not self._loading:
            self._loading = True
            try:
                self._module = importlib.import_module(self.module_name, self.package)
            except ImportError as e:
                raise ImportError(f"Could not import {self.module_name}: {e}")
            finally:
                self._loading = False

        if self._module is None:
            raise ImportError(f"Failed to load module {self.module_name}")

        return getattr(self._module, name)

    def __repr__(self) -> str:
        """Return a string representation of the lazy loader."""
        status = "loaded" if self._module is not None else "unloaded"
        return f"LazyLoader({self.module_name}, status={status})"


def lazy_import(module_name: str, package: Optional[str] = None) -> LazyLoader:
    """
    Create a lazy loader for the specified module.

    Args:
        module_name: The name of the module to load lazily
        package: The package name if module_name is relative

    Returns:
        A LazyLoader instance for the module

    Example:
        >>> matplotlib = lazy_import('matplotlib.pyplot')
        >>> # matplotlib is not imported yet
        >>> plt = matplotlib.pyplot  # Now it's imported
    """
    return LazyLoader(module_name, package)


# Global registry of lazy loaders
_lazy_loaders: Dict[str, LazyLoader] = {}


def get_lazy_loader(module_name: str, package: Optional[str] = None) -> LazyLoader:
    """
    Get or create a lazy loader for the specified module.

    This function maintains a registry of lazy loaders to ensure
    that the same module is not loaded multiple times.

    Args:
        module_name: The name of the module to load lazily
        package: The package name if module_name is relative

    Returns:
        A LazyLoader instance for the module
    """
    key = f"{package}.{module_name}" if package else module_name

    if key not in _lazy_loaders:
        _lazy_loaders[key] = LazyLoader(module_name, package)

    return _lazy_loaders[key]


def lazy_function(
    module_name: str, function_name: str, package: Optional[str] = None
) -> Callable:
    """
    Create a lazy-loaded function from a module.

    Args:
        module_name: The name of the module containing the function
        function_name: The name of the function to load lazily
        package: The package name if module_name is relative

    Returns:
        A callable that will load the function on first call

    Example:
        >>> create_plot = lazy_function('matplotlib.pyplot', 'plot')
        >>> # matplotlib.pyplot is not imported yet
        >>> create_plot([1, 2, 3], [1, 4, 9])  # Now it's imported and called
    """
    loader = get_lazy_loader(module_name, package)

    @wraps(lambda: None)  # Placeholder for the actual function
    def lazy_wrapper(*args, **kwargs):
        func = getattr(loader, function_name)
        return func(*args, **kwargs)

    # Set the function name for better debugging
    lazy_wrapper.__name__ = function_name
    lazy_wrapper.__qualname__ = f"{module_name}.{function_name}"

    return lazy_wrapper


# Pre-configured lazy loaders for common heavy modules
matplotlib = lazy_import("matplotlib.pyplot")
numpy = lazy_import("numpy")
pandas = lazy_import("pandas")
seaborn = lazy_import("seaborn")
plotly = lazy_import("plotly.graph_objects")
openai = lazy_import("openai")
anthropic = lazy_import("anthropic")
google_genai = lazy_import("google.generativeai")
docker = lazy_import("docker")
git = lazy_import("git")
