"""Pi Coding Agent — Codomyrmex integration.

Wraps the pi coding agent CLI (https://pi.dev/) for programmatic use
via its RPC (JSON-over-stdin/stdout) protocol.

Exports:
    PiClient        — High-level RPC client for the pi coding agent.
    PiConfig        — Configuration dataclass.
    PiError         — Exception hierarchy.
"""

from .pi_client import PiClient, PiConfig, PiError

__all__ = ["PiClient", "PiConfig", "PiError"]
