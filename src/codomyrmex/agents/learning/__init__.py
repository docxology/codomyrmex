"""Agent Learning Module for Codomyrmex.

Provides mechanisms for agents to improve via reflection and skill acquisition.
"""

# Lazy imports
import contextlib

with contextlib.suppress(ImportError):
    from .skills import Skill

__all__ = ["Skill"]
