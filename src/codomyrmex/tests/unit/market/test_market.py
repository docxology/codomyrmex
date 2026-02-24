"""Tests for the market module (auction + aggregator)."""

import pytest

from codomyrmex.market.aggregator import DemandAggregator
from codomyrmex.market.auction import AuctionRequest, Bid, ReverseAuction


@pytest.mark.unit
class TestBid:
    """Tests for the Bid dataclass."""

    def test_bid_creation(self):
        """Test functionality: bid creation."""
        bid = Bid(provider_id="p1", amount=10.0, details="offer A")
        assert bid.provider_id == "p1"
        assert bid.amount == 10.0
        assert bid.details == "offer A"
        assert bid.timestamp is not None

    def test_bid_fields_are_set(self):
        """Test functionality: bid fields are set."""
        bid = Bid(provider_id="p2", amount=5.5, details="cheap")
        assert isinstance(bid.amount, float)
        assert isinstance(bid.provider_id, str)


@pytest.mark.unit
class TestAuctionRequest:
    """Tests for the AuctionRequest dataclass."""

    def test_auction_request_creation(self):
        """Test functionality: auction request creation."""
        req = AuctionRequest(
            id="a1",
            requester_persona_id="persona1",
            item_description="GPU hours",
            max_price=100.0,
        )
        assert req.id == "a1"
        assert req.requester_persona_id == "persona1"
        assert req.item_description == "GPU hours"
        assert req.max_price == 100.0

    def test_auction_request_defaults(self):
        """Test functionality: auction request defaults."""
        req = AuctionRequest(
            id="a2",
            requester_persona_id="p2",
            item_description="Storage",
            max_price=50.0,
        )
        assert req.bids == []
        assert req.status == "OPEN"


@pytest.mark.unit
class TestReverseAuction:
    """Tests for the ReverseAuction class."""

    def setup_method(self):
        self.auction = ReverseAuction()

    def test_create_request(self):
        """Test functionality: create request."""
        auction_id = self.auction.create_request("persona1", "GPU hours", 100.0)
        assert isinstance(auction_id, str)
        assert len(auction_id) > 0

    def test_place_bid_success(self):
        """Test functionality: place bid success."""
        auction_id = self.auction.create_request("persona1", "GPU hours", 100.0)
        result = self.auction.place_bid(auction_id, "provider1", 80.0, "good deal")
        assert result is True

    def test_place_bid_nonexistent_auction(self):
        """Test functionality: place bid nonexistent auction."""
        result = self.auction.place_bid("fake_id", "provider1", 80.0, "deal")
        assert result is False

    def test_bid_exceeds_max_price(self):
        """Test functionality: bid exceeds max price."""
        auction_id = self.auction.create_request("persona1", "GPU hours", 100.0)
        result = self.auction.place_bid(auction_id, "provider1", 150.0, "expensive")
        assert result is False

    def test_get_best_bid(self):
        """Test functionality: get best bid."""
        auction_id = self.auction.create_request("persona1", "GPU hours", 100.0)
        self.auction.place_bid(auction_id, "p1", 90.0, "ok")
        self.auction.place_bid(auction_id, "p2", 70.0, "better")
        self.auction.place_bid(auction_id, "p3", 80.0, "mid")
        best = self.auction.get_best_bid(auction_id)
        assert best is not None
        assert best.amount == 70.0
        assert best.provider_id == "p2"

    def test_get_best_bid_no_bids(self):
        """Test functionality: get best bid no bids."""
        auction_id = self.auction.create_request("persona1", "GPU hours", 100.0)
        assert self.auction.get_best_bid(auction_id) is None

    def test_get_best_bid_nonexistent(self):
        """Test functionality: get best bid nonexistent."""
        assert self.auction.get_best_bid("fake") is None

    def test_close_auction(self):
        """Test functionality: close auction."""
        auction_id = self.auction.create_request("persona1", "GPU hours", 100.0)
        result = self.auction.close_auction(auction_id, "persona1")
        assert result is True

    def test_close_auction_wrong_owner(self):
        """Test functionality: close auction wrong owner."""
        auction_id = self.auction.create_request("persona1", "GPU hours", 100.0)
        result = self.auction.close_auction(auction_id, "persona2")
        assert result is False

    def test_cancel_auction(self):
        """Test functionality: cancel auction."""
        auction_id = self.auction.create_request("persona1", "GPU hours", 100.0)
        result = self.auction.cancel_auction(auction_id, "persona1")
        assert result is True

    def test_cancel_closed_auction_fails(self):
        """Test functionality: cancel closed auction fails."""
        auction_id = self.auction.create_request("persona1", "GPU hours", 100.0)
        self.auction.close_auction(auction_id, "persona1")
        result = self.auction.cancel_auction(auction_id, "persona1")
        assert result is False

    def test_bid_on_closed_auction_fails(self):
        """Test functionality: bid on closed auction fails."""
        auction_id = self.auction.create_request("persona1", "GPU hours", 100.0)
        self.auction.close_auction(auction_id, "persona1")
        result = self.auction.place_bid(auction_id, "p1", 50.0, "late bid")
        assert result is False

    def test_get_history(self):
        """Test functionality: get history."""
        self.auction.create_request("persona1", "GPU hours", 100.0)
        self.auction.create_request("persona1", "Storage", 50.0)
        self.auction.create_request("persona2", "Bandwidth", 30.0)
        history = self.auction.get_history("persona1")
        assert len(history) == 2


@pytest.mark.unit
class TestDemandAggregator:
    """Tests for the DemandAggregator class."""

    def setup_method(self):
        self.auction = ReverseAuction()
        self.aggregator = DemandAggregator(self.auction)

    def test_aggregator_init(self):
        """Test functionality: aggregator init."""
        assert self.aggregator.auction_system is self.auction
        assert self.aggregator._pending_demands == {}

    def test_register_interest(self):
        """Test functionality: register interest."""
        self.aggregator.register_interest("GPU", "p1", 100.0)
        assert "GPU" in self.aggregator._pending_demands
        assert len(self.aggregator._pending_demands["GPU"]) == 1

    def test_threshold_not_met(self):
        """Test functionality: threshold not met."""
        for i in range(3):
            self.aggregator.register_interest("GPU", f"p{i}", 100.0)
        result = self.aggregator.trigger_bulk_auction("GPU", threshold=5)
        assert result == ""

    def test_threshold_trigger(self):
        """Test functionality: threshold trigger."""
        for i in range(5):
            self.aggregator.register_interest("GPU", f"p{i}", 100.0)
        auction_id = self.aggregator.trigger_bulk_auction("GPU", threshold=5)
        assert isinstance(auction_id, str)
        assert len(auction_id) > 0
        # Pending should be cleared after trigger
        assert "GPU" not in self.aggregator._pending_demands

    def test_bulk_discount_applied(self):
        """Test functionality: bulk discount applied."""
        for i in range(5):
            self.aggregator.register_interest("GPU", f"p{i}", 100.0)
        auction_id = self.aggregator.trigger_bulk_auction("GPU", threshold=5)
        # The auction max_price should reflect 10% bulk discount: avg(100)*0.9*5 = 450
        best = self.auction.get_best_bid(auction_id)
        # No bids yet, but verify auction was created
        assert best is None
        history = self.auction.get_history("p0")
        assert len(history) == 1
        assert history[0].max_price == 450.0

    def test_trigger_nonexistent_category(self):
        """Test functionality: trigger nonexistent category."""
        result = self.aggregator.trigger_bulk_auction("NonExistent")
        assert result == ""
