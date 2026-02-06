
from codomyrmex.logging_monitoring import get_logger

"""Utilities for composing system, task, and context prompts."""



logger = get_logger(__name__)

def compose_prompt(system: str | None, task: str | None, context: str | None) -> str:
    parts = [p.strip() for p in ((system or ""), (task or ""), (context or "")) if p and p.strip()]
    return "\n\n".join(parts)
