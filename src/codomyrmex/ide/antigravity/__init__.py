"""Antigravity IDE Integration

Integration with Google DeepMind's Antigravity IDE - the agentic AI coding
assistant. Provides programmatic access to Antigravity's capabilities for
meta-level control and automation.

Example:
    >>> from codomyrmex.ide.antigravity import AntigravityClient
    >>> client = AntigravityClient()
    >>> client.connect()
    >>> capabilities = client.get_capabilities()
"""

import contextlib

from .client import AntigravityClient
from .models import Artifact, ConversationContext

# ── Bridge Imports (lazy, optional dependencies) ──────────────────────
try:
    from .tool_provider import (
        CONTROL_TOOLS as AG_CONTROL_TOOLS,
    )
    from .tool_provider import (
        DESTRUCTIVE_TOOLS as AG_DESTRUCTIVE_TOOLS,
    )
    from .tool_provider import (
        SAFE_TOOLS as AG_SAFE_TOOLS,
    )
    from .tool_provider import (
        AntigravityToolProvider,
    )
except ImportError:
    AG_SAFE_TOOLS = frozenset()
    AG_DESTRUCTIVE_TOOLS = frozenset()
    AG_CONTROL_TOOLS = frozenset()

with contextlib.suppress(ImportError):
    from .agent_bridge import AntigravityAgent

with contextlib.suppress(ImportError):
    from .skill_adapter import (
        AntigravitySkillFactory,
        AntigravityToolSkill,
    )

with contextlib.suppress(ImportError):
    from .history_bridge import ArtifactHistoryBridge

with contextlib.suppress(ImportError):
    from .agent_relay import AgentRelay, RelayMessage

with contextlib.suppress(ImportError):
    from .live_bridge import (
        ClaudeCodeEndpoint,
        LiveAgentBridge,
    )

with contextlib.suppress(ImportError):
    from .message_scheduler import (
        MessageScheduler,
        SchedulerConfig,
    )

with contextlib.suppress(ImportError):
    from .relay_endpoint import RelayEndpoint

with contextlib.suppress(ImportError):
    from .antigravity_dispatcher import (
        AntigravityDispatcher,
        DispatcherConfig,
    )

__all__ = [
    # Relay
    "AgentRelay",
    "AntigravityAgent",
    # Core
    "AntigravityClient",
    "AntigravityDispatcher",
    "AntigravitySkillFactory",
    # Bridges
    "AntigravityToolProvider",
    "AntigravityToolSkill",
    "Artifact",
    "ArtifactHistoryBridge",
    "ClaudeCodeEndpoint",
    "ConversationContext",
    "DispatcherConfig",
    "LiveAgentBridge",
    # Scheduler & Endpoint
    "MessageScheduler",
    "RelayEndpoint",
    "RelayMessage",
    "SchedulerConfig",
]
