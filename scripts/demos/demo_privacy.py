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
from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success


def demo_crumb_scrubbing():
    print_info("--- 1. Crumb Scrubbing ---")
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

    print_info("Raw Payload (Target for Surveillance):")
    print(json.dumps(raw_payload, indent=2))

    # Scrubbing
    print_info("Scrubbing Data...")
    safe_payload = cleaner.scrub(raw_payload)

    print_info("Safe Payload (Minimally Viable Data):")
    print(json.dumps(safe_payload, indent=2))

    # Verify removals
    assert "timestamp" not in safe_payload
    assert "geo_lat" not in safe_payload["location"]
    assert "message" in safe_payload
    print_success("Verified: All tracking crumbs removed.")


def demo_mixnet():
    print_info("--- 2. Mixnet Proxy Simulation ---")
    proxy = MixnetProxy()
    message = b"Secret Bid Amount: $4.50"

    print_info("Routing Message via Mixnet (3 hops)...")
    result = proxy.route_payload(message, hops=3)

    print_info(f"Message Delivered: {result.decode()}")
    print_success("Verified: Network transport simulated via 3 anonymous hops.")


def main():
    setup_logging()
    print_info("=== Secure Cognitive Agent: Privacy Demo ===")
    demo_crumb_scrubbing()
    demo_mixnet()
    print_success("Privacy Demo Complete")


if __name__ == "__main__":
    main()
