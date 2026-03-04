"""Comprehensive tests for the wallet module."""

import hashlib
import tempfile
from pathlib import Path

import pytest

from codomyrmex.wallet import (
    BackupManager,
    KeyRotation,
    NaturalRitualRecovery,
    RitualError,
    RitualStep,
    RotationPolicy,
    RotationRecord,
    WalletError,
    WalletKeyError,
    WalletManager,
    WalletNotFoundError,
    create_wallet,
    get_wallet_manager,
    hash_response,
)
from codomyrmex.wallet.wallet import Wallet

# ---------------------------------------------------------------------------
# WalletManager Tests
# ---------------------------------------------------------------------------


class TestWalletManager:
    """Tests for WalletManager core operations."""

    def test_create_wallet(self):
        """Verify create wallet behavior."""
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")
        assert address.startswith("0x")
        assert len(address) > 10

    def test_get_wallet_address(self):
        """Verify get wallet address behavior."""
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")
        assert wallet_mgr.get_wallet_address("u1") == address
        assert wallet_mgr.get_wallet_address("nonexistent") is None

    def test_has_wallet(self):
        """Verify has wallet behavior."""
        wallet_mgr = WalletManager()
        assert not wallet_mgr.has_wallet("u1")
        wallet_mgr.create_wallet("u1")
        assert wallet_mgr.has_wallet("u1")

    def test_create_wallet_duplicate_raises(self):
        """Verify create wallet duplicate raises behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        with pytest.raises(WalletError, match="already has a wallet"):
            wallet_mgr.create_wallet("u1")

    def test_sign_message(self):
        """Verify sign message behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        sig = wallet_mgr.sign_message("u1", b"message")
        assert isinstance(sig, bytes)
        assert len(sig) == 32  # HMAC-SHA256 produces 32 bytes

    def test_sign_message_no_wallet_raises(self):
        """Verify sign message no wallet raises behavior."""
        wallet_mgr = WalletManager()
        with pytest.raises(WalletNotFoundError):
            wallet_mgr.sign_message("u2", b"message")

    def test_sign_message_deterministic(self):
        """Verify sign message deterministic behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        sig1 = wallet_mgr.sign_message("u1", b"same message")
        sig2 = wallet_mgr.sign_message("u1", b"same message")
        assert sig1 == sig2

    def test_sign_message_different_messages(self):
        """Verify sign message different messages behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        sig1 = wallet_mgr.sign_message("u1", b"message A")
        sig2 = wallet_mgr.sign_message("u1", b"message B")
        assert sig1 != sig2

    def test_verify_signature(self):
        """Verify verify signature behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        msg = b"test message"
        sig = wallet_mgr.sign_message("u1", msg)
        assert wallet_mgr.verify_signature("u1", msg, sig)

    def test_verify_signature_invalid(self):
        """Verify verify signature invalid behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        msg = b"test message"
        sig = wallet_mgr.sign_message("u1", msg)
        assert not wallet_mgr.verify_signature("u1", b"different message", sig)

    def test_verify_signature_wrong_bytes(self):
        """Verify verify signature wrong bytes behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        assert not wallet_mgr.verify_signature("u1", b"msg", b"invalid_sig")

    def test_rotate_keys(self):
        """Verify rotate keys behavior."""
        wallet_mgr = WalletManager()
        old_address = wallet_mgr.create_wallet("u1")
        new_address = wallet_mgr.rotate_keys("u1")
        assert new_address.startswith("0x")
        assert new_address != old_address
        assert wallet_mgr.get_wallet_address("u1") == new_address

    def test_rotate_keys_changes_signatures(self):
        """Verify rotate keys changes signatures behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        sig_before = wallet_mgr.sign_message("u1", b"test")
        wallet_mgr.rotate_keys("u1")
        sig_after = wallet_mgr.sign_message("u1", b"test")
        assert sig_before != sig_after

    def test_rotate_keys_no_wallet_raises(self):
        """Verify rotate keys no wallet raises behavior."""
        wallet_mgr = WalletManager()
        with pytest.raises(WalletNotFoundError):
            wallet_mgr.rotate_keys("u2")

    def test_backup_wallet(self):
        """Verify backup wallet behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        backup = wallet_mgr.backup_wallet("u1")
        assert backup["user_id"] == "u1"
        assert backup["wallet_id"].startswith("0x")
        assert backup["key_hash"] is not None
        assert backup["backup_ts"] is not None
        assert backup["created_at"] is not None

    def test_backup_wallet_no_wallet_raises(self):
        """Verify backup wallet no wallet raises behavior."""
        wallet_mgr = WalletManager()
        with pytest.raises(WalletNotFoundError):
            wallet_mgr.backup_wallet("u2")

    def test_delete_wallet(self):
        """Verify delete wallet behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        assert wallet_mgr.has_wallet("u1")
        result = wallet_mgr.delete_wallet("u1")
        assert result is True
        assert not wallet_mgr.has_wallet("u1")
        assert wallet_mgr.get_wallet_address("u1") is None

    def test_delete_wallet_no_wallet_raises(self):
        """Verify delete wallet no wallet raises behavior."""
        wallet_mgr = WalletManager()
        with pytest.raises(WalletNotFoundError):
            wallet_mgr.delete_wallet("u2")

    def test_list_wallets(self):
        """Verify list wallets behavior."""
        wallet_mgr = WalletManager()
        assert wallet_mgr.list_wallets() == {}
        addr1 = wallet_mgr.create_wallet("u1")
        addr2 = wallet_mgr.create_wallet("u2")
        wallets = wallet_mgr.list_wallets()
        assert wallets == {"u1": addr1, "u2": addr2}

    def test_list_wallets_is_copy(self):
        """Verify list wallets is copy behavior."""
        wallet_mgr = WalletManager()
        wallet_mgr.create_wallet("u1")
        wallets = wallet_mgr.list_wallets()
        wallets["u1"] = "tampered"
        assert wallet_mgr.get_wallet_address("u1") != "tampered"

    def test_custom_storage_path(self):
        """Verify custom storage path behavior."""
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
        """Verify register and recover success behavior."""
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert recovery.initiate_recovery("u1", ["Red", "Cat"])

    def test_recovery_failure_wrong_answer(self):
        """Verify recovery failure wrong answer behavior."""
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert not recovery.initiate_recovery("u1", ["Blue", "Cat"])
        assert not recovery.initiate_recovery("u1", ["Red", "Dog"])

    def test_recovery_failure_wrong_count(self):
        """Verify recovery failure wrong count behavior."""
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert not recovery.initiate_recovery("u1", ["Red"])
        assert not recovery.initiate_recovery("u1", ["Red", "Cat", "Extra"])

    def test_recovery_invalid_user(self):
        """Verify recovery invalid user behavior."""
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert not recovery.initiate_recovery("u2", ["Red", "Cat"])

    def test_has_ritual(self):
        """Verify has ritual behavior."""
        recovery = NaturalRitualRecovery()
        assert not recovery.has_ritual("u1")
        recovery.register_ritual("u1", self._make_steps())
        assert recovery.has_ritual("u1")

    def test_get_prompts(self):
        """Verify get prompts behavior."""
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        prompts = recovery.get_prompts("u1")
        assert prompts == ["Color?", "Animal?"]

    def test_get_prompts_no_ritual_raises(self):
        """Verify get prompts no ritual raises behavior."""
        recovery = NaturalRitualRecovery()
        with pytest.raises(RitualError):
            recovery.get_prompts("u1")

    def test_register_empty_steps_raises(self):
        """Verify register empty steps raises behavior."""
        recovery = NaturalRitualRecovery()
        with pytest.raises(RitualError, match="at least one step"):
            recovery.register_ritual("u1", [])

    def test_attempt_tracking(self):
        """Verify attempt tracking behavior."""
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert recovery.get_remaining_attempts("u1") == 5
        recovery.initiate_recovery("u1", ["Wrong", "Wrong"])
        assert recovery.get_remaining_attempts("u1") == 4

    def test_lockout_after_max_attempts(self):
        """Verify lockout after max attempts behavior."""
        recovery = NaturalRitualRecovery()
        recovery.max_attempts = 2
        recovery.register_ritual("u1", self._make_steps())
        recovery.initiate_recovery("u1", ["Wrong", "Wrong"])
        recovery.initiate_recovery("u1", ["Wrong", "Wrong"])
        assert recovery.is_locked("u1")
        with pytest.raises(RitualError, match="locked out"):
            recovery.initiate_recovery("u1", ["Red", "Cat"])

    def test_reset_attempts(self):
        """Verify reset attempts behavior."""
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
        """Verify success resets attempts behavior."""
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        recovery.initiate_recovery("u1", ["Wrong", "Wrong"])
        assert recovery.get_remaining_attempts("u1") == 4
        recovery.initiate_recovery("u1", ["Red", "Cat"])
        assert recovery.get_remaining_attempts("u1") == 5

    def test_max_attempts_property(self):
        """Verify max attempts property behavior."""
        recovery = NaturalRitualRecovery()
        assert recovery.max_attempts == 5
        recovery.max_attempts = 10
        assert recovery.max_attempts == 10

    def test_max_attempts_invalid_raises(self):
        """Verify max attempts invalid raises behavior."""
        recovery = NaturalRitualRecovery()
        with pytest.raises(ValueError):
            recovery.max_attempts = 0

    def test_unregister_ritual(self):
        """Verify unregister ritual behavior."""
        recovery = NaturalRitualRecovery()
        recovery.register_ritual("u1", self._make_steps())
        assert recovery.has_ritual("u1")
        assert recovery.unregister_ritual("u1")
        assert not recovery.has_ritual("u1")

    def test_unregister_ritual_nonexistent(self):
        """Verify unregister ritual nonexistent behavior."""
        recovery = NaturalRitualRecovery()
        assert not recovery.unregister_ritual("u1")


# ---------------------------------------------------------------------------
# hash_response Tests
# ---------------------------------------------------------------------------


class TestHashResponse:
    """Tests for the hash_response convenience function."""

    def test_returns_sha256(self):
        """Verify returns sha256 behavior."""
        result = hash_response("test")
        expected = hashlib.sha256(b"test").hexdigest()
        assert result == expected

    def test_deterministic(self):
        """Verify deterministic behavior."""
        assert hash_response("hello") == hash_response("hello")

    def test_different_inputs(self):
        """Verify different inputs behavior."""
        assert hash_response("a") != hash_response("b")

    def test_case_sensitive(self):
        """Verify case sensitive behavior."""
        assert hash_response("Red") != hash_response("red")


# ---------------------------------------------------------------------------
# BackupManager Tests
# ---------------------------------------------------------------------------


class TestBackupManager:
    """Tests for BackupManager."""

    def test_create_and_list_backup(self):
        """Verify create and list backup behavior."""
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
        """Verify create backup no key raises behavior."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from codomyrmex.encryption.keys.key_manager import KeyManager

            isolated_km = KeyManager(key_dir=Path(tmpdir) / "keys")
            backup_mgr = BackupManager(
                backup_dir=Path(tmpdir) / "backups", key_manager=isolated_km
            )
            with pytest.raises(WalletNotFoundError):
                backup_mgr.create_backup("nonexistent_user", "0xfake")

    def test_verify_backup_valid(self):
        """Verify verify backup valid behavior."""
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(
                backup_dir=Path(tmpdir), key_manager=wallet_mgr.key_manager
            )
            record = backup_mgr.create_backup("u1", address)
            assert backup_mgr.verify_backup("u1", record["backup_id"])

    def test_verify_backup_stale_after_rotation(self):
        """Verify verify backup stale after rotation behavior."""
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
        """Verify verify backup not found raises behavior."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(backup_dir=Path(tmpdir))
            with pytest.raises(WalletNotFoundError):
                backup_mgr.verify_backup("u1", "nonexistent")

    def test_delete_backup(self):
        """Verify delete backup behavior."""
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
        """Verify delete backup nonexistent behavior."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(backup_dir=Path(tmpdir))
            assert not backup_mgr.delete_backup("u1", "nonexistent")

    def test_list_backups_empty(self):
        """Verify list backups empty behavior."""
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(backup_dir=Path(tmpdir))
            assert backup_mgr.list_backups("u1") == []

    def test_multiple_backups_sorted(self):
        """Verify multiple backups sorted behavior."""
        wallet_mgr = WalletManager()
        address = wallet_mgr.create_wallet("u1")

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_mgr = BackupManager(
                backup_dir=Path(tmpdir), key_manager=wallet_mgr.key_manager
            )
            backup_mgr.create_backup("u1", address)
            backup_mgr.create_backup("u1", address, metadata={"seq": 2})
            backups = backup_mgr.list_backups("u1")
            assert len(backups) == 2
            # Newest first
            assert backups[0]["timestamp"] >= backups[1]["timestamp"]

    def test_backup_with_metadata(self):
        """Verify backup with metadata behavior."""
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
        """Verify register and needs rotation false behavior."""
        rotation = KeyRotation()
        rotation.register_wallet("u1", "0xabc")
        assert not rotation.needs_rotation("u1")

    def test_needs_rotation_by_signatures(self):
        """Verify needs rotation by signatures behavior."""
        policy = RotationPolicy(max_signatures=3)
        rotation = KeyRotation(policy=policy)
        rotation.register_wallet("u1", "0xabc")
        for _ in range(3):
            rotation.record_signature("u1")
        assert rotation.needs_rotation("u1")

    def test_record_rotation(self):
        """Verify record rotation behavior."""
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
        """Verify rotation resets counters behavior."""
        policy = RotationPolicy(max_signatures=3)
        rotation = KeyRotation(policy=policy)
        rotation.register_wallet("u1", "0xold")
        for _ in range(3):
            rotation.record_signature("u1")
        assert rotation.needs_rotation("u1")
        rotation.record_rotation("u1", "0xold", "0xnew")
        assert not rotation.needs_rotation("u1")

    def test_get_rotation_history(self):
        """Verify get rotation history behavior."""
        rotation = KeyRotation()
        rotation.register_wallet("u1", "0xold")
        rotation.record_rotation("u1", "0xold", "0xnew1")
        rotation.record_rotation("u1", "0xnew1", "0xnew2")
        history = rotation.get_rotation_history("u1")
        assert len(history) == 2

    def test_get_rotation_history_no_user_raises(self):
        """Verify get rotation history no user raises behavior."""
        rotation = KeyRotation()
        with pytest.raises(WalletNotFoundError):
            rotation.get_rotation_history("nonexistent")

    def test_post_rotate_hook(self):
        """Verify post rotate hook behavior."""
        rotation = KeyRotation()
        rotation.register_wallet("u1", "0xold")
        hook_calls = []
        rotation.add_post_rotate_hook(lambda record: hook_calls.append(record))
        rotation.record_rotation("u1", "0xold", "0xnew")
        assert len(hook_calls) == 1
        assert hook_calls[0].new_wallet_id == "0xnew"

    def test_rotation_policy_defaults(self):
        """Verify rotation policy defaults behavior."""
        policy = RotationPolicy()
        assert policy.max_age_days == 90
        assert policy.max_signatures == 10000
        assert policy.auto_rotate is False

    def test_rotation_policy_custom(self):
        """Verify rotation policy custom behavior."""
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
        """Verify create and properties behavior."""
        w = Wallet("u1")
        assert not w.is_active
        assert w.address is None
        address = w.create()
        assert w.is_active
        assert w.address == address
        assert address.startswith("0x")

    def test_sign_and_verify(self):
        """Verify sign and verify behavior."""
        w = Wallet("u1")
        w.create()
        sig = w.sign(b"hello")
        assert w.verify(b"hello", sig)
        assert not w.verify(b"world", sig)

    def test_rotate(self):
        """Verify rotate behavior."""
        w = Wallet("u1")
        old = w.create()
        new = w.rotate(reason="test")
        assert new != old
        assert w.address == new

    def test_setup_recovery_and_recover(self):
        """Verify setup recovery and recover behavior."""
        w = Wallet("u1")
        w.create()
        w.setup_recovery(
            [
                RitualStep("Q?", hash_response("A")),
            ]
        )
        assert w.recover(["A"])
        assert not w.recover(["B"])

    def test_backup(self):
        """Verify backup behavior."""
        w = Wallet("u1")
        w.create()
        backup = w.backup()
        assert backup["user_id"] == "u1"
        assert "key_hash" in backup

    def test_delete(self):
        """Verify delete behavior."""
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
        """Verify create wallet function behavior."""
        address = create_wallet("conv_user")
        assert address.startswith("0x")

    def test_get_wallet_manager_function(self):
        """Verify get wallet manager function behavior."""
        mgr = get_wallet_manager()
        assert isinstance(mgr, WalletManager)

    def test_get_wallet_manager_with_path(self):
        """Verify get wallet manager with path behavior."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mgr = get_wallet_manager(storage_path=Path(tmpdir))
            assert isinstance(mgr, WalletManager)


# ---------------------------------------------------------------------------
# Exception Hierarchy Tests
# ---------------------------------------------------------------------------


class TestExceptions:
    """Tests for the exception hierarchy."""

    def test_wallet_error_is_base(self):
        """Verify wallet error is base behavior."""
        with pytest.raises(WalletError):
            raise WalletNotFoundError("test")

    def test_wallet_key_error_inherits(self):
        """Verify wallet key error inherits behavior."""
        with pytest.raises(WalletError):
            raise WalletKeyError("test")

    def test_ritual_error_inherits(self):
        """Verify ritual error inherits behavior."""
        with pytest.raises(WalletError):
            raise RitualError("test")

    def test_exception_messages(self):
        """Verify exception messages behavior."""
        e = WalletNotFoundError("user xyz not found")
        assert "xyz" in str(e)


# ---------------------------------------------------------------------------
# Module Metadata Tests
# ---------------------------------------------------------------------------


class TestModuleMetadata:
    """Tests for module-level attributes."""

    def test_version(self):
        """Verify version behavior."""
        import codomyrmex.wallet as wallet_module

        assert wallet_module.__version__ == "0.1.0"

    def test_all_exports(self):
        """Verify all exports behavior."""
        import codomyrmex.wallet as wallet_module

        assert "WalletManager" in wallet_module.__all__
        assert "NaturalRitualRecovery" in wallet_module.__all__
        assert "BackupManager" in wallet_module.__all__
        assert "KeyRotation" in wallet_module.__all__
        assert "WalletError" in wallet_module.__all__
        assert "hash_response" in wallet_module.__all__
        assert "create_wallet" in wallet_module.__all__
        assert "get_wallet_manager" in wallet_module.__all__
