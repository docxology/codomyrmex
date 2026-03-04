"""Tests for market MCP tools.

Zero-mock tests that exercise auction creation, demand stats,
and category listing using real ReverseAuction instances.
"""

from __future__ import annotations

from codomyrmex.market.mcp_tools import (
    market_create_auction,
    market_demand_stats,
    market_list_categories,
)


class TestMarketCreateAuction:
    """Tests for market_create_auction."""

    def test_create_auction_success(self):
        """Create an auction and get back a UUID."""
        result = market_create_auction(
            persona_id="agent-42",
            description="GPU compute hours",
            max_price=500.0,
        )
        assert result["status"] == "success"
        assert "auction_id" in result
        assert len(result["auction_id"]) > 0

    def test_create_auction_zero_price(self):
        """Auction with zero max price still succeeds."""
        result = market_create_auction(
            persona_id="agent-0",
            description="Free tier request",
            max_price=0.0,
        )
        assert result["status"] == "success"
        assert "auction_id" in result

    def test_create_multiple_auctions_unique_ids(self):
        """Multiple auctions produce distinct IDs."""
        r1 = market_create_auction("p1", "item A", 100.0)
        r2 = market_create_auction("p2", "item B", 200.0)
        assert r1["auction_id"] != r2["auction_id"]


class TestMarketDemandStats:
    """Tests for market_demand_stats."""

    def test_empty_category(self):
        """No demand returns stats=None with message."""
        result = market_demand_stats(category="nonexistent_category")
        assert result["status"] == "success"
        assert result["stats"] is None
        assert "no demand" in result["message"].lower()

    def test_returns_category_name(self):
        """Response echoes back the requested category."""
        result = market_demand_stats(category="test_widgets")
        assert result["category"] == "test_widgets"


class TestMarketListCategories:
    """Tests for market_list_categories."""

    def test_empty_aggregator(self):
        """Fresh aggregator has no categories."""
        result = market_list_categories()
        assert result["status"] == "success"
        assert result["categories"] == []
        assert result["count"] == 0
