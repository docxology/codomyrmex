"""Durable SQLite backend for Colony pheromone signals."""

from __future__ import annotations

import json
import sqlite3
import time
from typing import Any

from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig
from codomyrmex.colony_kernel.models import (
    ColonySignal,
    DecayRate,
    SignalSource,
    SignalType,
)


class SQLiteSignalStore:
    """WAL-backed signal field with atomic deposit, reinforcement, and decay."""

    def __init__(
        self, db_path: str, *, config: StigmergyConfig | None = None
    ) -> None:
        self.db_path = db_path
        self.config = config or StigmergyConfig()
        self._conn = sqlite3.connect(db_path, check_same_thread=False, timeout=10.0)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=10000")
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS pheromone_signals (
                location TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                strength REAL NOT NULL,
                decay_rate TEXT NOT NULL,
                source TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                last_reinforced REAL NOT NULL,
                PRIMARY KEY (location, signal_type)
            );
            """
        )
        self._conn.commit()

    def _row_to_signal(self, row: tuple[Any, ...]) -> ColonySignal:
        return ColonySignal(
            location=str(row[0]),
            signal_type=SignalType(str(row[1])),
            strength=float(row[2]),
            decay_rate=DecayRate(float(row[3])),
            source=SignalSource(str(row[4])),
            evidence=dict(json.loads(row[5])),
            last_reinforced=float(row[6]),
        )

    def deposit(self, signal: ColonySignal) -> None:
        now = time.time()
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO pheromone_signals
                  (location, signal_type, strength, decay_rate, source,
                   evidence_json, last_reinforced)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(location, signal_type) DO UPDATE SET
                  strength = MIN(?, pheromone_signals.strength + excluded.strength),
                  decay_rate = excluded.decay_rate,
                  source = excluded.source,
                  evidence_json = excluded.evidence_json,
                  last_reinforced = excluded.last_reinforced
                """,
                (
                    signal.location,
                    signal.signal_type.value,
                    signal.strength,
                    signal.decay_rate.value,
                    signal.source.value,
                    json.dumps(signal.evidence, sort_keys=True, default=str),
                    signal.last_reinforced or now,
                    self.config.max_strength,
                ),
            )

    def reinforce(self, location: str, signal_type: SignalType) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE pheromone_signals SET strength = MIN(?, strength + ?), "
                "last_reinforced = ? WHERE location = ? AND signal_type = ?",
                (
                    self.config.max_strength,
                    self.config.reinforce_on_read_delta,
                    time.time(),
                    location,
                    signal_type.value,
                ),
            )

    def sense(self, location: str, signal_type: SignalType) -> ColonySignal | None:
        row = self._conn.execute(
            "SELECT location, signal_type, strength, decay_rate, source, "
            "evidence_json, last_reinforced FROM pheromone_signals "
            "WHERE location = ? AND signal_type = ?",
            (location, signal_type.value),
        ).fetchone()
        return None if row is None else self._row_to_signal(row)

    def all_signals(self) -> list[ColonySignal]:
        rows = self._conn.execute(
            "SELECT location, signal_type, strength, decay_rate, source, "
            "evidence_json, last_reinforced FROM pheromone_signals "
            "ORDER BY strength DESC"
        ).fetchall()
        return [self._row_to_signal(row) for row in rows]

    def evaporate(self) -> int:
        with self._conn:
            before = int(
                self._conn.execute("SELECT COUNT(*) FROM pheromone_signals").fetchone()[0]
            )
            self._conn.execute(
                "UPDATE pheromone_signals SET strength = strength - "
                "(CASE decay_rate WHEN 'fast' THEN 0.3 WHEN 'slow' THEN 0.02 ELSE 0.1 END)"
            )
            self._conn.execute(
                "DELETE FROM pheromone_signals WHERE strength <= ?",
                (self.config.min_strength,),
            )
            after = int(
                self._conn.execute("SELECT COUNT(*) FROM pheromone_signals").fetchone()[0]
            )
        return max(0, before - after)

    def clear(self) -> int:
        with self._conn:
            count = int(
                self._conn.execute("SELECT COUNT(*) FROM pheromone_signals").fetchone()[0]
            )
            self._conn.execute("DELETE FROM pheromone_signals")
        return count

    def close(self) -> None:
        self._conn.close()

    def __len__(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) FROM pheromone_signals").fetchone()[0])


__all__ = ["SQLiteSignalStore"]
