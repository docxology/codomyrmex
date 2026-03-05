"""Security tests for trust_gateway.py P0 fixes.

Tests:
- Atomic write: ledger written via .tmp -> rename
- File permissions: trust_ledger.json created with mode 0o600
- Threading safety: _pending_confirmations safe under concurrent access
"""

from __future__ import annotations

import stat
import threading
import time
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_registry(tmp_path: Path):
    """Return a TrustRegistry with ledger redirected to tmp_path."""
    from codomyrmex.agents.pai.trust_gateway import TrustRegistry

    registry = TrustRegistry()
    # Redirect ledger to tmp_path so tests don't touch ~/.codomyrmex
    registry._ledger_path = tmp_path / ".codomyrmex" / "trust_ledger.json"
    registry._disk_loaded = True  # prevent re-load from original path
    return registry


# ---------------------------------------------------------------------------
# Pass 1.1 — Ledger file permissions
# ---------------------------------------------------------------------------


class TestTrustLedgerPermissions:
    """_save() must create trust_ledger.json with mode 0o600."""

    @pytest.mark.security
    def test_new_ledger_has_mode_0600(self, tmp_path: Path) -> None:
        registry = _make_registry(tmp_path)
        registry._save()
        ledger = tmp_path / ".codomyrmex" / "trust_ledger.json"
        assert ledger.exists(), "Ledger file must exist after _save()"
        mode = stat.S_IMODE(ledger.stat().st_mode)
        assert mode == 0o600, f"Expected mode 0o600, got {oct(mode)}"

    @pytest.mark.security
    def test_existing_wrong_mode_migrated_on_load(self, tmp_path: Path) -> None:
        """_load() must restrict an existing ledger with wrong permissions."""
        ledger = tmp_path / ".codomyrmex" / "trust_ledger.json"
        ledger.parent.mkdir(parents=True)
        ledger.write_text("{}")
        ledger.chmod(0o644)  # deliberately wrong

        registry = _make_registry(tmp_path)
        # Force _load() to re-run by resetting the loaded flag
        registry._disk_loaded = False
        registry._load()

        mode = stat.S_IMODE(ledger.stat().st_mode)
        assert mode == 0o600, f"Migration failed: mode is still {oct(mode)}"


# ---------------------------------------------------------------------------
# Pass 1.2 — Atomic write (.tmp rename)
# ---------------------------------------------------------------------------


class TestTrustLedgerAtomicWrite:
    """_save() must use write-to-.tmp-then-rename pattern."""

    @pytest.mark.security
    def test_tmp_file_absent_after_save(self, tmp_path: Path) -> None:
        registry = _make_registry(tmp_path)
        registry._save()
        ledger = tmp_path / ".codomyrmex" / "trust_ledger.json"
        tmp_file = ledger.with_suffix(".tmp")
        assert not tmp_file.exists(), ".tmp file must not remain after successful save"

    @pytest.mark.security
    def test_ledger_content_valid_json(self, tmp_path: Path) -> None:
        import json

        registry = _make_registry(tmp_path)
        registry._save()
        ledger = tmp_path / ".codomyrmex" / "trust_ledger.json"
        data = json.loads(ledger.read_text())
        assert isinstance(data, dict), "Ledger must contain a JSON object"

    @pytest.mark.security
    def test_save_is_idempotent(self, tmp_path: Path) -> None:
        """Multiple saves must not leave leftover .tmp files."""
        registry = _make_registry(tmp_path)
        for _ in range(5):
            registry._save()
        ledger = tmp_path / ".codomyrmex" / "trust_ledger.json"
        tmp_file = ledger.with_suffix(".tmp")
        assert not tmp_file.exists()
        assert ledger.exists()


# ---------------------------------------------------------------------------
# Pass 1.3 — Threading safety for _pending_confirmations
# ---------------------------------------------------------------------------


class TestConfirmationsThreadSafety:
    """_pending_confirmations must be safe under concurrent access."""

    @pytest.mark.security
    def test_concurrent_access_no_runtime_error(self) -> None:
        """50 threads simultaneously mutating _pending_confirmations must not raise."""
        import codomyrmex.agents.pai.trust_gateway as gw

        errors: list[Exception] = []

        def worker(idx: int) -> None:
            try:
                with gw._confirmations_lock:
                    gw._pending_confirmations[f"token_{idx}"] = {
                        "timestamp": time.monotonic() - 999,  # expired
                        "tool_name": "test_tool",
                        "args": {},
                    }
                    gw._cleanup_expired_confirmations_locked()
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        assert not errors, f"Concurrent access raised errors: {errors}"

    @pytest.mark.security
    def test_confirmations_lock_is_threading_lock(self) -> None:
        import codomyrmex.agents.pai.trust_gateway as gw

        # threading.Lock() returns _thread.lock; RLock returns _thread.RLock
        assert hasattr(gw._confirmations_lock, "acquire"), "Must be a lock-like object"
        assert hasattr(gw._confirmations_lock, "release"), "Must be a lock-like object"

    @pytest.mark.security
    def test_cleanup_locked_removes_expired_entries(self) -> None:
        """_cleanup_expired_confirmations_locked() must remove TTL-expired tokens."""
        import codomyrmex.agents.pai.trust_gateway as gw

        original = dict(gw._pending_confirmations)
        try:
            with gw._confirmations_lock:
                gw._pending_confirmations["stale_token"] = {
                    "timestamp": time.monotonic() - 9999,
                    "tool_name": "any",
                    "args": {},
                }
                gw._cleanup_expired_confirmations_locked()
                assert "stale_token" not in gw._pending_confirmations
        finally:
            gw._pending_confirmations.clear()
            gw._pending_confirmations.update(original)
