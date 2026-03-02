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
    AntigravityToolProvider = None
    AG_SAFE_TOOLS = frozenset()
    AG_DESTRUCTIVE_TOOLS = frozenset()
    AG_CONTROL_TOOLS = frozenset()

try:
    from .agent_bridge import AntigravityAgent
except ImportError:
    AntigravityAgent = None

try:
    from .skill_adapter import (
        AntigravitySkillFactory,
        AntigravityToolSkill,
    )
except ImportError:
    AntigravityToolSkill = None
    AntigravitySkillFactory = None

try:
    from .history_bridge import ArtifactHistoryBridge
except ImportError:
    ArtifactHistoryBridge = None

try:
    from .agent_relay import AgentRelay, RelayMessage
except ImportError:
    AgentRelay = None
    RelayMessage = None

try:
    from .live_bridge import (
        ClaudeCodeEndpoint,
        LiveAgentBridge,
    )
except ImportError:
    LiveAgentBridge = None
    ClaudeCodeEndpoint = None

try:
    from .message_scheduler import (
        MessageScheduler,
        SchedulerConfig,
    )
except ImportError:
    MessageScheduler = None
    SchedulerConfig = None

try:
    from .relay_endpoint import RelayEndpoint
except ImportError:
    RelayEndpoint = None

try:
    from .antigravity_dispatcher import (
        AntigravityDispatcher,
        DispatcherConfig,
    )
except ImportError:
    AntigravityDispatcher = None
    DispatcherConfig = None

__all__ = [
    # Core
    "AntigravityClient",
    "Artifact",
    "ConversationContext",
    # Bridges
    "AntigravityToolProvider",
    "AntigravityAgent",
    "AntigravityToolSkill",
    "AntigravitySkillFactory",
    "ArtifactHistoryBridge",
    # Relay
    "AgentRelay",
    "RelayMessage",
    "LiveAgentBridge",
    "ClaudeCodeEndpoint",
    # Scheduler & Endpoint
    "MessageScheduler",
    "SchedulerConfig",
    "RelayEndpoint",
    "AntigravityDispatcher",
    "DispatcherConfig",
]
