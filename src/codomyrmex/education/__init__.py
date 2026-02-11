"""Education Module for Codomyrmex.

Provides curriculum generation, tutoring, and certification.
"""

# Lazy imports
try:
    from .curriculum import Curriculum
except ImportError:
    Curriculum = None

__all__ = ["Curriculum"]
