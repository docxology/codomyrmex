"""Tests for the identity module (persona, manager, biocognitive)."""

import pytest
from codomyrmex.identity.persona import Persona, VerificationLevel
from codomyrmex.identity.manager import IdentityManager

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@pytest.mark.unit
class TestVerificationLevel:
    """Tests for the VerificationLevel enum."""

    def test_verification_levels_exist(self):
        assert VerificationLevel.UNVERIFIED.value == "unverified"
        assert VerificationLevel.ANON.value == "anonymous_verified"
        assert VerificationLevel.VERIFIED_ANON.value == "verified_anon"
        assert VerificationLevel.KYC.value == "kyc_verified"

    def test_all_levels_count(self):
        assert len(VerificationLevel) == 4


@pytest.mark.unit
class TestPersona:
    """Tests for the Persona dataclass."""

    def test_persona_creation(self):
        p = Persona(id="p1", name="Alice", level=VerificationLevel.ANON)
        assert p.id == "p1"
        assert p.name == "Alice"
        assert p.level == VerificationLevel.ANON
        assert p.created_at is not None

    def test_persona_defaults(self):
        p = Persona(id="p2", name="Bob", level=VerificationLevel.UNVERIFIED)
        assert p.attributes == {}
        assert p.crumbs == []

    def test_persona_add_attribute(self):
        p = Persona(id="p1", name="Alice", level=VerificationLevel.ANON)
        p.add_attribute("role", "admin")
        assert p.attributes["role"] == "admin"

    def test_persona_add_crumb(self):
        p = Persona(id="p1", name="Alice", level=VerificationLevel.ANON)
        p.add_crumb("visited_page_x")
        assert "visited_page_x" in p.crumbs

    def test_persona_crumbs_accumulate(self):
        p = Persona(id="p1", name="Alice", level=VerificationLevel.ANON)
        p.add_crumb("c1")
        p.add_crumb("c2")
        p.add_crumb("c3")
        assert len(p.crumbs) == 3


@pytest.mark.unit
class TestIdentityManager:
    """Tests for the IdentityManager class."""

    def setup_method(self):
        self.mgr = IdentityManager()

    def test_init(self):
        assert self.mgr._personas == {}
        assert self.mgr._active_persona_id is None

    def test_create_persona(self):
        persona = self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        assert persona.id == "p1"
        assert persona.name == "Alice"

    def test_create_duplicate_raises(self):
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        with pytest.raises(ValueError, match="already exists"):
            self.mgr.create_persona("p1", "Bob", VerificationLevel.KYC)

    def test_get_persona(self):
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        p = self.mgr.get_persona("p1")
        assert p is not None
        assert p.name == "Alice"

    def test_get_persona_nonexistent(self):
        assert self.mgr.get_persona("fake") is None

    def test_set_active_persona(self):
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        self.mgr.set_active_persona("p1")
        assert self.mgr.active_persona is not None
        assert self.mgr.active_persona.name == "Alice"

    def test_set_active_nonexistent_raises(self):
        with pytest.raises(ValueError, match="not found"):
            self.mgr.set_active_persona("fake")

    def test_active_persona_none_by_default(self):
        assert self.mgr.active_persona is None

    def test_list_personas(self):
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        self.mgr.create_persona("p2", "Bob", VerificationLevel.KYC)
        personas = self.mgr.list_personas()
        assert len(personas) == 2

    def test_revoke_persona(self):
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        result = self.mgr.revoke_persona("p1")
        assert result is True
        assert self.mgr.get_persona("p1") is None

    def test_revoke_active_persona_clears_active(self):
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        self.mgr.set_active_persona("p1")
        self.mgr.revoke_persona("p1")
        assert self.mgr.active_persona is None

    def test_revoke_nonexistent(self):
        assert self.mgr.revoke_persona("fake") is False

    def test_export_persona(self):
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        exported = self.mgr.export_persona("p1")
        assert exported is not None
        assert exported["id"] == "p1"
        assert exported["name"] == "Alice"
        assert exported["level"] == "anonymous_verified"
        assert "crumbs_count" in exported

    def test_export_nonexistent(self):
        assert self.mgr.export_persona("fake") is None


@pytest.mark.unit
@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
class TestBioCognitiveVerifier:
    """Tests for the BioCognitiveVerifier class."""

    def setup_method(self):
        from codomyrmex.identity.biocognitive import BioCognitiveVerifier
        self.verifier = BioCognitiveVerifier()

    def test_verifier_init(self):
        assert self.verifier._baselines == {}
        assert "keystroke_flight_time" in self.verifier._thresholds

    def test_record_metric(self):
        self.verifier.record_metric("u1", "keystroke_flight_time", 0.12)
        assert "u1" in self.verifier._baselines
        assert len(self.verifier._baselines["u1"]["keystroke_flight_time"]) == 1

    def test_record_metric_window(self):
        for i in range(105):
            self.verifier.record_metric("u1", "kft", float(i))
        assert len(self.verifier._baselines["u1"]["kft"]) == 100

    def test_verify_no_baseline_returns_false(self):
        result = self.verifier.verify("unknown", "kft", 0.5)
        assert result is False

    def test_verify_insufficient_samples_returns_true(self):
        for i in range(5):
            self.verifier.record_metric("u1", "kft", 0.1 + i * 0.01)
        result = self.verifier.verify("u1", "kft", 0.12)
        assert result is True

    def test_verify_valid_sample(self):
        for i in range(20):
            self.verifier.record_metric("u1", "kft", 0.1 + (i % 3) * 0.01)
        result = self.verifier.verify("u1", "kft", 0.11)
        assert bool(result) is True

    def test_verify_outlier_rejected(self):
        for _ in range(20):
            self.verifier.record_metric("u1", "kft", 0.1)
        result = self.verifier.verify("u1", "kft", 10.0)
        assert bool(result) is False
