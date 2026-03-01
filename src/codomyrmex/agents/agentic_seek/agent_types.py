"""Data models for the agenticSeek integration.

Defines enums, dataclasses, and typed structures that mirror the
agenticSeek framework's agent types, configuration, memory, task
planning, and execution result schemas.

Reference: https://github.com/Fosowl/agenticSeek
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Any

from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL


# ---------------------------------------------------------------------------
# Agent type taxonomy
# ---------------------------------------------------------------------------

@unique
class AgenticSeekAgentType(Enum):
    """Enumeration of agent specialisations exposed by agenticSeek.

    Each value maps to a concrete agent class in the upstream project:

    * ``CODER``   → ``CoderAgent``  (Python / C / Go / Java / Bash)
    * ``BROWSER`` → ``BrowserAgent`` (SearxNG + Selenium web navigation)
    * ``PLANNER`` → ``PlannerAgent`` (multi-agent task decomposition)
    * ``FILE``    → ``FileAgent``    (filesystem operations)
    * ``CASUAL``  → ``CasualAgent``  (conversational chat, no tools)
    """

    CODER = "coder"
    BROWSER = "browser"
    PLANNER = "planner"
    FILE = "file"
    CASUAL = "casual"

    @classmethod
    def from_string(cls, value: str) -> AgenticSeekAgentType:
        """Resolve an agent type from a case-insensitive string.

        Args:
            value: Agent type name (e.g. ``"coder"``, ``"BROWSER"``).

        Returns:
            The matching ``AgenticSeekAgentType`` member.

        Raises:
            ValueError: If *value* does not match any member.
        """
        normalised = value.strip().lower()
        for member in cls:
            if member.value == normalised:
                return member
        valid = ", ".join(m.value for m in cls)
        raise ValueError(
            f"Unknown agent type {value!r}. Valid types: {valid}"
        )


# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------

@unique
class AgenticSeekProvider(Enum):
    """LLM provider backends supported by agenticSeek."""

    OLLAMA = "ollama"
    LM_STUDIO = "lm-studio"
    OPENAI = "openai"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"
    HUGGINGFACE = "huggingface"
    TOGETHER_AI = "togetherAI"
    OPENROUTER = "openrouter"
    SERVER = "server"


@dataclass(frozen=True)
class AgenticSeekConfig:
    """Typed representation of an agenticSeek ``config.ini``.

    Every field corresponds to a key in ``[MAIN]`` or ``[BROWSER]``.
    Defaults match the upstream project defaults.
    """

    # [MAIN]
    is_local: bool = True
    provider_name: str = "ollama"
    provider_model: str = "deepseek-r1:14b"
    provider_server_address: str = field(
        default_factory=lambda: os.getenv("AGENTIC_SEEK_PROVIDER_URL", DEFAULT_OLLAMA_URL)
    )
    agent_name: str = "Friday"
    recover_last_session: bool = False
    save_session: bool = False
    speak: bool = False
    listen: bool = False
    work_dir: str = ""
    jarvis_personality: bool = False
    languages: list[str] = field(default_factory=lambda: ["en"])

    # [BROWSER]
    headless_browser: bool = True
    stealth_mode: bool = True

    def to_ini_dict(self) -> dict[str, dict[str, str]]:
        """Serialise to a dict suitable for ``configparser.write()``.

        Returns:
            Two-level mapping ``{"MAIN": {…}, "BROWSER": {…}}``.
        """
        return {
            "MAIN": {
                "is_local": str(self.is_local),
                "provider_name": self.provider_name,
                "provider_model": self.provider_model,
                "provider_server_address": self.provider_server_address,
                "agent_name": self.agent_name,
                "recover_last_session": str(self.recover_last_session),
                "save_session": str(self.save_session),
                "speak": str(self.speak),
                "listen": str(self.listen),
                "work_dir": self.work_dir,
                "jarvis_personality": str(self.jarvis_personality),
                "languages": " ".join(self.languages),
            },
            "BROWSER": {
                "headless_browser": str(self.headless_browser),
                "stealth_mode": str(self.stealth_mode),
            },
        }


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------

@dataclass
class AgenticSeekMemoryEntry:
    """Single turn in the agenticSeek conversation memory.

    Mirrors the ``{'role': …, 'content': …}`` dicts used by
    ``sources.memory.Memory``.
    """

    role: str  # "system" | "user" | "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, str]:
        """Return the OpenAI-compatible message dict."""
        return {"role": self.role, "content": self.content}


# ---------------------------------------------------------------------------
# Task planning
# ---------------------------------------------------------------------------

@unique
class AgenticSeekTaskStatus(Enum):
    """Lifecycle states for a single planning step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgenticSeekTaskStep:
    """One step in a ``PlannerAgent`` execution plan.

    Attributes:
        agent_type: Which agent should execute this step.
        task_id: Unique identifier within the plan.
        description: Human-readable task description.
        dependencies: IDs of steps that must complete first.
        status: Current lifecycle state.
        result: Output produced once complete.
    """

    agent_type: AgenticSeekAgentType
    task_id: int
    description: str
    dependencies: list[int] = field(default_factory=list)
    status: AgenticSeekTaskStatus = AgenticSeekTaskStatus.PENDING
    result: str | None = None


# ---------------------------------------------------------------------------
# Execution results
# ---------------------------------------------------------------------------

@dataclass
class AgenticSeekExecutionResult:
    """Outcome of running a single code / tool block.

    Mirrors ``sources.schemas.executorResult`` in upstream agenticSeek.
    """

    code: str
    feedback: str
    success: bool
    tool_type: str
    execution_time: float = 0.0

    def __str__(self) -> str:
        status = "✓" if self.success else "✗"
        return (
            f"[{status}] {self.tool_type} "
            f"({self.execution_time:.2f}s):\n{self.feedback}"
        )


# ---------------------------------------------------------------------------
# Supported languages for code execution
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES: dict[str, dict[str, Any]] = {
    "python": {"extension": ".py", "runner": ["python3"], "aliases": ["py", "python3"]},
    "c": {"extension": ".c", "runner": ["gcc", "-o", "/tmp/a.out"], "aliases": ["c"]},
    "go": {"extension": ".go", "runner": ["go", "run"], "aliases": ["golang"]},
    "java": {"extension": ".java", "runner": ["javac"], "aliases": ["java"]},
    "bash": {"extension": ".sh", "runner": ["bash"], "aliases": ["sh", "shell", "zsh"]},
}


def resolve_language(name: str) -> str | None:
    """Map an alias or canonical name to a canonical language key.

    Args:
        name: Language name or alias (case-insensitive).

    Returns:
        Canonical language key, or ``None`` if unrecognised.
    """
    normalised = name.strip().lower()
    if normalised in SUPPORTED_LANGUAGES:
        return normalised
    for lang, meta in SUPPORTED_LANGUAGES.items():
        if normalised in meta.get("aliases", []):
            return lang
    return None
