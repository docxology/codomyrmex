#!/usr/bin/env python3
"""
scripts/demo_market.py

Demonstrates:
1. Reverse Auctions: Identity-protected demand posting.
2. Demand Aggregation: Bulk buying power.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from codomyrmex.market import ReverseAuction, DemandAggregator
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger("demo_market")

def demo_reverse_auction():
    print("\n--- 1. Reverse Auction ---")
    market = ReverseAuction()
    persona_id = "anon_buyer_01"

    # 1. Create Request
    print(f"User {persona_id} posting demand...")
    auction_id = market.create_request(
        persona_id=persona_id, 
        description="High-Performance GPU Compute (1hr)", 
        max_price=5.00
    )
    print(f"Auction Open: {auction_id}")

    # 2. Providers Bid
    print("\nProviders submitting bids...")
    market.place_bid(auction_id, "provider_A", 4.50, "NVIDIA A100")
    market.place_bid(auction_id, "provider_B", 3.00, "NVIDIA H100 (Spot)") # Winner

    # 3. Selection
    best = market.get_best_bid(auction_id)
    print(f"Best Bid Selected: ${best.amount} from {best.provider_id} ({best.details})")
    
    # 4. Close
    if market.close_auction(auction_id, persona_id):
        print("Auction Closed successfully.")

def demo_aggregation():
    print("\n--- 2. Demand Aggregation ---")
    market = ReverseAuction()
    agg = DemandAggregator(market)
    category = "Cloud Storage 1TB"

    print("Aggregating demand for 'Cloud Storage 1TB'...")
    
    # 3 Users register interest
    agg.register_interest(category, "user_1", 10.0)
    print("User 1 joined pool.")
    
    agg.register_interest(category, "user_2", 10.0)
    print("User 2 joined pool.")

    # Threshold trigger
    print("User 3 joining pool (Trigger Threshold=3)...")
    auction_id = agg.trigger_bulk_auction(category, threshold=3)
    
    if auction_id:
        print(f"✅ BULK AUCTION TRIGGERED: {auction_id}")
        print("Vendors now bid on supplying 3 users at once.")
    else:
        print("Threshold not met yet.")

    # Simulate 3rd user to actually trigger if logic allows (mock aggregator is simple)
    # Re-triggering manually with threshold logic visible in output
    agg.register_interest(category, "user_3", 10.0)
    auction_id = agg.trigger_bulk_auction(category, threshold=3)
    if auction_id:
         print(f"✅ BULK AUCTION CONFIGIRMED: {auction_id}")

def main():
    print("=== Secure Cognitive Agent: Market Demo ===")
    demo_reverse_auction()
    demo_aggregation()
    print("\n[SUCCESS] Market Demo Complete")

if __name__ == "__main__":
    main()
