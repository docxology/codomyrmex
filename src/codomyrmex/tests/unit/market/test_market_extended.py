
from codomyrmex.market import DemandAggregator, ReverseAuction


def test_reverse_auction_lifecycle():
    """Test functionality: reverse auction lifecycle."""
    auction = ReverseAuction()

    # Create
    aid = auction.create_request("requester_1", "Item", 100.0)

    # Bids
    assert auction.place_bid(aid, "p1", 90.0, "desc")
    assert auction.place_bid(aid, "p2", 80.0, "desc") # Better
    assert not auction.place_bid(aid, "p3", 110.0, "desc") # Too high

    # Best bid
    best = auction.get_best_bid(aid)
    assert best.provider_id == "p2"
    assert best.amount == 80.0

    # Close
    assert auction.close_auction(aid, "requester_1")
    assert not auction.close_auction(aid, "requester_2") # Wrong owner

def test_demand_aggregation():
    """Test functionality: demand aggregation."""
    auction = ReverseAuction()
    agg = DemandAggregator(auction)
    cat = "Compute"

    # Threshold 2
    agg.register_interest(cat, "u1", 100)
    assert agg.trigger_bulk_auction(cat, threshold=2) == ""

    agg.register_interest(cat, "u2", 100)
    aid = agg.trigger_bulk_auction(cat, threshold=2)
    assert aid != ""

    # Check auction created
    assert aid in auction._auctions


# From test_coverage_boost_r2.py
class TestMarket:
    """Tests for Market multi-agent marketplace."""

    def test_register_and_post(self):
        from codomyrmex.market.market import Market

        m = Market()
        m.register_agent("agent-1", ["python", "testing"])
        m.post_task("task-1", ["python"], priority=5)
        stats = m.get_stats()
        assert stats["total_agents"] == 1
        assert stats["total_tasks"] == 1
        assert stats["open_tasks"] == 1

    def test_allocation(self):
        from codomyrmex.market.market import Market

        m = Market()
        m.register_agent("a1", ["python", "testing"], max_concurrent=2)
        m.register_agent("a2", ["java"], max_concurrent=1)
        m.post_task("t1", ["python"], priority=10)
        m.post_task("t2", ["java"], priority=5)
        result = m.process()
        assert result["allocated"] == 2
        assert result["unallocated"] == 0

    def test_capacity_limit(self):
        from codomyrmex.market.market import Market

        m = Market()
        m.register_agent("a1", ["python"], max_concurrent=1)
        m.post_task("t1", ["python"], priority=10)
        m.post_task("t2", ["python"], priority=5)
        result = m.process()
        assert result["allocated"] == 1
        assert result["unallocated"] == 1

    def test_complete_task(self):
        from codomyrmex.market.market import Market

        m = Market()
        m.register_agent("a1", ["python"], max_concurrent=1)
        m.post_task("t1", ["python"])
        m.process()
        assert m.complete_task("t1")
        stats = m.get_stats()
        assert stats["completed_tasks"] == 1

    def test_complete_nonexistent(self):
        from codomyrmex.market.market import Market

        m = Market()
        assert not m.complete_task("nope")

    def test_no_capability_match(self):
        from codomyrmex.market.market import Market

        m = Market()
        m.register_agent("a1", ["rust"])
        m.post_task("t1", ["python"])
        result = m.process()
        assert result["allocated"] == 0

    def test_create_market_factory(self):
        from codomyrmex.market.market import create_market

        m = create_market({"region": "us"})
        assert m.config == {"region": "us"}
