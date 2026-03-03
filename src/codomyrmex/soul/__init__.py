"""soul — Persistent markdown-memory LLM agent integration (soul.py wrapper).

Wraps the ``soul-agent`` library (https://github.com/menonpg/soul.py) for use
within Codomyrmex.  Agents maintain identity in SOUL.md and conversation
history in MEMORY.md — no database or server required.

Providers: anthropic, openai, openai-compatible (Ollama, any HTTP endpoint)

Optional dependency::

    uv sync --extra soul

Quick start::

    from codomyrmex.soul import SoulAgent

    agent = SoulAgent(provider="anthropic")
    reply = agent.ask("Hello! My name is Ada.")
    print(reply)

    # Memory persists — a new instance can recall the name.
    agent2 = SoulAgent(provider="anthropic")
    print(agent2.ask("What is my name?"))
"""

__version__ = "0.1.0"

from .agent import HAS_SOUL, SoulAgent
from .exceptions import SoulError, SoulImportError, SoulMemoryError, SoulProviderError

__all__ = [
    "__version__",
    "HAS_SOUL",
    "SoulAgent",
    "SoulError",
    "SoulImportError",
    "SoulMemoryError",
    "SoulProviderError",
]
