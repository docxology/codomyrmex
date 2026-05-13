"""Education Module for Codomyrmex.

Provides curriculum generation, interactive tutoring, and
certification / assessment capabilities.
"""

import contextlib

from .curriculum import Curriculum, Difficulty, Lesson

Tutor = None
TutoringSession = None
Assessment = None
Certificate = None

# Optional submodules (scaffolded paths; names stay None until implemented)
with contextlib.suppress(ImportError):
    from .tutoring import Tutor as _Tutor
    from .tutoring import TutoringSession as _TutoringSession

    Tutor = _Tutor
    TutoringSession = _TutoringSession

with contextlib.suppress(ImportError):
    from .certification import Assessment as _Assessment
    from .certification import Certificate as _Certificate

    Assessment = _Assessment
    Certificate = _Certificate

__all__ = [
    "Assessment",
    "Certificate",
    "Curriculum",
    "Difficulty",
    "Lesson",
    "Tutor",
    "TutoringSession",
]
