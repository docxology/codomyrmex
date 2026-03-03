import pytest

from codomyrmex.privacy.mcp_tools import (
    privacy_process,
    privacy_route_payload,
    privacy_scan,
    privacy_scrub_crumbs,
)


@pytest.mark.unit
class TestPrivacyMCPTools:
    """Strictly zero-mock unit tests for privacy MCP tools."""

    # -- privacy_scan tests --

    def test_privacy_scan_success(self):
        """Test scanning valid data for PII."""
        data = {
            "email": "test@example.com",
            "safe_field": "Hello World",
            "phone": "Call 555-123-4567",
        }
        matches = privacy_scan(data)
        assert isinstance(matches, list)

        pii_types = {match["pii_type"] for match in matches}
        assert "email" in pii_types
        assert "phone" in pii_types

        # Verify the structure of the returned match dict
        email_match = next(m for m in matches if m["pii_type"] == "email")
        assert email_match["field"] == "email"
        assert email_match["value"] == "test@example.com"
        assert "start" in email_match
        assert "end" in email_match

    def test_privacy_scan_no_pii(self):
        """Test scanning data with no PII."""
        data = {"message": "Hello world, everything is fine here."}
        matches = privacy_scan(data)
        assert isinstance(matches, list)
        assert len(matches) == 0

    def test_privacy_scan_invalid_input(self):
        """Test scanning invalid input triggers TypeError."""
        with pytest.raises(TypeError, match="must be a dictionary"):
            privacy_scan("not a dict")

    # -- privacy_scrub_crumbs tests --

    def test_privacy_scrub_crumbs_success(self):
        """Test scrubbing data successfully."""
        data = {
            "name": "Alice",
            "ip_address": "192.168.1.1",
            "timestamp": "2024-01-01T00:00:00Z",
            "nested": {"cookie_id": "abc", "value": 42},
        }
        result = privacy_scrub_crumbs(data)

        assert "name" in result
        assert "ip_address" not in result
        assert "timestamp" not in result
        assert "cookie_id" not in result["nested"]
        assert result["nested"]["value"] == 42

    def test_privacy_scrub_crumbs_invalid_input(self):
        """Test scrubbing None triggers ValueError."""
        with pytest.raises(ValueError, match="cannot be None"):
            privacy_scrub_crumbs(None)

    # -- privacy_route_payload tests --

    def test_privacy_route_payload_success(self):
        """Test routing a string payload."""
        payload = "secret data"
        result = privacy_route_payload(payload, hops=2)

        assert isinstance(result, str)
        assert result == payload  # MixnetProxy returns the decoded original payload

    def test_privacy_route_payload_invalid_payload_type(self):
        """Test routing an invalid payload type triggers TypeError."""
        with pytest.raises(TypeError, match="must be a string"):
            privacy_route_payload({"not": "a string"})

    def test_privacy_route_payload_invalid_hops_type(self):
        """Test routing with invalid hops type triggers TypeError."""
        with pytest.raises(TypeError, match="must be an integer"):
            privacy_route_payload("payload", hops="3")

    def test_privacy_route_payload_invalid_hops_value(self):
        """Test routing with invalid hops value triggers ValueError."""
        with pytest.raises(ValueError, match="must be at least 1"):
            privacy_route_payload("payload", hops=0)

    # -- privacy_process tests --

    def test_privacy_process_success(self):
        """Test processing data with specific rules."""
        data = {
            "email": "alice@example.com",
            "ssn": "123-45-6789",
            "public_id": "user123",
        }
        rules = [
            {"field": "email", "strategy": "email"},
            {"field": "ssn", "strategy": "redact"},
        ]

        result = privacy_process(data, rules)

        assert "@example.com" in result["email"]
        assert not result["email"].startswith("alice")
        assert result["ssn"] == "***"
        assert result["public_id"] == "user123"

    def test_privacy_process_invalid_data_type(self):
        """Test processing invalid data type triggers TypeError."""
        with pytest.raises(TypeError, match="must be a dictionary"):
            privacy_process("not a dict", [{"field": "test", "strategy": "redact"}])

    def test_privacy_process_invalid_rules_type(self):
        """Test processing invalid rules type triggers TypeError."""
        with pytest.raises(TypeError, match="must be a list of dictionaries"):
            privacy_process({"key": "value"}, {"not": "a list"})

    def test_privacy_process_invalid_rule_item_type(self):
        """Test processing invalid rule item type triggers TypeError."""
        with pytest.raises(TypeError, match="Each rule must be a dictionary"):
            privacy_process({"key": "value"}, ["not a dict"])

    def test_privacy_process_missing_rule_fields(self):
        """Test processing rule missing required fields triggers ValueError."""
        with pytest.raises(ValueError, match="must have 'field' and 'strategy' defined"):
            privacy_process({"key": "value"}, [{"field": "only_field"}])

        with pytest.raises(ValueError, match="must have 'field' and 'strategy' defined"):
            privacy_process({"key": "value"}, [{"strategy": "only_strategy"}])
