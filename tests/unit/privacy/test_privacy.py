
import pytest
from codomyrmex.privacy import CrumbCleaner, MixnetProxy

def test_crumb_cleaning():
    cleaner = CrumbCleaner()
    data = {
        "valid": "data",
        "timestamp": 12345,
        "meta": {
            "device_id": "xyz",
            "nested": "keep"
        }
    }
    
    clean = cleaner.scrub(data)
    assert "valid" in clean
    assert "timestamp" not in clean
    assert "nested" in clean["meta"]
    assert "device_id" not in clean["meta"]

def test_mixnet_proxy():
    proxy = MixnetProxy()
    payload = b"test"
    
    # Should return same payload simulation
    assert proxy.route_payload(payload, hops=1) == payload
    assert proxy.route_payload(payload, hops=5) == payload
