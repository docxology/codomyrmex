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

import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from codomyrmex.ide.antigravity.agent_relay import AgentRelay
from codomyrmex.agents.llm_client import OllamaClient, AgentRequest

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
        }


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
        # Use the unified factory which tries Claude first, then Ollama.
        from codomyrmex.agents.llm_client import get_llm_client
        return get_llm_client(identity=spec.identity)

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
    ) -> None:
        self.channel_id = channel or f"conv-{uuid.uuid4().hex[:8]}"
        self.seed_prompt = seed_prompt
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
        self._running = True
        logger.info(
            f"[Orchestrator] Starting conversation '{self.channel_id}' — "
            f"{len(self.agents)} agents, {rounds or '∞'} rounds"
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

        # Real LLM call.
        req = AgentRequest(prompt=prompt)
        start = time.monotonic()
        try:
            resp = client.execute_with_session(req)
            content = resp.content.strip() if hasattr(resp, "content") else str(resp)
        except Exception as exc:
            content = f"[Error: {exc}]"
            logger.error(f"[{spec.identity}] LLM error: {exc}")
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
