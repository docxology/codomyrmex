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

try:
    from .agent_bridge import AntigravityAgent
except ImportError:
    pass

try:
    from .skill_adapter import (
        AntigravitySkillFactory,
        AntigravityToolSkill,
    )
except ImportError:
    pass

try:
    from .history_bridge import ArtifactHistoryBridge
except ImportError:
    pass

try:
    from .agent_relay import AgentRelay, RelayMessage
except ImportError:
    pass

try:
    from .live_bridge import (
        ClaudeCodeEndpoint,
        LiveAgentBridge,
    )
except ImportError:
    pass

try:
    from .message_scheduler import (
        MessageScheduler,
        SchedulerConfig,
    )
except ImportError:
    pass

try:
    from .relay_endpoint import RelayEndpoint
except ImportError:
    pass

try:
    from .antigravity_dispatcher import (
        AntigravityDispatcher,
        DispatcherConfig,
    )
except ImportError:
    pass

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
