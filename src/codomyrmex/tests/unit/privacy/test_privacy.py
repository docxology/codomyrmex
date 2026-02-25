import hashlib
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
        """Test functionality: init has default blacklist."""
        assert "ip_address" in self.cleaner._blacklist
        assert "cookie_id" in self.cleaner._blacklist
        assert "timestamp" in self.cleaner._blacklist

    def test_scrub_dict_removes_blacklisted(self):
        """Test functionality: scrub dict removes blacklisted."""
        data = {"name": "Alice", "ip_address": "1.2.3.4", "value": 42}
        result = self.cleaner.scrub(data)
        assert "name" in result
        assert "value" in result
        assert "ip_address" not in result

    def test_scrub_preserves_non_blacklisted(self):
        """Test functionality: scrub preserves non blacklisted."""
        data = {"name": "Bob", "role": "admin"}
        result = self.cleaner.scrub(data)
        assert result == data

    def test_scrub_nested_dict(self):
        """Test functionality: scrub nested dict."""
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
        """Test functionality: scrub list."""
        data = [
            {"name": "Alice", "ip_address": "1.2.3.4"},
            {"name": "Bob", "user_agent": "Chrome"},
        ]
        result = self.cleaner.scrub(data)
        assert len(result) == 2
        assert "ip_address" not in result[0]
        assert "user_agent" not in result[1]

    def test_scrub_non_dict_passthrough(self):
        """Test functionality: scrub non dict passthrough."""
        assert self.cleaner.scrub("hello") == "hello"
        assert self.cleaner.scrub(42) == 42
        assert self.cleaner.scrub(None) is None

    def test_scrub_case_insensitive(self):
        """Test functionality: scrub case insensitive."""
        data = {"IP_ADDRESS": "1.2.3.4", "name": "test"}
        result = self.cleaner.scrub(data)
        assert "IP_ADDRESS" not in result
        assert "name" in result

    def test_generate_noise(self):
        """Test functionality: generate noise."""
        noise = self.cleaner.generate_noise(64)
        assert isinstance(noise, bytes)
        assert len(noise) == 64

    def test_generate_noise_custom_size(self):
        """Test functionality: generate noise custom size."""
        noise = self.cleaner.generate_noise(128)
        assert len(noise) == 128

    def test_configure_blacklist_add(self):
        """Test functionality: configure blacklist add."""
        self.cleaner.configure_blacklist(add=["custom_field"])
        assert "custom_field" in self.cleaner._blacklist
        data = {"custom_field": "secret", "name": "test"}
        result = self.cleaner.scrub(data)
        assert "custom_field" not in result

    def test_configure_blacklist_remove(self):
        """Test functionality: configure blacklist remove."""
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
        """Test functionality: packet creation."""
        pkt = Packet(payload=b"hello", route_id="r1", hops_remaining=3)
        assert pkt.payload == b"hello"
        assert pkt.route_id == "r1"
        assert pkt.hops_remaining == 3


@pytest.mark.unit
class TestMixNode:
    """Tests for the MixNode class — uses real time.sleep."""

    def test_mix_node_creation(self):
        """Test functionality: mix node creation."""
        node = MixNode("node_0")
        assert node.node_id == "node_0"

    def test_mix_node_relay_decrements_hops(self):
        """Test functionality: mix node relay decrements hops."""
        node = MixNode("node_0")
        pkt = Packet(payload=b"data", route_id="r1", hops_remaining=3)
        result = node.relay(pkt)
        assert result.hops_remaining == 2
        assert result.payload == b"data"

    def test_mix_node_relay_zero_hops(self):
        """Test functionality: mix node relay zero hops."""
        node = MixNode("node_0")
        pkt = Packet(payload=b"data", route_id="r1", hops_remaining=0)
        result = node.relay(pkt)
        assert result.hops_remaining == 0
        assert result.payload == b"data"


@pytest.mark.unit
class TestMixnetProxy:
    """Tests for the MixnetProxy class — uses real time.sleep."""

    def test_mixnet_init(self):
        """Test functionality: mixnet init."""
        proxy = MixnetProxy()
        assert len(proxy._nodes) == 10

    def test_route_payload(self):
        """Test functionality: route payload."""
        proxy = MixnetProxy()
        payload = b"secret message"
        result = proxy.route_payload(payload, hops=3)
        assert result == payload

    def test_route_payload_single_hop(self):
        """Test functionality: route payload single hop."""
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


# From test_coverage_boost.py
class TestDetectPII:
    """Tests for PII detection."""

    def test_detect_email(self):
        from codomyrmex.privacy.privacy import detect_pii

        matches = detect_pii("Contact alice@example.com for info")
        types = {m.pii_type for m in matches}
        assert "email" in types

    def test_detect_phone(self):
        from codomyrmex.privacy.privacy import detect_pii

        matches = detect_pii("Call 555-123-4567 now")
        types = {m.pii_type for m in matches}
        assert "phone" in types

    def test_detect_ssn(self):
        from codomyrmex.privacy.privacy import detect_pii

        matches = detect_pii("SSN: 123-45-6789")
        types = {m.pii_type for m in matches}
        assert "ssn" in types

    def test_no_pii(self):
        from codomyrmex.privacy.privacy import detect_pii

        matches = detect_pii("No sensitive data here")
        assert len(matches) == 0


# From test_coverage_boost.py
class TestMasking:
    """Tests for data masking functions."""

    def test_mask_hash(self):
        from codomyrmex.privacy.privacy import mask_hash

        result = mask_hash("secret")
        expected = hashlib.sha256(b"secret").hexdigest()
        assert result == expected

    def test_mask_redact(self):
        from codomyrmex.privacy.privacy import mask_redact

        assert mask_redact("sensitive") == "***"
        assert mask_redact("sensitive", "REDACTED") == "REDACTED"

    def test_mask_partial(self):
        from codomyrmex.privacy.privacy import mask_partial

        result = mask_partial("1234567890", 4)
        assert result.endswith("7890")
        assert result.startswith("*")

    def test_mask_email(self):
        from codomyrmex.privacy.privacy import mask_email

        result = mask_email("alice@example.com")
        assert "@example.com" in result
        assert result.startswith("a")


# From test_coverage_boost.py
class TestDifferentialPrivacy:
    """Tests for differential privacy functions."""

    def test_laplace_noise_returns_float(self):
        from codomyrmex.privacy.privacy import laplace_noise

        noise = laplace_noise(epsilon=1.0)
        assert isinstance(noise, float)

    def test_add_laplace_noise(self):
        from codomyrmex.privacy.privacy import add_laplace_noise

        noised = add_laplace_noise(100.0, epsilon=1.0)
        assert isinstance(noised, float)
        # With epsilon=1.0, noise should be moderate
        assert 50 < noised < 150  # Very loose bounds

    def test_dp_mean(self):
        from codomyrmex.privacy.privacy import dp_mean

        values = [10.0, 20.0, 30.0, 40.0, 50.0]
        result = dp_mean(values, epsilon=10.0, lower=0.0, upper=100.0)
        # High epsilon = low noise, should be close to true mean (30)
        assert 10 < result < 50

    def test_dp_count(self):
        from codomyrmex.privacy.privacy import dp_count

        result = dp_count(100, epsilon=10.0)
        assert isinstance(result, float)
        assert 90 < result < 110  # High epsilon = low noise


# From test_coverage_boost.py
class TestPrivacyProcessor:
    """Tests for the Privacy processor class."""

    def test_process_with_rules(self):
        from codomyrmex.privacy.privacy import Privacy, PrivacyRule

        p = Privacy()
        p.add_rule(PrivacyRule("email", "email"))
        p.add_rule(PrivacyRule("ssn", "redact"))

        data = {"email": "alice@example.com", "ssn": "123-45-6789", "name": "Alice"}
        result = p.process(data)
        assert "@example.com" in result["email"]  # Domain preserved
        assert result["ssn"] == "***"  # Redacted
        assert result["name"] == "Alice"  # Untouched

    def test_hash_strategy(self):
        from codomyrmex.privacy.privacy import Privacy, PrivacyRule

        p = Privacy()
        p.add_rule(PrivacyRule("secret", "hash"))
        result = p.process({"secret": "my-password"})
        assert result["secret"] == hashlib.sha256(b"my-password").hexdigest()

    def test_partial_strategy(self):
        from codomyrmex.privacy.privacy import Privacy, PrivacyRule

        p = Privacy()
        p.add_rule(PrivacyRule("card", "partial", {"visible_chars": 4}))
        result = p.process({"card": "4111111111111111"})
        assert result["card"].endswith("1111")

    def test_scan_pii(self):
        from codomyrmex.privacy.privacy import Privacy

        p = Privacy()
        matches = p.scan_pii({"bio": "Email me at test@test.com", "age": "25"})
        assert len(matches) > 0

    def test_create_privacy_factory(self):
        from codomyrmex.privacy.privacy import create_privacy

        p = create_privacy()
        assert p is not None
