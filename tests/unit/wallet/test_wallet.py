"""Comprehensive tests for the wallet module."""

import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from codomyrmex.wallet import (
    BackupManager,
    KeyRotation,
    NaturalRitualRecovery,
    RitualStep,
    RotationPolicy,
    RotationRecord,
    WalletError,
    WalletKeyError,
    WalletManager,
    WalletNotFoundError,
    RitualError,
    hash_response,
    create_wallet,
    get_wallet_manager,
)
from codomyrmex.wallet.wallet import Wallet


# ---------------------------------------------------------------------------
# WalletManager Tests
# ---------------------------------------------------------------------------


class TestWalletManager:
    """Tests for WalletManager core operations."""

    def test_create_wallet(self):
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")
        assert address.startswith("0x")
        assert len(address) > 10

    def test_get_wallet_address(self):
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")
        assert wallet_mgr.get_wallet_address("u1") == address
        assert wallet_mgr.get_wallet_address("nonexistent") is None

    def test_has_wallet(self):
        wallet_mgr = WalletManager()
        assert not wallet_mgr.has_wallet("u1")
        wallet_mgr.create_wallet("u1")
        assert wallet_mgr.has_wallet("u1")

    def test_create_wallet_duplicate_raises(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        with pytest.raises(WalletError, match="already has a wallet"):
            wallet_mgr.create_wallet("u1")

    def test_sign_message(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        sig = wallet_mgr.sign_message("u1", b"message")
        assert isinstance(sig, bytes)
        assert len(sig) == 32  # HMAC-SHA256 produces 32 bytes

    def test_sign_message_no_wallet_raises(self):
        wallet_mgr = WalletManager()
        with pytest.raises(WalletNotFoundError):
            wallet_mgr.sign_message("u2", b"message")

    def test_sign_message_deterministic(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        sig1 = wallet_mgr.sign_message("u1", b"same message")
        sig2 = wallet_mgr.sign_message("u1", b"same message")
        assert sig1 == sig2

    def test_sign_message_different_messages(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        sig1 = wallet_mgr.sign_message("u1", b"message A")
        sig2 = wallet_mgr.sign_message("u1", b"message B")
        assert sig1 != sig2

    def test_verify_signature(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        msg = b"test message"
        sig = wallet_mgr.sign_message("u1", msg)
        assert wallet_mgr.verify_signature("u1", msg, sig)

    def test_verify_signature_invalid(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        msg = b"test message"
        sig = wallet_mgr.sign_message("u1", msg)
        assert not wallet_mgr.verify_signature("u1", b"different message", sig)

    def test_verify_signature_wrong_bytes(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        assert not wallet_mgr.verify_signature("u1", b"msg", b"invalid_sig")

    def test_rotate_keys(self):
        wallet_mgr = WalletManager()
        old_address = wallet_mgr.create_wallet("u1")
        new_address = wallet_mgr.rotate_keys("u1")
        assert new_address.startswith("0x")
        assert new_address != old_address
        assert wallet_mgr.get_wallet_address("u1") == new_address

    def test_rotate_keys_changes_signatures(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        sig_before = wallet_mgr.sign_message("u1", b"test")
        wallet_mgr.rotate_keys("u1")
        sig_after = wallet_mgr.sign_message("u1", b"test")
        assert sig_before != sig_after

    def test_rotate_keys_no_wallet_raises(self):
        wallet_mgr = WalletManager()
        with pytest.raises(WalletNotFoundError):
            wallet_mgr.rotate_keys("u2")

    def test_backup_wallet(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        backup = wallet_mgr.backup_wallet("u1")
        assert backup["user_id"] == "u1"
        assert backup["wallet_id"].startswith("0x")
        assert backup["key_hash"] is not None
        assert backup["backup_ts"] is not None
        assert backup["created_at"] is not None

    def test_backup_wallet_no_wallet_raises(self):
        wallet_mgr = WalletManager()
        with pytest.raises(WalletNotFoundError):
            wallet_mgr.backup_wallet("u2")

    def test_delete_wallet(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        assert wallet_mgr.has_wallet("u1")
        result = wallet_mgr.delete_wallet("u1")
        assert result is True
        assert not wallet_mgr.has_wallet("u1")
        assert wallet_mgr.get_wallet_address("u1") is None

    def test_delete_wallet_no_wallet_raises(self):
        wallet_mgr = WalletManager()
        with pytest.raises(WalletNotFoundError):
            wallet_mgr.delete_wallet("u2")

    def test_list_wallets(self):
        wallet_mgr = WalletManager()
        assert wallet_mgr.list_wallets() == {}
        addr1 = wallet_mgr.create_wallet("u1")
        addr2 = wallet_mgr.create_wallet("u2")
        wallets = wallet_mgr.list_wallets()
        assert wallets == {"u1": addr1, "u2": addr2}

    def test_list_wallets_is_copy(self):
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        wallets = wallet_mgr.list_wallets()
        wallets["u1"] = "tampered"
        assert wallet_mgr.get_wallet_address("u1") != "tampered"

    def test_custom_storage_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            wallet_mgr = WalletManager(storage_path=Path(tmpdir))
            address = wallet_mgr.create_wallet("u1")
            assert address.startswith("0x")
            sig = wallet_mgr.sign_message("u1", b"test")
            assert len(sig) == 32


# ---------------------------------------------------------------------------
# NaturalRitualRecovery Tests
# ---------------------------------------------------------------------------


class TestNaturalRitualRecovery:
    """Tests for the NaturalRitualRecovery system."""

    def _make_steps(self):
        return [
            RitualStep("Color?", hashlib.sha256(b"Red").hexdigest()),
            RitualStep("Animal?", hashlib.sha256(b"Cat").hexdigest()),
        ]

    def test_register_and_recover_success(self):
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert recovery.initiate_recovery("u1", ["Red", "Cat"])

    def test_recovery_failure_wrong_answer(self):
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert not recovery.initiate_recovery("u1", ["Blue", "Cat"])
        assert not recovery.initiate_recovery("u1", ["Red", "Dog"])

    def test_recovery_failure_wrong_count(self):
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert not recovery.initiate_recovery("u1", ["Red"])
        assert not recovery.initiate_recovery("u1", ["Red", "Cat", "Extra"])

    def test_recovery_invalid_user(self):
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert not recovery.initiate_recovery("u2", ["Red", "Cat"])

    def test_has_ritual(self):
        recovery = NaturalRitualRecovery()
        assert not recovery.has_ritual("u1")
        recovery.register_ritual("u1", self._make_steps())
        assert recovery.has_ritual("u1")

    def test_get_prompts(self):
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        prompts = recovery.get_prompts("u1")
        assert prompts == ["Color?", "Animal?"]

    def test_get_prompts_no_ritual_raises(self):
        recovery = NaturalRitualRecovery()
        with pytest.raises(RitualError):
            recovery.get_prompts("u1")

    def test_register_empty_steps_raises(self):
        recovery = NaturalRitualRecovery()
        with pytest.raises(RitualError, match="at least one step"):
            recovery.register_ritual("u1", [])

    def test_attempt_tracking(self):
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert recovery.get_remaining_attempts("u1") == 5
        recovery.initiate_recovery("u1", ["Wrong", "Wrong"])
        assert recovery.get_remaining_attempts("u1") == 4

    def test_lockout_after_max_attempts(self):
        recovery = NaturalRitualRecovery()
        recovery.max_attempts = 2
        recovery.register_ritual("u1", self._make_steps())
        recovery.initiate_recovery("u1", ["Wrong", "Wrong"])
        recovery.initiate_recovery("u1", ["Wrong", "Wrong"])
        assert recovery.is_locked("u1")
        with pytest.raises(RitualError, match="locked out"):
            recovery.initiate_recovery("u1", ["Red", "Cat"])

    def test_reset_attempts(self):
        recovery = NaturalRitualRecovery()
        recovery.max_attempts = 2
        recovery.register_ritual("u1", self._make_steps())
        recovery.initiate_recovery("u1", ["Wrong", "Wrong"])
        recovery.initiate_recovery("u1", ["Wrong", "Wrong"])
        assert recovery.is_locked("u1")
        recovery.reset_attempts("u1")
        assert not recovery.is_locked("u1")
        assert recovery.get_remaining_attempts("u1") == 2

    def test_success_resets_attempts(self):
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        recovery.initiate_recovery("u1", ["Wrong", "Wrong"])
        assert recovery.get_remaining_attempts("u1") == 4
        recovery.initiate_recovery("u1", ["Red", "Cat"])
        assert recovery.get_remaining_attempts("u1") == 5

    def test_max_attempts_property(self):
        recovery = NaturalRitualRecovery()
        assert recovery.max_attempts == 5
        recovery.max_attempts = 10
        assert recovery.max_attempts == 10

    def test_max_attempts_invalid_raises(self):
        recovery = NaturalRitualRecovery()
        with pytest.raises(ValueError):
            recovery.max_attempts = 0

    def test_unregister_ritual(self):
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert recovery.has_ritual("u1")
        assert recovery.unregister_ritual("u1")
        assert not recovery.has_ritual("u1")

    def test_unregister_ritual_nonexistent(self):
        recovery = NaturalRitualRecovery()
        assert not recovery.unregister_ritual("u1")


# ---------------------------------------------------------------------------
# hash_response Tests
# ---------------------------------------------------------------------------


class TestHashResponse:
    """Tests for the hash_response convenience function."""

    def test_returns_sha256(self):
        result = hash_response("test")
        expected = hashlib.sha256(b"test").hexdigest()
        assert result == expected

    def test_deterministic(self):
        assert hash_response("hello") == hash_response("hello")

    def test_different_inputs(self):
        assert hash_response("a") != hash_response("b")

    def test_case_sensitive(self):
        assert hash_response("Red") != hash_response("red")


# ---------------------------------------------------------------------------
# BackupManager Tests
# ---------------------------------------------------------------------------


class TestBackupManager:
    """Tests for BackupManager."""

    def test_create_and_list_backup(self):
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(
                backup_dir=Path(tmpdir), key_manager=wallet_mgr.key_manager
            )
            record = backup_mgr.create_backup("u1", address)
            assert "backup_id" in record
            assert record["user_id"] == "u1"
            assert record["wallet_id"] == address
            assert "key_hash" in record
            assert "timestamp" in record

            backups = backup_mgr.list_backups("u1")
            assert len(backups) == 1
            assert backups[0]["backup_id"] == record["backup_id"]

    def test_create_backup_no_key_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(backup_dir=Path(tmpdir))
            with pytest.raises(WalletNotFoundError):
                backup_mgr.create_backup("u1", "0xfake")

    def test_verify_backup_valid(self):
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(
                backup_dir=Path(tmpdir), key_manager=wallet_mgr.key_manager
            )
            record = backup_mgr.create_backup("u1", address)
            assert backup_mgr.verify_backup("u1", record["backup_id"])

    def test_verify_backup_stale_after_rotation(self):
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(
                backup_dir=Path(tmpdir), key_manager=wallet_mgr.key_manager
            )
            record = backup_mgr.create_backup("u1", address)
            wallet_mgr.rotate_keys("u1")
            assert not backup_mgr.verify_backup("u1", record["backup_id"])

    def test_verify_backup_not_found_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(backup_dir=Path(tmpdir))
            with pytest.raises(WalletNotFoundError):
                backup_mgr.verify_backup("u1", "nonexistent")

    def test_delete_backup(self):
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(
                backup_dir=Path(tmpdir), key_manager=wallet_mgr.key_manager
            )
            record = backup_mgr.create_backup("u1", address)
            assert backup_mgr.delete_backup("u1", record["backup_id"])
            assert len(backup_mgr.list_backups("u1")) == 0

    def test_delete_backup_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(backup_dir=Path(tmpdir))
            assert not backup_mgr.delete_backup("u1", "nonexistent")

    def test_list_backups_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(backup_dir=Path(tmpdir))
            assert backup_mgr.list_backups("u1") == []

    def test_multiple_backups_sorted(self):
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(
                backup_dir=Path(tmpdir), key_manager=wallet_mgr.key_manager
            )
            r1 = backup_mgr.create_backup("u1", address)
            r2 = backup_mgr.create_backup("u1", address, metadata={"seq": 2})
            backups = backup_mgr.list_backups("u1")
            assert len(backups) == 2
            # Newest first
            assert backups[0]["timestamp"] >= backups[1]["timestamp"]

    def test_backup_with_metadata(self):
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(
                backup_dir=Path(tmpdir), key_manager=wallet_mgr.key_manager
            )
            record = backup_mgr.create_backup(
                "u1", address, metadata={"reason": "pre-rotation"}
            )
            assert record["metadata"]["reason"] == "pre-rotation"


# ---------------------------------------------------------------------------
# KeyRotation Tests
# ---------------------------------------------------------------------------


class TestKeyRotation:
    """Tests for KeyRotation."""

    def test_register_and_needs_rotation_false(self):
        rotation = KeyRotation()
        rotation.register_wallet("u1", "0xabc")
        assert not rotation.needs_rotation("u1")

    def test_needs_rotation_by_signatures(self):
        policy = RotationPolicy(max_signatures=3)
        rotation = KeyRotation(policy=policy)
        rotation.register_wallet("u1", "0xabc")
        for _ in range(3):
            rotation.record_signature("u1")
        assert rotation.needs_rotation("u1")

    def test_record_rotation(self):
        rotation = KeyRotation()
        rotation.register_wallet("u1", "0xold")
        record = rotation.record_rotation("u1", "0xold", "0xnew", "test")
        assert isinstance(record, RotationRecord)
        assert record.user_id == "u1"
        assert record.old_wallet_id == "0xold"
        assert record.new_wallet_id == "0xnew"
        assert record.reason == "test"
        assert record.timestamp is not None

    def test_rotation_resets_counters(self):
        policy = RotationPolicy(max_signatures=3)
        rotation = KeyRotation(policy=policy)
        rotation.register_wallet("u1", "0xold")
        for _ in range(3):
            rotation.record_signature("u1")
        assert rotation.needs_rotation("u1")
        rotation.record_rotation("u1", "0xold", "0xnew")
        assert not rotation.needs_rotation("u1")

    def test_get_rotation_history(self):
        rotation = KeyRotation()
        rotation.register_wallet("u1", "0xold")
        rotation.record_rotation("u1", "0xold", "0xnew1")
        rotation.record_rotation("u1", "0xnew1", "0xnew2")
        history = rotation.get_rotation_history("u1")
        assert len(history) == 2

    def test_get_rotation_history_no_user_raises(self):
        rotation = KeyRotation()
        with pytest.raises(WalletNotFoundError):
            rotation.get_rotation_history("nonexistent")

    def test_post_rotate_hook(self):
        rotation = KeyRotation()
        rotation.register_wallet("u1", "0xold")
        hook_calls = []
        rotation.add_post_rotate_hook(lambda record: hook_calls.append(record))
        rotation.record_rotation("u1", "0xold", "0xnew")
        assert len(hook_calls) == 1
        assert hook_calls[0].new_wallet_id == "0xnew"

    def test_rotation_policy_defaults(self):
        policy = RotationPolicy()
        assert policy.max_age_days == 90
        assert policy.max_signatures == 10000
        assert policy.auto_rotate is False

    def test_rotation_policy_custom(self):
        policy = RotationPolicy(max_age_days=7, max_signatures=100, auto_rotate=True)
        assert policy.max_age_days == 7
        assert policy.max_signatures == 100
        assert policy.auto_rotate is True


# ---------------------------------------------------------------------------
# Wallet Facade Tests
# ---------------------------------------------------------------------------


class TestWalletFacade:
    """Tests for the Wallet facade class."""

    def test_create_and_properties(self):
        w = Wallet("u1")
        assert not w.is_active
        assert w.address is None
        address = w.create()
        assert w.is_active
        assert w.address == address
        assert address.startswith("0x")

    def test_sign_and_verify(self):
        w = Wallet("u1")
        w.create()
        sig = w.sign(b"hello")
        assert w.verify(b"hello", sig)
        assert not w.verify(b"world", sig)

    def test_rotate(self):
        w = Wallet("u1")
        old = w.create()
        new = w.rotate(reason="test")
        assert new != old
        assert w.address == new

    def test_setup_recovery_and_recover(self):
        w = Wallet("u1")
        w.create()
        w.setup_recovery([
            RitualStep("Q?", hash_response("A")),
        ])
        assert w.recover(["A"])
        assert not w.recover(["B"])

    def test_backup(self):
        w = Wallet("u1")
        w.create()
        backup = w.backup()
        assert backup["user_id"] == "u1"
        assert "key_hash" in backup

    def test_delete(self):
        w = Wallet("u1")
        w.create()
        assert w.is_active
        result = w.delete()
        assert result is True
        assert not w.is_active
        assert w.address is None


# ---------------------------------------------------------------------------
# Convenience Function Tests
# ---------------------------------------------------------------------------


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_create_wallet_function(self):
        address = create_wallet("conv_user")
        assert address.startswith("0x")

    def test_get_wallet_manager_function(self):
        mgr = get_wallet_manager()
        assert isinstance(mgr, WalletManager)

    def test_get_wallet_manager_with_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = get_wallet_manager(storage_path=Path(tmpdir))
            assert isinstance(mgr, WalletManager)


# ---------------------------------------------------------------------------
# Exception Hierarchy Tests
# ---------------------------------------------------------------------------


class TestExceptions:
    """Tests for the exception hierarchy."""

    def test_wallet_error_is_base(self):
        with pytest.raises(WalletError):
            raise WalletNotFoundError("test")

    def test_wallet_key_error_inherits(self):
        with pytest.raises(WalletError):
            raise WalletKeyError("test")

    def test_ritual_error_inherits(self):
        with pytest.raises(WalletError):
            raise RitualError("test")

    def test_exception_messages(self):
        e = WalletNotFoundError("user xyz not found")
        assert "xyz" in str(e)


# ---------------------------------------------------------------------------
# Module Metadata Tests
# ---------------------------------------------------------------------------


class TestModuleMetadata:
    """Tests for module-level attributes."""

    def test_version(self):
        import codomyrmex.wallet as wallet_module
        assert wallet_module.__version__ == "0.1.0"

    def test_all_exports(self):
        import codomyrmex.wallet as wallet_module
        assert "WalletManager" in wallet_module.__all__
        assert "NaturalRitualRecovery" in wallet_module.__all__
        assert "BackupManager" in wallet_module.__all__
        assert "KeyRotation" in wallet_module.__all__
        assert "WalletError" in wallet_module.__all__
        assert "hash_response" in wallet_module.__all__
        assert "create_wallet" in wallet_module.__all__
        assert "get_wallet_manager" in wallet_module.__all__
