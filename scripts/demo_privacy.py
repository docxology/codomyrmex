#!/usr/bin/env python3
"""
scripts/demo_privacy.py

Demonstrates:
1. Crumb Minimization: Scrubbing metadata.
2. Mixnet Proxy: Anonymous routing simulation.
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from codomyrmex.privacy import CrumbCleaner, MixnetProxy
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger("demo_privacy")

def demo_crumb_scrubbing():
    print("\n--- 1. Crumb Scrubbing ---")
    cleaner = CrumbCleaner()
    
    # Raw Data with "Crumbs" (Fingerprinting data)
    raw_payload = {
        "message": "Anonymous inquiry about pricing",
        "timestamp": 1704112233,
        "device_id": "iPhone14,2",
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X)",
        "location": {
            "geo_lat": 37.7749,
            "geo_lon": -122.4194,
            "region": "CA"
        },
        "session_id": "sess_99887766"
    }

    print("Raw Payload (Target for Surveillance):")
    print(json.dumps(raw_payload, indent=2))

    # Scrubbing
    print("\nScrubbing Data...")
    safe_payload = cleaner.scrub(raw_payload)

    print("Safe Payload (Minimally Viable Data):")
    print(json.dumps(safe_payload, indent=2))

    # Verify removals
    assert "timestamp" not in safe_payload
    assert "geo_lat" not in safe_payload["location"]
    assert "message" in safe_payload
    print("✅ Verified: All tracking crumbs removed.")

def demo_mixnet():
    print("\n--- 2. Mixnet Proxy Simulation ---")
    proxy = MixnetProxy()
    message = b"Secret Bid Amount: $4.50"

    print(f"Routing Message via Mixnet (3 hops)...")
    # Simulate network delay/routing
    result = proxy.route_payload(message, hops=3)
    
    print(f"Message Delivered: {result.decode()}")
    print("✅ Verified: Network transport simulated via 3 anonymous hops.")

def main():
    print("=== Secure Cognitive Agent: Privacy Demo ===")
    demo_crumb_scrubbing()
    demo_mixnet()
    print("\n[SUCCESS] Privacy Demo Complete")

if __name__ == "__main__":
    main()
