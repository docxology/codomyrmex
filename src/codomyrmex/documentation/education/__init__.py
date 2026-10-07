"""Education Module for Codomyrmex.

Provides curriculum generation: lessons, difficulty levels, and learning
paths. Tutoring and certification are not implemented.
"""

from .curriculum import Curriculum, Difficulty, Lesson

__all__ = [
    "Curriculum",
    "Difficulty",
    "Lesson",
]
