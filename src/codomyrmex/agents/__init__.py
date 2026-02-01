"""Agents Module for Codomyrmex.

This module provides integration with various agentic frameworks including
Jules CLI, Claude API, OpenAI Codex, OpenCode CLI, Gemini CLI, Mistral Vibe CLI,
and Every Code CLI. It includes theoretical foundations, generic utilities, and
framework-specific implementations.

Integration:
    pass 
- Uses `logging_monitoring` for all logging
- Integrates with `ai_code_editing` for code generation workflows
- Integrates with `llm` for LLM infrastructure
- Integrates with `code` for safe code execution

Available classes:
    pass 
- AgentInterface: Abstract base class for all agents
- AgentRequest, AgentResponse: Request/response data structures
- AgentCapabilities: Enum of agent capabilities
- AgentConfig: Configuration management

Available submodules:
    pass 
- generic: Base agent classes and utilities
- theory: Theoretical foundations for agentic systems
- jules: Jules CLI integration
- claude: Claude API integration
- codex: OpenAI Codex integration
- opencode: OpenCode CLI integration
- gemini: Gemini CLI integration
- mistral_vibe: Mistral Vibe CLI integration
- every_code: Every Code CLI integration (multi-agent orchestration)
- o1: OpenAI o1/o3 reasoning model integration
- deepseek: DeepSeek Coder integration
- qwen: Qwen-Coder integration
- pooling: Multi-agent load balancing and failover
- evaluation: Agent benchmarking and quality metrics
- history: Conversation and context persistence
"""


from codomyrmex.agents.ai_code_editing.code_editor import CodeEditor
from codomyrmex.agents.claude import ClaudeClient
from codomyrmex.agents.codex import CodexClient
from codomyrmex.agents.droid import DroidController
from codomyrmex.agents.every_code import EveryCodeClient
from codomyrmex.agents.gemini import GeminiClient
from codomyrmex.agents.jules import JulesClient
from codomyrmex.agents.mistral_vibe import MistralVibeClient
from codomyrmex.agents.opencode import OpenCodeClient
from codomyrmex.agents.generic.agent_orchestrator import AgentOrchestrator
from codomyrmex.agents.theory.agent_architectures import (
    ReactiveArchitecture,
    DeliberativeArchitecture,
    HybridArchitecture,
    KnowledgeBase,
)

from .core import (
    AgentConfig,
    get_config,
    reset_config,
    set_config,
    BaseAgent,
    AgentCapabilities,
    AgentInterface,
    AgentIntegrationAdapter,
    AgentRequest,
    AgentResponse,
    AgentSession,
    SessionManager,
    Message,
    parse_json_response,
    parse_code_blocks,
    parse_first_code_block,
    parse_structured_output,
    CodeBlock,
    ParseResult,
    clean_response,
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

from .git_agent import GitAgent
from .generic import APIAgentBase, CLIAgentBase
from .exceptions import (
    AgentError,
    AgentTimeoutError,
    AgentConfigurationError,
    ExecutionError,
    ToolError,
    ContextError,
    SessionError,
)

__all__ = [
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
]

__version__ = "0.1.0"
