"""Tests for SqliteTraceLedger — real temp SQLite files."""

from __future__ import annotations

from pathlib import Path

from codomyrmex.agentic_memory.stigmergy import SqliteTraceLedger, StigmergyConfig


def test_sqlite_deposit_reinforce_sense(tmp_path: Path) -> None:
    db = tmp_path / "traces.db"
    cfg = StigmergyConfig(max_strength=8.0)
    ledger = SqliteTraceLedger(str(db), config=cfg)
    ledger.deposit("k1", 1.0, metadata={"n": 1})
    m = ledger.sense("k1")
    assert m is not None
    assert m.strength == 1.0
    ledger.reinforce("k1")
    m2 = ledger.sense("k1")
    assert m2 is not None
    assert m2.strength > 1.0


def test_sqlite_tick_and_top_k(tmp_path: Path) -> None:
    db = tmp_path / "t2.db"
    cfg = StigmergyConfig(evaporation_per_tick=5.0, min_strength=0.0)
    ledger = SqliteTraceLedger(str(db), config=cfg)
    ledger.deposit("a", 10.0)
    ledger.deposit("b", 3.0)
    n = ledger.tick()
    assert n >= 0
    top = ledger.top_k(5)
    assert len(top) >= 1


def test_sqlite_len(tmp_path: Path) -> None:
    db = tmp_path / "t3.db"
    ledger = SqliteTraceLedger(str(db))
    assert len(ledger) == 0
    ledger.deposit("z", 1.0)
    assert len(ledger) == 1
