"""Polymarket Bridge — Finance module integration for PrediHermes.

Extracts structured market price and forecast data from PrediHermes sessions
and brings it into the :mod:`codomyrmex.finance` ecosystem for unified market
analytics, budget tracking, and visualisation.

The bridge operates in two modes:

1. **Session-based**: parses an existing Hermes session that ran a PrediHermes
   pipeline and extracts Polymarket pricing blocks from the conversation.
2. **Live query**: sends a prompt to Hermes (with the PrediHermes skill loaded)
   asking for current market prices for a given topic, then parses the response.

Quick start::

    from codomyrmex.finance.polymarket_bridge import PolymarketBridge

    bridge = PolymarketBridge()

    # Ask PrediHermes for current market prices on a query
    snapshot = bridge.get_market_snapshot("Taiwan invasion 2025")
    print(snapshot.topic, snapshot.markets)

    # Compare implied (market) vs simulated (MiroFish) forecast
    delta = bridge.compare_implied_vs_forecast("iran-conflict")
    print(delta)

See also:
    - :mod:`codomyrmex.skills.skills.custom.geopolitical_market_sim` — pipeline facade
    - ``docs/agents/hermes/predihermes.md`` — integration guide
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

# Regex to find JSON-like price blocks in LLM output
_PRICE_BLOCK_RE = re.compile(
    r"\{[^{}]*\"market[^{}]*\}",
    re.DOTALL | re.IGNORECASE,
)
_YES_PROB_RE = re.compile(
    r"yes\s*(?:price|prob(?:ability)?)[:\s]*([0-9]+(?:\.[0-9]+)?)\s*%?",
    re.IGNORECASE,
)


@dataclass
class MarketPrice:
    """A single Polymarket market price entry.

    Attributes:
        question: Market question text.
        yes_price: Current YES price (0.0 – 1.0).
        no_price: Current NO price (0.0 – 1.0).
        volume: Total volume traded (USD, optional).
        end_date: Market end date string (optional).
        raw: Raw extracted text / dict from LLM output.
    """

    question: str
    yes_price: float
    no_price: float
    volume: float | None = None
    end_date: str | None = None
    raw: Any = field(default=None, repr=False)


@dataclass
class PolymarketSnapshot:
    """A structured snapshot of Polymarket markets for a topic.

    Attributes:
        topic: The topic / query string used to retrieve the snapshot.
        markets: List of :class:`MarketPrice` entries.
        session_id: Hermes session ID that produced this snapshot (if any).
        response_raw: Full raw content from the Hermes response.
    """

    topic: str
    markets: list[MarketPrice] = field(default_factory=list)
    session_id: str | None = None
    response_raw: str = ""


@dataclass
class ForecastDelta:
    """Comparison between market-implied and MiroFish-simulated probability.

    Attributes:
        topic_id: PrediHermes topic identifier.
        implied_yes: Polymarket YES price (market-implied probability).
        simulated_yes: MiroFish simulation YES probability.
        delta: ``simulated_yes - implied_yes``; positive = simulation more bullish.
        interpretation: Human-readable interpretation of the delta.
    """

    topic_id: str
    implied_yes: float | None = None
    simulated_yes: float | None = None
    delta: float | None = None
    interpretation: str = ""


def _parse_yes_price(text: str) -> float | None:
    """Extract the first YES/probability value from LLM text output."""
    m = _YES_PROB_RE.search(text)
    if m:
        val = float(m.group(1))
        return val / 100.0 if val > 1.0 else val
    return None


def _parse_markets_from_text(text: str, topic: str) -> list[MarketPrice]:
    """Best-effort extraction of market prices from raw LLM output."""
    markets: list[MarketPrice] = []

    # Try JSON blocks first
    json_candidates = _PRICE_BLOCK_RE.findall(text)
    for candidate in json_candidates:
        try:
            obj = json.loads(candidate)
            question = obj.get("market", obj.get("question", topic))
            yes_price = float(obj.get("yes", obj.get("yes_price", 0.5)))
            no_price = float(obj.get("no", obj.get("no_price", 1.0 - yes_price)))
            markets.append(
                MarketPrice(
                    question=question,
                    yes_price=yes_price,
                    no_price=no_price,
                    volume=obj.get("volume"),
                    end_date=obj.get("end_date"),
                    raw=obj,
                )
            )
        except (json.JSONDecodeError, ValueError, KeyError):
            continue

    if not markets:
        # Fallback: parse a single implied YES probability from the text
        yes_price = _parse_yes_price(text)
        if yes_price is not None:
            markets.append(
                MarketPrice(
                    question=topic,
                    yes_price=yes_price,
                    no_price=round(1.0 - yes_price, 4),
                    raw=text[:500],
                )
            )

    return markets


class PolymarketBridge:
    """Bridge between PrediHermes Polymarket data and Codomyrmex Finance.

    Args:
        session_prefix: Prefix for Hermes session names created by this bridge.
    """

    def __init__(self, session_prefix: str = "polymarket-bridge") -> None:
        self._session_prefix = session_prefix
        self._client: Any = None

    def _get_client(self) -> Any:
        """Return lazily-initialised :class:`HermesClient`."""
        if self._client is None:
            from codomyrmex.agents.hermes.hermes_client import HermesClient

            self._client = HermesClient()
        return self._client

    def _chat(self, prompt: str, session_suffix: str) -> Any:
        """Execute prompt via Hermes with PrediHermes skill loaded."""
        return self._get_client().chat_session(
            prompt=prompt,
            session_name=f"{self._session_prefix}-{session_suffix}",
            hermes_skill="geopolitical-market-sim",
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_market_snapshot(
        self, topic: str, market_query: str | None = None
    ) -> PolymarketSnapshot:
        """Retrieve current Polymarket prices for a topic via PrediHermes.

        Sends a prompt asking PrediHermes to search Polymarket and return
        structured market prices, then parses the response.

        Args:
            topic: Human-readable topic description (used as context).
            market_query: Specific Polymarket search query (defaults to *topic*).

        Returns:
            :class:`PolymarketSnapshot` with extracted markets.
        """
        query = market_query or topic
        prompt = (
            f"Search Polymarket for markets related to: '{query}'. "
            f"Return the top 5 markets with their YES prices, NO prices, and volume. "
            f"Format each as JSON: {{\"market\": \"...\", \"yes\": 0.XX, \"no\": 0.XX, \"volume\": N}}."
        )
        logger.info("PolymarketBridge.get_market_snapshot: topic=%s", topic)
        resp = self._chat(prompt, session_suffix=f"snapshot-{topic[:20]}")

        raw = getattr(resp, "content", str(resp))
        session_id = (
            resp.metadata.get("session_id") if hasattr(resp, "metadata") else None
        )
        markets = _parse_markets_from_text(raw, topic)

        snapshot = PolymarketSnapshot(
            topic=topic,
            markets=markets,
            session_id=session_id,
            response_raw=raw,
        )
        logger.info(
            "PolymarketBridge: extracted %d markets for '%s'",
            len(markets),
            topic,
        )
        return snapshot

    def get_market_prices(self, topic_id: str) -> list[MarketPrice]:
        """Get current market prices for a tracked PrediHermes topic.

        Convenience wrapper around :meth:`get_market_snapshot` that uses the
        topic_id as both topic and market query.

        Args:
            topic_id: PrediHermes tracked topic identifier slug.

        Returns:
            List of :class:`MarketPrice` entries.
        """
        snapshot = self.get_market_snapshot(topic=topic_id)
        return snapshot.markets

    def compare_implied_vs_forecast(
        self, topic_id: str, session_id: str | None = None
    ) -> ForecastDelta:
        """Compare Polymarket-implied probability vs MiroFish simulation forecast.

        Sends a prompt asking PrediHermes to run the full pipeline for
        *topic_id* and compare the implied market probability against the
        simulation output.

        Args:
            topic_id: PrediHermes tracked topic identifier slug.
            session_id: Optional existing session to continue in.

        Returns:
            :class:`ForecastDelta` with implied, simulated, and delta values.
        """
        prompt = (
            f"Use PrediHermes run-tracked {topic_id} --simulate. "
            f"After the run, summarize implied vs forecast: provide the market-implied "
            f"YES probability and the MiroFish simulated YES probability as two numbers."
        )
        logger.info(
            "PolymarketBridge.compare_implied_vs_forecast: topic=%s", topic_id
        )
        client = self._get_client()
        resp = client.chat_session(
            prompt=prompt,
            session_id=session_id,
            session_name=f"{self._session_prefix}-compare-{topic_id}",
            hermes_skill="geopolitical-market-sim",
        )
        raw = getattr(resp, "content", str(resp))

        # Extract two probabilities from the response
        matches = re.findall(
            r"(?:implied|market)[^\d]*([0-9]+(?:\.[0-9]+)?)\s*%?",
            raw,
            re.IGNORECASE,
        )
        sim_matches = re.findall(
            r"(?:simulated?|forecast|mirofish)[^\d]*([0-9]+(?:\.[0-9]+)?)\s*%?",
            raw,
            re.IGNORECASE,
        )

        def _to_prob(s: str) -> float:
            v = float(s)
            return v / 100.0 if v > 1.0 else v

        implied = _to_prob(matches[0]) if matches else None
        simulated = _to_prob(sim_matches[0]) if sim_matches else None
        delta_val: float | None = None
        interpretation = ""
        if implied is not None and simulated is not None:
            delta_val = round(simulated - implied, 4)
            if delta_val > 0.05:
                interpretation = "Simulation more bullish than market — potential upside mispricing."
            elif delta_val < -0.05:
                interpretation = "Simulation more bearish than market — potential downside risk underpriced."
            else:
                interpretation = "Simulation broadly in line with market pricing."

        return ForecastDelta(
            topic_id=topic_id,
            implied_yes=implied,
            simulated_yes=simulated,
            delta=delta_val,
            interpretation=interpretation,
        )

    def __repr__(self) -> str:
        return f"PolymarketBridge(session_prefix={self._session_prefix!r})"
