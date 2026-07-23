"""SQLite-backed signal-store adapter for restart and concurrency experiments."""

from __future__ import annotations

import json
import os
import sqlite3
import threading
from collections.abc import Callable
from typing import TYPE_CHECKING

from codomyrmex.colony_kernel.pheromone_store import (
    _META_EVAPORATION,
    _META_LOCATION,
    PheromoneStore,
)

if TYPE_CHECKING:
    from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
    from codomyrmex.colony_kernel.models import ColonySignal, SignalType


class PersistentPheromoneStore(PheromoneStore):
    """Persist the PheromoneStore marker state after each mutation.

    The default in-memory PheromoneStore remains unchanged.  This adapter is
    intentionally explicit because persistence changes failure and latency
    semantics and must be measured separately.
    """

    def __init__(
        self,
        db_path: str | os.PathLike[str],
        config: StigmergyConfig | None = None,
        failure_injector: Callable[[str], None] | None = None,
    ) -> None:
        super().__init__(config=config)
        self._persistent_lock = threading.RLock()
        self._failure_injector = failure_injector
        self._persistent_conn = sqlite3.connect(
            os.fspath(db_path), check_same_thread=False, isolation_level=None
        )
        self._persistent_conn.execute("PRAGMA journal_mode=WAL")
        self._persistent_conn.execute("PRAGMA busy_timeout=5000")
        self._persistent_conn.execute(
            "CREATE TABLE IF NOT EXISTS pheromone_markers (key TEXT PRIMARY KEY, strength REAL NOT NULL, metadata_json TEXT NOT NULL)"
        )
        self._load_persistent()

    def _load_persistent(self) -> None:
        rows = self._persistent_conn.execute(
            "SELECT key, strength, metadata_json FROM pheromone_markers ORDER BY key"
        ).fetchall()
        for key, strength, metadata_json in rows:
            metadata = json.loads(metadata_json)
            self._field.deposit(key, initial=float(strength), metadata=metadata)
            self._key_evaporation[key] = float(metadata.get(_META_EVAPORATION, 0.1))
            location = str(metadata.get(_META_LOCATION, key.rsplit(":", 1)[0]))
            self._location_index.setdefault(location, set()).add(key)

    def _clear_memory(self) -> None:
        self._field._markers.clear()
        self._key_evaporation.clear()
        self._location_index.clear()

    def _write_persistent_rows(self) -> None:
        """Replace durable rows while the caller owns the write transaction."""
        rows = [
            (
                key,
                marker.strength,
                json.dumps(
                    marker.metadata, sort_keys=True, separators=(",", ":"), default=str
                ),
            )
            for key, marker in self._field._markers.items()
        ]
        if self._failure_injector:
            self._failure_injector("before_delete")
        self._persistent_conn.execute("DELETE FROM pheromone_markers")
        if self._failure_injector:
            self._failure_injector("before_insert")
        self._persistent_conn.executemany(
            "INSERT INTO pheromone_markers(key, strength, metadata_json) VALUES (?, ?, ?)",
            rows,
        )

    def _transactional_mutation(self, mutation: Callable[[], None]) -> None:
        """Apply one mutation against the latest durable state atomically.

        Reloading after acquiring ``BEGIN IMMEDIATE`` prevents two independent
        adapter instances from overwriting one another with stale in-memory
        snapshots.  A failed write is rolled back in SQLite and the adapter is
        reloaded, so callers never observe a mutation that durable state rejected.
        """
        with self._persistent_lock:
            if self._failure_injector:
                self._failure_injector("before_begin")
            self._persistent_conn.execute("BEGIN IMMEDIATE")
            try:
                self._clear_memory()
                self._load_persistent()
                mutation()
                self._write_persistent_rows()
                if self._failure_injector:
                    self._failure_injector("before_commit")
                self._persistent_conn.execute("COMMIT")
            except Exception:
                self._persistent_conn.execute("ROLLBACK")
                self._clear_memory()
                self._load_persistent()
                raise

    def deposit_signal(self, signal: ColonySignal) -> None:
        def mutation() -> None:
            super(PersistentPheromoneStore, self).deposit_signal(signal)

        self._transactional_mutation(mutation)

    def reinforce_path(self, location: str, signal_type: SignalType) -> None:
        def mutation() -> None:
            super(PersistentPheromoneStore, self).reinforce_path(location, signal_type)

        self._transactional_mutation(mutation)

    def evaporate(self) -> None:
        def mutation() -> None:
            super(PersistentPheromoneStore, self).evaporate()

        self._transactional_mutation(mutation)

    def refresh(self) -> None:
        """Reload durable state after another process has written the store."""
        with self._persistent_lock:
            self._clear_memory()
            self._load_persistent()

    def close(self) -> None:
        with self._persistent_lock:
            self._persistent_conn.close()


__all__ = ["PersistentPheromoneStore"]
