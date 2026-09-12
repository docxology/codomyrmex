"""Tests for the wallet ZK proof module.

Zero-mock policy: all tests use real WalletManager, IdentityManager,
and real HMAC-SHA256 operations. No mocks.

Covers:
- ZKProof dataclass serialization
- ZKProofVerifier generate / verify round-trip
- ZKProofVerifier failure cases (wrong message, wrong user, tampered response)
- Decoupled verification (verify_proof_with_response)
- SignedCapabilityProofBuilder build / verify round-trip
- SignedCapabilityProofBuilder capability enforcement
- MCP tool wrappers (wallet_generate_zk_proof, wallet_verify_zk_proof)
- Convenience functions (generate_zk_proof, verify_zk_proof)
- Package-level exports
"""

from __future__ import annotations

import hashlib
import hmac
import tempfile

import pytest

from codomyrmex.identity.manager import IdentityManager
from codomyrmex.identity.persona import VerificationLevel
from codomyrmex.wallet.core import WalletManager
from codomyrmex.wallet.exceptions import WalletNotFoundError
from codomyrmex.wallet.zk_proof import (
    CapabilityAttestation,
    SignedCapabilityProof,
    SignedCapabilityProofBuilder,
    ZKProof,
    ZKProofVerifier,
    generate_zk_proof,
    verify_zk_proof,
)


@pytest.mark.unit
class TestZKProofDataclass:
    """Tests for the ZKProof dataclass."""

    def test_creation_with_defaults(self):
        proof = ZKProof(
            user_id="u1",
            wallet_address="0xabc",
            challenge="deadbeef",
            response="cafebabe",
        )
        assert proof.user_id == "u1"
        assert proof.wallet_address == "0xabc"
        assert proof.challenge == "deadbeef"
        assert proof.response == "cafebabe"
        assert proof.message == ""
        assert proof.timestamp != ""
        assert proof.nonce != ""

    def test_to_dict_and_from_dict_roundtrip(self):
        proof = ZKProof(
            user_id="u1",
            wallet_address="0xabc",
            challenge="deadbeef",
            response="cafebabe",
            message="68656c6c6f",
            timestamp="2026-01-01T00:00:00Z",
            nonce="abcdef0123456789",
        )
        d = proof.to_dict()
        restored = ZKProof.from_dict(d)
        assert restored.user_id == proof.user_id
        assert restored.wallet_address == proof.wallet_address
        assert restored.challenge == proof.challenge
        assert restored.response == proof.response
        assert restored.message == proof.message
        assert restored.timestamp == proof.timestamp
        assert restored.nonce == proof.nonce

    def test_to_json(self):
        proof = ZKProof(
            user_id="u1",
            wallet_address="0xabc",
            challenge="deadbeef",
            response="cafebabe",
        )
        import json

        data = json.loads(proof.to_json())
        assert data["user_id"] == "u1"
        assert data["wallet_address"] == "0xabc"


@pytest.mark.unit
class TestZKProofVerifier:
    """Tests for the ZKProofVerifier class."""

    def setup_method(self):
        self.mgr = WalletManager()
        self.address = self.mgr.create_wallet("alice")
        self.verifier = ZKProofVerifier(wallet_manager=self.mgr)

    def test_generate_proof_returns_valid_structure(self):
        proof = self.verifier.generate_proof("alice")
        assert isinstance(proof, ZKProof)
        assert proof.user_id == "alice"
        assert proof.wallet_address == self.address
        assert len(proof.challenge) == 64  # sha256 hex
        assert len(proof.response) > 0
        assert proof.nonce != ""

    def test_generate_proof_with_message(self):
        msg = b"transfer 10 ETH"
        proof = self.verifier.generate_proof("alice", message=msg)
        assert proof.message == msg.hex()

    def test_generate_proof_no_wallet_raises(self):
        with pytest.raises(WalletNotFoundError):
            self.verifier.generate_proof("nobody")

    def test_verify_proof_success(self):
        proof = self.verifier.generate_proof("alice")
        assert self.verifier.verify_proof(proof) is True

    def test_verify_proof_with_message_success(self):
        msg = b"transfer 10 ETH"
        proof = self.verifier.generate_proof("alice", message=msg)
        assert self.verifier.verify_proof(proof, message=msg) is True

    def test_verify_proof_wrong_message_fails(self):
        proof = self.verifier.generate_proof("alice", message=b"original")
        assert self.verifier.verify_proof(proof, message=b"tampered") is False

    def test_verify_proof_no_wallet_fails(self):
        proof = ZKProof(
            user_id="nobody",
            wallet_address="0xdead",
            challenge="aa",
            response="bb",
        )
        assert self.verifier.verify_proof(proof) is False

    def test_verify_proof_wrong_address_fails(self):
        proof = self.verifier.generate_proof("alice")
        tampered = ZKProof(
            user_id=proof.user_id,
            wallet_address="0xwrong",
            challenge=proof.challenge,
            response=proof.response,
            message=proof.message,
            timestamp=proof.timestamp,
            nonce=proof.nonce,
        )
        assert self.verifier.verify_proof(tampered) is False

    def test_verify_proof_tampered_response_fails(self):
        proof = self.verifier.generate_proof("alice")
        tampered_response = "00" * 32  # different from real HMAC
        tampered = ZKProof(
            user_id=proof.user_id,
            wallet_address=proof.wallet_address,
            challenge=proof.challenge,
            response=tampered_response,
            message=proof.message,
            timestamp=proof.timestamp,
            nonce=proof.nonce,
        )
        assert self.verifier.verify_proof(tampered) is False

    def test_verify_proof_tampered_challenge_fails(self):
        proof = self.verifier.generate_proof("alice")
        tampered = ZKProof(
            user_id=proof.user_id,
            wallet_address=proof.wallet_address,
            challenge="00" * 32,
            response=proof.response,
            message=proof.message,
            timestamp=proof.timestamp,
            nonce=proof.nonce,
        )
        assert self.verifier.verify_proof(tampered) is False

    def test_verify_proof_tampered_nonce_fails(self):
        proof = self.verifier.generate_proof("alice")
        tampered = ZKProof(
            user_id=proof.user_id,
            wallet_address=proof.wallet_address,
            challenge=proof.challenge,
            response=proof.response,
            message=proof.message,
            timestamp=proof.timestamp,
            nonce="00" * 16,
        )
        assert self.verifier.verify_proof(tampered) is False

    def test_lazy_wallet_manager_creation(self):
        """ZKProofVerifier can use a pre-created WalletManager."""
        mgr = WalletManager()
        mgr.create_wallet("lazy_user")
        verifier = ZKProofVerifier(wallet_manager=mgr)
        proof = verifier.generate_proof("lazy_user")
        assert verifier.verify_proof(proof) is True


@pytest.mark.unit
class TestZKProofDecoupledVerification:
    """Tests for the decoupled (no WalletManager key access) verification."""

    def setup_method(self):
        self.mgr = WalletManager()
        self.address = self.mgr.create_wallet("bob")
        self.verifier = ZKProofVerifier(wallet_manager=self.mgr)

    def test_decoupled_verify_success(self):
        proof = self.verifier.generate_proof("bob", message=b"hello")
        # In decoupled mode, the verifier has the expected response
        # (e.g. pre-shared or from an attestation service).
        expected = bytes.fromhex(proof.response)
        assert ZKProofVerifier.verify_proof_with_response(
            proof, expected, message=b"hello"
        ) is True

    def test_decoupled_verify_wrong_response_fails(self):
        proof = self.verifier.generate_proof("bob")
        wrong_response = b"\x00" * 32
        assert ZKProofVerifier.verify_proof_with_response(
            proof, wrong_response
        ) is False

    def test_decoupled_verify_wrong_message_fails(self):
        proof = self.verifier.generate_proof("bob", message=b"original")
        expected = bytes.fromhex(proof.response)
        assert ZKProofVerifier.verify_proof_with_response(
            proof, expected, message=b"wrong"
        ) is False

    def test_decoupled_verify_tampered_challenge_fails(self):
        proof = self.verifier.generate_proof("bob")
        expected = bytes.fromhex(proof.response)
        tampered = ZKProof(
            user_id=proof.user_id,
            wallet_address=proof.wallet_address,
            challenge="00" * 32,
            response=proof.response,
            message=proof.message,
            timestamp=proof.timestamp,
            nonce=proof.nonce,
        )
        assert ZKProofVerifier.verify_proof_with_response(
            tampered, expected
        ) is False


@pytest.mark.unit
class TestCapabilityAttestation:
    """Tests for the CapabilityAttestation dataclass."""

    def test_creation_with_defaults(self):
        att = CapabilityAttestation(
            persona_id="p1",
            persona_name="Alice",
            verification_level="kyc_verified",
        )
        assert att.persona_id == "p1"
        assert att.persona_name == "Alice"
        assert att.verification_level == "kyc_verified"
        assert att.capabilities == []
        assert att.wallet_address == ""
        assert att.timestamp != ""

    def test_to_dict(self):
        att = CapabilityAttestation(
            persona_id="p1",
            persona_name="Alice",
            verification_level="kyc_verified",
            capabilities=["send_funds", "view_balance"],
            wallet_address="0xabc",
        )
        d = att.to_dict()
        assert d["persona_id"] == "p1"
        assert d["capabilities"] == ["send_funds", "view_balance"]
        assert d["wallet_address"] == "0xabc"

    def test_to_json(self):
        att = CapabilityAttestation(
            persona_id="p1",
            persona_name="Alice",
            verification_level="kyc_verified",
        )
        import json

        data = json.loads(att.to_json())
        assert data["persona_id"] == "p1"


@pytest.mark.unit
class TestSignedCapabilityProofBuilder:
    """Tests for the SignedCapabilityProofBuilder class."""

    def setup_method(self):
        self.mgr = WalletManager()
        self.address = self.mgr.create_wallet("alice")
        self.id_mgr = IdentityManager()
        self.id_mgr.create_persona(
            "alice_p",
            "Alice",
            level=VerificationLevel.KYC,
            capabilities=["send_funds", "view_balance"],
        )
        self.builder = SignedCapabilityProofBuilder(
            wallet_manager=self.mgr,
            identity_manager=self.id_mgr,
        )

    def test_build_returns_signed_capability_proof(self):
        proof = self.builder.build("alice", "alice_p", message=b"transfer")
        assert isinstance(proof, SignedCapabilityProof)
        assert proof.zk_proof.user_id == "alice"
        assert proof.zk_proof.wallet_address == self.address
        assert proof.attestation.persona_id == "alice_p"
        assert proof.attestation.persona_name == "Alice"
        assert proof.attestation.verification_level == "kyc_verified"
        assert "send_funds" in proof.attestation.capabilities
        assert proof.attestation_signature != ""

    def test_build_with_required_capability_success(self):
        proof = self.builder.build(
            "alice",
            "alice_p",
            message=b"tx",
            required_capability="send_funds",
        )
        assert isinstance(proof, SignedCapabilityProof)

    def test_build_with_required_capability_missing_raises(self):
        with pytest.raises(ValueError, match="lacks required capability"):
            self.builder.build(
                "alice",
                "alice_p",
                required_capability="admin_access",
            )

    def test_build_persona_not_found_raises(self):
        with pytest.raises(ValueError, match="not found"):
            self.builder.build("alice", "nonexistent_persona")

    def test_build_no_wallet_raises(self):
        with pytest.raises(WalletNotFoundError):
            self.builder.build("nobody", "alice_p")

    def test_verify_success(self):
        proof = self.builder.build("alice", "alice_p", message=b"authorize")
        assert self.builder.verify(proof, message=b"authorize") is True

    def test_verify_wrong_message_fails(self):
        proof = self.builder.build("alice", "alice_p", message=b"original")
        assert self.builder.verify(proof, message=b"wrong") is False

    def test_verify_tampered_attestation_fails(self):
        proof = self.builder.build("alice", "alice_p")
        # Tamper with the attestation
        tampered = SignedCapabilityProof(
            zk_proof=proof.zk_proof,
            attestation=CapabilityAttestation(
                persona_id=proof.attestation.persona_id,
                persona_name="Eve",  # Changed name
                verification_level=proof.attestation.verification_level,
                capabilities=proof.attestation.capabilities,
                wallet_address=proof.attestation.wallet_address,
                timestamp=proof.attestation.timestamp,
            ),
            attestation_signature=proof.attestation_signature,
        )
        assert self.builder.verify(tampered) is False

    def test_verify_tampered_attestation_signature_fails(self):
        proof = self.builder.build("alice", "alice_p")
        tampered = SignedCapabilityProof(
            zk_proof=proof.zk_proof,
            attestation=proof.attestation,
            attestation_signature="00" * 32,
        )
        assert self.builder.verify(tampered) is False

    def test_proof_serialization_roundtrip(self):
        proof = self.builder.build("alice", "alice_p", message=b"test")
        d = proof.to_dict()
        restored = SignedCapabilityProof.from_dict(d)
        assert restored.zk_proof.user_id == proof.zk_proof.user_id
        assert restored.attestation.persona_id == proof.attestation.persona_id
        assert restored.attestation_signature == proof.attestation_signature

    def test_proof_to_json(self):
        proof = self.builder.build("alice", "alice_p")
        import json

        data = json.loads(proof.to_json())
        assert data["zk_proof"]["user_id"] == "alice"
        assert data["attestation"]["persona_id"] == "alice_p"


@pytest.mark.unit
class TestConvenienceFunctions:
    """Tests for the generate_zk_proof and verify_zk_proof functions."""

    def test_generate_and_verify_roundtrip_with_manager(self):
        mgr = WalletManager()
        mgr.create_wallet("conv_user")

        gen_result = generate_zk_proof(
            "conv_user", message="hello", wallet_manager=mgr
        )
        assert "status" not in gen_result  # success has no status key
        assert "user_id" in gen_result
        assert "challenge" in gen_result
        assert "response" in gen_result

        verify_result = verify_zk_proof(
            gen_result, message="hello", wallet_manager=mgr
        )
        assert verify_result["status"] == "success"
        assert verify_result["verified"] is True

    def test_generate_and_verify_roundtrip_stateless(self):
        """Test stateless generate/verify using storage_path + wallet_address."""
        mgr = WalletManager()
        addr = mgr.create_wallet("conv_stateless")
        storage = str(mgr.key_manager.key_dir)

        gen_result = generate_zk_proof(
            "conv_stateless",
            storage_path=storage,
            message="hello",
            wallet_address=addr,
        )
        assert "user_id" in gen_result
        assert "challenge" in gen_result

        verify_result = verify_zk_proof(
            gen_result, storage_path=storage, message="hello"
        )
        assert verify_result["status"] == "success"
        assert verify_result["verified"] is True

    def test_generate_no_wallet_returns_error(self):
        mgr = WalletManager()
        result = generate_zk_proof("nobody", wallet_manager=mgr)
        assert result["status"] == "error"

    def test_verify_wrong_message_returns_false(self):
        mgr = WalletManager()
        mgr.create_wallet("conv_user2")

        gen_result = generate_zk_proof(
            "conv_user2", message="original", wallet_manager=mgr
        )
        verify_result = verify_zk_proof(
            gen_result, message="tampered", wallet_manager=mgr
        )
        assert verify_result["status"] == "success"
        assert verify_result["verified"] is False

    def test_generate_without_wallet_manager(self):
        """generate_zk_proof works with default storage path (temp dir)."""
        result = generate_zk_proof("zk_default_user_12345")
        # This should fail since no wallet exists in default storage
        assert result["status"] == "error"


@pytest.mark.unit
class TestMCPToolWrappers:
    """Tests for the MCP tool wrapper functions."""

    def test_wallet_generate_zk_proof_mcp_tool(self):
        from codomyrmex.wallet.mcp_tools import wallet_generate_zk_proof

        mgr = WalletManager()
        addr = mgr.create_wallet("mcp_user")
        storage = str(mgr.key_manager.key_dir)

        result = wallet_generate_zk_proof(
            user_id="mcp_user",
            storage_path=storage,
            message="test msg",
            wallet_address=addr,
        )
        assert result["status"] == "success"
        assert "proof" in result
        assert result["proof"]["user_id"] == "mcp_user"
        assert "challenge" in result["proof"]

    def test_wallet_verify_zk_proof_mcp_tool_success(self):
        from codomyrmex.wallet.mcp_tools import (
            wallet_generate_zk_proof,
            wallet_verify_zk_proof,
        )

        mgr = WalletManager()
        addr = mgr.create_wallet("mcp_user2")
        storage = str(mgr.key_manager.key_dir)

        gen = wallet_generate_zk_proof(
            user_id="mcp_user2",
            storage_path=storage,
            message="verify me",
            wallet_address=addr,
        )
        assert gen["status"] == "success"

        result = wallet_verify_zk_proof(
            proof=gen["proof"], storage_path=storage, message="verify me"
        )
        assert result["status"] == "success"
        assert result["verified"] is True

    def test_wallet_verify_zk_proof_mcp_tool_failure(self):
        from codomyrmex.wallet.mcp_tools import (
            wallet_generate_zk_proof,
            wallet_verify_zk_proof,
        )

        mgr = WalletManager()
        addr = mgr.create_wallet("mcp_user3")
        storage = str(mgr.key_manager.key_dir)

        gen = wallet_generate_zk_proof(
            user_id="mcp_user3",
            storage_path=storage,
            message="original",
            wallet_address=addr,
        )
        result = wallet_verify_zk_proof(
            proof=gen["proof"], storage_path=storage, message="wrong"
        )
        assert result["status"] == "success"
        assert result["verified"] is False

    def test_mcp_tools_have_metadata(self):
        """Verify the @mcp_tool decorator attached metadata."""
        from codomyrmex.wallet.mcp_tools import (
            wallet_generate_zk_proof,
            wallet_verify_zk_proof,
        )

        assert hasattr(wallet_generate_zk_proof, "_mcp_tool_meta")
        meta = wallet_generate_zk_proof._mcp_tool_meta
        assert meta["category"] == "wallet"
        assert "zero-knowledge" in meta["description"].lower()

        assert hasattr(wallet_verify_zk_proof, "_mcp_tool_meta")
        meta2 = wallet_verify_zk_proof._mcp_tool_meta
        assert meta2["category"] == "wallet"

    def test_mcp_tool_generate_no_wallet_returns_error(self):
        from codomyrmex.wallet.mcp_tools import wallet_generate_zk_proof

        result = wallet_generate_zk_proof(
            user_id="nonexistent",
            wallet_address="0xdead",
        )
        assert result["status"] == "error"


@pytest.mark.unit
class TestPackageExports:
    """Verify the wallet __init__ exports the new classes."""

    def test_zk_proof_classes_exported(self):
        import codomyrmex.wallet as wallet_mod

        assert hasattr(wallet_mod, "ZKProof")
        assert hasattr(wallet_mod, "ZKProofVerifier")
        assert hasattr(wallet_mod, "SignedCapabilityProof")
        assert hasattr(wallet_mod, "SignedCapabilityProofBuilder")
        assert hasattr(wallet_mod, "CapabilityAttestation")
        assert hasattr(wallet_mod, "generate_zk_proof")
        assert hasattr(wallet_mod, "verify_zk_proof")

    def test_zk_proof_classes_in_all(self):
        import codomyrmex.wallet as wallet_mod

        assert "ZKProof" in wallet_mod.__all__
        assert "ZKProofVerifier" in wallet_mod.__all__
        assert "SignedCapabilityProof" in wallet_mod.__all__
        assert "SignedCapabilityProofBuilder" in wallet_mod.__all__
        assert "CapabilityAttestation" in wallet_mod.__all__
        assert "generate_zk_proof" in wallet_mod.__all__
        assert "verify_zk_proof" in wallet_mod.__all__
