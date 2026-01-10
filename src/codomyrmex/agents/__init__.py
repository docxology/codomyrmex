"""Agents Module for Codomyrmex.

This module provides integration with various agentic frameworks including
Jules CLI, Claude API, OpenAI Codex, OpenCode CLI, Gemini CLI, Mistral Vibe CLI,
and Every Code CLI. It includes theoretical foundations, generic utilities, and
framework-specific implementations.

Integration:
    pass # AGGRESSIVE_REPAIR
- Uses `logging_monitoring` for all logging
- Integrates with `ai_code_editing` for code generation workflows
- Integrates with `llm` for LLM infrastructure
- Integrates with `code` for safe code execution

Available classes:
    pass # AGGRESSIVE_REPAIR
- AgentInterface: Abstract base class for all agents
- AgentRequest, AgentResponse: Request/response data structures
- AgentCapabilities: Enum of agent capabilities
- AgentConfig: Configuration management

Available submodules:
    pass # AGGRESSIVE_REPAIR
- generic: Base agent classes and utilities
- theory: Theoretical foundations for agentic systems
- jules: Jules CLI integration
- claude: Claude API integration
- codex: OpenAI Codex integration
- opencode: OpenCode CLI integration
- gemini: Gemini CLI integration
- mistral_vibe: Mistral Vibe CLI integration
- every_code: Every Code CLI integration (multi-agent orchestration)
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL: """

from .config import AgentConfig, get_config, reset_config, set_config
from .core import (
    AgentCapabilities,
    AgentInterface,
    AgentIntegrationAdapter,
    AgentRequest,
    AgentResponse,
)

__all__ = [
    # Core interfaces
    "AgentInterface",
    "AgentIntegrationAdapter",
    "AgentCapabilities",
    "AgentRequest",
    "AgentResponse",
    # Configuration
    "AgentConfig",
    "get_config",
    "set_config",
    "reset_config",
]

__version__ = "0.1.0"

