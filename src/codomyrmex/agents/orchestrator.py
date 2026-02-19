"""Infinite Conversation Orchestrator.

Orchestrates sustained multi-turn conversations between Ollama, Claude Code,
and Antigravity agents using real LLM inference over the file-based relay bus.

Usage::

    from codomyrmex.agents.orchestrator import ConversationOrchestrator

    orch = ConversationOrchestrator(
        channel="demo-conv",
        agents=[
            {"identity": "ollama-analyst", "persona": "data analyst", "provider": "ollama"},
            {"identity": "antigravity-reviewer", "persona": "code reviewer", "provider": "ollama"},
        ],
    )
    transcript = orch.run(rounds=5)
    for turn in transcript:
        print(f"[{turn.speaker}] {turn.content[:80]}")
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codomyrmex.ide.antigravity.agent_relay import AgentRelay
from codomyrmex.agents.llm_client import OllamaClient, AgentRequest
from codomyrmex.logging_monitoring.correlation import (
    with_correlation,
    get_correlation_id,
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
        if not self.model:
            if self.provider == "ollama":
                self.model = os.environ.get("OLLAMA_MODEL", "llama3.2:1b")
            else:
                self.model = "claude-3-haiku-20240307"


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
                return get_llm_client(identity=spec.identity)
            except Exception:
                pass
        # Fallback: same Ollama path, preserving the user's model choice.
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        logger.info(
            f"[{spec.identity}] Provider '{spec.provider}' → "
            f"Ollama fallback ({spec.model})"
        )
        return OllamaClient(model=spec.model, base_url=base_url)

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
    """

    def __init__(
        self,
        *,
        channel: str = "",
        agents: list[dict[str, str] | AgentSpec] | None = None,
        seed_prompt: str = "Let's discuss how AI agents can collaborate effectively.",
        relay_dir: str | None = None,
        max_retries: int = 2,
    ) -> None:
        self.channel_id = channel or f"conv-{uuid.uuid4().hex[:8]}"
        self.seed_prompt = seed_prompt
        self.max_retries = max_retries
        self._running = False

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

    def run(self, rounds: int = 3, *, max_tokens_per_turn: int = 256) -> list[ConversationTurn]:
        """Run the conversation for N rounds (0 = infinite).

        A ''round'' consists of every agent speaking once in order.

        Args:
            rounds: Number of rounds.  ``0`` means infinite (until ``stop()``).
            max_tokens_per_turn: Hint for max response length.

        Returns:
            The conversation transcript.
        """
        cid = f"conv-{self.channel_id}-{uuid.uuid4().hex[:8]}"
        with with_correlation(cid) as active_cid:
            self.log.correlation_id = active_cid
            return self._run_loop(rounds, max_tokens_per_turn)

    def _run_loop(self, rounds: int, max_tokens_per_turn: int) -> list[ConversationTurn]:
        """Internal loop — runs inside a correlation context."""
        self._running = True
        logger.info(
            f"[Orchestrator] Starting conversation '{self.channel_id}' — "
            f"{len(self.agents)} agents, {rounds or '∞'} rounds, "
            f"cid={self.log.correlation_id}"
        )

        # Post the seed prompt from a neutral "moderator".
        self.relay.post_message("moderator", self.seed_prompt)
        context = self.seed_prompt

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

        # Build prompt with full conversation context for the agent.
        recent_turns = self.log.turns[-6:]  # last 6 for context
        history = "\n".join(
            f"[{t.speaker}]: {t.content}" for t in recent_turns
        )
        prompt = (
            f"System: You are {spec.identity}. Persona: {spec.persona}. "
            f"Keep responses concise (under {max_tokens} tokens). "
            f"Continue the conversation naturally.\n"
            f"Conversation so far:\n{history}\n"
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
