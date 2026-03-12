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
import contextlib

with contextlib.suppress(ImportError):
    from codomyrmex.validation.schemas import Result, ResultStatus

with contextlib.suppress(ImportError):
    from codomyrmex.agents.ai_code_editing.code_editor import CodeEditor

with contextlib.suppress(ImportError):
    from codomyrmex.agents.claude import ClaudeClient

with contextlib.suppress(ImportError):
    from codomyrmex.agents.codex import CodexClient

with contextlib.suppress(ImportError):
    from codomyrmex.agents.droid import DroidController

with contextlib.suppress(ImportError):
    from codomyrmex.agents.every_code import EveryCodeClient

with contextlib.suppress(ImportError):
    from codomyrmex.agents.gemini import GeminiClient

with contextlib.suppress(ImportError):
    from codomyrmex.agents.generic.agent_orchestrator import AgentOrchestrator

with contextlib.suppress(ImportError):
    from codomyrmex.agents.jules import JulesClient

with contextlib.suppress(ImportError):
    from codomyrmex.agents.mistral_vibe import MistralVibeClient

with contextlib.suppress(ImportError):
    from codomyrmex.agents.openclaw import OpenClawClient

with contextlib.suppress(ImportError):
    from codomyrmex.agents.openfang import OpenFangClient

with contextlib.suppress(ImportError):
    from codomyrmex.agents.opencode import OpenCodeClient

with contextlib.suppress(ImportError):
    from codomyrmex.agents.theory.agent_architectures import (
        DeliberativeArchitecture,
        HybridArchitecture,
        KnowledgeBase,
        ReactiveArchitecture,
    )

import contextlib

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
with contextlib.suppress(ImportError):
    from .o1 import O1Client

with contextlib.suppress(ImportError):
    from .deepseek import DeepSeekClient

with contextlib.suppress(ImportError):
    from .qwen import QwenClient

with contextlib.suppress(ImportError):
    from .pooling import AgentPool

with contextlib.suppress(ImportError):
    from .evaluation import AgentEvaluator

with contextlib.suppress(ImportError):
    from .history import ConversationHistory

with contextlib.suppress(ImportError):
    from .infrastructure import InfrastructureAgent

with contextlib.suppress(ImportError):
    from .agent_setup import AgentRegistry

with contextlib.suppress(ImportError):
    from .core.exceptions import (
        AgentConfigurationError,
        AgentError,
        AgentTimeoutError,
        ContextError,
        ExecutionError,
        SessionError,
        ToolError,
    )

with contextlib.suppress(ImportError):
    from .generic import APIAgentBase, CLIAgentBase

with contextlib.suppress(ImportError):
    from .git_agent import GitAgent

with contextlib.suppress(ImportError):
    from .agentic_seek import AgenticSeekClient

with contextlib.suppress(ImportError):
    from .mission_control import MissionControlClient

with contextlib.suppress(ImportError):
    from .pi import PiClient


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
            "mission_control": MissionControlClient,
            "pi": PiClient,
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
    # Mission Control (lazy-loaded)
    "MissionControlClient",
    "MistralVibeClient",
    # New submodules (lazy-loaded, may be None if not installed)
    "O1Client",
    "OpenClawClient",
    "OpenCodeClient",
    # Pi coding agent (lazy-loaded)
    "PiClient",
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
