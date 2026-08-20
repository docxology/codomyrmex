"""Tests for Persistence and Concurrency Study Harness (R5)."""

from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.research.concurrency_study import (
    ConcurrencyAuditReport,
    CrashRecoveryReport,
    PersistenceConcurrencyStudy,
)


def test_concurrent_load_test(tmp_path) -> None:
    db_file = tmp_path / "concurrent.db"
    study = PersistenceConcurrencyStudy(db_file)

    report = study.run_concurrent_load_test(num_workers=3, operations_per_worker=15)

    assert isinstance(report, ConcurrencyAuditReport)
    assert report.total_operations == 45
    assert report.successful_operations == 45
    assert report.failed_operations == 0
    assert report.data_consistent is True
    assert report.final_marker_count > 0


def test_crash_injection_and_recovery(tmp_path) -> None:
    db_file = tmp_path / "crash_test.db"
    study = PersistenceConcurrencyStudy(db_file)

    report = study.test_crash_injection(injection_point="before_commit")

    assert isinstance(report, CrashRecoveryReport)
    assert report.crash_induced is True
    assert report.recovered_cleanly is True
    assert report.integrity_check_passed is True
