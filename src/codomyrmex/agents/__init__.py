"""Agents Module for Codomyrmex.

This module provides integration with 13 agentic frameworks:

- **API-based**: Claude, Codex, O1, DeepSeek, Qwen (extend ``APIAgentBase``)
- **CLI-based**: Jules, OpenCode, OpenClaw, Gemini, Mistral Vibe, Every Code, agenticSeek (extend ``CLIAgentBase``)
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
- AgentConfig: Configuration management for all 12 agents

Available submodules:
- agent_setup: Agent discovery, YAML config, interactive setup wizard
- generic: Base agent classes (APIAgentBase, CLIAgentBase, AgentOrchestrator)
- theory: Theoretical foundations for agentic systems
- claude, codex, o1, deepseek, qwen: API-based agent clients
- jules, opencode, gemini, mistral_vibe, every_code: CLI-based agent clients
- pooling: Multi-agent load balancing and failover
- evaluation: Agent benchmarking and quality metrics
- history: Conversation and context persistence
"""


# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

try:
    from codomyrmex.agents.ai_code_editing.code_editor import CodeEditor
except ImportError:
    CodeEditor = None

try:
    from codomyrmex.agents.claude import ClaudeClient
except ImportError:
    ClaudeClient = None

try:
    from codomyrmex.agents.codex import CodexClient
except ImportError:
    CodexClient = None

try:
    from codomyrmex.agents.droid import DroidController
except ImportError:
    DroidController = None

try:
    from codomyrmex.agents.every_code import EveryCodeClient
except ImportError:
    EveryCodeClient = None

try:
    from codomyrmex.agents.gemini import GeminiClient
except ImportError:
    GeminiClient = None

try:
    from codomyrmex.agents.generic.agent_orchestrator import AgentOrchestrator
except ImportError:
    AgentOrchestrator = None

try:
    from codomyrmex.agents.jules import JulesClient
except ImportError:
    JulesClient = None

try:
    from codomyrmex.agents.mistral_vibe import MistralVibeClient
except ImportError:
    MistralVibeClient = None

try:
    from codomyrmex.agents.openclaw import OpenClawClient
except ImportError:
    OpenClawClient = None

try:
    from codomyrmex.agents.opencode import OpenCodeClient
except ImportError:
    OpenCodeClient = None

try:
    from codomyrmex.agents.theory.agent_architectures import (
        DeliberativeArchitecture,
        HybridArchitecture,
        KnowledgeBase,
        ReactiveArchitecture,
    )
except ImportError:
    DeliberativeArchitecture = None
    HybridArchitecture = None
    KnowledgeBase = None
    ReactiveArchitecture = None

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
    O1Client = None

try:
    from .deepseek import DeepSeekClient
except ImportError:
    DeepSeekClient = None

try:
    from .qwen import QwenClient
except ImportError:
    QwenClient = None

try:
    from .pooling import AgentPool
except ImportError:
    AgentPool = None

try:
    from .evaluation import AgentEvaluator
except ImportError:
    AgentEvaluator = None

try:
    from .history import ConversationHistory
except ImportError:
    ConversationHistory = None

try:
    from .infrastructure import InfrastructureAgent
except ImportError:
    InfrastructureAgent = None

try:
    from .agent_setup import AgentRegistry
except ImportError:
    AgentRegistry = None

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
    AgentConfigurationError = None
    AgentError = None
    AgentTimeoutError = None
    ContextError = None
    ExecutionError = None
    SessionError = None
    ToolError = None

try:
    from .generic import APIAgentBase, CLIAgentBase
except ImportError:
    APIAgentBase = None
    CLIAgentBase = None

try:
    from .git_agent import GitAgent
except ImportError:
    GitAgent = None

try:
    from .agentic_seek import AgenticSeekClient
except ImportError:
    AgenticSeekClient = None

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
    "cli_commands",
    "AgentInterface",
    "AgentIntegrationAdapter",
    "BaseAgent",
    "GitAgent",
    "APIAgentBase",
    "CLIAgentBase",
    "AgentCapabilities",
    "AgentRequest",
    "AgentResponse",
    "AgentConfig",
    "get_config",
    "set_config",
    "reset_config",
    "CodeEditor",
    "ClaudeClient",
    "CodexClient",
    "DroidController",
    "EveryCodeClient",
    "GeminiClient",
    "JulesClient",
    "MistralVibeClient",
    "OpenClawClient",
    "OpenCodeClient",
    "ReactiveArchitecture",
    "DeliberativeArchitecture",
    "HybridArchitecture",
    "KnowledgeBase",
    "AgentOrchestrator",
    # Session management
    "AgentSession",
    "SessionManager",
    "Message",
    # Parsers
    "parse_json_response",
    "parse_code_blocks",
    "parse_first_code_block",
    "parse_structured_output",
    "CodeBlock",
    "ParseResult",
    "clean_response",
    # Exceptions
    "AgentError",
    "AgentTimeoutError",
    "AgentConfigurationError",
    "ExecutionError",
    "ToolError",
    "ContextError",
    "SessionError",
    # New submodules (lazy-loaded, may be None if not installed)
    "O1Client",
    "DeepSeekClient",
    "QwenClient",
    "AgentPool",
    "AgentEvaluator",
    "ConversationHistory",
    # Infrastructure agent (lazy-loaded)
    "InfrastructureAgent",
    # Agent setup
    "AgentRegistry",
    # agenticSeek (lazy-loaded)
    "AgenticSeekClient",
]

__version__ = "0.2.0"
