"""Tests for privacy MCP tools.

Zero-mock tests that exercise the real privacy MCP tool implementations.
"""

from __future__ import annotations


class TestPrivacyScrub:
    """Tests for privacy_scrub MCP tool."""

    def test_removes_blacklisted_keys(self):
        from codomyrmex.privacy.mcp_tools import privacy_scrub

        result = privacy_scrub(
            data={
                "name": "Alice",
                "ip_address": "10.0.0.1",
                "device_id": "abc123",
                "email": "alice@example.com",
            }
        )
        assert result["status"] == "success"
        scrubbed = result["scrubbed"]
        assert "name" in scrubbed
        assert "email" in scrubbed
        assert "ip_address" not in scrubbed
        assert "device_id" not in scrubbed

    def test_handles_nested_dicts(self):
        from codomyrmex.privacy.mcp_tools import privacy_scrub

        result = privacy_scrub(
            data={
                "user": {
                    "name": "Bob",
                    "session_id": "sess-123",
                },
                "trace_id": "t-456",
            }
        )
        assert result["status"] == "success"
        scrubbed = result["scrubbed"]
        assert "trace_id" not in scrubbed
        assert "session_id" not in scrubbed["user"]
        assert scrubbed["user"]["name"] == "Bob"

    def test_none_data_returns_error(self):
        from codomyrmex.privacy.mcp_tools import privacy_scrub

        result = privacy_scrub(data=None)
        assert result["status"] == "error"

    def test_preserves_non_blacklisted_keys(self):
        from codomyrmex.privacy.mcp_tools import privacy_scrub

        result = privacy_scrub(data={"safe_key": "value", "another": 42})
        assert result["status"] == "success"
        assert result["scrubbed"]["safe_key"] == "value"
        assert result["scrubbed"]["another"] == 42


class TestPrivacyListBlacklist:
    """Tests for privacy_list_blacklist MCP tool."""

    def test_returns_success_status(self):
        from codomyrmex.privacy.mcp_tools import privacy_list_blacklist

        result = privacy_list_blacklist()
        assert result["status"] == "success"

    def test_blacklist_contains_known_keys(self):
        from codomyrmex.privacy.mcp_tools import privacy_list_blacklist

        result = privacy_list_blacklist()
        blacklist = result["blacklist"]
        assert "ip_address" in blacklist
        assert "device_id" in blacklist
        assert "session_id" in blacklist

    def test_blacklist_is_sorted(self):
        from codomyrmex.privacy.mcp_tools import privacy_list_blacklist

        result = privacy_list_blacklist()
        blacklist = result["blacklist"]
        assert blacklist == sorted(blacklist)


class TestPrivacyGenerateNoise:
    """Tests for privacy_generate_noise MCP tool."""

    def test_generates_correct_size(self):
        from codomyrmex.privacy.mcp_tools import privacy_generate_noise

        result = privacy_generate_noise(size_bytes=32)
        assert result["status"] == "success"
        assert result["size_bytes"] == 32
        assert len(bytes.fromhex(result["noise_hex"])) == 32

    def test_default_size_64_bytes(self):
        from codomyrmex.privacy.mcp_tools import privacy_generate_noise

        result = privacy_generate_noise()
        assert result["status"] == "success"
        assert result["size_bytes"] == 64
        assert len(bytes.fromhex(result["noise_hex"])) == 64

    def test_zero_size_returns_error(self):
        from codomyrmex.privacy.mcp_tools import privacy_generate_noise

        result = privacy_generate_noise(size_bytes=0)
        assert result["status"] == "error"

    def test_noise_is_random(self):
        from codomyrmex.privacy.mcp_tools import privacy_generate_noise

        r1 = privacy_generate_noise(size_bytes=16)
        r2 = privacy_generate_noise(size_bytes=16)
        # Two random outputs should differ (probability of collision is 2^-128)
        assert r1["noise_hex"] != r2["noise_hex"]
