#!/usr/bin/env python3
"""
verify_phase3.py

Verifies Privacy module functionality:
1. Crumb scrubbing (metadata removal).
2. Mixnet routing simulation.
"""

import sys

from codomyrmex.privacy import CrumbCleaner, MixnetProxy
from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success


def verify_privacy():
    print_info("--- Verifying Privacy ---")
    cleaner = CrumbCleaner()

    # 1. Crumb Scrubbing
    data = {
        "user_id": "u123",
        "timestamp": "2023-01-01",
        "location": {"lat": 10, "lon": 20},
        "payload": "secret message",
        "meta": {
             "device_id": "iphone",
             "valid": True
        }
    }

    clean = cleaner.scrub(data)

    assert "timestamp" not in clean
    assert "location" in clean
    assert "payload" in clean
    assert "user_id" in clean
    assert "device_id" not in clean["meta"]
    print_success("Crumb cleaner removes blacklisted metadata")

    # 2. Mixnet Proxy
    proxy = MixnetProxy()
    msg = b"Hello Anonymity"

    # Route with 3 hops
    received = proxy.route_payload(msg, hops=3)
    assert received == msg
    print_success("Mixnet routing successful (simulation)")


def main() -> int:
    setup_logging()
    verify_privacy()
    print_success("Phase 3 Verification Complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
