"""Geopolitical Market Simulation Pipeline — Codomyrmex Skill Facade.

Typed Python facade for the `PrediHermes` Hermes skill
(``nativ3ai/hermes-geopolitical-market-sim``).  Wraps the Hermes CLI skill
commands into importable, documented, zero-mock Python callables backed by
:class:`~codomyrmex.agents.hermes.hermes_client.HermesClient`.

This module works at two levels:

1. **High-level**: Use :class:`GeopoliticalMarketPipeline`.
2. **Function-level**: Call free functions (``health``, ``list_worldosint_modules``,
   ``track_topic``, …) for quick one-off invocations.

Prerequisites
-------------
- Hermes Agent CLI installed and configured (``hermes --help``).
- PrediHermes skill installed: ``./scripts/install_hermes_skill.sh``
  (or ``hermes skills list | grep geopolitical-market-sim``).
- Companion services running if needed: WorldOSINT headless, MiroFish.

Quick start::

    from codomyrmex.skills.skills.custom.geopolitical_market_sim import (
        GeopoliticalMarketPipeline,
        health,
    )

    # Verify companion stack
    print(health())

    # Programmatic pipeline
    pipeline = GeopoliticalMarketPipeline()
    pipeline.track_topic(
        topic_id="iran-conflict",
        topic="Iran conflict and nuclear diplomacy",
        market_query="Iran nuclear deal",
        keywords=["iran", "nuclear", "iaea"],
        regions=["IR", "IL", "US"],
    )
    pipeline.run_tracked("iran-conflict", simulate=True)

See also:
    - :mod:`codomyrmex.skills.hermes_skill_bridge` — low-level bridge
    - ``docs/agents/hermes/predihermes.md`` — full integration guide
    - https://github.com/nativ3ai/hermes-geopolitical-market-sim
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

# Canonical Hermes skill name (must match `hermes skills list` output)
SKILL_NAME = "geopolitical-market-sim"
_DEFAULT_SESSION_PREFIX = "predihermes"


def _get_client():
    """Return a lazily-created :class:`HermesClient`."""
    from codomyrmex.agents.hermes.hermes_client import HermesClient

    return HermesClient()


def _chat(prompt: str, session_name: str | None = None, session_id: str | None = None) -> Any:
    """Execute *prompt* via Hermes with the PrediHermes skill preloaded."""
    client = _get_client()
    logger.info("PrediHermes chat: session=%s, prompt=%.80s…", session_name, prompt)
    return client.chat_session(
        prompt=prompt,
        session_id=session_id,
        session_name=session_name,
        hermes_skill=SKILL_NAME,
    )


# ── Free-function API ──────────────────────────────────────────────────────────


def health(session_name: str = f"{_DEFAULT_SESSION_PREFIX}-health") -> Any:
    """Run the PrediHermes stack health check.

    Equivalent to ``predihermes health`` or
    ``hermes -s geopolitical-market-sim`` → "Use PrediHermes health".

    Returns:
        :class:`~codomyrmex.agents.core.AgentResponse` with health output.
    """
    return _chat("Use PrediHermes health", session_name=session_name)


def list_worldosint_modules(
    session_name: str = f"{_DEFAULT_SESSION_PREFIX}-modules",
) -> Any:
    """List available WorldOSINT headless modules.

    Returns:
        :class:`~codomyrmex.agents.core.AgentResponse` with module list.
    """
    return _chat(
        "Use PrediHermes list-worldosint-modules",
        session_name=session_name,
    )


def track_topic(
    topic_id: str,
    topic: str,
    market_query: str,
    keywords: list[str],
    regions: list[str],
    session_name: str | None = None,
) -> Any:
    """Track a new geopolitical topic in PrediHermes.

    Args:
        topic_id: Short identifier slug (e.g. ``"iran-conflict"``).
        topic: Human-readable topic description.
        market_query: Polymarket search query string.
        keywords: List of OSINT keywords to monitor.
        regions: ISO 3166-1 alpha-2 region codes.
        session_name: Optional Hermes session name (auto-generated if omitted).

    Returns:
        :class:`~codomyrmex.agents.core.AgentResponse`.
    """
    kw_str = " ".join(f"--keyword {k}" for k in keywords)
    region_str = " ".join(f"--region-code {r}" for r in regions)
    prompt = (
        f"Use PrediHermes track-topic "
        f"--topic-id {topic_id} "
        f"--topic \"{topic}\" "
        f"--market-query \"{market_query}\" "
        f"{kw_str} {region_str}"
    ).strip()
    sn = session_name or f"{_DEFAULT_SESSION_PREFIX}-{topic_id}"
    return _chat(prompt, session_name=sn)


def run_tracked(
    topic_id: str,
    simulate: bool = False,
    simulation_mode: str | None = None,
    target_agents: int | None = None,
    target_rounds: int | None = None,
    require_feed_confirmation: bool = False,
    session_name: str | None = None,
) -> Any:
    """Run a tracked topic (optionally with MiroFish simulation).

    Args:
        topic_id: Topic identifier slug.
        simulate: Whether to run MiroFish simulation after seed.
        simulation_mode: ``"auto"`` | ``"manual"`` (requires *target_agents*).
        target_agents: Number of simulation agents.
        target_rounds: Number of simulation rounds (manual mode).
        require_feed_confirmation: Pause for feed quality confirmation.
        session_name: Optional Hermes session name.

    Returns:
        :class:`~codomyrmex.agents.core.AgentResponse`.
    """
    parts = [f"Use PrediHermes run-tracked {topic_id}"]
    if simulate:
        parts.append("--simulate")
    if simulation_mode:
        parts.append(f"--simulation-mode {simulation_mode}")
    if target_agents is not None:
        parts.append(f"--target-agents {target_agents}")
    if target_rounds is not None:
        parts.append(f"--target-rounds {target_rounds}")
    if require_feed_confirmation:
        parts.append("--require-feed-confirmation")
    prompt = " ".join(parts)
    sn = session_name or f"{_DEFAULT_SESSION_PREFIX}-run-{topic_id}"
    return _chat(prompt, session_name=sn)


def plan_tracked(
    topic_id: str,
    target_agents: int | None = None,
    session_name: str | None = None,
) -> Any:
    """Plan a tracked topic run (check feed quality + simulation sizing).

    Args:
        topic_id: Topic identifier slug.
        target_agents: Optional target agent count for sizing.
        session_name: Optional Hermes session name.

    Returns:
        :class:`~codomyrmex.agents.core.AgentResponse`.
    """
    prompt = f"Use PrediHermes plan-tracked {topic_id}"
    if target_agents is not None:
        prompt += f" --target-agents {target_agents}"
    sn = session_name or f"{_DEFAULT_SESSION_PREFIX}-plan-{topic_id}"
    return _chat(prompt, session_name=sn)


def dashboard(topic_id: str, session_name: str | None = None) -> Any:
    """Show the ASCII drift dashboard for a tracked topic.

    Args:
        topic_id: Topic identifier slug.
        session_name: Optional Hermes session name.

    Returns:
        :class:`~codomyrmex.agents.core.AgentResponse` with dashboard text.
    """
    sn = session_name or f"{_DEFAULT_SESSION_PREFIX}-dash-{topic_id}"
    return _chat(
        f"Use PrediHermes dashboard {topic_id} and summarize top drift signals.",
        session_name=sn,
    )


def update_topic(
    topic_id: str,
    add_module: str | None = None,
    remove_module: str | None = None,
    set_max_rounds: int | None = None,
    set_simulation_mode: str | None = None,
    set_target_agents: int | None = None,
    session_name: str | None = None,
) -> Any:
    """Update an existing tracked topic's configuration.

    Args:
        topic_id: Topic identifier slug.
        add_module: WorldOSINT module name to add.
        remove_module: WorldOSINT module name to remove.
        set_max_rounds: Override maximum rounds.
        set_simulation_mode: ``"auto"`` | ``"manual"``.
        set_target_agents: Override target agent count.
        session_name: Optional Hermes session name.

    Returns:
        :class:`~codomyrmex.agents.core.AgentResponse`.
    """
    parts = [f"Use PrediHermes update-topic {topic_id}"]
    if add_module:
        parts.append(f"add module {add_module}")
    if remove_module:
        parts.append(f"remove module {remove_module}")
    if set_max_rounds is not None:
        parts.append(f"set max rounds to {set_max_rounds}")
    if set_simulation_mode:
        parts.append(f"set simulation mode to {set_simulation_mode}")
    if set_target_agents is not None:
        parts.append(f"set target agents to {set_target_agents}")
    prompt = " and ".join(parts)
    sn = session_name or f"{_DEFAULT_SESSION_PREFIX}-update-{topic_id}"
    return _chat(prompt, session_name=sn)


# ── Object-oriented API ────────────────────────────────────────────────────────


@dataclass
class TopicConfig:
    """Configuration for a PrediHermes tracked topic.

    Attributes:
        topic_id: Short identifier slug (e.g. ``"iran-conflict"``).
        topic: Human-readable description.
        market_query: Polymarket search string.
        keywords: OSINT keyword list.
        regions: ISO 3166-1 alpha-2 region codes.
        max_rounds: Maximum simulation rounds (optional).
        target_agents: Target number of simulation agents.
        simulation_mode: ``"auto"`` | ``"manual"`` (default: ``"auto"``).
    """

    topic_id: str
    topic: str
    market_query: str
    keywords: list[str] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)
    max_rounds: int | None = None
    target_agents: int = 48
    simulation_mode: str = "auto"


class GeopoliticalMarketPipeline:
    """High-level object-oriented interface for the PrediHermes skill.

    Wraps all :mod:`geopolitical_market_pipeline` free functions into a
    stateful pipeline object that tracks a *session_prefix* so multi-turn
    interactions stay in the same Hermes session.

    Args:
        session_prefix: Prefix for all Hermes session names created by this
            pipeline instance (default: ``"predihermes"``).

    Example::

        pipeline = GeopoliticalMarketPipeline()
        pipeline.track_topic(
            topic_id="taiwan-strait",
            topic="Taiwan strait military tension",
            market_query="Taiwan conflict 2025",
            keywords=["taiwan", "pla", "tsmc", "7th fleet"],
            regions=["TW", "CN", "US", "JP"],
        )
        result = pipeline.run_tracked("taiwan-strait", simulate=True, target_agents=48)
        print(result.content)
    """

    def __init__(self, session_prefix: str = _DEFAULT_SESSION_PREFIX) -> None:
        self._session_prefix = session_prefix

    def _sn(self, suffix: str) -> str:
        return f"{self._session_prefix}-{suffix}"

    # ── Delegation to free functions ──────────────────────────────────────

    def health(self) -> Any:
        """Check PrediHermes stack health."""
        return health(session_name=self._sn("health"))

    def list_worldosint_modules(self) -> Any:
        """List available WorldOSINT modules."""
        return list_worldosint_modules(session_name=self._sn("modules"))

    def track_topic(
        self,
        topic_id: str,
        topic: str,
        market_query: str,
        keywords: list[str],
        regions: list[str],
    ) -> Any:
        """Track a new geopolitical topic."""
        return track_topic(
            topic_id=topic_id,
            topic=topic,
            market_query=market_query,
            keywords=keywords,
            regions=regions,
            session_name=self._sn(f"track-{topic_id}"),
        )

    def track_from_config(self, config: TopicConfig) -> Any:
        """Track a topic from a :class:`TopicConfig` dataclass."""
        return self.track_topic(
            topic_id=config.topic_id,
            topic=config.topic,
            market_query=config.market_query,
            keywords=config.keywords,
            regions=config.regions,
        )

    def run_tracked(
        self,
        topic_id: str,
        simulate: bool = False,
        target_agents: int | None = None,
        simulation_mode: str | None = None,
    ) -> Any:
        """Run a tracked topic, optionally with MiroFish simulation."""
        return run_tracked(
            topic_id=topic_id,
            simulate=simulate,
            target_agents=target_agents,
            simulation_mode=simulation_mode,
            session_name=self._sn(f"run-{topic_id}"),
        )

    def plan_tracked(self, topic_id: str, target_agents: int | None = None) -> Any:
        """Plan a tracked topic run (feed quality + sizing check)."""
        return plan_tracked(
            topic_id=topic_id,
            target_agents=target_agents,
            session_name=self._sn(f"plan-{topic_id}"),
        )

    def dashboard(self, topic_id: str) -> Any:
        """Show the ASCII drift dashboard for a topic."""
        return dashboard(topic_id=topic_id, session_name=self._sn(f"dash-{topic_id}"))

    def update_topic(self, topic_id: str, **kwargs: Any) -> Any:
        """Update a tracked topic's configuration."""
        return update_topic(
            topic_id=topic_id,
            session_name=self._sn(f"update-{topic_id}"),
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"GeopoliticalMarketPipeline(session_prefix={self._session_prefix!r})"
