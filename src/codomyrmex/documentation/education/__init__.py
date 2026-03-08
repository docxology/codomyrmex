"""Education Module for Codomyrmex.

Provides curriculum generation, interactive tutoring, and
certification / assessment capabilities.
"""

import contextlib

from .curriculum import Curriculum, Difficulty, Lesson

# Optional submodules (not yet implemented)
with contextlib.suppress(ImportError):
    from .tutoring import Tutor, TutoringSession

with contextlib.suppress(ImportError):
    from .certification import Assessment, Certificate

__all__ = [
    "Assessment",
    "Certificate",
    "Curriculum",
    "Difficulty",
    "Lesson",
    "Tutor",
    "TutoringSession",
]
