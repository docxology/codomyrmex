"""Tests for the identity module (persona, manager, biocognitive, and orchestrator)."""

import time

import pytest

from codomyrmex.identity.biocognitive import BioCognitiveVerifier
from codomyrmex.identity.identity import Identity, PasswordProvider
from codomyrmex.identity.manager import IdentityManager
from codomyrmex.identity.persona import Persona, VerificationLevel

try:
    import numpy as np  # noqa: F401

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@pytest.mark.unit
class TestVerificationLevel:
    """Tests for the VerificationLevel enum."""

    def test_verification_levels_exist(self):
        """Test functionality: verification levels exist."""
        assert VerificationLevel.UNVERIFIED.value == "unverified"
        assert VerificationLevel.ANON.value == "anonymous_verified"
        assert VerificationLevel.VERIFIED_ANON.value == "verified_anon"
        assert VerificationLevel.KYC.value == "kyc_verified"

    def test_all_levels_count(self):
        """Test functionality: all levels count."""
        assert len(VerificationLevel) == 4


@pytest.mark.unit
class TestPersona:
    """Tests for the Persona dataclass."""

    def test_persona_creation(self):
        """Test functionality: persona creation."""
        p = Persona(id="p1", name="Alice", level=VerificationLevel.ANON)
        assert p.id == "p1"
        assert p.name == "Alice"
        assert p.level == VerificationLevel.ANON
        assert p.created_at is not None
        assert p.is_active is True

    def test_persona_defaults(self):
        """Test functionality: persona defaults."""
        p = Persona(id="p2", name="Bob", level=VerificationLevel.UNVERIFIED)
        assert p.attributes == {}
        assert p.crumbs == []
        assert p.capabilities == []

    def test_persona_add_attribute(self):
        """Test functionality: persona add attribute."""
        p = Persona(id="p1", name="Alice", level=VerificationLevel.ANON)
        p.add_attribute("role", "admin")
        assert p.attributes["role"] == "admin"

    def test_persona_add_crumb(self):
        """Test functionality: persona add crumb."""
        p = Persona(id="p1", name="Alice", level=VerificationLevel.ANON)
        p.add_crumb("visited_page_x")
        assert "visited_page_x" in p.crumbs

    def test_persona_capabilities(self):
        """Test functionality: persona capabilities."""
        p = Persona(id="p1", name="Alice", level=VerificationLevel.ANON)
        p.add_capability("read")
        assert p.has_capability("read")
        assert not p.has_capability("write")

    def test_persona_to_dict(self):
        """Test functionality: persona to_dict conversion."""
        p = Persona(
            id="p1", name="Alice", level=VerificationLevel.KYC, capabilities=["root"]
        )
        p.add_attribute("email", "alice@example.com")
        p.add_crumb("logged_in")
        d = p.to_dict()
        assert d["id"] == "p1"
        assert d["name"] == "Alice"
        assert d["level"] == "kyc_verified"
        assert d["attributes"]["email"] == "alice@example.com"
        assert d["crumbs_count"] == 1
        assert "root" in d["capabilities"]
        assert d["is_active"] is True


@pytest.mark.unit
class TestIdentityManager:
    """Tests for the IdentityManager class."""

    def setup_method(self, method):
        self.mgr = IdentityManager()

    def test_init(self):
        """Test functionality: init."""
        assert self.mgr._personas == {}
        assert self.mgr._active_persona_id is None

    def test_create_persona(self):
        """Test functionality: create persona."""
        persona = self.mgr.create_persona(
            "p1", "Alice", VerificationLevel.ANON, capabilities=["test"]
        )
        assert persona.id == "p1"
        assert persona.name == "Alice"
        assert "test" in persona.capabilities

    def test_register_persona(self):
        """Test functionality: register persona."""
        p = Persona(id="p1", name="Alice", level=VerificationLevel.ANON)
        self.mgr.register_persona(p)
        assert self.mgr.get_persona("p1") is p

    def test_create_duplicate_raises(self):
        """Test functionality: create duplicate raises."""
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        with pytest.raises(ValueError, match="already exists"):
            self.mgr.create_persona("p1", "Bob", VerificationLevel.KYC)

    def test_get_persona(self):
        """Test functionality: get persona."""
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        p = self.mgr.get_persona("p1")
        assert p is not None
        assert p.name == "Alice"

    def test_set_active_persona(self):
        """Test functionality: set active persona."""
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        self.mgr.set_active_persona("p1")
        assert self.mgr.active_persona is not None
        assert self.mgr.active_persona.name == "Alice"

    def test_list_personas_filtered(self):
        """Test functionality: list personas filtered by level."""
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        self.mgr.create_persona("p2", "Bob", VerificationLevel.KYC)
        anon_list = self.mgr.list_personas(level=VerificationLevel.ANON)
        assert len(anon_list) == 1
        assert anon_list[0].id == "p1"

    def test_revoke_persona(self):
        """Test functionality: revoke persona."""
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        result = self.mgr.revoke_persona("p1")
        assert result is True
        assert self.mgr.get_persona("p1") is None

    def test_promote_persona(self):
        """Test functionality: promote persona."""
        self.mgr.create_persona("p1", "Alice", VerificationLevel.ANON)
        success = self.mgr.promote_persona("p1", VerificationLevel.KYC)
        assert success is True
        assert self.mgr.get_persona("p1").level == VerificationLevel.KYC


@pytest.mark.unit
@pytest.mark.skipif(not HAS_NUMPY, reason="numpy not installed")
class TestBioCognitiveVerifier:
    """Tests for the BioCognitiveVerifier class."""

    def setup_method(self, method):
        self.verifier = BioCognitiveVerifier()

    def test_record_and_verify(self):
        """Test functionality: record metric and verify."""
        user = "u1"
        metric = "kft"
        for _ in range(15):
            self.verifier.record_metric(user, metric, 0.12)

        # Valid sample
        assert self.verifier.verify(user, metric, 0.125) is True
        # Outlier sample
        assert self.verifier.verify(user, metric, 0.35) is False

    def test_get_confidence(self):
        """Test functionality: confidence calculation."""
        user = "u1"
        for i in range(50):
            self.verifier.record_metric(user, "m1", float(i))
        assert self.verifier.get_confidence(user) == 0.5

    def test_enroll(self):
        """Test functionality: manual enrollment."""
        baseline = [0.1, 0.11, 0.12, 0.1, 0.11] * 3
        self.verifier.enroll("u1", "kft", baseline)
        assert self.verifier.verify("u1", "kft", 0.11) is True

    def test_create_challenge(self):
        """Test functionality: create challenge."""
        p = Persona(id="p1", name="Alice", level=VerificationLevel.ANON)
        challenge = self.verifier.create_challenge(p)
        assert challenge["type"] == "keystroke_dynamics"
        assert challenge["persona_id"] == "p1"


@pytest.mark.unit
class TestIdentityOrchestrator:
    """Tests for the main Identity orchestrator class."""

    def setup_method(self, method):
        self.ident = Identity(session_ttl=10.0)
        self.pw_prov = PasswordProvider()
        self.pw_prov.register("alice", "password123")
        self.ident.register_provider("password", self.pw_prov)

    def test_login_logout(self):
        """Test functionality: login and logout flow."""
        token = self.ident.login(
            "alice", {"user_id": "alice", "password": "password123"}
        )
        assert token is not None
        assert self.ident.validate_token(token.token) is True

        self.ident.logout(token.token)
        assert self.ident.validate_token(token.token) is False

    def test_token_expiry(self):
        """Test functionality: token expiration."""
        # Short TTL for test
        ident = Identity(session_ttl=0.001)
        ident.register_provider("password", self.pw_prov)
        token = ident.login("alice", {"user_id": "alice", "password": "password123"})
        time.sleep(0.005)
        assert ident.validate_token(token.token) is False

    def test_refresh_token(self):
        """Test functionality: token refresh."""
        token = self.ident.login(
            "alice", {"user_id": "alice", "password": "password123"}
        )
        old_token_str = token.token
        new_token = self.ident.refresh_token(old_token_str)
        assert new_token is not None
        assert new_token.token != old_token_str
        assert self.ident.validate_token(new_token.token) is True
        assert self.ident.validate_token(old_token_str) is False

    def test_process_with_persona(self):
        """Test functionality: data processing with active persona context."""
        self.ident.manager.create_persona("p1", "Alice", VerificationLevel.KYC)
        self.ident.manager.set_active_persona("p1")

        data = {"message": "hello"}
        processed = self.ident.process(data)
        assert "_identity_signature" in processed
        assert processed["_identity_signature"] == "verified:p1"

    def test_audit_log(self):
        """Test functionality: audit logging."""
        self.ident.login("alice", {"user_id": "alice", "password": "password123"})
        self.ident.login("alice", {"user_id": "alice", "password": "wrong"})
        log = self.ident.audit_log
        assert len(log) == 2
        assert log[0].event_type == "login"
        assert log[1].event_type == "failed"
