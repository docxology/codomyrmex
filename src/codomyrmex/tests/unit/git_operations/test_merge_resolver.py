"""Tests for git_operations.merge_resolver — conflict detection and resolution.

Uses real git repositories with actual merge conflicts. No mocks.
"""

import shutil
import subprocess

import pytest

_GIT_AVAILABLE = shutil.which("git") is not None

from codomyrmex.git_operations.merge_resolver import (
    ConflictBlock,
    MergeConflictReport,
    MergeResolver,
    ResolutionStrategy,
)

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not available"),
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_git_repo(tmp_path):
    """A minimal git repo with one commit and no conflicts."""
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)

    readme = tmp_path / "README.md"
    readme.write_text("# Repo\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    return tmp_path


@pytest.fixture
def conflicted_repo(tmp_path):
    """Real git repo in a merge-conflicted state.

    main:    x = 3  # main
    feature: x = 2  # feature
    The merge is attempted but NOT resolved, leaving conflict markers in hello.py.
    """
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)

    # Initial commit
    f = tmp_path / "hello.py"
    f.write_text("x = 1\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)

    # Feature branch changes same line
    subprocess.run(["git", "checkout", "-b", "feature"], cwd=tmp_path, check=True, capture_output=True)
    f.write_text("x = 2  # feature\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feature change"], cwd=tmp_path, check=True, capture_output=True)

    # Main branch changes same line differently
    subprocess.run(["git", "checkout", "main"], cwd=tmp_path, check=True, capture_output=True)
    f.write_text("x = 3  # main\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "main change"], cwd=tmp_path, check=True, capture_output=True)

    # Merge — will conflict (don't check=True, failure expected)
    subprocess.run(["git", "merge", "--no-ff", "feature"], cwd=tmp_path, capture_output=True)

    return tmp_path


@pytest.fixture
def trivial_conflict_repo(tmp_path):
    """Repo with a trivial (whitespace-only) conflict."""
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True, capture_output=True)

    f = tmp_path / "style.css"
    f.write_text("body { color: red; }\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)

    # Feature: adds trailing spaces
    subprocess.run(["git", "checkout", "-b", "feature"], cwd=tmp_path, check=True, capture_output=True)
    f.write_text("body { color: blue; }  \n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "feature whitespace"], cwd=tmp_path, check=True, capture_output=True)

    # Main: same content but no trailing spaces
    subprocess.run(["git", "checkout", "main"], cwd=tmp_path, check=True, capture_output=True)
    f.write_text("body { color: blue; }\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "main trim"], cwd=tmp_path, check=True, capture_output=True)

    subprocess.run(["git", "merge", "--no-ff", "feature"], cwd=tmp_path, capture_output=True)
    return tmp_path


# ---------------------------------------------------------------------------
# ConflictBlock dataclass
# ---------------------------------------------------------------------------

class TestConflictBlock:
    """Tests for the ConflictBlock dataclass and its is_trivial property."""

    def test_is_trivial_when_whitespace_only_diff(self):
        block = ConflictBlock(
            file_path="a.py", start_line=1,
            ours_content=" hello ", theirs_content="hello",
        )
        assert block.is_trivial is True

    def test_is_not_trivial_when_content_differs(self):
        block = ConflictBlock(
            file_path="a.py", start_line=1,
            ours_content="x = 1", theirs_content="x = 2",
        )
        assert block.is_trivial is False

    def test_resolved_defaults_to_false(self):
        block = ConflictBlock(file_path="a.py", start_line=1,
                              ours_content="a", theirs_content="b")
        assert block.resolved is False

    def test_resolution_defaults_to_empty_string(self):
        block = ConflictBlock(file_path="a.py", start_line=1,
                              ours_content="a", theirs_content="b")
        assert block.resolution == ""


# ---------------------------------------------------------------------------
# MergeConflictReport dataclass
# ---------------------------------------------------------------------------

class TestMergeConflictReport:

    def test_default_values(self):
        report = MergeConflictReport()
        assert report.conflicts == []
        assert report.files_affected == 0
        assert report.auto_resolved == 0
        assert report.manual_required == 0


# ---------------------------------------------------------------------------
# MergeResolver.detect_conflicts
# ---------------------------------------------------------------------------

class TestMergeResolverDetectConflicts:

    def test_detect_conflicts_returns_report_on_clean_repo(self, clean_git_repo):
        resolver = MergeResolver(clean_git_repo)
        report = resolver.detect_conflicts()
        assert isinstance(report, MergeConflictReport)
        assert len(report.conflicts) == 0
        assert report.files_affected == 0

    def test_detect_conflicts_finds_conflicts_after_merge(self, conflicted_repo):
        resolver = MergeResolver(conflicted_repo)
        report = resolver.detect_conflicts()
        assert len(report.conflicts) >= 1

    def test_detect_conflicts_counts_files_correctly(self, conflicted_repo):
        resolver = MergeResolver(conflicted_repo)
        report = resolver.detect_conflicts()
        # We created exactly one conflicted file (hello.py)
        assert report.files_affected == 1


# ---------------------------------------------------------------------------
# MergeResolver.resolve_file
# ---------------------------------------------------------------------------

class TestMergeResolverResolveFile:

    def test_resolve_file_with_ours_strategy(self, conflicted_repo):
        resolver = MergeResolver(conflicted_repo)
        result = resolver.resolve_file("hello.py", ResolutionStrategy.OURS)
        assert result is True
        content = (conflicted_repo / "hello.py").read_text()
        assert "<<<<<<" not in content
        assert "main" in content

    def test_resolve_file_with_theirs_strategy(self, conflicted_repo):
        resolver = MergeResolver(conflicted_repo)
        result = resolver.resolve_file("hello.py", ResolutionStrategy.THEIRS)
        assert result is True
        content = (conflicted_repo / "hello.py").read_text()
        assert "<<<<<<" not in content
        assert "feature" in content

    def test_resolve_file_with_union_strategy(self, conflicted_repo):
        resolver = MergeResolver(conflicted_repo)
        result = resolver.resolve_file("hello.py", ResolutionStrategy.UNION)
        assert result is True
        content = (conflicted_repo / "hello.py").read_text()
        assert "<<<<<<" not in content
        # Union includes both sides
        assert "main" in content
        assert "feature" in content

    def test_resolve_file_nonexistent_returns_false(self, conflicted_repo):
        resolver = MergeResolver(conflicted_repo)
        result = resolver.resolve_file("nonexistent.py", ResolutionStrategy.OURS)
        assert result is False

    def test_resolve_file_already_resolved_returns_true(self, clean_git_repo):
        """A file with no conflict markers is considered already resolved."""
        (clean_git_repo / "clean.py").write_text("x = 42\n")
        subprocess.run(["git", "add", "."], cwd=clean_git_repo, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "add clean"], cwd=clean_git_repo, check=True, capture_output=True)
        resolver = MergeResolver(clean_git_repo)
        result = resolver.resolve_file("clean.py", ResolutionStrategy.OURS)
        assert result is True


# ---------------------------------------------------------------------------
# MergeResolver.auto_resolve_trivial
# ---------------------------------------------------------------------------

class TestAutoResolveTrivial:

    def test_auto_resolve_returns_zero_on_no_conflicts(self, clean_git_repo):
        resolver = MergeResolver(clean_git_repo)
        count = resolver.auto_resolve_trivial()
        assert count == 0

    def test_auto_resolve_counts_trivially_resolved(self, trivial_conflict_repo):
        resolver = MergeResolver(trivial_conflict_repo)
        report = resolver.detect_conflicts()
        # Verify we actually have a trivial conflict before testing auto_resolve
        if report.conflicts and any(c.is_trivial for c in report.conflicts):
            count = resolver.auto_resolve_trivial()
            assert count >= 1
        else:
            # If git resolved the whitespace conflict automatically, no conflicts to resolve
            count = resolver.auto_resolve_trivial()
            assert count == 0
