"""Agent Learning Module for Codomyrmex.

Provides mechanisms for agents to improve via reflection and skill acquisition.
"""

# Lazy imports
try:
    from .skills import Skill
except ImportError:
    pass

__all__ = ["Skill"]
