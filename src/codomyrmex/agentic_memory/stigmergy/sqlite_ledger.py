"""Persistent stigmergic traces in SQLite."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from typing import Any

from codomyrmex.agentic_memory.stigmergy.models import StigmergyConfig, TraceMarker


class SqliteTraceLedger:
    """Thread-safe trace ledger with the same operations as :class:`TraceField`."""

    def __init__(
        self,
        db_path: str,
        config: StigmergyConfig | None = None,
    ) -> None:
        self.db_path = db_path
        self.config = config or StigmergyConfig()
        self._lock = threading.Lock()
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.db_path, check_same_thread=False)
        c.row_factory = sqlite3.Row
        return c

    def _init_db(self) -> None:
        with self._lock, self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS stigmergy_traces (
                    key TEXT PRIMARY KEY,
                    strength REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                )
                """
            )

    def _clamp(self, strength: float) -> float:
        return max(
            self.config.min_strength,
            min(self.config.max_strength, strength),
        )

    def deposit(
        self,
        key: str,
        initial: float = 1.0,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> TraceMarker:
        now = time.time()
        meta_json = json.dumps(metadata or {})
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT strength, metadata FROM stigmergy_traces WHERE key = ?",
                (key,),
            ).fetchone()
            if row:
                prev = float(row["strength"])
                merged_meta: dict[str, Any] = {}
                try:
                    merged_meta = json.loads(row["metadata"] or "{}")
                except (json.JSONDecodeError, TypeError):
                    merged_meta = {}
                if metadata:
                    merged_meta.update(metadata)
                new_s = self._clamp(prev + initial)
                conn.execute(
                    """UPDATE stigmergy_traces
                       SET strength = ?, updated_at = ?, metadata = ?
                       WHERE key = ?""",
                    (new_s, now, json.dumps(merged_meta), key),
                )
                return TraceMarker(
                    key=key, strength=new_s, updated_at=now, metadata=merged_meta
                )
            conn.execute(
                """INSERT INTO stigmergy_traces (key, strength, updated_at, metadata)
                   VALUES (?, ?, ?, ?)""",
                (key, self._clamp(initial), now, meta_json),
            )
        return TraceMarker(
            key=key,
            strength=self._clamp(initial),
            updated_at=now,
            metadata=dict(metadata or {}),
        )

    def reinforce(self, key: str) -> TraceMarker | None:
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT strength, metadata FROM stigmergy_traces WHERE key = ?",
                (key,),
            ).fetchone()
            if not row:
                return None
            new_s = self._clamp(
                float(row["strength"]) + self.config.reinforce_on_read_delta
            )
            now = time.time()
            meta: dict[str, Any] = {}
            try:
                meta = json.loads(row["metadata"] or "{}")
            except (json.JSONDecodeError, TypeError):
                pass
            conn.execute(
                "UPDATE stigmergy_traces SET strength = ?, updated_at = ? WHERE key = ?",
                (new_s, now, key),
            )
        return TraceMarker(key=key, strength=new_s, updated_at=now, metadata=meta)

    def sense(self, key: str, *, reinforce: bool = False) -> TraceMarker | None:
        if reinforce:
            return self.reinforce(key)
        with self._lock, self._conn() as conn:
            row = conn.execute(
                "SELECT strength, updated_at, metadata FROM stigmergy_traces WHERE key = ?",
                (key,),
            ).fetchone()
            if not row:
                return None
            meta: dict[str, Any] = {}
            try:
                meta = json.loads(row["metadata"] or "{}")
            except (json.JSONDecodeError, TypeError):
                pass
            return TraceMarker(
                key=key,
                strength=float(row["strength"]),
                updated_at=float(row["updated_at"]),
                metadata=meta,
            )

    def tick(self) -> int:
        removed = 0
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                "SELECT key, strength FROM stigmergy_traces"
            ).fetchall()
            for row in rows:
                key = row["key"]
                new_s = float(row["strength"]) - self.config.evaporation_per_tick
                if new_s <= self.config.min_strength:
                    conn.execute("DELETE FROM stigmergy_traces WHERE key = ?", (key,))
                    removed += 1
                else:
                    conn.execute(
                        "UPDATE stigmergy_traces SET strength = ?, updated_at = ? WHERE key = ?",
                        (new_s, time.time(), key),
                    )
        return removed

    def top_k(self, k: int = 10) -> list[TraceMarker]:
        with self._lock, self._conn() as conn:
            rows = conn.execute(
                """SELECT key, strength, updated_at, metadata FROM stigmergy_traces
                   ORDER BY strength DESC LIMIT ?""",
                (k,),
            ).fetchall()
        out: list[TraceMarker] = []
        for row in rows:
            meta: dict[str, Any] = {}
            try:
                meta = json.loads(row["metadata"] or "{}")
            except (json.JSONDecodeError, TypeError):
                pass
            out.append(
                TraceMarker(
                    key=row["key"],
                    strength=float(row["strength"]),
                    updated_at=float(row["updated_at"]),
                    metadata=meta,
                )
            )
        return out

    def __len__(self) -> int:
        with self._lock, self._conn() as conn:
            n = conn.execute(
                "SELECT COUNT(*) FROM stigmergy_traces"
            ).fetchone()[0]
        return int(n)
