# DEPRECATED(v0.2.0): Shim module. Import from codomyrmex.performance.optimization.lazy_loader instead. Will be removed in v0.3.0.
"""
Backward-compatibility shim.

This module has been moved to codomyrmex.performance.optimization.lazy_loader.
All imports are re-exported here for backward compatibility.
"""

from codomyrmex.performance.optimization.lazy_loader import (  # noqa: F401
    LazyLoader,
    lazy_import,
    get_lazy_loader,
    lazy_function,
    matplotlib,
    numpy,
    pandas,
    seaborn,
    plotly,
    openai,
    anthropic,
    google_genai,
    docker,
    git,
)
