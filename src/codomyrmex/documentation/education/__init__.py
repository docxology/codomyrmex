"""Education Module for Codomyrmex.

Provides curriculum generation, interactive tutoring, and
certification / assessment capabilities.
"""

from .curriculum import Curriculum, Difficulty, Lesson

# Optional submodules (not yet implemented)
try:
    from .tutoring import Tutor, TutoringSession
except ImportError:
    pass

try:
    from .certification import Assessment, Certificate
except ImportError:
    pass

__all__ = [
    "Assessment",
    "Certificate",
    "Curriculum",
    "Difficulty",
    "Lesson",
    "Tutor",
    "TutoringSession",
]
