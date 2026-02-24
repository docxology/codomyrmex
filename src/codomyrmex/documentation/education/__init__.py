"""Education Module for Codomyrmex.

Provides curriculum generation, interactive tutoring, and
certification / assessment capabilities.
"""

from .curriculum import Curriculum, Lesson, Difficulty

# Optional submodules (not yet implemented)
try:
    from .tutoring import Tutor, TutoringSession
except ImportError:
    Tutor = None
    TutoringSession = None

try:
    from .certification import Assessment, Certificate
except ImportError:
    Assessment = None
    Certificate = None

__all__ = [
    "Assessment",
    "Certificate",
    "Curriculum",
    "Difficulty",
    "Lesson",
    "Tutor",
    "TutoringSession",
]

