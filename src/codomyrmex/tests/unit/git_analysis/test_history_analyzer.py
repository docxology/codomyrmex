"""Unit tests for GitHistoryAnalyzer.

Tests run against the actual codomyrmex repository at the project root.
No mocking — per codomyrmex zero-mock policy.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from codomyrmex.git_analysis.core.history_analyzer import GitHistoryAnalyzer

# Project root — the git repo these tests run inside
PROJECT_ROOT = str(Path(__file__).parents[5])


@pytest.fixture(scope="module")
def analyzer() -> GitHistoryAnalyzer:
    """Shared analyzer instance for the codomyrmex repository."""
    return GitHistoryAnalyzer(PROJECT_ROOT)


@pytest.mark.unit
def test_get_commit_history_returns_list(analyzer: GitHistoryAnalyzer) -> None:
    """get_commit_history returns a non-empty list of commit dicts."""
    commits = analyzer.get_commit_history(max_count=10)
    assert isinstance(commits, list)
    assert len(commits) > 0


@pytest.mark.unit
def test_get_commit_history_required_keys(analyzer: GitHistoryAnalyzer) -> None:
    """Each commit dict contains the required metadata keys."""
    commits = analyzer.get_commit_history(max_count=5)
    required_keys = {"sha", "author", "email", "date", "message",
                     "insertions", "deletions", "files_changed"}
    for commit in commits:
        assert required_keys.issubset(commit.keys()), (
            f"Missing keys: {required_keys - set(commit.keys())}"
        )


@pytest.mark.unit
def test_get_commit_history_respects_max_count(analyzer: GitHistoryAnalyzer) -> None:
    """max_count parameter limits the number of commits returned."""
    commits = analyzer.get_commit_history(max_count=3)
    assert len(commits) <= 3


@pytest.mark.unit
def test_contributor_stats_returns_list(analyzer: GitHistoryAnalyzer) -> None:
    """get_contributor_stats returns a non-empty list."""
    stats = analyzer.get_contributor_stats()
    assert isinstance(stats, list)
    assert len(stats) > 0


@pytest.mark.unit
def test_contributor_stats_has_required_fields(analyzer: GitHistoryAnalyzer) -> None:
    """Each contributor entry has the required aggregate fields."""
    stats = analyzer.get_contributor_stats()
    required = {"author", "commits", "insertions", "deletions",
                "first_commit", "last_commit"}
    for entry in stats:
        assert required.issubset(entry.keys()), (
            f"Missing keys: {required - set(entry.keys())}"
        )


@pytest.mark.unit
def test_contributor_stats_sorted_by_commits(analyzer: GitHistoryAnalyzer) -> None:
    """Contributors are sorted by commit count descending."""
    stats = analyzer.get_contributor_stats()
    if len(stats) >= 2:
        for i in range(len(stats) - 1):
            assert stats[i]["commits"] >= stats[i + 1]["commits"]


@pytest.mark.unit
def test_code_churn_returns_list(analyzer: GitHistoryAnalyzer) -> None:
    """get_code_churn returns a list of file churn entries."""
    churn = analyzer.get_code_churn(top_n=10)
    assert isinstance(churn, list)
    assert len(churn) > 0


@pytest.mark.unit
def test_code_churn_respects_top_n(analyzer: GitHistoryAnalyzer) -> None:
    """top_n parameter limits churn results."""
    churn = analyzer.get_code_churn(top_n=5)
    assert len(churn) <= 5


@pytest.mark.unit
def test_code_churn_required_fields(analyzer: GitHistoryAnalyzer) -> None:
    """Each churn entry has 'file' and 'change_count' fields."""
    churn = analyzer.get_code_churn(top_n=10)
    for entry in churn:
        assert "file" in entry
        assert "change_count" in entry
        assert isinstance(entry["change_count"], int)
        assert entry["change_count"] > 0


@pytest.mark.unit
def test_branch_topology_has_active_branch(analyzer: GitHistoryAnalyzer) -> None:
    """get_branch_topology returns dict with 'active_branch' key."""
    topology = analyzer.get_branch_topology()
    assert "active_branch" in topology
    assert isinstance(topology["active_branch"], str)
    assert len(topology["active_branch"]) > 0


@pytest.mark.unit
def test_branch_topology_has_branches_list(analyzer: GitHistoryAnalyzer) -> None:
    """get_branch_topology includes branches list with required fields."""
    topology = analyzer.get_branch_topology()
    assert "branches" in topology
    assert "branch_count" in topology
    assert topology["branch_count"] == len(topology["branches"])
    for branch in topology["branches"]:
        assert "name" in branch
        assert "tip_sha" in branch
        assert "tip_message" in branch
        assert "tip_date" in branch


@pytest.mark.unit
def test_commit_frequency_by_week(analyzer: GitHistoryAnalyzer) -> None:
    """Commit frequency bucketed by week uses YYYY-WNN format."""
    freq = analyzer.get_commit_frequency(by="week")
    assert isinstance(freq, dict)
    assert len(freq) > 0
    week_pattern = re.compile(r"^\d{4}-W\d{2}$")
    for key in freq:
        assert week_pattern.match(key), f"Key {key!r} doesn't match YYYY-WNN format"


@pytest.mark.unit
def test_commit_frequency_by_month(analyzer: GitHistoryAnalyzer) -> None:
    """Commit frequency bucketed by month uses YYYY-MM format."""
    freq = analyzer.get_commit_frequency(by="month")
    month_pattern = re.compile(r"^\d{4}-\d{2}$")
    for key in freq:
        assert month_pattern.match(key), f"Key {key!r} doesn't match YYYY-MM format"


@pytest.mark.unit
def test_commit_frequency_by_day(analyzer: GitHistoryAnalyzer) -> None:
    """Commit frequency bucketed by day uses YYYY-MM-DD format."""
    freq = analyzer.get_commit_frequency(by="day")
    day_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    for key in freq:
        assert day_pattern.match(key), f"Key {key!r} doesn't match YYYY-MM-DD format"


@pytest.mark.unit
def test_commit_frequency_sorted_chronologically(analyzer: GitHistoryAnalyzer) -> None:
    """Commit frequency results are sorted in chronological order."""
    freq = analyzer.get_commit_frequency(by="month")
    keys = list(freq.keys())
    assert keys == sorted(keys)


# ── New methods: filtered history ────────────────────────────────────────────


@pytest.mark.unit
def test_get_commit_history_filtered_returns_list(analyzer: GitHistoryAnalyzer) -> None:
    """get_commit_history_filtered returns a list."""
    commits = analyzer.get_commit_history_filtered(max_count=10)
    assert isinstance(commits, list)
    assert len(commits) > 0


@pytest.mark.unit
def test_get_commit_history_filtered_respects_max_count(analyzer: GitHistoryAnalyzer) -> None:
    """max_count limits filtered history results."""
    commits = analyzer.get_commit_history_filtered(max_count=3)
    assert len(commits) <= 3


@pytest.mark.unit
def test_get_commit_history_filtered_by_author(analyzer: GitHistoryAnalyzer) -> None:
    """Author filter returns only commits matching the author substring."""
    # Get any author from the repo
    all_commits = analyzer.get_commit_history(max_count=20)
    if not all_commits:
        pytest.skip("No commits in test repo")
    author_name = all_commits[0]["author"]
    # Use just first name as substring filter
    first_word = author_name.split()[0] if author_name else author_name
    filtered = analyzer.get_commit_history_filtered(author=first_word, max_count=50)
    for commit in filtered:
        assert first_word.lower() in commit["author"].lower(), (
            f"Author {commit['author']!r} does not contain {first_word!r}"
        )


# ── New methods: file history ────────────────────────────────────────────────


@pytest.mark.unit
def test_get_file_history_returns_list(analyzer: GitHistoryAnalyzer) -> None:
    """get_file_history returns a list for a known file."""
    history = analyzer.get_file_history("README.md", max_count=10)
    assert isinstance(history, list)


@pytest.mark.unit
def test_get_file_history_respects_max_count(analyzer: GitHistoryAnalyzer) -> None:
    """max_count limits file history results."""
    history = analyzer.get_file_history("README.md", max_count=3)
    assert len(history) <= 3


@pytest.mark.unit
def test_get_file_history_required_fields(analyzer: GitHistoryAnalyzer) -> None:
    """File history entries have the required metadata keys."""
    history = analyzer.get_file_history("README.md", max_count=5)
    required_keys = {"sha", "author", "email", "date", "message"}
    for commit in history:
        assert required_keys.issubset(commit.keys())


# ── New methods: directory churn ─────────────────────────────────────────────


@pytest.mark.unit
def test_get_churn_by_directory_returns_list(analyzer: GitHistoryAnalyzer) -> None:
    """get_churn_by_directory returns a non-empty list."""
    churn = analyzer.get_churn_by_directory(top_n=5)
    assert isinstance(churn, list)
    assert len(churn) > 0


@pytest.mark.unit
def test_get_churn_by_directory_required_keys(analyzer: GitHistoryAnalyzer) -> None:
    """Each directory churn entry has directory, change_count, and files keys."""
    churn = analyzer.get_churn_by_directory(top_n=5)
    for entry in churn:
        assert "directory" in entry
        assert "change_count" in entry
        assert "files" in entry
        assert isinstance(entry["change_count"], int)
        assert entry["change_count"] > 0


@pytest.mark.unit
def test_get_churn_by_directory_respects_top_n(analyzer: GitHistoryAnalyzer) -> None:
    """top_n limits directory churn results."""
    churn = analyzer.get_churn_by_directory(top_n=3)
    assert len(churn) <= 3


# ── New methods: hotspot analysis ────────────────────────────────────────────


@pytest.mark.unit
def test_get_hotspot_analysis_returns_list(analyzer: GitHistoryAnalyzer) -> None:
    """get_hotspot_analysis returns a non-empty list."""
    hotspots = analyzer.get_hotspot_analysis(top_n=5)
    assert isinstance(hotspots, list)
    assert len(hotspots) > 0


@pytest.mark.unit
def test_get_hotspot_analysis_required_keys(analyzer: GitHistoryAnalyzer) -> None:
    """Each hotspot entry has file, change_count, last_changed, hotspot_score keys."""
    hotspots = analyzer.get_hotspot_analysis(top_n=5)
    for entry in hotspots:
        assert "file" in entry
        assert "change_count" in entry
        assert "last_changed" in entry
        assert "hotspot_score" in entry
        assert isinstance(entry["hotspot_score"], float)
        assert entry["hotspot_score"] > 0


@pytest.mark.unit
def test_get_hotspot_analysis_sorted_descending(analyzer: GitHistoryAnalyzer) -> None:
    """Hotspot results are sorted by hotspot_score descending."""
    hotspots = analyzer.get_hotspot_analysis(top_n=10)
    if len(hotspots) >= 2:
        for i in range(len(hotspots) - 1):
            assert hotspots[i]["hotspot_score"] >= hotspots[i + 1]["hotspot_score"]
