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

Public names are loaded lazily (PEP 562): importing this package does not
import any agent framework subpackage; each name in ``__all__`` is imported
on first attribute access via the module-level ``__getattr__``.
"""

from __future__ import annotations

import importlib
from types import MappingProxyType
from typing import Any

__version__ = "1.1.0"

# name -> (module, attribute). Module strings are relative to this package
# unless they are absolute (``codomyrmex.validation.schemas``).
_EXPORTS: MappingProxyType[str, tuple[str, str]] = MappingProxyType(
    {
        # Shared schemas for cross-module interop
        "Result": ("codomyrmex.validation.schemas", "Result"),
        "ResultStatus": ("codomyrmex.validation.schemas", "ResultStatus"),
        # Agent clients (API-based)
        "ClaudeClient": ("codomyrmex.agents.claude", "ClaudeClient"),
        "CodexClient": ("codomyrmex.agents.codex", "CodexClient"),
        "GeminiClient": ("codomyrmex.agents.gemini", "GeminiClient"),
        "O1Client": ("codomyrmex.agents.o1", "O1Client"),
        "DeepSeekClient": ("codomyrmex.agents.deepseek", "DeepSeekClient"),
        "QwenClient": ("codomyrmex.agents.qwen", "QwenClient"),
        "MistralVibeClient": ("codomyrmex.agents.mistral_vibe", "MistralVibeClient"),
        "EveryCodeClient": ("codomyrmex.agents.every_code", "EveryCodeClient"),
        # Agent clients (CLI-based)
        "JulesClient": ("codomyrmex.agents.jules", "JulesClient"),
        "OpenClawClient": ("codomyrmex.agents.openclaw", "OpenClawClient"),
        "OpenCodeClient": ("codomyrmex.agents.opencode", "OpenCodeClient"),
        "OpenFangRunner": ("codomyrmex.agents.openfang", "OpenFangRunner"),
        "AgenticSeekClient": ("codomyrmex.agents.agentic_seek", "AgenticSeekClient"),
        "MissionControlClient": ("codomyrmex.agents.mission_control", "MissionControlClient"),
        "PiClient": ("codomyrmex.agents.pi", "PiClient"),
        "DroidController": ("codomyrmex.agents.droid", "DroidController"),
        "GitAgent": ("codomyrmex.agents.git_agent", "GitAgent"),
        # Editing / orchestration / theory
        "CodeEditor": ("codomyrmex.agents.ai_code_editing.code_editor", "CodeEditor"),
        "AgentOrchestrator": ("codomyrmex.agents.generic.agent_orchestrator", "AgentOrchestrator"),
        "APIAgentBase": ("codomyrmex.agents.generic", "APIAgentBase"),
        "CLIAgentBase": ("codomyrmex.agents.generic", "CLIAgentBase"),
        "DeliberativeArchitecture": ("codomyrmex.agents.theory.agent_architectures", "DeliberativeArchitecture"),
        "HybridArchitecture": ("codomyrmex.agents.theory.agent_architectures", "HybridArchitecture"),
        "KnowledgeBase": ("codomyrmex.agents.theory.agent_architectures", "KnowledgeBase"),
        "ReactiveArchitecture": ("codomyrmex.agents.theory.agent_architectures", "ReactiveArchitecture"),
        # Core
        "AgentCapabilities": ("codomyrmex.agents.core", "AgentCapabilities"),
        "AgentConfig": ("codomyrmex.agents.core", "AgentConfig"),
        "AgentIntegrationAdapter": ("codomyrmex.agents.core", "AgentIntegrationAdapter"),
        "AgentInterface": ("codomyrmex.agents.core", "AgentInterface"),
        "AgentRequest": ("codomyrmex.agents.core", "AgentRequest"),
        "AgentResponse": ("codomyrmex.agents.core", "AgentResponse"),
        "AgentSession": ("codomyrmex.agents.core", "AgentSession"),
        "BaseAgent": ("codomyrmex.agents.core", "BaseAgent"),
        "CodeBlock": ("codomyrmex.agents.core", "CodeBlock"),
        "Message": ("codomyrmex.agents.core", "Message"),
        "ParseResult": ("codomyrmex.agents.core", "ParseResult"),
        "SessionManager": ("codomyrmex.agents.core", "SessionManager"),
        "clean_response": ("codomyrmex.agents.core", "clean_response"),
        "get_config": ("codomyrmex.agents.core", "get_config"),
        "parse_code_blocks": ("codomyrmex.agents.core", "parse_code_blocks"),
        "parse_first_code_block": ("codomyrmex.agents.core", "parse_first_code_block"),
        "parse_json_response": ("codomyrmex.agents.core", "parse_json_response"),
        "parse_structured_output": ("codomyrmex.agents.core", "parse_structured_output"),
        "reset_config": ("codomyrmex.agents.core", "reset_config"),
        "set_config": ("codomyrmex.agents.core", "set_config"),
        # Core exceptions
        "AgentConfigurationError": ("codomyrmex.agents.core.exceptions", "AgentConfigurationError"),
        "AgentError": ("codomyrmex.agents.core.exceptions", "AgentError"),
        "AgentTimeoutError": ("codomyrmex.agents.core.exceptions", "AgentTimeoutError"),
        "ContextError": ("codomyrmex.agents.core.exceptions", "ContextError"),
        "ExecutionError": ("codomyrmex.agents.core.exceptions", "ExecutionError"),
        "SessionError": ("codomyrmex.agents.core.exceptions", "SessionError"),
        "ToolError": ("codomyrmex.agents.core.exceptions", "ToolError"),
        # Submodules / registries
        "AgentPool": ("codomyrmex.agents.pooling", "AgentPool"),
        "AgentEvaluator": ("codomyrmex.agents.evaluation.benchmark", "AgentBenchmark"),
        "ConversationHistory": ("codomyrmex.agents.memory.conversation", "ConversationHistory"),
        "InfrastructureAgent": ("codomyrmex.agents.infrastructure", "InfrastructureAgent"),
        "AgentRegistry": ("codomyrmex.agents.agent_setup", "AgentRegistry"),
    }
)


def _resolve(name: str) -> Any:
    module_name, attr = _EXPORTS[name]
    module = importlib.import_module(module_name)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise ImportError(f"cannot import name {attr!r} from {module_name!r}") from exc


def __getattr__(name: str) -> Any:
    """PEP 562 lazy loading: import public names on first access."""
    if name in _EXPORTS:
        value = _resolve(name)
        globals()[name] = value  # cache so future lookups skip __getattr__
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_EXPORTS))


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
    "ParseResult",
    # Pi coding agent (lazy-loaded)
    "PiClient",
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


def cli_commands() -> dict[str, Any]:
    """Return CLI commands for the agents module (lazy import of clients)."""
    return _cli_commands_impl()


def _cli_commands_impl() -> dict[str, Any]:
    def _list_agents() -> None:
        providers = []
        provider_map = {
            "claude": _resolve("ClaudeClient"),
            "codex": _resolve("CodexClient"),
            "gemini": _resolve("GeminiClient"),
            "jules": _resolve("JulesClient"),
            "mistral_vibe": _resolve("MistralVibeClient"),
            "openclaw": _resolve("OpenClawClient"),
            "opencode": _resolve("OpenCodeClient"),
            "every_code": _resolve("EveryCodeClient"),
            "o1": _resolve("O1Client"),
            "deepseek": _resolve("DeepSeekClient"),
            "qwen": _resolve("QwenClient"),
            "agentic_seek": _resolve("AgenticSeekClient"),
            "mission_control": _resolve("MissionControlClient"),
            "pi": _resolve("PiClient"),
        }
        for name, client in provider_map.items():
            status = "available" if client is not None else "not installed"
            providers.append(f"  {name}: {status}")
        print("Registered agent providers:")
        print("\n".join(providers))

    def _show_config() -> None:
        config = get_config()
        print("Agent configuration:")
        for key, value in vars(config).items():
            print(f"  {key}: {value}")

    return {
        "list": _list_agents,
        "config": _show_config,
    }
