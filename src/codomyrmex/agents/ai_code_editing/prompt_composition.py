"""Utilities for composing system, task, and context prompts."""

from typing import Optional


def compose_prompt(system: Optional[str], task: Optional[str], context: Optional[str]) -> str:
    parts = [p.strip() for p in ((system or ""), (task or ""), (context or "")) if p and p.strip()]
    return "\n\n".join(parts)
