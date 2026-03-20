"""Geopolitical Market Simulation Pipeline — typed Codomyrmex facade.

Wraps the ``hermes-geopolitical-market-sim`` skill
(https://github.com/nativ3ai/hermes-geopolitical-market-sim)
as a first-class Python API, delegating execution to the Hermes CLI via
:class:`~codomyrmex.agents.hermes.HermesClient`.

Typical usage::

    from codomyrmex.skills.skills.custom.geopolitical_market_sim import (
        GeopoliticalMarketPipeline,
    )

    pipeline = GeopoliticalMarketPipeline()
    result = pipeline.track_topic(
        topic_id="btc_fed",
        topic="Federal Reserve rate decision",
        market_query="BTC price impact",
        keywords=["FOMC", "interest rate", "BTC"],
        regions=["US"],
    )
    print(result["content"])

"""

from __future__ import annotations

from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

SKILL_NAME = "geopolitical_market_sim"
SKILL_DESCRIPTION = "Geopolitical + Polymarket intelligence simulation skill"


class GeopoliticalMarketPipeline:
    """High-level API for the PrediHermes geopolitical-market-sim skill.

    Each method corresponds to a skill command (``/run``, ``/plan``,
    ``/dashboard``, ``/health``) and routes through
    :class:`~codomyrmex.agents.hermes.HermesClient` so that Hermes
    session persistence, context compression, and tool-use are active.

    Args:
        hermes_home: Override ``HERMES_HOME`` if needed.
        session_id: Pre-existing session ID to continue.
        timeout: Default subprocess timeout in seconds (default 300).

    """

    def __init__(
        self,
        hermes_home: str | None = None,
        session_id: str | None = None,
        timeout: int = 300,
    ) -> None:
        import os

        self._hermes_home = hermes_home or os.environ.get(
            "HERMES_HOME", str(__import__("pathlib").Path.home() / ".hermes")
        )
        self._session_id = session_id
        self._timeout = timeout

    # ------------------------------------------------------------------
    # Core commands
    # ------------------------------------------------------------------

    def track_topic(
        self,
        topic_id: str,
        topic: str,
        market_query: str,
        keywords: list[str] | None = None,
        regions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Start or resume tracking a geopolitical topic.

        Builds a structured prompt and sends it to the geopolitical skill,
        creating or continuing a session keyed by *topic_id*.

        Args:
            topic_id: Unique identifier (used as session key).
            topic: Human-readable topic description.
            market_query: Financial/market question to resolve.
            keywords: Optional list of search keywords.
            regions: Optional list of relevant regions / countries.

        Returns:
            dict with ``status``, ``content``, ``session_id``, ``error``.

        """
        kw_str = ", ".join(keywords or [])
        reg_str = ", ".join(regions or [])
        prompt = (
            f"TOPIC: {topic}\n"
            f"MARKET QUERY: {market_query}\n"
            + (f"KEYWORDS: {kw_str}\n" if kw_str else "")
            + (f"REGIONS: {reg_str}\n" if reg_str else "")
            + "\nAnalyse the geopolitical situation and its likely market impact."
        )
        return self._run_skill_prompt(prompt, session_label=topic_id)

    def run_tracked(
        self,
        topic_id: str,
        simulate: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Run the full pipeline for a tracked topic.

        Args:
            topic_id: Topic to run (must have been set up with :meth:`track_topic`).
            simulate: If True, adds a simulation flag to the prompt.
            **kwargs: Extra context passed as key=value lines in the prompt.

        Returns:
            dict with ``status``, ``content``, ``session_id``, ``error``.

        """
        extra = "\n".join(f"{k}: {v}" for k, v in kwargs.items())
        prompt = (
            f"/run topic_id={topic_id}"
            + (" simulate=true" if simulate else "")
            + (f"\n{extra}" if extra else "")
        )
        return self._run_skill_prompt(prompt, session_label=topic_id)

    def plan_tracked(self, topic_id: str, **kwargs: Any) -> dict[str, Any]:
        """Generate a research plan for *topic_id*.

        Args:
            topic_id: Topic identifier.
            **kwargs: Additional prompt context.

        Returns:
            dict with ``status``, ``content``, ``session_id``, ``error``.

        """
        extra = "\n".join(f"{k}: {v}" for k, v in kwargs.items())
        prompt = f"/plan topic_id={topic_id}" + (f"\n{extra}" if extra else "")
        return self._run_skill_prompt(prompt, session_label=f"{topic_id}_plan")

    def dashboard(self, topic_id: str) -> dict[str, Any]:
        """Retrieve the current dashboard / summary for *topic_id*.

        Args:
            topic_id: Topic identifier.

        Returns:
            dict with ``status``, ``content``, ``session_id``, ``error``.

        """
        prompt = f"/dashboard topic_id={topic_id}"
        return self._run_skill_prompt(prompt, session_label=f"{topic_id}_dashboard")

    def health(self) -> dict[str, Any]:
        """Run the skill stack health check.

        Returns:
            dict with ``status`` and ``content`` describing system health.

        """
        prompt = "/health"
        result = self._run_skill_prompt(prompt, session_label="health_check")
        return result

    def list_worldosint_modules(self) -> dict[str, Any]:
        """List available WorldOSINT modules within the skill.

        Returns:
            dict with ``status``, ``modules`` (list of str), ``content``.

        """
        prompt = "/list_modules"
        result = self._run_skill_prompt(prompt, session_label="list_modules")
        if result["status"] == "success":
            # Parse bullet-list style output into a clean list
            lines = result.get("content", "").splitlines()
            modules = [
                l.lstrip("•-* ").strip()
                for l in lines
                if l.strip().startswith(("•", "-", "*"))
            ]
            result["modules"] = modules
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run_skill_prompt(
        self,
        prompt: str,
        session_label: str = "default",
    ) -> dict[str, Any]:
        """Send *prompt* to the geopolitical skill, managing session state."""
        from codomyrmex.agents.hermes.hermes_client import HermesClient

        session_id = self._session_id or f"geopol_{session_label}"
        client = HermesClient(config={"hermes_timeout": self._timeout})
        try:
            response = client.chat_session(
                prompt=prompt,
                session_id=session_id,
                hermes_skill=SKILL_NAME,
            )
            # Persist the session for subsequent calls
            if response.metadata.get("session_id"):
                self._session_id = response.metadata["session_id"]
            return {
                "status": "success" if response.is_success() else "error",
                "content": response.content,
                "session_id": self._session_id,
                "error": response.error,
            }
        except Exception as exc:
            logger.error("GeopoliticalMarketPipeline error: %s", exc, exc_info=True)
            return {
                "status": "error",
                "content": "",
                "session_id": session_id,
                "error": str(exc),
            }
