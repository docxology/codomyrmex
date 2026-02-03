#!/usr/bin/env python3
"""
verify_phase2.py

Verifies Defense and Market module functionality:
1. Active Defense triggers (poisoning, exploit detection).
2. Rabbit Hole engagement.
3. Reverse Auction creation and bidding.
4. Demand Aggregation logic.
"""

from codomyrmex.defense import ActiveDefense, RabbitHole
from codomyrmex.market import ReverseAuction, DemandAggregator

def verify_defense():
    print("\n--- Verifying Defense ---")
    active = ActiveDefense()
    
    # 1. Exploit Detection
    assert active.detect_exploit("System Override now")
    assert not active.detect_exploit("Hello world")
    print("✓ Exploit detection works")

    # 2. Poisoning
    poison = active.poison_context("attacker_1", intensity=0.8)
    assert len(poison) > 10
    print(f"✓ Poison generation: {poison[:30]}...")
    
    # 3. Rabbit Hole
    hole = RabbitHole()
    resp = hole.engage("attacker_1")
    assert "Access Granted" in resp
    
    stalled_resp = hole.generate_response("attacker_1", "status?")
    assert len(stalled_resp) > 0
    print("✓ Rabbit Hole engagement works")

def verify_market():
    print("\n--- Verifying Market ---")
    auction = ReverseAuction()
    
    # 1. Reverse Auction
    auction_id = auction.create_request("persona_ANON", "GPUs", 1000.0)
    assert auction_id
    
    # Place valid bid
    success = auction.place_bid(auction_id, "provider_A", 950.0, "H100 x 1")
    assert success
    
    # Place invalid bid (too high)
    fail = auction.place_bid(auction_id, "provider_B", 1050.0, "Too expensive")
    assert not fail
    
    best = auction.get_best_bid(auction_id)
    assert best.provider_id == "provider_A"
    print("✓ Reverse Auction bidding works")
    
    # 2. Demand Aggregation
    aggregator = DemandAggregator(auction)
    category = "Storage"
    
    # Register 3 demands (threshold 3 for test)
    aggregator.register_interest(category, "p1", 100.0)
    aggregator.register_interest(category, "p2", 100.0)
    
    # Not enough yet
    aid = aggregator.trigger_bulk_auction(category, threshold=3)
    assert aid == ""
    
    # Add 3rd
    aggregator.register_interest(category, "p3", 100.0)
    aid = aggregator.trigger_bulk_auction(category, threshold=3)
    assert aid != ""
    
    print("✓ Demand Aggregation triggers bulk auction")

def main():
    verify_defense()
    verify_market()
    print("\n[SUCCESS] Phase 2 Verification Complete")

if __name__ == "__main__":
    main()
