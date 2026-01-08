from typing import Optional

from codomyrmex.logging_monitoring import get_logger


















































































"""Utilities for composing system, task, and context prompts."""



logger = get_logger(__name__)
This module provides prompt_composition functionality including:
- 1 functions: compose_prompt
- 0 classes: 

Usage:
    # Example usage here
"""
def compose_prompt(system: Optional[str], task: Optional[str], context: Optional[str]) -> str:
    parts = [p.strip() for p in ((system or ""), (task or ""), (context or "")) if p and p.strip()]
    return "\n\n".join(parts)
