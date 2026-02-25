"""Tests for the wallet module (recovery, key_rotation, exceptions, core)."""

import hashlib

import pytest

from codomyrmex.wallet.exceptions import (
    RitualError,
    WalletError,
    WalletKeyError,
    WalletNotFoundError,
)
from codomyrmex.wallet.security.key_rotation import (
    KeyRotation,
    RotationPolicy,
    RotationRecord,
)
from codomyrmex.wallet.security.recovery import (
    NaturalRitualRecovery,
    RitualStep,
    hash_response,
)


@pytest.mark.unit
class TestWalletExceptions:
    """Tests for wallet exception hierarchy."""

    def test_wallet_error_is_codomyrmex_error(self):
        """Test functionality: wallet error is codomyrmex error."""
        from codomyrmex.exceptions import CodomyrmexError
        assert issubclass(WalletError, CodomyrmexError)

    def test_wallet_not_found_is_wallet_error(self):
        """Test functionality: wallet not found is wallet error."""
        assert issubclass(WalletNotFoundError, WalletError)

    def test_wallet_key_error_is_wallet_error(self):
        """Test functionality: wallet key error is wallet error."""
        assert issubclass(WalletKeyError, WalletError)

    def test_ritual_error_is_wallet_error(self):
        """Test functionality: ritual error is wallet error."""
        assert issubclass(RitualError, WalletError)

    def test_exception_message(self):
        """Test functionality: exception message."""
        err = WalletError("test message")
        assert "test message" in str(err)


@pytest.mark.unit
class TestHashResponse:
    """Tests for the hash_response function."""

    def test_hash_response(self):
        """Test functionality: hash response."""
        result = hash_response("my secret answer")
        expected = hashlib.sha256(b"my secret answer").hexdigest()
        assert result == expected

    def test_hash_response_deterministic(self):
        """Test functionality: hash response deterministic."""
        r1 = hash_response("same input")
        r2 = hash_response("same input")
        assert r1 == r2

    def test_hash_response_different_inputs(self):
        """Test functionality: hash response different inputs."""
        r1 = hash_response("input1")
        r2 = hash_response("input2")
        assert r1 != r2


@pytest.mark.unit
class TestRitualStep:
    """Tests for the RitualStep dataclass."""

    def test_ritual_step_creation(self):
        """Test functionality: ritual step creation."""
        step = RitualStep(prompt="What is your pet's name?", expected_response_hash="abc123")
        assert step.prompt == "What is your pet's name?"
        assert step.expected_response_hash == "abc123"


@pytest.mark.unit
class TestNaturalRitualRecovery:
    """Tests for the NaturalRitualRecovery class."""

    def setup_method(self):
        self.recovery = NaturalRitualRecovery()
        self.steps = [
            RitualStep(prompt="Pet name?", expected_response_hash=hash_response("fluffy")),
            RitualStep(prompt="City born?", expected_response_hash=hash_response("portland")),
        ]

    def test_init(self):
        """Test functionality: init."""
        assert self.recovery._rituals == {}
        assert self.recovery.max_attempts == 5

    def test_register_ritual(self):
        """Test functionality: register ritual."""
        self.recovery.register_ritual("u1", self.steps)
        assert self.recovery.has_ritual("u1")

    def test_register_empty_raises(self):
        """Test functionality: register empty raises."""
        with pytest.raises(RitualError, match="at least one step"):
            self.recovery.register_ritual("u1", [])

    def test_get_prompts(self):
        """Test functionality: get prompts."""
        self.recovery.register_ritual("u1", self.steps)
        prompts = self.recovery.get_prompts("u1")
        assert prompts == ["Pet name?", "City born?"]

    def test_get_prompts_no_ritual_raises(self):
        """Test functionality: get prompts no ritual raises."""
        with pytest.raises(RitualError, match="No ritual defined"):
            self.recovery.get_prompts("unknown")

    def test_initiate_recovery_correct(self):
        """Test functionality: initiate recovery correct."""
        self.recovery.register_ritual("u1", self.steps)
        result = self.recovery.initiate_recovery("u1", ["fluffy", "portland"])
        assert result is True

    def test_initiate_recovery_incorrect(self):
        """Test functionality: initiate recovery incorrect."""
        self.recovery.register_ritual("u1", self.steps)
        result = self.recovery.initiate_recovery("u1", ["wrong", "portland"])
        assert result is False

    def test_initiate_recovery_wrong_step_count(self):
        """Test functionality: initiate recovery wrong step count."""
        self.recovery.register_ritual("u1", self.steps)
        result = self.recovery.initiate_recovery("u1", ["fluffy"])
        assert result is False

    def test_lockout_after_max_attempts(self):
        """Test functionality: lockout after max attempts."""
        self.recovery.register_ritual("u1", self.steps)
        for _ in range(5):
            self.recovery.initiate_recovery("u1", ["wrong", "wrong"])
        with pytest.raises(RitualError, match="locked out"):
            self.recovery.initiate_recovery("u1", ["fluffy", "portland"])

    def test_remaining_attempts(self):
        """Test functionality: remaining attempts."""
        self.recovery.register_ritual("u1", self.steps)
        assert self.recovery.get_remaining_attempts("u1") == 5
        self.recovery.initiate_recovery("u1", ["wrong", "wrong"])
        assert self.recovery.get_remaining_attempts("u1") == 4

    def test_success_resets_attempts(self):
        """Test functionality: success resets attempts."""
        self.recovery.register_ritual("u1", self.steps)
        self.recovery.initiate_recovery("u1", ["wrong", "wrong"])
        self.recovery.initiate_recovery("u1", ["fluffy", "portland"])
        assert self.recovery.get_remaining_attempts("u1") == 5

    def test_unregister_ritual(self):
        """Test functionality: unregister ritual."""
        self.recovery.register_ritual("u1", self.steps)
        result = self.recovery.unregister_ritual("u1")
        assert result is True
        assert not self.recovery.has_ritual("u1")

    def test_unregister_nonexistent(self):
        """Test functionality: unregister nonexistent."""
        assert self.recovery.unregister_ritual("fake") is False

    def test_is_locked(self):
        """Test functionality: is locked."""
        self.recovery.register_ritual("u1", self.steps)
        assert self.recovery.is_locked("u1") is False

    def test_reset_attempts(self):
        """Test functionality: reset attempts."""
        self.recovery.register_ritual("u1", self.steps)
        for _ in range(5):
            self.recovery.initiate_recovery("u1", ["wrong", "wrong"])
        assert self.recovery.is_locked("u1") is True
        self.recovery.reset_attempts("u1")
        assert self.recovery.is_locked("u1") is False

    def test_max_attempts_setter(self):
        """Test functionality: max attempts setter."""
        self.recovery.max_attempts = 3
        assert self.recovery.max_attempts == 3

    def test_max_attempts_setter_invalid(self):
        """Test functionality: max attempts setter invalid."""
        with pytest.raises(ValueError):
            self.recovery.max_attempts = 0


@pytest.mark.unit
class TestRotationPolicy:
    """Tests for the RotationPolicy dataclass."""

    def test_defaults(self):
        """Test functionality: defaults."""
        policy = RotationPolicy()
        assert policy.max_age_days == 90
        assert policy.max_signatures == 10000
        assert policy.auto_rotate is False

    def test_custom_values(self):
        """Test functionality: custom values."""
        policy = RotationPolicy(max_age_days=30, max_signatures=500, auto_rotate=True)
        assert policy.max_age_days == 30
        assert policy.max_signatures == 500
        assert policy.auto_rotate is True


@pytest.mark.unit
class TestRotationRecord:
    """Tests for the RotationRecord dataclass."""

    def test_creation(self):
        """Test functionality: creation."""
        rec = RotationRecord(
            user_id="u1",
            old_wallet_id="0xaaa",
            new_wallet_id="0xbbb",
            timestamp="2024-01-01T00:00:00Z",
        )
        assert rec.user_id == "u1"
        assert rec.reason == "scheduled"

    def test_custom_reason(self):
        """Test functionality: custom reason."""
        rec = RotationRecord(
            user_id="u1",
            old_wallet_id="0xaaa",
            new_wallet_id="0xbbb",
            timestamp="2024-01-01T00:00:00Z",
            reason="compromised",
        )
        assert rec.reason == "compromised"


@pytest.mark.unit
class TestKeyRotation:
    """Tests for the KeyRotation class."""

    def setup_method(self):
        self.kr = KeyRotation()

    def test_init_defaults(self):
        """Test functionality: init defaults."""
        assert self.kr.policy.max_age_days == 90
        assert self.kr.policy.max_signatures == 10000

    def test_init_custom_policy(self):
        """Test functionality: init custom policy."""
        policy = RotationPolicy(max_age_days=7, max_signatures=100)
        kr = KeyRotation(policy=policy)
        assert kr.policy.max_age_days == 7

    def test_register_wallet(self):
        """Test functionality: register wallet."""
        self.kr.register_wallet("u1", "0xabc")
        assert self.kr._signature_counts["u1"] == 0
        assert "u1" in self.kr._creation_times

    def test_record_signature(self):
        """Test functionality: record signature."""
        self.kr.register_wallet("u1", "0xabc")
        self.kr.record_signature("u1")
        assert self.kr._signature_counts["u1"] == 1

    def test_needs_rotation_by_signatures(self):
        """Test functionality: needs rotation by signatures."""
        policy = RotationPolicy(max_signatures=3)
        kr = KeyRotation(policy=policy)
        kr.register_wallet("u1", "0xabc")
        assert kr.needs_rotation("u1") is False
        for _ in range(3):
            kr.record_signature("u1")
        assert kr.needs_rotation("u1") is True

    def test_needs_rotation_no_wallet(self):
        """Test functionality: needs rotation no wallet."""
        assert self.kr.needs_rotation("unknown") is False

    def test_record_rotation(self):
        """Test functionality: record rotation."""
        self.kr.register_wallet("u1", "0xold")
        self.kr.record_signature("u1")
        rec = self.kr.record_rotation("u1", "0xold", "0xnew", reason="manual")
        assert rec.user_id == "u1"
        assert rec.old_wallet_id == "0xold"
        assert rec.new_wallet_id == "0xnew"
        assert rec.reason == "manual"
        # Counter should be reset
        assert self.kr._signature_counts["u1"] == 0

    def test_get_rotation_history(self):
        """Test functionality: get rotation history."""
        self.kr.register_wallet("u1", "0xold")
        self.kr.record_rotation("u1", "0xold", "0xnew")
        history = self.kr.get_rotation_history("u1")
        assert len(history) == 1

    def test_get_rotation_history_no_user_raises(self):
        """Test functionality: get rotation history no user raises."""
        with pytest.raises(WalletNotFoundError):
            self.kr.get_rotation_history("unknown")

    def test_post_rotate_hook(self):
        """Test functionality: post rotate hook."""
        hook_calls = []
        self.kr.add_post_rotate_hook(lambda rec: hook_calls.append(rec))
        self.kr.register_wallet("u1", "0xold")
        self.kr.record_rotation("u1", "0xold", "0xnew")
        assert len(hook_calls) == 1

    def test_post_rotate_hook_error_caught(self):
        """Test functionality: post rotate hook error caught."""
        self.kr.add_post_rotate_hook(lambda rec: 1 / 0)
        self.kr.register_wallet("u1", "0xold")
        # Should not raise
        self.kr.record_rotation("u1", "0xold", "0xnew")


@pytest.mark.unit
class TestWalletManager:
    """Tests for the WalletManager class (requires KeyManager)."""

    def setup_method(self):
        from codomyrmex.wallet.core import WalletManager
        self.mgr = WalletManager()

    def test_create_wallet(self):
        """Test functionality: create wallet."""
        addr = self.mgr.create_wallet("u1")
        assert addr.startswith("0x")
        assert self.mgr.has_wallet("u1")

    def test_create_duplicate_raises(self):
        """Test functionality: create duplicate raises."""
        self.mgr.create_wallet("u1")
        with pytest.raises(WalletError, match="already has a wallet"):
            self.mgr.create_wallet("u1")

    def test_get_wallet_address(self):
        """Test functionality: get wallet address."""
        addr = self.mgr.create_wallet("u1")
        assert self.mgr.get_wallet_address("u1") == addr

    def test_get_wallet_address_nonexistent(self):
        """Test functionality: get wallet address nonexistent."""
        assert self.mgr.get_wallet_address("fake") is None

    def test_sign_and_verify(self):
        """Test functionality: sign and verify."""
        self.mgr.create_wallet("u1")
        msg = b"hello world"
        sig = self.mgr.sign_message("u1", msg)
        assert isinstance(sig, bytes)
        assert self.mgr.verify_signature("u1", msg, sig) is True

    def test_verify_wrong_signature(self):
        """Test functionality: verify wrong signature."""
        self.mgr.create_wallet("u1")
        msg = b"hello world"
        assert self.mgr.verify_signature("u1", msg, b"bad_sig") is False

    def test_sign_no_wallet_raises(self):
        """Test functionality: sign no wallet raises."""
        with pytest.raises(WalletNotFoundError):
            self.mgr.sign_message("fake", b"msg")

    def test_rotate_keys(self):
        """Test functionality: rotate keys."""
        old_addr = self.mgr.create_wallet("u1")
        new_addr = self.mgr.rotate_keys("u1")
        assert new_addr != old_addr
        assert self.mgr.get_wallet_address("u1") == new_addr

    def test_delete_wallet(self):
        """Test functionality: delete wallet."""
        self.mgr.create_wallet("u1")
        assert self.mgr.delete_wallet("u1") is True
        assert not self.mgr.has_wallet("u1")

    def test_delete_nonexistent_raises(self):
        """Test functionality: delete nonexistent raises."""
        with pytest.raises(WalletNotFoundError):
            self.mgr.delete_wallet("fake")

    def test_list_wallets(self):
        """Test functionality: list wallets."""
        self.mgr.create_wallet("u1")
        self.mgr.create_wallet("u2")
        wallets = self.mgr.list_wallets()
        assert len(wallets) == 2
        assert "u1" in wallets
        assert "u2" in wallets

    def test_backup_wallet(self):
        """Test functionality: backup wallet."""
        self.mgr.create_wallet("u1")
        backup = self.mgr.backup_wallet("u1")
        assert backup["user_id"] == "u1"
        assert "key_hash" in backup
        assert "wallet_id" in backup
