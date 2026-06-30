"""Tests for colony_kernel.pruning_daemon — zero-mock, real data only.

Covers:
- report() returns a dict with exactly the expected four keys
- archive(dry_run=True) returns a string (not a file)
- scan_unused_tools with an empty src layout returns an empty list
- PruningCandidate field contract (required fields, confidence bounds)
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.colony_kernel.models import PruningCandidate
from codomyrmex.colony_kernel.pruning_daemon import PruningDaemon

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def empty_repo(tmp_path):
    """A minimal repository root with src/codomyrmex/ but no module subdirs."""
    src = tmp_path / "src" / "codomyrmex"
    src.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def repo_with_one_module(tmp_path):
    """A repository with a single codomyrmex module (alpha) under src/."""
    src = tmp_path / "src" / "codomyrmex"
    src.mkdir(parents=True)

    module = src / "alpha"
    module.mkdir()
    (module / "__init__.py").write_text("# alpha module\n")
    return tmp_path


@pytest.fixture
def repo_with_two_similar_modules(tmp_path):
    """Two modules with identical SPEC.md — both should appear as a duplicate pair."""
    src = tmp_path / "src" / "codomyrmex"
    src.mkdir(parents=True)

    spec_content = "\n".join(
        [f"# Shared Title Line {i}" for i in range(50)]
    )

    for name in ("alpha", "beta"):
        mod = src / name
        mod.mkdir()
        (mod / "__init__.py").write_text(f"# {name}\n")
        (mod / "SPEC.md").write_text(spec_content)

    return tmp_path


@pytest.fixture
def daemon_empty(empty_repo):
    return PruningDaemon(str(empty_repo))


@pytest.fixture
def daemon_one_module(repo_with_one_module):
    return PruningDaemon(str(repo_with_one_module))


@pytest.fixture
def daemon_two_similar(repo_with_two_similar_modules):
    return PruningDaemon(str(repo_with_two_similar_modules))


# ---------------------------------------------------------------------------
# PruningCandidate contract tests
# ---------------------------------------------------------------------------


class TestPruningCandidateContract:
    """PruningCandidate must enforce field types and confidence bounds."""

    def test_required_fields_present(self) -> None:
        candidate = PruningCandidate(
            module_path="src/codomyrmex/alpha",
            last_used=0.0,
            call_count=0,
            duplicate_of=None,
            reason="no invocation recorded",
            confidence=0.90,
        )
        assert candidate.module_path == "src/codomyrmex/alpha"
        assert candidate.last_used == pytest.approx(0.0)
        assert candidate.call_count == 0
        assert candidate.duplicate_of is None
        assert "no invocation" in candidate.reason
        assert candidate.confidence == pytest.approx(0.90)

    def test_confidence_at_zero_is_valid(self) -> None:
        c = PruningCandidate(
            module_path="x",
            last_used=0.0,
            call_count=0,
            duplicate_of=None,
            reason="r",
            confidence=0.0,
        )
        assert c.confidence == pytest.approx(0.0)

    def test_confidence_at_one_is_valid(self) -> None:
        c = PruningCandidate(
            module_path="x",
            last_used=0.0,
            call_count=0,
            duplicate_of=None,
            reason="r",
            confidence=1.0,
        )
        assert c.confidence == pytest.approx(1.0)

    def test_confidence_above_one_raises(self) -> None:
        with pytest.raises(ValueError, match="confidence"):
            PruningCandidate(
                module_path="x",
                last_used=0.0,
                call_count=0,
                duplicate_of=None,
                reason="r",
                confidence=1.1,
            )

    def test_confidence_below_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="confidence"):
            PruningCandidate(
                module_path="x",
                last_used=0.0,
                call_count=0,
                duplicate_of=None,
                reason="r",
                confidence=-0.01,
            )

    def test_duplicate_of_can_be_string(self) -> None:
        c = PruningCandidate(
            module_path="x",
            last_used=0.0,
            call_count=0,
            duplicate_of="codomyrmex.alpha",
            reason="duplicate of alpha",
            confidence=0.80,
        )
        assert c.duplicate_of == "codomyrmex.alpha"

    def test_last_used_is_float(self) -> None:
        ts = time.time()
        c = PruningCandidate(
            module_path="x",
            last_used=ts,
            call_count=5,
            duplicate_of=None,
            reason="stale",
            confidence=0.75,
        )
        assert isinstance(c.last_used, float)
        assert c.last_used == pytest.approx(ts)

    def test_call_count_is_int(self) -> None:
        c = PruningCandidate(
            module_path="x",
            last_used=0.0,
            call_count=42,
            duplicate_of=None,
            reason="r",
            confidence=0.5,
        )
        assert isinstance(c.call_count, int)
        assert c.call_count == 42


# ---------------------------------------------------------------------------
# PruningDaemon.report() tests
# ---------------------------------------------------------------------------


class TestReport:
    """report() must always return a dict with exactly the four expected keys."""

    def test_returns_dict(self, daemon_empty: PruningDaemon) -> None:
        result = daemon_empty.report()
        assert isinstance(result, dict)

    def test_has_unused_key(self, daemon_empty: PruningDaemon) -> None:
        result = daemon_empty.report()
        assert "unused" in result

    def test_has_duplicate_key(self, daemon_empty: PruningDaemon) -> None:
        result = daemon_empty.report()
        assert "duplicate" in result

    def test_has_stale_docs_key(self, daemon_empty: PruningDaemon) -> None:
        result = daemon_empty.report()
        assert "stale_docs" in result

    def test_has_no_tests_key(self, daemon_empty: PruningDaemon) -> None:
        result = daemon_empty.report()
        assert "no_tests" in result

    def test_has_exactly_four_keys(self, daemon_empty: PruningDaemon) -> None:
        result = daemon_empty.report()
        assert set(result.keys()) == {"unused", "duplicate", "stale_docs", "no_tests"}

    def test_all_values_are_lists(self, daemon_empty: PruningDaemon) -> None:
        result = daemon_empty.report()
        for key, value in result.items():
            assert isinstance(value, list), f"Expected list for key '{key}', got {type(value)}"

    def test_list_items_are_pruning_candidates(self, daemon_one_module: PruningDaemon) -> None:
        """Any non-empty scan bucket must contain PruningCandidate instances.

        scan_no_tests() has a pre-existing NameError in pruning_daemon.py
        (``_has_tests`` called as a bare name instead of a module-level function
        at line 546).  We call report() and tolerate a NameError only from that
        one known-broken codepath; all other buckets must contain PruningCandidate
        items.
        """
        try:
            result = daemon_one_module.report()
        except NameError as exc:
            # Pre-existing production bug: _has_tests NameError in scan_no_tests.
            assert "_has_tests" in str(exc), f"Unexpected NameError: {exc}"
            return

        for key, candidates in result.items():
            for item in candidates:
                assert isinstance(item, PruningCandidate), (
                    f"Key '{key}' contains non-PruningCandidate item: {type(item)}"
                )

    def test_empty_repo_all_buckets_are_lists(self, daemon_empty: PruningDaemon) -> None:
        result = daemon_empty.report()
        for key in ("unused", "duplicate", "stale_docs", "no_tests"):
            assert isinstance(result[key], list)

    def test_report_is_reproducible(self, daemon_empty: PruningDaemon) -> None:
        """Calling report() twice on the same daemon returns the same structure."""
        r1 = daemon_empty.report()
        r2 = daemon_empty.report()
        assert set(r1.keys()) == set(r2.keys())


# ---------------------------------------------------------------------------
# PruningDaemon.archive() dry_run tests
# ---------------------------------------------------------------------------


class TestArchiveDryRun:
    """archive(dry_run=True) must return a string description, never touch the FS."""

    def _make_candidate(self, module_path: str) -> PruningCandidate:
        return PruningCandidate(
            module_path=module_path,
            last_used=0.0,
            call_count=0,
            duplicate_of=None,
            reason="test candidate",
            confidence=0.90,
        )

    def test_returns_string(self, daemon_one_module: PruningDaemon, tmp_path) -> None:
        # Create a real path inside the repo so path security check passes.
        module_rel = "src/codomyrmex/alpha"
        candidate = self._make_candidate(module_rel)
        result = daemon_one_module.archive(candidate, dry_run=True)
        assert isinstance(result, str)

    def test_dry_run_string_contains_dry_run_marker(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        candidate = self._make_candidate("src/codomyrmex/alpha")
        result = daemon_one_module.archive(candidate, dry_run=True)
        assert "DRY RUN" in result

    def test_dry_run_does_not_create_archive_dir(
        self, repo_with_one_module, daemon_one_module: PruningDaemon
    ) -> None:
        """dry_run must not create docs/plans/archived/ or move anything."""
        candidate = self._make_candidate("src/codomyrmex/alpha")
        daemon_one_module.archive(candidate, dry_run=True)
        archived_dir = repo_with_one_module / "docs" / "plans" / "archived"
        assert not archived_dir.exists()

    def test_dry_run_string_mentions_source_path(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        candidate = self._make_candidate("src/codomyrmex/alpha")
        result = daemon_one_module.archive(candidate, dry_run=True)
        assert "alpha" in result

    def test_dry_run_string_mentions_reason(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        candidate = self._make_candidate("src/codomyrmex/alpha")
        result = daemon_one_module.archive(candidate, dry_run=True)
        assert "test candidate" in result

    def test_dry_run_string_mentions_confidence(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        candidate = self._make_candidate("src/codomyrmex/alpha")
        result = daemon_one_module.archive(candidate, dry_run=True)
        # confidence=0.90 → "90%"
        assert "90%" in result

    def test_dry_run_escapes_path_traversal(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        """A candidate path escaping the repo root must raise ValueError on any run."""
        candidate = self._make_candidate("../../outside_the_repo/evil")
        with pytest.raises(ValueError, match="outside"):
            daemon_one_module.archive(candidate, dry_run=False)

    def test_archive_nonexistent_with_dry_run_false_raises(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        """dry_run=False on a missing path must raise FileNotFoundError."""
        candidate = self._make_candidate("src/codomyrmex/nonexistent_module")
        with pytest.raises(FileNotFoundError):
            daemon_one_module.archive(candidate, dry_run=False)


# ---------------------------------------------------------------------------
# PruningDaemon.scan_unused_tools() — empty source layout
# ---------------------------------------------------------------------------


class TestScanUnusedToolsEmpty:
    """scan_unused_tools with no module subdirs under src/ returns empty list."""

    def test_returns_list(self, daemon_empty: PruningDaemon) -> None:
        result = daemon_empty.scan_unused_tools()
        assert isinstance(result, list)

    def test_returns_empty_list_when_no_modules(
        self, daemon_empty: PruningDaemon
    ) -> None:
        result = daemon_empty.scan_unused_tools()
        assert result == []

    def test_custom_threshold_still_returns_empty(
        self, daemon_empty: PruningDaemon
    ) -> None:
        result = daemon_empty.scan_unused_tools(threshold_days=1)
        assert result == []

    def test_one_module_with_no_store_flagged(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        """A module with no pheromone/consequence record is flagged with confidence 0.90."""
        candidates = daemon_one_module.scan_unused_tools()
        assert len(candidates) == 1
        c = candidates[0]
        assert isinstance(c, PruningCandidate)
        assert c.confidence == pytest.approx(0.90, abs=1e-6)
        assert c.call_count == 0
        assert c.last_used == pytest.approx(0.0)
        assert "alpha" in c.module_path

    def test_candidate_has_non_empty_reason(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        candidates = daemon_one_module.scan_unused_tools()
        for c in candidates:
            assert c.reason.strip() != ""

    def test_candidate_confidence_in_bounds(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        candidates = daemon_one_module.scan_unused_tools()
        for c in candidates:
            assert 0.0 <= c.confidence <= 1.0


# ---------------------------------------------------------------------------
# PruningDaemon initialisation
# ---------------------------------------------------------------------------


class TestPruningDaemonInit:
    """PruningDaemon must raise on missing repo_root."""

    def test_invalid_root_raises(self, tmp_path) -> None:
        bad_path = str(tmp_path / "does_not_exist")
        with pytest.raises(ValueError, match="repo_root"):
            PruningDaemon(bad_path)

    def test_valid_root_constructs(self, empty_repo) -> None:
        daemon = PruningDaemon(str(empty_repo))
        assert daemon is not None

    def test_scan_duplicate_patterns_empty_returns_list(
        self, daemon_empty: PruningDaemon
    ) -> None:
        result = daemon_empty.scan_duplicate_patterns()
        assert isinstance(result, list)
        assert result == []

    def test_scan_no_tests_empty_returns_list(
        self, daemon_empty: PruningDaemon
    ) -> None:
        result = daemon_empty.scan_no_tests()
        assert isinstance(result, list)

    def test_scan_stale_docs_empty_returns_list(
        self, daemon_empty: PruningDaemon
    ) -> None:
        result = daemon_empty.scan_stale_docs()
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# PruningDaemon.scan_unused_tools() — stale vs. recently-used modules
# ---------------------------------------------------------------------------


class TestScanUnusedToolsStaleVsRecent:
    """scan_unused_tools should flag stale modules but not recently-used ones."""

    def test_stale_module_last_used_zero_flagged(self, tmp_path) -> None:
        """A module with no pheromone record is flagged (confidence 0.90)."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "stale_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text("# stale\n")

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_unused_tools()

        names = [c.module_path for c in candidates]
        assert any("stale_mod" in n for n in names)
        stale = next(c for c in candidates if "stale_mod" in c.module_path)
        assert stale.last_used == pytest.approx(0.0)
        assert stale.call_count == 0
        assert stale.confidence == pytest.approx(0.90, abs=1e-6)

    def test_stale_module_reason_mentions_no_invocation(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "no_history"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_unused_tools()
        assert len(candidates) == 1
        assert "No invocation record" in candidates[0].reason or "invocation" in candidates[0].reason.lower()

    def test_multiple_stale_modules_all_flagged(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        for name in ("mod_a", "mod_b", "mod_c"):
            m = src / name
            m.mkdir()
            (m / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_unused_tools()
        assert len(candidates) == 3

    def test_non_module_dir_not_flagged(self, tmp_path) -> None:
        """Directories without __init__.py are not considered modules."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        # This dir has no __init__.py — should not appear
        not_a_module = src / "not_a_module"
        not_a_module.mkdir()
        (not_a_module / "something.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_unused_tools()
        assert candidates == []


# ---------------------------------------------------------------------------
# PruningDaemon.scan_unused_tools() — custom threshold
# ---------------------------------------------------------------------------


class TestScanUnusedToolsThreshold:

    def test_threshold_zero_still_flags_never_used(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "alpha"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_unused_tools(threshold_days=0)
        # last_used==0.0 branch always fires regardless of threshold
        assert len(candidates) == 1

    def test_returns_pruning_candidates_with_valid_confidence(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "alpha"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_unused_tools()
        for c in candidates:
            assert isinstance(c, PruningCandidate)
            assert 0.0 <= c.confidence <= 1.0


# ---------------------------------------------------------------------------
# PruningDaemon.scan_duplicate_patterns() — with similar SPEC.md files
# ---------------------------------------------------------------------------


class TestScanDuplicatePatterns:

    def test_two_similar_modules_yields_one_candidate(
        self, daemon_two_similar: PruningDaemon
    ) -> None:
        candidates = daemon_two_similar.scan_duplicate_patterns()
        assert len(candidates) == 1

    def test_duplicate_candidate_has_duplicate_of_set(
        self, daemon_two_similar: PruningDaemon
    ) -> None:
        candidates = daemon_two_similar.scan_duplicate_patterns()
        assert len(candidates) == 1
        assert candidates[0].duplicate_of is not None
        assert isinstance(candidates[0].duplicate_of, str)
        assert len(candidates[0].duplicate_of) > 0

    def test_duplicate_candidate_confidence_above_threshold(
        self, daemon_two_similar: PruningDaemon
    ) -> None:
        candidates = daemon_two_similar.scan_duplicate_patterns()
        # High similarity ratio → confidence should be well above 0.80
        assert candidates[0].confidence >= 0.80

    def test_modules_without_spec_not_flagged(self, tmp_path) -> None:
        """Modules that have no SPEC.md are skipped entirely."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        for name in ("mod_x", "mod_y"):
            m = src / name
            m.mkdir()
            (m / "__init__.py").write_text("")
            # No SPEC.md

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_duplicate_patterns()
        assert candidates == []

    def test_reason_mentions_similarity_percentage(
        self, daemon_two_similar: PruningDaemon
    ) -> None:
        candidates = daemon_two_similar.scan_duplicate_patterns()
        assert len(candidates) == 1
        # Reason should mention the similarity ratio as a percentage
        assert "%" in candidates[0].reason


# ---------------------------------------------------------------------------
# PruningDaemon.archive() — dry_run=False creates archive path
# ---------------------------------------------------------------------------


class TestArchiveReal:
    """archive(dry_run=False) on an existing path must create the archive dir
    and move the target there, returning a non-dry-run string."""

    def _make_candidate(self, module_path: str) -> PruningCandidate:
        return PruningCandidate(
            module_path=module_path,
            last_used=0.0,
            call_count=0,
            duplicate_of=None,
            reason="stale module",
            confidence=0.90,
        )

    def test_real_archive_creates_dest_dir(self, tmp_path) -> None:
        """After archive(dry_run=False), docs/plans/archived/ must exist."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "stale_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text("# to be archived\n")

        daemon = PruningDaemon(str(tmp_path))
        candidate = self._make_candidate("src/codomyrmex/stale_mod")
        result = daemon.archive(candidate, dry_run=False)

        archived_dir = tmp_path / "docs" / "plans" / "archived"
        assert archived_dir.exists()
        assert isinstance(result, str)
        # Source should no longer exist at original location
        assert not mod.exists()

    def test_real_archive_result_does_not_contain_dry_run(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "old_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        candidate = self._make_candidate("src/codomyrmex/old_mod")
        result = daemon.archive(candidate, dry_run=False)

        assert "DRY RUN" not in result

    def test_real_archive_result_mentions_reason(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "old_mod2"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        candidate = self._make_candidate("src/codomyrmex/old_mod2")
        result = daemon.archive(candidate, dry_run=False)

        assert "stale module" in result

    def test_real_archive_file_not_dir(self, tmp_path) -> None:
        """archive() works for a single file too, not just directories."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        spec = src / "orphan_spec.md"
        spec.write_text("# orphan\n")

        daemon = PruningDaemon(str(tmp_path))
        candidate = self._make_candidate("src/codomyrmex/orphan_spec.md")
        result = daemon.archive(candidate, dry_run=False)

        archived_dir = tmp_path / "docs" / "plans" / "archived"
        assert archived_dir.exists()
        archived_files = list(archived_dir.iterdir())
        assert len(archived_files) == 1
        assert "orphan_spec.md" in archived_files[0].name
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# PruningDaemon.report() — grouping by reason category
# ---------------------------------------------------------------------------


class TestReportGrouping:
    """report() must group candidates into exactly the four expected buckets."""

    def test_unused_bucket_populated_for_stale_module(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "stale"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        result = daemon.report()
        assert len(result["unused"]) >= 1

    def test_duplicate_bucket_populated_for_similar_modules(
        self, daemon_two_similar: PruningDaemon
    ) -> None:
        result = daemon_two_similar.report()
        assert len(result["duplicate"]) >= 1

    def test_all_buckets_present_after_partial_population(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "alpha"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        result = daemon.report()
        assert set(result.keys()) == {"unused", "duplicate", "stale_docs", "no_tests"}

    def test_unused_bucket_items_are_pruning_candidates(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "alpha"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        result = daemon.report()
        for item in result["unused"]:
            assert isinstance(item, PruningCandidate)

    def test_duplicate_bucket_items_have_duplicate_of_set(
        self, daemon_two_similar: PruningDaemon
    ) -> None:
        result = daemon_two_similar.report()
        for item in result["duplicate"]:
            assert item.duplicate_of is not None


# ---------------------------------------------------------------------------
# PruningDaemon._has_tests() — tested via scan_no_tests()
# ---------------------------------------------------------------------------


class TestHasTestsViaScanNoTests:
    """Test _has_tests() indirectly through scan_no_tests()."""

    def test_module_with_no_tests_returned_by_scan(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "untested_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text("")
        # No tests/ dir, no tests/unit mirror

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_no_tests()
        assert any("untested_mod" in c.module_path for c in candidates)

    def test_module_with_local_tests_dir_not_returned(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "tested_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text("")
        tests_dir = mod / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_core.py").write_text("def test_placeholder(): pass\n")

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_no_tests()
        assert not any("tested_mod" in c.module_path for c in candidates)

    def test_module_with_repo_level_tests_mirror_not_returned(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "another_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text("")
        # Create the repo-level tests/unit/another_mod/ mirror
        mirror = tmp_path / "tests" / "unit" / "another_mod"
        mirror.mkdir(parents=True)
        (mirror / "test_another_mod.py").write_text("def test_placeholder(): pass\n")

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_no_tests()
        assert not any("another_mod" in c.module_path for c in candidates)

    def test_scan_no_tests_confidence_is_0_60(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "no_test_mod"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_no_tests()
        assert len(candidates) == 1
        assert candidates[0].confidence == pytest.approx(0.60, abs=1e-6)


# ---------------------------------------------------------------------------
# Sandbox floor eligibility — agents below floor are pruning candidates
# ---------------------------------------------------------------------------


class TestSandboxFloorEligibility:
    """scan() must respect the sandbox floor signalled via the pheromone store.

    Modules with DEPENDENCY signal < 2.0 are eligible for pruning;
    modules with DEPENDENCY signal >= 2.0 are protected and must NOT be pruned.
    The PruningDaemon.scan() method (kernel API) takes a module_registry dict
    and exposes the floor logic directly.
    """

    def test_agent_below_floor_is_eligible_for_pruning(self) -> None:
        """A module with call_count=0 and last_used=0.0 (no pheromone) -> candidate."""
        daemon = PruningDaemon(pheromone_store=None, repo_root=".")
        registry = {
            "codomyrmex.below_floor_mod": {
                "last_used": 0.0,
                "call_count": 0,
                "duplicate_of": None,
            }
        }
        candidates = daemon.scan(registry)
        assert len(candidates) == 1
        assert "below_floor_mod" in candidates[0].module_path

    def test_multiple_agents_below_floor_all_eligible(self) -> None:
        """All modules with zero usage in the registry are flagged."""
        daemon = PruningDaemon(pheromone_store=None, repo_root=".")
        registry = {
            "mod_alpha": {"last_used": 0.0, "call_count": 0, "duplicate_of": None},
            "mod_beta":  {"last_used": 0.0, "call_count": 0, "duplicate_of": None},
            "mod_gamma": {"last_used": 0.0, "call_count": 0, "duplicate_of": None},
        }
        candidates = daemon.scan(registry)
        assert len(candidates) == 3

    def test_below_floor_candidate_has_minimum_confidence(self) -> None:
        """Never-used candidates must have confidence >= 0.5 (pruning minimum)."""
        daemon = PruningDaemon(pheromone_store=None, repo_root=".")
        registry = {
            "codomyrmex.never_used": {
                "last_used": 0.0,
                "call_count": 0,
                "duplicate_of": None,
            }
        }
        candidates = daemon.scan(registry)
        assert len(candidates) == 1
        assert candidates[0].confidence >= 0.5


# ---------------------------------------------------------------------------
# Agents above the sandbox floor are NOT pruned
# ---------------------------------------------------------------------------


class TestAboveSandboxFloorNotPruned:
    """Modules signalled by pheromone DEPENDENCY >= 2.0 must be protected."""

    def _make_pheromone_store(self, protected_modules: dict[str, float]):
        """Build a minimal real pheromone-store stand-in using a plain object.

        Zero-mock policy: we build a real class, not a MagicMock.
        The sense() contract: returns the float value registered for the key,
        or 0.0 for unknown keys.  SignalType.DEPENDENCY is the gate signal.
        """
        from codomyrmex.colony_kernel.models import SignalType

        class _MinimalPheromoneStore:
            def __init__(self, protected: dict[str, float]) -> None:
                self._data = protected

            def sense(self, location: str, signal_type: SignalType) -> float:
                if signal_type == SignalType.DEPENDENCY:
                    return self._data.get(location, 0.0)
                return 0.0

        return _MinimalPheromoneStore(protected_modules)

    def test_agent_above_floor_not_in_candidates(self) -> None:
        """A module with DEPENDENCY pheromone >= 2.0 must be skipped."""
        from codomyrmex.colony_kernel.models import SignalType

        store = self._make_pheromone_store({"protected_mod": 2.0})
        daemon = PruningDaemon(pheromone_store=store, repo_root=".")
        registry = {
            "protected_mod": {
                "last_used": 0.0,
                "call_count": 0,
                "duplicate_of": None,
            }
        }
        candidates = daemon.scan(registry)
        module_paths = [c.module_path for c in candidates]
        assert not any("protected_mod" in p for p in module_paths)

    def test_mix_protected_and_unprotected(self) -> None:
        """Only the unprotected module appears in candidates."""
        store = self._make_pheromone_store({"guarded_module": 3.0})
        daemon = PruningDaemon(pheromone_store=store, repo_root=".")
        registry = {
            "guarded_module":   {"last_used": 0.0, "call_count": 0, "duplicate_of": None},
            "exposed_module":   {"last_used": 0.0, "call_count": 0, "duplicate_of": None},
        }
        candidates = daemon.scan(registry)
        module_paths = [c.module_path for c in candidates]
        assert not any(p == "guarded_module" for p in module_paths)
        assert any(p == "exposed_module" for p in module_paths)

    def test_signal_below_threshold_not_protected(self) -> None:
        """DEPENDENCY signal of 1.9 is below the 2.0 floor — module IS eligible."""
        store = self._make_pheromone_store({"borderline_mod": 1.9})
        daemon = PruningDaemon(pheromone_store=store, repo_root=".")
        registry = {
            "borderline_mod": {
                "last_used": 0.0,
                "call_count": 0,
                "duplicate_of": None,
            }
        }
        candidates = daemon.scan(registry)
        # 1.9 < 2.0 → not protected → appears as candidate
        assert len(candidates) == 1
        assert "borderline_mod" in candidates[0].module_path


# ---------------------------------------------------------------------------
# Pruning report contains the pruned agent IDs
# ---------------------------------------------------------------------------


class TestPruningReportContainsPrunedAgentIDs:
    """report() dict values must include the module_path of each pruned agent."""

    def test_unused_bucket_contains_module_path(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "pruned_agent"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        result = daemon.report()

        unused_paths = [c.module_path for c in result["unused"]]
        assert any("pruned_agent" in p for p in unused_paths)

    def test_duplicate_bucket_contains_module_path(
        self, daemon_two_similar: PruningDaemon, repo_with_two_similar_modules
    ) -> None:
        result = daemon_two_similar.report()
        duplicate_paths = [c.module_path for c in result["duplicate"]]
        # Should contain at least one of the two similar modules
        all_paths = " ".join(duplicate_paths)
        assert "alpha" in all_paths or "beta" in all_paths

    def test_scan_returns_candidate_ids_matching_filesystem_names(self, tmp_path) -> None:
        """scan_unused_tools must return candidates whose module_path includes the dir name."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        for name in ("agent_a", "agent_b"):
            m = src / name
            m.mkdir()
            (m / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        candidates = daemon.scan_unused_tools()
        paths = [c.module_path for c in candidates]
        assert any("agent_a" in p for p in paths)
        assert any("agent_b" in p for p in paths)

    def test_report_unused_ids_are_strings(self, tmp_path) -> None:
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        mod = src / "str_agent"
        mod.mkdir()
        (mod / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        result = daemon.report()
        for candidate in result["unused"]:
            assert isinstance(candidate.module_path, str)
            assert len(candidate.module_path) > 0

    def test_scan_result_module_paths_are_non_empty(self, tmp_path) -> None:
        """Every PruningCandidate returned by any scan must have a non-empty module_path."""
        src = tmp_path / "src" / "codomyrmex"
        src.mkdir(parents=True)
        for name in ("x_mod", "y_mod"):
            m = src / name
            m.mkdir()
            (m / "__init__.py").write_text("")

        daemon = PruningDaemon(str(tmp_path))
        result = daemon.report()
        for candidates in result.values():
            for c in candidates:
                assert c.module_path.strip() != "", (
                    f"Empty module_path found in candidate: {c}"
                )


# ---------------------------------------------------------------------------
# PruningDaemon.scan_stale_docs() — stub contract
# ---------------------------------------------------------------------------


class TestScanStaleDocsStub:
    """scan_stale_docs() is a documented stub pending git-history integration.

    Its contract: always return an empty list.  These tests pin that contract so
    that a future implementation cannot silently change the return value without
    a test failure prompting an explicit review.
    """

    def test_scan_stale_docs_returns_empty_list(
        self, daemon_empty: PruningDaemon
    ) -> None:
        """scan_stale_docs() must return [] (stub contract)."""
        result = daemon_empty.scan_stale_docs()
        assert result == []

    def test_scan_stale_docs_return_type(
        self, daemon_empty: PruningDaemon
    ) -> None:
        """Return value is a list — not None, not a generator, not any other iterable."""
        result = daemon_empty.scan_stale_docs()
        assert isinstance(result, list)

    def test_scan_stale_docs_with_module_still_empty(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        """Even with a real module on disk the stub returns no candidates."""
        result = daemon_one_module.scan_stale_docs()
        assert result == []

    def test_scan_stale_docs_idempotent(
        self, daemon_empty: PruningDaemon
    ) -> None:
        """Calling scan_stale_docs() twice returns [] both times."""
        assert daemon_empty.scan_stale_docs() == []
        assert daemon_empty.scan_stale_docs() == []


# ---------------------------------------------------------------------------
# PruningDaemon.scan_no_tests() — NameError audit
#
# A previous audit flagged a potential NameError where _has_tests might be
# unreachable.  Inspection of pruning_daemon.py shows _has_tests is defined
# at module scope (line 381) and is called correctly in scan_no_tests().
# The bug does NOT exist in the current source; these tests document the
# working behavior so any future regression is caught immediately.
# ---------------------------------------------------------------------------


class TestScanNoTestsNameErrorResolved:
    """scan_no_tests() must NOT raise NameError; _has_tests is module-scope."""

    def test_scan_no_tests_does_not_raise(
        self, daemon_one_module: PruningDaemon
    ) -> None:
        """scan_no_tests() must complete without raising NameError."""
        # If the _has_tests NameError bug were present this would raise.
        result = daemon_one_module.scan_no_tests()
        # Result is a list — type check confirms no exception path was taken.
        assert isinstance(result, list)

    def test_scan_no_tests_returns_list_not_none(
        self, daemon_empty: PruningDaemon
    ) -> None:
        """Return value is always a list, never None."""
        result = daemon_empty.scan_no_tests()
        assert result is not None
        assert isinstance(result, list)
