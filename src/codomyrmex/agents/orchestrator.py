"""Infinite Conversation Orchestrator.

Orchestrates sustained multi-turn conversations between Ollama, Claude Code,
and Antigravity agents using real LLM inference over the file-based relay bus.

Supports file-injection: inject real project files (TO-DO.md, SPEC.md, source
files, etc.) into agent context so conversations are grounded in actual code.

Usage — basic conversation::

    from codomyrmex.agents.orchestrator import ConversationOrchestrator

    orch = ConversationOrchestrator(
        channel="demo-conv",
        agents=[
            {"identity": "ollama-analyst", "persona": "data analyst", "provider": "ollama"},
            {"identity": "antigravity-reviewer", "persona": "code reviewer", "provider": "ollama"},
        ],
    )
    transcript = orch.run(rounds=5)

Usage — file-injected TO-DO development loop::

    orch = ConversationOrchestrator.dev_loop(
        todo_path="TO-DO.md",
        extra_files=["CHANGELOG.md", "src/codomyrmex/agents/orchestrator.py"],
    )
    transcript = orch.run(rounds=0)  # infinite, scaffolded by TO-DO items
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codomyrmex.agents.llm_client import AgentRequest, OllamaClient
from codomyrmex.ide.antigravity.agent_relay import AgentRelay
from codomyrmex.logging_monitoring.core.correlation import (
    with_correlation,
)

logger = logging.getLogger(__name__)


# ── Data Structures ──────────────────────────────────────────────────

@dataclass
class ConversationTurn:
    """A single turn in the conversation."""

    turn_number: int
    speaker: str
    provider: str
    model: str
    content: str
    timestamp: str
    elapsed_seconds: float
    token_estimate: int = 0


@dataclass
class AgentSpec:
    """Specification for a conversation participant."""

    identity: str
    persona: str
    provider: str = "ollama"
    model: str = ""

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        if not self.model:
            if self.provider == "ollama":
                self.model = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
            else:
                self.model = "claude-3-haiku-20240307"


@dataclass
class FileContext:
    """A project file injected into agent context.

    Reads the file on construction; optionally clips to ``max_lines``.
    """

    path: Path
    content: str = ""
    max_lines: int = 200

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        self.path = Path(self.path)
        if not self.content and self.path.is_file():
            raw = self.path.read_text(errors="replace")
            lines = raw.splitlines()
            if len(lines) > self.max_lines:
                self.content = "\n".join(lines[: self.max_lines])
                self.content += f"\n... ({len(lines) - self.max_lines} more lines)"
            else:
                self.content = raw

    @property
    def name(self) -> str:
        """Execute Name operations natively."""
        return self.path.name

    @property
    def token_estimate(self) -> int:
        """Execute Token Estimate operations natively."""
        return len(self.content.split())


def extract_todo_items(text: str) -> list[str]:
    """Extract unchecked TO-DO items (``- [ ]``) from markdown text.

    Returns a list of item strings, one per unchecked checkbox.
    """
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            items.append(stripped[5:].strip())
        elif stripped.startswith("- [/]"):
            items.append(stripped[5:].strip() + " (in progress)")
    return items


@dataclass
class ConversationLog:
    """Complete conversation log with metadata."""

    channel_id: str
    started_at: str
    ended_at: str = ""
    turns: list[ConversationTurn] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    total_rounds: int = 0
    status: str = "running"
    correlation_id: str = ""

    def summary(self) -> dict[str, Any]:
        """Return a summary dict."""
        return {
            "channel_id": self.channel_id,
            "status": self.status,
            "total_turns": len(self.turns),
            "total_rounds": self.total_rounds,
            "agents": self.agents,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "correlation_id": self.correlation_id,
        }

    def export(self, path: str | Path) -> Path:
        """Export conversation to JSONL."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w") as f:
            f.write(json.dumps(self.summary()) + "\n")
            for turn in self.turns:
                f.write(json.dumps(asdict(turn)) + "\n")
        logger.info(f"[Orchestrator] Exported {len(self.turns)} turns to {p}")
        return p


# ── LLM Clients ─────────────────────────────────────────────────────

def _create_llm_client(spec: AgentSpec) -> Any:
    """Create a real LLM client for the given agent spec.

    Args:
        spec: Agent specification with provider and model.

    Returns:
        A client with an ``execute_with_session(request)`` method.

    Raises:
        RuntimeError: If the provider is unavailable.
    """
    if spec.provider == "ollama":
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        return OllamaClient(model=spec.model, base_url=base_url)

    if spec.provider in ("claude", "claude_code", "antigravity"):
        # Try Claude first (if API key present), otherwise Ollama with spec's model.
        if os.environ.get("ANTHROPIC_API_KEY"):
            try:
                from codomyrmex.agents.llm_client import get_llm_client
                client = get_llm_client(identity=spec.identity)

                if spec.provider == "antigravity":
                    from codomyrmex.ide.antigravity import AntigravityClient
                    from codomyrmex.ide.antigravity.tool_provider import (
                        AntigravityToolProvider,
                    )

                    ag_client = AntigravityClient()
                    try:
                        ag_client.connect()
                    except (ValueError, RuntimeError, AttributeError, OSError, TypeError):
                        pass

                    provider = AntigravityToolProvider(ag_client)
                    registry = provider.get_tool_registry()

                    for tool in registry.list_tools():
                        client.register_tool(
                            name=tool.name,
                            description=tool.description,
                            input_schema=tool.args_schema,
                            handler=tool.func
                        )

                    # Wrap the client so execute_with_session calls execute_with_tools
                    class AntigravityCodeImplementerWrapper:
                        """Functional component: AntigravityCodeImplementerWrapper."""
                        def __init__(self, base_client):
                            """Execute   Init   operations natively."""
                            self.client = base_client

                        def execute_with_session(self, request, session=None, session_id=None):
                            """Execute Execute With Session operations natively."""
                            if hasattr(self.client, 'execute_with_tools'):
                                logger.info(f"[{spec.identity}] Executing with full Antigravity tool loop...")
                                return self.client.execute_with_tools(request, auto_execute=True, max_tool_rounds=15)
                            return self.client.execute_with_session(request, session, session_id)

                    return AntigravityCodeImplementerWrapper(client)
                return client
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                logger.error(f"Failed to create Claude client: {e}")

        # Fallback: same Ollama path, overriding the user's model choice for valid local inference if they selected Claude but don't have a key.
        fallback_model = spec.model
        if spec.provider != "ollama":
            fallback_model = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")

        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        logger.info(
            f"[{spec.identity}] Provider '{spec.provider}' → "
            f"Ollama fallback ({fallback_model})"
        )
        return OllamaClient(model=fallback_model, base_url=base_url)

    raise RuntimeError(f"Unknown provider: {spec.provider}")


# ── Orchestrator ─────────────────────────────────────────────────────

class ConversationOrchestrator:
    """Orchestrate infinite conversations between LLM agents over a relay.

    Each agent uses a real LLM backend (Ollama, Claude, etc.) and posts
    messages to a shared ``AgentRelay`` channel.  The orchestrator drives
    a round-robin conversation loop, optionally forever (``rounds=0``).

    Args:
        channel: Relay channel ID (auto-generated if empty).
        agents: List of agent specs (dicts or ``AgentSpec`` instances).
        seed_prompt: Initial prompt to kick off the conversation.
        relay_dir: Override relay storage directory (for tests).
        context_files: Paths to project files to inject into agent context.
        todo_path: Path to TO-DO.md for per-round scaffolding.
        max_retries: Number of LLM retry attempts on failure.
    """

    def __init__(
        self,
        *,
        channel: str = "",
        agents: list[dict[str, str] | AgentSpec] | None = None,
        seed_prompt: str = "Let's discuss how AI agents can collaborate effectively.",
        relay_dir: str | None = None,
        context_files: list[str | Path] | None = None,
        todo_path: str | Path | None = None,
        max_retries: int = 2,
    ) -> None:
        """Execute   Init   operations natively."""
        self.channel_id = channel or f"conv-{uuid.uuid4().hex[:8]}"
        self.seed_prompt = seed_prompt
        self.max_retries = max_retries
        self._running = False

        # Load context files.
        self.context_files: list[FileContext] = []
        for fp in (context_files or []):
            fc = FileContext(path=Path(fp))
            if fc.content:
                self.context_files.append(fc)
                logger.info(
                    f"[Orchestrator] Loaded context file: {fc.name} "
                    f"(~{fc.token_estimate} tokens)"
                )

        # Parse TO-DO items for per-round scaffolding.
        self.todo_items: list[str] = []
        if todo_path:
            todo_fc = FileContext(path=Path(todo_path), max_lines=500)
            if todo_fc.content:
                self.todo_items = extract_todo_items(todo_fc.content)
                # Also add TO-DO as a context file.
                if todo_fc not in self.context_files:
                    self.context_files.append(todo_fc)
                logger.info(
                    f"[Orchestrator] Extracted {len(self.todo_items)} TO-DO items "
                    f"for per-round scaffolding"
                )

        # Parse agent specs.
        raw_agents = agents or [
            {"identity": "ollama-agent", "persona": "helpful AI assistant", "provider": "ollama"},
            {"identity": "antigravity-agent", "persona": "code reviewer", "provider": "ollama"},
        ]
        self.agents: list[AgentSpec] = []
        for a in raw_agents:
            if isinstance(a, AgentSpec):
                self.agents.append(a)
            else:
                self.agents.append(AgentSpec(**a))

        # Create relay.
        relay_kwargs: dict[str, Any] = {"channel_id": self.channel_id}
        if relay_dir:
            relay_kwargs["relay_dir"] = relay_dir
        self.relay = AgentRelay(**relay_kwargs)

        # Create real LLM clients.
        self.clients: dict[str, Any] = {}
        for spec in self.agents:
            self.clients[spec.identity] = _create_llm_client(spec)
            logger.info(
                f"[Orchestrator] Agent '{spec.identity}' → "
                f"{spec.provider}/{spec.model}"
            )

        # Conversation state.
        self.log = ConversationLog(
            channel_id=self.channel_id,
            started_at=datetime.now(timezone.utc).isoformat(),
            agents=[a.identity for a in self.agents],
        )

    # ── Public API ───────────────────────────────────────────────────

    def run(
        self,
        rounds: int = 3,
        *,
        max_tokens_per_turn: int = 256,
        on_turn: Callable[[ConversationTurn], None] | None = None
    ) -> list[ConversationTurn]:
        """Run the conversation for N rounds (0 = infinite).

        A ''round'' consists of every agent speaking once in order.

        Args:
            rounds: Number of rounds.  ``0`` means infinite (until ``stop()``).
            max_tokens_per_turn: Hint for max response length.
            on_turn: Optional callback invoked after each turn.

        Returns:
            The conversation transcript.
        """
        cid = f"conv-{self.channel_id}-{uuid.uuid4().hex[:8]}"
        with with_correlation(cid) as active_cid:
            self.log.correlation_id = active_cid
            return self._run_loop(rounds, max_tokens_per_turn, on_turn=on_turn)

    def _run_loop(
        self,
        rounds: int,
        max_tokens_per_turn: int,
        on_turn: Callable[[ConversationTurn], None] | None = None
    ) -> list[ConversationTurn]:
        """Internal loop — runs inside a correlation context."""
        self._running = True
        logger.info(
            f"[Orchestrator] Starting conversation '{self.channel_id}' — "
            f"{len(self.agents)} agents, {rounds or '∞'} rounds, "
            f"cid={self.log.correlation_id}"
        )

        # Post the seed prompt from a neutral "moderator" if starting fresh.
        if not self.log.turns:
            self.relay.post_message("moderator", self.seed_prompt)
            context = self.seed_prompt
        else:
            context = self.log.turns[-1].content

        round_num = 0
        while self._running:
            round_num += 1
            if rounds > 0 and round_num > rounds:
                break

            for spec in self.agents:
                if not self._running:
                    break

                turn = self._execute_turn(
                    spec, context, round_num, max_tokens_per_turn
                )
                self.log.turns.append(turn)
                context = turn.content  # next agent responds to this

                if on_turn:
                    on_turn(turn)

        self.log.total_rounds = round_num - 1 if rounds > 0 else round_num
        self.log.status = "completed"
        self.log.ended_at = datetime.now(timezone.utc).isoformat()
        self._running = False

        logger.info(
            f"[Orchestrator] Conversation ended — {len(self.log.turns)} turns, "
            f"{self.log.total_rounds} rounds"
        )
        return list(self.log.turns)

    def stop(self) -> None:
        """Signal the orchestrator to stop after the current turn."""
        logger.info("[Orchestrator] Stop requested")
        self._running = False

    def get_transcript(self) -> list[ConversationTurn]:
        """Return all turns so far."""
        return list(self.log.turns)

    def get_log(self) -> ConversationLog:
        """Return the full conversation log."""
        return self.log

    def load_export(self, path: str | Path) -> None:
        """Load an exported conversation JSONL into the current state."""
        import json
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Export not found: {p}")

        with p.open("r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        if not lines:
            return

        metadata = json.loads(lines[0])
        self.channel_id = metadata.get("channel_id", self.channel_id)
        self.log.channel_id = self.channel_id

        # We start from 1 since 0 is metadata
        self.log.turns.clear()
        for line in lines[1:]:
            if not line.strip():
                continue
            turn_data = json.loads(line)
            turn = ConversationTurn(**turn_data)
            self.log.turns.append(turn)
            # Re-seed into the relay so agents can read it natively if needed
            self.relay.post_message(turn.speaker, turn.content)

        logger.info(f"[Orchestrator] Loaded {len(self.log.turns)} turns from {p}")

    @classmethod
    def dev_loop(
        cls,
        *,
        todo_path: str | Path = "TO-DO.md",
        extra_files: list[str | Path] | None = None,
        agents: list[dict[str, str]] | None = None,
        channel: str = "",
        relay_dir: str | None = None,
    ) -> ConversationOrchestrator:
        """Convenience constructor for TO-DO-scaffolded infinite dev loops.

        Creates an orchestrator pre-loaded with project files and TO-DO
        items for per-round development scaffolding.

        Args:
            todo_path: Path to TO-DO.md (or any checklist file).
            extra_files: Additional project files to inject as context.
            agents: Agent specs (defaults to architect + developer + reviewer).
            channel: Relay channel ID.
            relay_dir: Override relay storage directory.

        Returns:
            A configured ``ConversationOrchestrator`` ready for ``.run()``.
        """
        default_agents = agents or [
            {
                "identity": "architect",
                "persona": (
                    "software architect who reads the TO-DO and project files, "
                    "proposes implementation plans, and identifies dependencies"
                ),
                "provider": "ollama",
            },
            {
                "identity": "developer",
                "persona": (
                    "developer who reviews the architect's plan, writes "
                    "implementation details, and identifies edge cases"
                ),
                "provider": "ollama",
            },
            {
                "identity": "reviewer",
                "persona": (
                    "code reviewer who evaluates the proposed changes, "
                    "checks for correctness, and suggests improvements"
                ),
                "provider": "antigravity",
            },
        ]
        return cls(
            channel=channel or f"devloop-{uuid.uuid4().hex[:6]}",
            agents=default_agents,
            seed_prompt=(
                "Review the TO-DO items and project files below. "
                "Each round, focus on the next unchecked item. "
                "Propose concrete implementation steps."
            ),
            context_files=extra_files or [],
            todo_path=todo_path,
            relay_dir=relay_dir,
        )

    # ── Private ──────────────────────────────────────────────────────

    def _execute_turn(
        self,
        spec: AgentSpec,
        context: str,
        round_num: int,
        max_tokens: int,
    ) -> ConversationTurn:
        """Execute a single turn: prompt → real LLM → relay → log."""
        client = self.clients[spec.identity]
        turn_number = len(self.log.turns) + 1

        # Build prompt with file context + TO-DO scaffolding.
        recent_turns = self.log.turns[-6:]  # last 6 for context
        history = "\n".join(
            f"[{t.speaker}]: {t.content}" for t in recent_turns
        )

        # File context section.
        file_section = ""
        if self.context_files:
            parts = []
            for fc in self.context_files:
                parts.append(f"=== {fc.name} ===\n{fc.content}")
            file_section = (
                "\n\nProject Files (read-only reference):\n"
                + "\n\n".join(parts)
                + "\n"
            )

        # Per-round TO-DO focus.
        todo_focus = ""
        if self.todo_items:
            # Cycle through items round-robin.
            idx = (round_num - 1) % len(self.todo_items)
            todo_focus = (
                f"\n\nCurrent Development Focus (round {round_num}): "
                f"{self.todo_items[idx]}\n"
            )

        prompt = (
            f"System: You are {spec.identity}. Persona: {spec.persona}. "
            f"Keep responses concise (under {max_tokens} tokens). "
            f"Continue the conversation naturally."
            f"{file_section}"
            f"{todo_focus}"
            f"\nConversation so far:\n{history}\n"
            f"[Last message]: {context}\n"
            f"Your response:"
        )

        # Real LLM call with retry.
        req = AgentRequest(prompt=prompt)
        content = ""
        start = time.monotonic()
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 2):  # +2 because range is [1, max+2)
            try:
                resp = client.execute_with_session(req)
                content = resp.content.strip() if hasattr(resp, "content") else str(resp)
                last_error = None
                break
            except Exception as exc:
                last_error = exc
                logger.warning(
                    f"[{spec.identity}] LLM attempt {attempt}/{self.max_retries + 1} "
                    f"failed: {exc}"
                )
                if attempt <= self.max_retries:
                    time.sleep(0.5 * attempt)  # exponential-ish backoff

        if last_error is not None:
            content = f"[Error after {self.max_retries + 1} attempts: {last_error}]"
            logger.error(f"[{spec.identity}] LLM exhausted retries: {last_error}")
        elapsed = time.monotonic() - start

        # Post to relay (persists in JSONL).
        self.relay.post_message(spec.identity, content)

        turn = ConversationTurn(
            turn_number=turn_number,
            speaker=spec.identity,
            provider=spec.provider,
            model=spec.model,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            elapsed_seconds=round(elapsed, 3),
            token_estimate=len(content.split()),
        )
        logger.info(
            f"[Turn {turn_number}] [{spec.identity}] "
            f"({elapsed:.1f}s, ~{turn.token_estimate} tokens): "
            f"{content[:80]}..."
        )
        return turn
