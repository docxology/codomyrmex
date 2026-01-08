from typing import Optional

from prompt_composition import FunctionName, ClassName




"""Utilities for composing system, task, and context prompts."""



"""Core functionality module

This module provides prompt_composition functionality including:
- 1 functions: compose_prompt
- 0 classes: 

Usage:
    # Example usage here
"""
def compose_prompt(system: Optional[str], task: Optional[str], context: Optional[str]) -> str:
    """Brief description of compose_prompt.

Args:
    system : Description of system
    task : Description of task
    context : Description of context

    Returns: Description of return value (type: str)
"""
    parts = [p.strip() for p in ((system or ""), (task or ""), (context or "")) if p and p.strip()]
    return "\n\n".join(parts)
