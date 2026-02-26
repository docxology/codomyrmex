"""
Unit tests for DataProvider PAI mixin — Zero-Mock compliant.

Creates real filesystem structure matching PAI memory layout to exercise
get_pai_missions, get_pai_projects, get_pai_tasks, get_pai_telos,
get_pai_memory_overview, _build_pai_mermaid_graph, and get_pai_awareness_data.

Note: _PAI_ROOT is overridden as an instance attribute on each DataProvider
so tests are fully isolated from the real ~/.claude directory.
"""
import pytest
from pathlib import Path
from codomyrmex.website.data_provider import DataProvider


def _seed_pai_memory(tmp_path: Path) -> Path:
    """Create minimal PAI-like memory structure under tmp_path."""
    # ~/.claude-like structure under tmp_path
    claude = tmp_path / ".claude"
    mem = claude / "MEMORY"
    state = mem / "STATE"

    # Missions
    missions = state / "missions" / "codomyrmex"
    missions.mkdir(parents=True)
    (missions / "MISSION.yaml").write_text(
        "title: Build Codomyrmex\npriority: HIGH\nstatus: active\n"
    )
    (missions / "progress.json").write_text('{"completion_percentage": 42}')

    # Projects
    projects = state / "projects" / "dashboard"
    projects.mkdir(parents=True)
    (projects / "PROJECT.yaml").write_text(
        "title: Dashboard\nstatus: active\nparent_mission: codomyrmex\n"
    )
    (projects / "TASKS.md").write_text(
        "# Tasks\n- [x] Phase 1\n- [ ] Phase 3\n"
    )

    # Work sessions
    work = mem / "WORK" / "session-abc"
    work.mkdir(parents=True)
    (work / "META.yaml").write_text("title: Test session\n")

    # Telos
    telos = claude / "skills" / "PAI" / "USER" / "TELOS"
    telos.mkdir(parents=True)
    (telos / "goals.md").write_text("# Goals\nBe excellent.\n")

    return claude


def _make_provider(tmp_path: Path) -> DataProvider:
    """Create DataProvider with _PAI_ROOT overridden to the seeded tmp dir."""
    dp = DataProvider(tmp_path)
    dp._PAI_ROOT = tmp_path / ".claude"  # Override class attr with instance attr
    return dp


@pytest.mark.unit
class TestGetPaiMissions:
    def test_returns_list(self, tmp_path):
        """get_pai_missions returns a list."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        result = dp.get_pai_missions()
        assert isinstance(result, list)

    def test_empty_when_no_missions_dir(self, tmp_path):
        """get_pai_missions returns [] gracefully when directory is absent."""
        dp = _make_provider(tmp_path)
        result = dp.get_pai_missions()
        assert result == []

    def test_mission_has_expected_keys(self, tmp_path):
        """Each mission entry has title and status."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        missions = dp.get_pai_missions()
        assert len(missions) == 1
        m = missions[0]
        assert "title" in m
        assert "status" in m

    def test_mission_title_from_yaml(self, tmp_path):
        """Mission title matches what was written to MISSION.yaml."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        missions = dp.get_pai_missions()
        assert missions[0]["title"] == "Build Codomyrmex"


@pytest.mark.unit
class TestGetPaiProjects:
    def test_returns_list(self, tmp_path):
        """get_pai_projects returns a list."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        result = dp.get_pai_projects()
        assert isinstance(result, list)

    def test_empty_when_no_projects_dir(self, tmp_path):
        """get_pai_projects returns [] gracefully when directory is absent."""
        dp = _make_provider(tmp_path)
        result = dp.get_pai_projects()
        assert result == []

    def test_project_has_expected_keys(self, tmp_path):
        """Each project entry has title and status."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        projects = dp.get_pai_projects()
        assert len(projects) == 1
        p = projects[0]
        assert "title" in p
        assert "status" in p

    def test_project_title_from_yaml(self, tmp_path):
        """Project title matches what was written to PROJECT.yaml."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        projects = dp.get_pai_projects()
        assert projects[0]["title"] == "Dashboard"


@pytest.mark.unit
class TestGetPaiTasks:
    def test_returns_dict_for_known_project(self, tmp_path):
        """get_pai_tasks returns a dict for a known project."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        result = dp.get_pai_tasks("dashboard")
        assert isinstance(result, dict)

    def test_empty_dict_for_unknown_project(self, tmp_path):
        """get_pai_tasks returns {} for unknown project_id."""
        dp = _make_provider(tmp_path)
        result = dp.get_pai_tasks("nonexistent_xyz")
        assert result == {}

    def test_task_dict_has_done_and_completed_fields(self, tmp_path):
        """Task dict has 'done' (int count) and 'completed' (list) from TASKS.md."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        tasks = dp.get_pai_tasks("dashboard")
        assert "done" in tasks
        assert "completed" in tasks
        assert isinstance(tasks["completed"], list)

    def test_checkbox_parsing_counts_correctly(self, tmp_path):
        """Checked [x] and unchecked [ ] tasks are parsed separately."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        tasks = dp.get_pai_tasks("dashboard")
        # TASKS.md has 1 checked and 1 unchecked item
        assert tasks["done"] == 1
        assert len(tasks["remaining"]) == 1
        assert tasks["total"] == 2

    def test_traversal_rejected(self, tmp_path):
        """get_pai_tasks raises ValueError for path traversal."""
        dp = _make_provider(tmp_path)
        with pytest.raises(ValueError):
            dp.get_pai_tasks("../evil")


@pytest.mark.unit
class TestGetPaiMemoryOverview:
    def test_returns_dict(self, tmp_path):
        """get_pai_memory_overview returns a dict."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        result = dp.get_pai_memory_overview()
        assert isinstance(result, dict)

    def test_returns_dict_when_no_memory(self, tmp_path):
        """get_pai_memory_overview returns dict even when MEMORY dir is absent."""
        dp = _make_provider(tmp_path)
        result = dp.get_pai_memory_overview()
        assert isinstance(result, dict)

    def test_has_required_keys(self, tmp_path):
        """Memory overview has directories, total_files, work_sessions_count."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        result = dp.get_pai_memory_overview()
        assert "directories" in result
        assert "total_files" in result
        assert "work_sessions_count" in result

    def test_work_sessions_counted(self, tmp_path):
        """work_sessions_count reflects seeded session directories."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        result = dp.get_pai_memory_overview()
        assert result["work_sessions_count"] >= 1


@pytest.mark.unit
class TestBuildPaiMermaidGraph:
    def test_returns_string(self, tmp_path):
        """_build_pai_mermaid_graph returns a non-empty string."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        missions = dp.get_pai_missions()
        projects = dp.get_pai_projects()
        result = dp._build_pai_mermaid_graph(missions, projects)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_mermaid_header(self, tmp_path):
        """Graph string starts with 'graph TD' (Mermaid syntax)."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        missions = dp.get_pai_missions()
        projects = dp.get_pai_projects()
        result = dp._build_pai_mermaid_graph(missions, projects)
        assert result.strip().startswith("graph TD")

    def test_returns_string_with_empty_inputs(self, tmp_path):
        """_build_pai_mermaid_graph returns valid graph with empty lists."""
        dp = _make_provider(tmp_path)
        result = dp._build_pai_mermaid_graph([], [])
        assert isinstance(result, str)
        assert result.strip().startswith("graph TD")


@pytest.mark.unit
class TestGetPaiAwarenessData:
    def test_returns_dict_with_required_keys(self, tmp_path):
        """get_pai_awareness_data returns dict with missions, projects, mermaid_graph."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        result = dp.get_pai_awareness_data()
        assert isinstance(result, dict)
        assert "missions" in result
        assert "projects" in result
        assert "mermaid_graph" in result

    def test_missions_is_list(self, tmp_path):
        """get_pai_awareness_data['missions'] is a list."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        result = dp.get_pai_awareness_data()
        assert isinstance(result["missions"], list)

    def test_mermaid_graph_is_string(self, tmp_path):
        """get_pai_awareness_data['mermaid_graph'] is a string."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        result = dp.get_pai_awareness_data()
        assert isinstance(result["mermaid_graph"], str)

    def test_returns_safely_when_no_pai_data(self, tmp_path):
        """get_pai_awareness_data returns valid structure even with empty filesystem."""
        dp = _make_provider(tmp_path)
        result = dp.get_pai_awareness_data()
        assert isinstance(result, dict)
        assert "missions" in result
        assert "projects" in result
        assert "mermaid_graph" in result

    def test_metrics_key_present(self, tmp_path):
        """get_pai_awareness_data includes a metrics dict."""
        _seed_pai_memory(tmp_path)
        dp = _make_provider(tmp_path)
        result = dp.get_pai_awareness_data()
        assert "metrics" in result
        assert isinstance(result["metrics"], dict)
