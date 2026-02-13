"""Zero-Mock tests for the privacy module (crumbs + mixnet).

Uses real time.sleep with minimal delays for mixnet relay tests.
"""

import pytest

from codomyrmex.privacy.crumbs import CrumbCleaner
from codomyrmex.privacy.mixnet import MixnetProxy, MixNode, Packet


@pytest.mark.unit
class TestCrumbCleaner:
    """Tests for the CrumbCleaner class."""

    def setup_method(self):
        self.cleaner = CrumbCleaner()

    def test_init_has_default_blacklist(self):
        assert "ip_address" in self.cleaner._blacklist
        assert "cookie_id" in self.cleaner._blacklist
        assert "timestamp" in self.cleaner._blacklist

    def test_scrub_dict_removes_blacklisted(self):
        data = {"name": "Alice", "ip_address": "1.2.3.4", "value": 42}
        result = self.cleaner.scrub(data)
        assert "name" in result
        assert "value" in result
        assert "ip_address" not in result

    def test_scrub_preserves_non_blacklisted(self):
        data = {"name": "Bob", "role": "admin"}
        result = self.cleaner.scrub(data)
        assert result == data

    def test_scrub_nested_dict(self):
        data = {
            "user": {
                "name": "Alice",
                "device_id": "abc123",
                "prefs": {"theme": "dark", "session_id": "xyz"},
            }
        }
        result = self.cleaner.scrub(data)
        assert "name" in result["user"]
        assert "device_id" not in result["user"]
        assert "theme" in result["user"]["prefs"]
        assert "session_id" not in result["user"]["prefs"]

    def test_scrub_list(self):
        data = [
            {"name": "Alice", "ip_address": "1.2.3.4"},
            {"name": "Bob", "user_agent": "Chrome"},
        ]
        result = self.cleaner.scrub(data)
        assert len(result) == 2
        assert "ip_address" not in result[0]
        assert "user_agent" not in result[1]

    def test_scrub_non_dict_passthrough(self):
        assert self.cleaner.scrub("hello") == "hello"
        assert self.cleaner.scrub(42) == 42
        assert self.cleaner.scrub(None) is None

    def test_scrub_case_insensitive(self):
        data = {"IP_ADDRESS": "1.2.3.4", "name": "test"}
        result = self.cleaner.scrub(data)
        assert "IP_ADDRESS" not in result
        assert "name" in result

    def test_generate_noise(self):
        noise = self.cleaner.generate_noise(64)
        assert isinstance(noise, bytes)
        assert len(noise) == 64

    def test_generate_noise_custom_size(self):
        noise = self.cleaner.generate_noise(128)
        assert len(noise) == 128

    def test_configure_blacklist_add(self):
        self.cleaner.configure_blacklist(add=["custom_field"])
        assert "custom_field" in self.cleaner._blacklist
        data = {"custom_field": "secret", "name": "test"}
        result = self.cleaner.scrub(data)
        assert "custom_field" not in result

    def test_configure_blacklist_remove(self):
        assert "timestamp" in self.cleaner._blacklist
        self.cleaner.configure_blacklist(remove=["timestamp"])
        assert "timestamp" not in self.cleaner._blacklist
        data = {"timestamp": "2024-01-01", "name": "test"}
        result = self.cleaner.scrub(data)
        assert "timestamp" in result


@pytest.mark.unit
class TestPacket:
    """Tests for the Packet dataclass."""

    def test_packet_creation(self):
        pkt = Packet(payload=b"hello", route_id="r1", hops_remaining=3)
        assert pkt.payload == b"hello"
        assert pkt.route_id == "r1"
        assert pkt.hops_remaining == 3


@pytest.mark.unit
class TestMixNode:
    """Tests for the MixNode class — uses real time.sleep."""

    def test_mix_node_creation(self):
        node = MixNode("node_0")
        assert node.node_id == "node_0"

    def test_mix_node_relay_decrements_hops(self):
        node = MixNode("node_0")
        pkt = Packet(payload=b"data", route_id="r1", hops_remaining=3)
        result = node.relay(pkt)
        assert result.hops_remaining == 2
        assert result.payload == b"data"

    def test_mix_node_relay_zero_hops(self):
        node = MixNode("node_0")
        pkt = Packet(payload=b"data", route_id="r1", hops_remaining=0)
        result = node.relay(pkt)
        assert result.hops_remaining == 0
        assert result.payload == b"data"


@pytest.mark.unit
class TestMixnetProxy:
    """Tests for the MixnetProxy class — uses real time.sleep."""

    def test_mixnet_init(self):
        proxy = MixnetProxy()
        assert len(proxy._nodes) == 10

    def test_route_payload(self):
        proxy = MixnetProxy()
        payload = b"secret message"
        result = proxy.route_payload(payload, hops=3)
        assert result == payload

    def test_route_payload_single_hop(self):
        proxy = MixnetProxy()
        payload = b"data"
        result = proxy.route_payload(payload, hops=1)
        assert result == payload


@pytest.mark.unit
def test_crumb_cleaning_nested():
    """Test nested dictionary scrubbing."""
    cleaner = CrumbCleaner()
    data = {
        "valid": "data",
        "timestamp": 12345,
        "meta": {"device_id": "xyz", "nested": "keep"},
    }

    clean = cleaner.scrub(data)
    assert "valid" in clean
    assert "timestamp" not in clean
    assert "nested" in clean["meta"]
    assert "device_id" not in clean["meta"]


@pytest.mark.unit
def test_mixnet_proxy_multiple_hops():
    """Test mixnet proxy with configurable hops — uses real sleep."""
    proxy = MixnetProxy()
    payload = b"test"
    assert proxy.route_payload(payload, hops=1) == payload
    assert proxy.route_payload(payload, hops=5) == payload
