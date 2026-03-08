"""Agents Module for Codomyrmex.

This module provides integration with 13 agentic frameworks:

- **API-based**: Claude, Codex, O1, DeepSeek, Qwen (extend ``APIAgentBase``)
- **CLI-based**: Jules, OpenCode, OpenClaw, OpenFang, Gemini, Mistral Vibe, Every Code, agenticSeek (extend ``CLIAgentBase``)
- **Local**: Ollama (via ``llm/ollama/``)

Integration:
- Uses ``logging_monitoring`` for all logging
- Integrates with ``ai_code_editing`` for code generation workflows
- Integrates with ``llm`` for LLM infrastructure
- Integrates with ``code`` for safe code execution

Available classes:
- AgentInterface: Abstract base class for all agents
- AgentRequest, AgentResponse: Request/response data structures
- AgentCapabilities: Enum of agent capabilities
- AgentConfig: Configuration management for all 13 agents

Available submodules:
- agent_setup: Agent discovery, YAML config, interactive setup wizard
- generic: Base agent classes (APIAgentBase, CLIAgentBase, AgentOrchestrator)
- theory: Theoretical foundations for agentic systems
- claude, codex, o1, deepseek, qwen: API-based agent clients
- jules, opencode, gemini, mistral_vibe, every_code, openclaw, openfang, agentic_seek: CLI-based agent clients
- pooling: Multi-agent load balancing and failover
- evaluation: Agent benchmarking and quality metrics
- history: Conversation and context persistence
"""

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    pass

try:
    from codomyrmex.agents.ai_code_editing.code_editor import CodeEditor
except ImportError:
    pass

try:
    from codomyrmex.agents.claude import ClaudeClient
except ImportError:
    pass

try:
    from codomyrmex.agents.codex import CodexClient
except ImportError:
    pass

try:
    from codomyrmex.agents.droid import DroidController
except ImportError:
    pass

try:
    from codomyrmex.agents.every_code import EveryCodeClient
except ImportError:
    pass

try:
    from codomyrmex.agents.gemini import GeminiClient
except ImportError:
    pass

try:
    from codomyrmex.agents.generic.agent_orchestrator import AgentOrchestrator
except ImportError:
    pass

try:
    from codomyrmex.agents.jules import JulesClient
except ImportError:
    pass

try:
    from codomyrmex.agents.mistral_vibe import MistralVibeClient
except ImportError:
    pass

try:
    from codomyrmex.agents.openclaw import OpenClawClient
except ImportError:
    pass

try:
    from codomyrmex.agents.openfang import OpenFangClient
except ImportError:
    pass

try:
    from codomyrmex.agents.opencode import OpenCodeClient
except ImportError:
    pass

try:
    from codomyrmex.agents.theory.agent_architectures import (
        DeliberativeArchitecture,
        HybridArchitecture,
        KnowledgeBase,
        ReactiveArchitecture,
    )
except ImportError:
    pass

from .core import (
    AgentCapabilities,
    AgentConfig,
    AgentIntegrationAdapter,
    AgentInterface,
    AgentRequest,
    AgentResponse,
    AgentSession,
    BaseAgent,
    CodeBlock,
    Message,
    ParseResult,
    SessionManager,
    clean_response,
    get_config,
    parse_code_blocks,
    parse_first_code_block,
    parse_json_response,
    parse_structured_output,
    reset_config,
    set_config,
)

# Lazy imports for submodules that may not be installed yet
try:
    from .o1 import O1Client
except ImportError:
    pass

try:
    from .deepseek import DeepSeekClient
except ImportError:
    pass

try:
    from .qwen import QwenClient
except ImportError:
    pass

try:
    from .pooling import AgentPool
except ImportError:
    pass

try:
    from .evaluation import AgentEvaluator
except ImportError:
    pass

try:
    from .history import ConversationHistory
except ImportError:
    pass

try:
    from .infrastructure import InfrastructureAgent
except ImportError:
    pass

try:
    from .agent_setup import AgentRegistry
except ImportError:
    pass

try:
    from .core.exceptions import (
        AgentConfigurationError,
        AgentError,
        AgentTimeoutError,
        ContextError,
        ExecutionError,
        SessionError,
        ToolError,
    )
except ImportError:
    pass

try:
    from .generic import APIAgentBase, CLIAgentBase
except ImportError:
    pass

try:
    from .git_agent import GitAgent
except ImportError:
    pass

try:
    from .agentic_seek import AgenticSeekClient
except ImportError:
    pass


def cli_commands():
    """Return CLI commands for the agents module."""

    def _list_agents():
        providers = []
        provider_map = {
            "claude": ClaudeClient,
            "codex": CodexClient,
            "gemini": GeminiClient,
            "jules": JulesClient,
            "mistral_vibe": MistralVibeClient,
            "openclaw": OpenClawClient,
            "opencode": OpenCodeClient,
            "every_code": EveryCodeClient,
            "o1": O1Client,
            "deepseek": DeepSeekClient,
            "qwen": QwenClient,
            "agentic_seek": AgenticSeekClient,
        }
        for name, client in provider_map.items():
            status = "available" if client is not None else "not installed"
            providers.append(f"  {name}: {status}")
        print("Registered agent providers:")
        print("\n".join(providers))

    def _show_config():
        config = get_config()
        print("Agent configuration:")
        for key, value in vars(config).items():
            print(f"  {key}: {value}")

    return {
        "list": _list_agents,
        "config": _show_config,
    }


__all__ = [
    "APIAgentBase",
    "AgentCapabilities",
    "AgentConfig",
    "AgentConfigurationError",
    # Exceptions
    "AgentError",
    "AgentEvaluator",
    "AgentIntegrationAdapter",
    "AgentInterface",
    "AgentOrchestrator",
    "AgentPool",
    # Agent setup
    "AgentRegistry",
    "AgentRequest",
    "AgentResponse",
    # Session management
    "AgentSession",
    "AgentTimeoutError",
    # agenticSeek (lazy-loaded)
    "AgenticSeekClient",
    "BaseAgent",
    "CLIAgentBase",
    "ClaudeClient",
    "CodeBlock",
    "CodeEditor",
    "CodexClient",
    "ContextError",
    "ConversationHistory",
    "DeepSeekClient",
    "DeliberativeArchitecture",
    "DroidController",
    "EveryCodeClient",
    "ExecutionError",
    "GeminiClient",
    "GitAgent",
    "HybridArchitecture",
    # Infrastructure agent (lazy-loaded)
    "InfrastructureAgent",
    "JulesClient",
    "KnowledgeBase",
    "Message",
    "MistralVibeClient",
    # New submodules (lazy-loaded, may be None if not installed)
    "O1Client",
    "OpenClawClient",
    "OpenCodeClient",
    "ParseResult",
    "QwenClient",
    "ReactiveArchitecture",
    "SessionError",
    "SessionManager",
    "ToolError",
    "clean_response",
    "cli_commands",
    "get_config",
    "parse_code_blocks",
    "parse_first_code_block",
    # Parsers
    "parse_json_response",
    "parse_structured_output",
    "reset_config",
    "set_config",
]

__version__ = "1.1.0"
