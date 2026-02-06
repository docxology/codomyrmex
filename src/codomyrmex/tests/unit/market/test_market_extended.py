
import pytest
from codomyrmex.market import ReverseAuction, DemandAggregator

def test_reverse_auction_lifecycle():
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
