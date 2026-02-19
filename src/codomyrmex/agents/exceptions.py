# DEPRECATED(v0.2.0): Shim module. Import from codomyrmex.agents.core.exceptions instead. Will be removed in v0.3.0.
"""Agent exceptions shim for backward compatibility."""
from codomyrmex.agents.core.exceptions import (
    AgentConfigurationError,
    AgentError,
    AgentTimeoutError,
    ClaudeError,
    CodexError,
    ConfigError,
    ContextError,
    EveryCodeError,
    ExecutionError,
    GeminiError,
    JulesError,
    MistralVibeError,
    OpenCodeError,
    SessionError,
    ToolError,
)

__all__ = [
    "AgentError",
    "AgentTimeoutError",
    "AgentConfigurationError",
    "JulesError",
    "ClaudeError",
    "CodexError",
    "OpenCodeError",
    "GeminiError",
    "MistralVibeError",
    "EveryCodeError",
    "ConfigError",
    "SessionError",
    "ExecutionError",
    "ToolError",
    "ContextError",
]
