"""Demand Aggregation Module.

Aggregates demand from multiple entities to increase negotiation power
and trigger bulk auctions when thresholds are reached.

Features:
- Category-based demand registration with max-price constraints
- Configurable bulk thresholds per category
- Demand statistics and analytics
- Category lifecycle (register, query, clear)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

from .auction import ReverseAuction

logger = get_logger(__name__)


@dataclass
class DemandEntry:
    """A single demand registration."""

    persona_id: str
    category: str
    max_price: float
    quantity: int = 1
    registered_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CategoryStats:
    """Statistics for accumulated demand in a category."""

    category: str
    demand_count: int
    total_quantity: int
    avg_max_price: float
    min_max_price: float
    max_max_price: float
    unique_personas: int


class DemandAggregator:
    """Aggregates similar demands into bulk auctions.

    Tracks demand per category, provides analytics, and triggers
    bulk auctions when configurable thresholds are reached.

    Example::

        agg = DemandAggregator(auction_system)
        agg.register_interest("GPU Compute", "alice", 100.0, quantity=5)
        agg.register_interest("GPU Compute", "bob", 120.0, quantity=3)
        stats = agg.get_stats("GPU Compute")
        assert stats.demand_count == 2
    """

    def __init__(
        self,
        auction_system: ReverseAuction,
        default_threshold: int = 5,
        bulk_discount: float = 0.10,
    ) -> None:
        """Initialize this instance."""
        self.auction_system = auction_system
        self.default_threshold = default_threshold
        self.bulk_discount = bulk_discount
        self._demands: dict[str, list[DemandEntry]] = {}
        self._thresholds: dict[str, int] = {}
        self._triggered_auctions: list[str] = []

    @property
    def _pending_demands(self) -> dict[str, list[DemandEntry]]:
        """Backward-compatible alias for ``_demands``."""
        return self._demands

    # ── Registration ────────────────────────────────────────────────

    def register_interest(
        self,
        category: str,
        persona_id: str,
        max_price: float,
        quantity: int = 1,
        **metadata: Any,
    ) -> DemandEntry:
        """Register demand for a category.

        Args:
            category: Product or service category.
            persona_id: ID of the requesting persona.
            max_price: Maximum acceptable price per unit.
            quantity: Number of units desired.

        Returns:
            The registered DemandEntry.
        """
        entry = DemandEntry(
            persona_id=persona_id,
            category=category,
            max_price=max_price,
            quantity=quantity,
            metadata=metadata,
        )
        self._demands.setdefault(category, []).append(entry)
        logger.info("Registered demand for %s from %s (qty=%d, max=%.2f)", category, persona_id, quantity, max_price)
        return entry

    def set_threshold(self, category: str, threshold: int) -> None:
        """Set a custom bulk threshold for a category."""
        self._thresholds[category] = threshold

    # ── Statistics ──────────────────────────────────────────────────

    def get_stats(self, category: str) -> CategoryStats | None:
        """Get demand statistics for a category.

        Returns None if no demand exists.
        """
        entries = self._demands.get(category)
        if not entries:
            return None

        prices = [e.max_price for e in entries]
        return CategoryStats(
            category=category,
            demand_count=len(entries),
            total_quantity=sum(e.quantity for e in entries),
            avg_max_price=sum(prices) / len(prices),
            min_max_price=min(prices),
            max_max_price=max(prices),
            unique_personas=len({e.persona_id for e in entries}),
        )

    def list_categories(self) -> list[str]:
        """List all categories with pending demand."""
        return list(self._demands.keys())

    def get_demand(self, category: str) -> list[DemandEntry]:
        """Get all demand entries for a category."""
        return list(self._demands.get(category, []))

    # ── Bulk Auction Trigger ────────────────────────────────────────

    def trigger_bulk_auction(self, category: str, threshold: int | None = None) -> str:
        """Trigger a bulk auction if enough demand is gathered.

        Args:
            category: Category to check.
            threshold: Override threshold (default: per-category or global).

        Returns:
            Auction ID if triggered, empty string otherwise.
        """
        if category not in self._demands:
            return ""

        demands = self._demands[category]
        effective_threshold = threshold or self._thresholds.get(category, self.default_threshold)

        if len(demands) < effective_threshold:
            logger.debug("Insufficient demand for %s (%d/%d)", category, len(demands), effective_threshold)
            return ""

        # Calculate bulk parameters
        total_quantity = sum(e.quantity for e in demands)
        avg_price = sum(e.max_price for e in demands) / len(demands)
        target_price_per_unit = avg_price * (1.0 - self.bulk_discount)

        description = f"Bulk: {total_quantity} units of {category} ({len(demands)} buyers)"
        proxy_persona = demands[0].persona_id

        auction_id = self.auction_system.create_request(
            persona_id=proxy_persona,
            description=description,
            max_price=target_price_per_unit * total_quantity,
        )

        self._triggered_auctions.append(auction_id)
        del self._demands[category]
        logger.info("Triggered bulk auction %s for %s (%d units)", auction_id, category, total_quantity)
        return auction_id

    def check_all_categories(self) -> list[str]:
        """Check all categories and trigger auctions where possible.

        Returns:
            List of auction IDs triggered.
        """
        triggered: list[str] = []
        for category in list(self._demands.keys()):
            auction_id = self.trigger_bulk_auction(category)
            if auction_id:
                triggered.append(auction_id)
        return triggered

    # ── Cleanup ─────────────────────────────────────────────────────

    def clear_category(self, category: str) -> int:
        """Clear all demand for a category. Returns count cleared."""
        entries = self._demands.pop(category, [])
        return len(entries)

    @property
    def total_pending(self) -> int:
        """Total pending demand entries across all categories."""
        return sum(len(entries) for entries in self._demands.values())

    @property
    def triggered_auction_count(self) -> int:
        """Number of auctions triggered so far."""
        return len(self._triggered_auctions)
