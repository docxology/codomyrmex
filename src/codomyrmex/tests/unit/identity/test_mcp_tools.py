"""Strictly zero-mock tests for the identity module's MCP tools."""

from __future__ import annotations

import pytest

from codomyrmex.identity.mcp_tools import (
    _biocognitive_verifier,
    _identity_manager,
    identity_create_persona,
    identity_enroll_metric,
    identity_export_persona,
    identity_get_confidence,
    identity_list_personas,
    identity_promote_persona,
    identity_record_metric,
    identity_revoke_persona,
    identity_set_active_persona,
    identity_verify_metric,
)


@pytest.fixture(autouse=True)
def clean_state():
    """Reset the global state before each test."""
    _identity_manager._personas.clear()
    _identity_manager._active_persona_id = None
    _biocognitive_verifier._baselines.clear()
    yield


@pytest.mark.unit
class TestIdentityManagerMCPTools:
    """Zero-mock tests for IdentityManager MCP tools."""

    def test_identity_create_persona(self):
        """Test creating a new persona via MCP tool."""
        # Valid creation
        res = identity_create_persona(id="p-01", name="Test Persona", level="kyc_verified")
        assert res.get("status") == "success"
        assert res.get("persona", {}).get("id") == "p-01"
        assert res.get("persona", {}).get("name") == "Test Persona"

        # Invalid level
        res = identity_create_persona(id="p-02", name="P2", level="invalid_level")
        assert "error" in res
        assert "Invalid verification level" in res["error"]

        # Duplicate persona
        res = identity_create_persona(id="p-01", name="Duplicate")
        assert "error" in res
        assert "already exists" in res["error"]

    def test_identity_set_active_persona(self):
        """Test setting the active persona via MCP tool."""
        # Create first
        identity_create_persona(id="p-01", name="Test Persona")

        # Set active
        res = identity_set_active_persona("p-01")
        assert res.get("status") == "success"

        # Invalid ID
        res = identity_set_active_persona("invalid_id")
        assert "error" in res
        assert "not found" in res["error"]

    def test_identity_revoke_persona(self):
        """Test revoking a persona via MCP tool."""
        identity_create_persona(id="p-rev", name="To Revoke")

        # Valid revoke
        res = identity_revoke_persona("p-rev")
        assert res.get("status") == "success"

        # Verify it's revoked
        res = identity_revoke_persona("p-rev")
        assert "error" in res
        assert "not found" in res["error"]

    def test_identity_list_personas(self):
        """Test listing personas via MCP tool."""
        identity_create_persona(id="p-1", name="P1", level="unverified")
        identity_create_persona(id="p-2", name="P2", level="kyc_verified")

        # List all
        res = identity_list_personas()
        assert res.get("status") == "success"
        assert len(res.get("personas", [])) == 2

        # List filtered
        res = identity_list_personas("kyc_verified")
        assert res.get("status") == "success"
        assert len(res.get("personas", [])) == 1
        assert res["personas"][0]["id"] == "p-2"

        # Invalid filter
        res = identity_list_personas("invalid_level")
        assert "error" in res

    def test_identity_promote_persona(self):
        """Test promoting a persona via MCP tool."""
        identity_create_persona(id="p-pro", name="To Promote", level="unverified")

        # Valid promotion
        res = identity_promote_persona("p-pro", "kyc_verified")
        assert res.get("status") == "success"

        # Verify promotion
        res_list = identity_list_personas("kyc_verified")
        assert res_list["personas"][0]["id"] == "p-pro"

        # Invalid level
        res = identity_promote_persona("p-pro", "bad_level")
        assert "error" in res

        # Invalid persona
        res = identity_promote_persona("invalid_id", "kyc_verified")
        assert "error" in res

    def test_identity_export_persona(self):
        """Test exporting a persona via MCP tool."""
        identity_create_persona(id="p-exp", name="To Export", level="unverified", capabilities=["read"])

        # Valid export
        res = identity_export_persona("p-exp")
        assert res.get("status") == "success"
        assert res["persona"]["id"] == "p-exp"

        # Invalid export
        res = identity_export_persona("invalid_id")
        assert "error" in res


@pytest.mark.unit
class TestBioCognitiveVerifierMCPTools:
    """Zero-mock tests for BioCognitiveVerifier MCP tools."""

    def test_identity_record_metric(self):
        """Test recording a behavioral metric."""
        res = identity_record_metric(user_id="u-01", metric="flight_time", value=0.15)
        assert res.get("status") == "success"

        # Check confidence increased from 0
        res_conf = identity_get_confidence("u-01")
        assert res_conf.get("confidence") > 0.0

    def test_identity_enroll_metric(self):
        """Test enrolling a metric baseline."""
        baseline = [0.12, 0.13, 0.12, 0.14, 0.12]
        res = identity_enroll_metric(user_id="u-enr", metric_type="typing_speed", baseline=baseline)
        assert res.get("status") == "success"

        # Check confidence calculation is proportional to baseline len
        res_conf = identity_get_confidence("u-enr")
        assert res_conf.get("confidence") == len(baseline) / 100.0

    def test_identity_verify_metric(self):
        """Test verifying a metric against a baseline."""
        # Create a solid baseline
        baseline = [0.15] * 20
        identity_enroll_metric(user_id="u-ver", metric_type="flight_time", baseline=baseline)

        # Verification should succeed with a matching value
        res = identity_verify_metric(user_id="u-ver", metric="flight_time", current_value=0.15)
        assert res.get("status") == "success"
        assert res.get("verified") is True

        # Verification should fail with an outlier value
        res = identity_verify_metric(user_id="u-ver", metric="flight_time", current_value=0.50)
        assert res.get("status") == "success"
        assert res.get("verified") is False

        # Unenrolled user should fail
        res = identity_verify_metric(user_id="unkn", metric="flight_time", current_value=0.15)
        assert res.get("status") == "success"
        assert res.get("verified") is False

        # Insufficient samples (training phase) should return true
        identity_enroll_metric(user_id="u-train", metric_type="flight_time", baseline=[0.15] * 5)
        res = identity_verify_metric(user_id="u-train", metric="flight_time", current_value=0.99)
        assert res.get("status") == "success"
        assert res.get("verified") is True

    def test_identity_get_confidence(self):
        """Test getting confidence score."""
        res = identity_get_confidence("unkn")
        assert res.get("status") == "success"
        assert res.get("confidence") == 0.0

        # Add 100+ samples to reach max confidence
        baseline = [0.1] * 150
        identity_enroll_metric("u-conf", "flight_time", baseline)
        res = identity_get_confidence("u-conf")
        assert res.get("confidence") == 1.0
