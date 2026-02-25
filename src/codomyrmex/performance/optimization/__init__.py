"""
Optimization subpackage for Codomyrmex performance module.

Provides lazy loading capabilities to improve startup time by deferring
module imports until they are actually needed.
"""

from .lazy_loader import (
    LazyLoader,
    get_lazy_loader,
    lazy_function,
    lazy_import,
)

__all__ = [
    "LazyLoader",
    "lazy_import",
    "get_lazy_loader",
    "lazy_function",
]
