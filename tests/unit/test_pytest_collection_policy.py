"""Tests for repository-wide pytest collection policy."""

from pathlib import Path

from tests.conftest import _is_performance_test_path
from tests.support.repo_paths import REPO_ROOT


def test_performance_suite_path_is_classified_for_opt_in_markers() -> None:
    tests_root = REPO_ROOT / "tests"
    assert _is_performance_test_path(tests_root / "performance" / "test_latency.py")
    assert not _is_performance_test_path(tests_root / "unit" / "test_latency.py")
    assert not _is_performance_test_path(Path("/tmp/performance/test_latency.py"))
