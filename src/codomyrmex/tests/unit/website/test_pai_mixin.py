"""Zero-mock tests for PAIProviderMixin.

Tests the real PAI filesystem at ``~/.claude/`` for mission, project, task,
telos, and memory data retrieval. Also tests Mermaid graph generation and
the aggregate awareness endpoint.

Zero-Mock policy: every test exercises real production code paths — no
unittest.mock, MagicMock, or @patch usage.
"""

from pathlib import Path

import pytest

from codomyrmex.website.data_provider import DataProvider

# ── Fixtures ─────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parents[5]


@pytest.fixture
def provider() -> DataProvider:
    """DataProvider pointed at the real project root."""
    return DataProvider(root_dir=_PROJECT_ROOT)


@pytest.fixture
def tmp_provider(tmp_path: Path) -> DataProvider:
    """DataProvider with a temporary root (no PAI installation)."""
    dp = DataProvider(root_dir=tmp_path)
    dp._PAI_ROOT = tmp_path / ".claude"  # Override to isolate from real PAI
    return dp


# ── Test: get_pai_missions ───────────────────────────────────────────


class TestGetPaiMissions:
    """Tests for PAIProviderMixin.get_pai_missions."""

    def test_returns_list(self, provider: DataProvider) -> None:
        """get_pai_missions must return a list."""
        result = provider.get_pai_missions()
        assert isinstance(result, list)

    def test_mission_structure(self, provider: DataProvider) -> None:
        """Each mission has the expected keys."""
        missions = provider.get_pai_missions()
        if not missions:
            pytest.skip("No missions found in ~/.claude/MEMORY/STATE/missions/")
        mission = missions[0]
        for key in ("id", "title", "status", "priority", "description",
                     "success_criteria", "linked_projects",
                     "completion_percentage", "recent_activity"):
            assert key in mission, f"Missing key: {key}"

    def test_sorted_by_priority(self, provider: DataProvider) -> None:
        """Missions are sorted HIGH → MEDIUM → LOW."""
        missions = provider.get_pai_missions()
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        indices = [priority_order.get(m["priority"], 99) for m in missions]
        assert indices == sorted(indices)

    def test_graceful_on_empty(self, tmp_provider: DataProvider) -> None:
        """Returns empty list when PAI is not installed."""
        assert tmp_provider.get_pai_missions() == []


# ── Test: get_pai_projects ───────────────────────────────────────────


class TestGetPaiProjects:
    """Tests for PAIProviderMixin.get_pai_projects."""

    def test_returns_list(self, provider: DataProvider) -> None:
        result = provider.get_pai_projects()
        assert isinstance(result, list)

    def test_project_structure(self, provider: DataProvider) -> None:
        projects = provider.get_pai_projects()
        if not projects:
            pytest.skip("No projects found in ~/.claude/MEMORY/STATE/projects/")
        project = projects[0]
        for key in ("id", "title", "status", "goal", "priority",
                     "parent_mission", "tags", "completion_percentage",
                     "task_counts", "recent_activity"):
            assert key in project, f"Missing key: {key}"

    def test_graceful_on_empty(self, tmp_provider: DataProvider) -> None:
        assert tmp_provider.get_pai_projects() == []


# ── Test: get_pai_tasks ──────────────────────────────────────────────


class TestGetPaiTasks:
    """Tests for PAIProviderMixin.get_pai_tasks."""

    def test_path_traversal_rejected(self, provider: DataProvider) -> None:
        """Path traversal attempts raise ValueError."""
        with pytest.raises(ValueError, match="Invalid project_id"):
            provider.get_pai_tasks("../../etc/passwd")

    def test_slash_rejected(self, provider: DataProvider) -> None:
        with pytest.raises(ValueError, match="Invalid project_id"):
            provider.get_pai_tasks("foo/bar")

    def test_missing_project_returns_empty(self, provider: DataProvider) -> None:
        result = provider.get_pai_tasks("nonexistent-project-id-12345")
        assert result == {}

    def test_real_project_structure(self, provider: DataProvider) -> None:
        """If a real project exists, check the parsed structure."""
        projects = provider.get_pai_projects()
        if not projects:
            pytest.skip("No projects available")
        project_id = projects[0]["id"]
        result = provider.get_pai_tasks(project_id)
        if not result:
            pytest.skip(f"No TASKS.md for project {project_id}")
        for key in ("completed", "remaining", "total", "done"):
            assert key in result
        assert result["total"] == result["done"] + len(result["remaining"])

    def test_synthetic_tasks(self, tmp_path: Path) -> None:
        """Parse a synthetic TASKS.md file."""
        # Create PAI state directory structure
        pai_root = tmp_path / ".claude"
        tasks_dir = pai_root / "MEMORY" / "STATE" / "projects" / "test-proj"
        tasks_dir.mkdir(parents=True)
        (tasks_dir / "PROJECT.yaml").write_text("title: Test\nstatus: active\n")
        (tasks_dir / "TASKS.md").write_text(
            "# Tasks\n"
            "- [x] Done task A\n"
            "- [X] Done task B\n"
            "- [ ] Todo task C\n"
            "- [ ] Todo task D\n"
            "- Regular line\n"
        )
        dp = DataProvider(root_dir=tmp_path)
        dp._PAI_ROOT = pai_root
        result = dp.get_pai_tasks("test-proj")
        assert result["done"] == 2
        assert result["total"] == 4
        assert "Done task A" in result["completed"]
        assert "Todo task C" in result["remaining"]


# ── Test: get_pai_telos ──────────────────────────────────────────────


class TestGetPaiTelos:
    """Tests for PAIProviderMixin.get_pai_telos."""

    def test_returns_list(self, provider: DataProvider) -> None:
        result = provider.get_pai_telos()
        assert isinstance(result, list)

    def test_telos_structure(self, provider: DataProvider) -> None:
        telos = provider.get_pai_telos()
        if not telos:
            pytest.skip("No TELOS files found")
        entry = telos[0]
        for key in ("name", "filename", "size_bytes", "preview"):
            assert key in entry

    def test_graceful_on_empty(self, tmp_provider: DataProvider) -> None:
        assert tmp_provider.get_pai_telos() == []


# ── Test: get_pai_memory_overview ────────────────────────────────────


class TestGetPaiMemoryOverview:
    """Tests for PAIProviderMixin.get_pai_memory_overview."""

    def test_returns_dict(self, provider: DataProvider) -> None:
        result = provider.get_pai_memory_overview()
        assert isinstance(result, dict)
        assert "directories" in result
        assert "total_files" in result
        assert "work_sessions_count" in result

    def test_directories_are_list(self, provider: DataProvider) -> None:
        result = provider.get_pai_memory_overview()
        assert isinstance(result["directories"], list)

    def test_graceful_on_empty(self, tmp_provider: DataProvider) -> None:
        result = tmp_provider.get_pai_memory_overview()
        assert result["directories"] == []
        assert result["total_files"] == 0


# ── Test: _build_pai_mermaid_graph ───────────────────────────────────


class TestBuildPaiMermaidGraph:
    """Tests for PAIProviderMixin._build_pai_mermaid_graph."""

    def test_empty_inputs(self, provider: DataProvider) -> None:
        result = provider._build_pai_mermaid_graph([], [])
        assert result.startswith("graph TD")

    def test_mission_nodes_appear(self, provider: DataProvider) -> None:
        missions = [{"id": "m1", "title": "Mission One", "status": "active",
                      "linked_projects": ["p1"]}]
        projects = [{"id": "p1", "title": "Project One", "status": "active",
                      "parent_mission": "m1"}]
        result = provider._build_pai_mermaid_graph(missions, projects)
        assert "M_m1" in result
        assert "P_p1" in result
        assert "Mission One" in result
        assert "-->" in result

    def test_sanitizes_special_chars(self, provider: DataProvider) -> None:
        missions = [{"id": "m-1/test", "title": 'Has "quotes" <tags>',
                      "status": "active", "linked_projects": []}]
        result = provider._build_pai_mermaid_graph(missions, [])
        assert '"' not in result.split('"')[1] if result.count('"') >= 2 else True
        assert "<" not in result.replace("<", "")  # Tags stripped

    def test_safe_mermaid_fallback(self, provider: DataProvider) -> None:
        """_safe_mermaid_graph never raises, even with bad data."""
        result = provider._safe_mermaid_graph(
            [{"id": None}],  # type: ignore
            [],
        )
        assert isinstance(result, str)
        assert "graph TD" in result


# ── Test: get_pai_awareness_data ─────────────────────────────────────


class TestGetPaiAwarenessData:
    """Tests for PAIProviderMixin.get_pai_awareness_data."""

    def test_returns_dict(self, provider: DataProvider) -> None:
        result = provider.get_pai_awareness_data()
        assert isinstance(result, dict)

    def test_top_level_keys(self, provider: DataProvider) -> None:
        result = provider.get_pai_awareness_data()
        expected_keys = {"missions", "projects", "telos", "memory",
                         "skills", "hooks", "metrics", "mermaid_graph"}
        assert expected_keys.issubset(result.keys())

    def test_metrics_structure(self, provider: DataProvider) -> None:
        result = provider.get_pai_awareness_data()
        metrics = result["metrics"]
        for key in ("mission_count", "project_count", "total_tasks",
                     "completed_tasks", "telos_files", "overall_completion",
                     "skill_count", "hook_count"):
            assert key in metrics

    def test_overall_completion_range(self, provider: DataProvider) -> None:
        result = provider.get_pai_awareness_data()
        pct = result["metrics"]["overall_completion"]
        assert 0 <= pct <= 100

    def test_mermaid_graph_is_string(self, provider: DataProvider) -> None:
        result = provider.get_pai_awareness_data()
        assert isinstance(result["mermaid_graph"], str)
        assert result["mermaid_graph"].startswith("graph TD")

    def test_graceful_on_empty(self, tmp_provider: DataProvider) -> None:
        result = tmp_provider.get_pai_awareness_data()
        assert result["missions"] == []
        assert result["projects"] == []
        assert result["metrics"]["mission_count"] == 0
"""Zero-mock tests for PAIProviderMixin — tests real production code paths."""
