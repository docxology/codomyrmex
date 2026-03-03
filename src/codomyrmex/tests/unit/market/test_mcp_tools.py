"""Strictly zero-mock tests for market MCP tools."""

from collections.abc import Generator

import pytest

from codomyrmex.market import mcp_tools
from codomyrmex.market.aggregator import DemandAggregator
from codomyrmex.market.auction import ReverseAuction
from codomyrmex.market.market import Market


@pytest.fixture(autouse=True)
def reset_global_state() -> Generator[None, None, None]:
    """Reset the global state in mcp_tools before and after each test."""
    old_auction = mcp_tools._auction_system
    old_aggregator = mcp_tools._demand_aggregator
    old_market = mcp_tools._market_system

    mcp_tools._auction_system = ReverseAuction()
    mcp_tools._demand_aggregator = DemandAggregator(mcp_tools._auction_system)
    mcp_tools._market_system = Market()

    yield

    mcp_tools._auction_system = old_auction
    mcp_tools._demand_aggregator = old_aggregator
    mcp_tools._market_system = old_market

@pytest.mark.unit
class TestMarketMCPTools:
    """Zero-mock tests for market MCP tools."""

    def test_market_create_auction(self) -> None:
        """Test functionality: create auction tool."""
        result = mcp_tools.market_create_auction("persona_1", "GPU compute", 10.0)
        assert result["status"] == "success"
        assert "auction_id" in result

        # Verify the global state was updated
        auction_id = result["auction_id"]
        assert auction_id in mcp_tools._auction_system._auctions

        auction = mcp_tools._auction_system._auctions[auction_id]
        assert auction.requester_persona_id == "persona_1"
        assert auction.item_description == "GPU compute"
        assert auction.max_price == 10.0

    def test_market_place_bid_success(self) -> None:
        """Test functionality: place bid tool successfully."""
        # Create an auction first
        auction_result = mcp_tools.market_create_auction("persona_1", "GPU compute", 10.0)
        auction_id = auction_result["auction_id"]

        # Place a valid bid
        result = mcp_tools.market_place_bid(auction_id, "provider_1", 8.0, "High speed")
        assert result["status"] == "success"
        assert "successfully" in result["message"].lower()

    def test_market_place_bid_failure(self) -> None:
        """Test functionality: place bid tool failure (exceeds max price)."""
        auction_result = mcp_tools.market_create_auction("persona_1", "GPU compute", 10.0)
        auction_id = auction_result["auction_id"]

        # Place an invalid bid (too expensive)
        result = mcp_tools.market_place_bid(auction_id, "provider_1", 12.0, "High speed")
        assert result["status"] == "error"
        assert "failed" in result["message"].lower()

    def test_market_get_best_bid(self) -> None:
        """Test functionality: get best bid tool."""
        auction_result = mcp_tools.market_create_auction("persona_1", "GPU compute", 10.0)
        auction_id = auction_result["auction_id"]

        # Place a couple of bids
        mcp_tools.market_place_bid(auction_id, "provider_1", 8.0, "High speed")
        mcp_tools.market_place_bid(auction_id, "provider_2", 7.0, "Standard")
        mcp_tools.market_place_bid(auction_id, "provider_3", 9.0, "Premium")

        # Get the best bid
        result = mcp_tools.market_get_best_bid(auction_id)
        assert result["status"] == "success"
        assert "bid" in result
        assert result["bid"]["provider_id"] == "provider_2"
        assert result["bid"]["amount"] == 7.0

    def test_market_get_best_bid_no_bids(self) -> None:
        """Test functionality: get best bid when no bids exist."""
        auction_result = mcp_tools.market_create_auction("persona_1", "GPU compute", 10.0)
        auction_id = auction_result["auction_id"]

        result = mcp_tools.market_get_best_bid(auction_id)
        assert result["status"] == "success"
        assert "no bids" in result["message"].lower()

    def test_market_register_demand(self) -> None:
        """Test functionality: register demand tool."""
        result = mcp_tools.market_register_demand("Storage", "persona_1", 5.0, 100)
        assert result["status"] == "success"
        assert "entry" in result
        assert result["entry"]["category"] == "Storage"
        assert result["entry"]["quantity"] == 100
        assert result["entry"]["max_price"] == 5.0

    def test_market_trigger_bulk_auction(self) -> None:
        """Test functionality: trigger bulk auction tool."""
        # Register some demand
        mcp_tools.market_register_demand("Storage", "persona_1", 5.0, 100)
        mcp_tools.market_register_demand("Storage", "persona_2", 4.0, 50)
        mcp_tools.market_register_demand("Storage", "persona_3", 6.0, 50)

        # Trigger with threshold = 3
        result = mcp_tools.market_trigger_bulk_auction("Storage", threshold=3)
        assert result["status"] == "success"
        assert "auction_id" in result

        # Check that an auction was actually created in the system
        assert result["auction_id"] in mcp_tools._auction_system._auctions

    def test_market_trigger_bulk_auction_not_met(self) -> None:
        """Test functionality: trigger bulk auction tool when threshold not met."""
        mcp_tools.market_register_demand("Storage", "persona_1", 5.0, 100)

        # Trigger with threshold = 3 (we only have 1)
        result = mcp_tools.market_trigger_bulk_auction("Storage", threshold=3)
        assert result["status"] == "success"
        assert "threshold not met" in result["message"].lower()

    def test_market_get_stats(self) -> None:
        """Test functionality: get market stats tool."""
        mcp_tools._market_system.register_agent("agent_1", ["python"])
        mcp_tools._market_system.post_task("task_1", ["python"], priority=1)

        result = mcp_tools.market_get_stats()
        assert result["status"] == "success"
        assert "stats" in result
        assert result["stats"]["total_agents"] == 1
        assert result["stats"]["total_tasks"] == 1
