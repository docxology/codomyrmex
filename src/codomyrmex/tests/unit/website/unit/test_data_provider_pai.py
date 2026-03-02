"""
Unit tests for the DataProvider class — PAI-specific methods.

Tests cover:
- PAI missions retrieval
- PAI projects retrieval
- PAI tasks retrieval and security
- PAI TELOS data
- PAI memory overview
- PAI awareness data aggregation
- PAI Mermaid graph building
"""

import json
import sys
from pathlib import Path

import pytest

# Add src to path for imports
TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent.parent
SRC_DIR = MODULE_DIR.parent.parent
sys.path.insert(0, str(SRC_DIR))

from codomyrmex.website.data_provider import DataProvider


def _make_provider(tmp_path):
    """Create a DataProvider with _PAI_ROOT pointing to tmp_path."""
    provider = DataProvider(tmp_path)
    provider._PAI_ROOT = tmp_path
    return provider


@pytest.mark.unit
class TestGetPaiMissions:
    """Tests for get_pai_missions() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_missions()
        assert isinstance(result, list)

    def test_empty_when_no_dir(self, tmp_path):
        """Test empty list when missions dir doesn't exist."""
        provider = _make_provider(tmp_path)
        assert provider.get_pai_missions() == []

    def test_reads_mission_yaml(self, tmp_path):
        """Test that MISSION.yaml is parsed correctly."""
        m_dir = tmp_path / "MEMORY" / "STATE" / "missions" / "m1"
        m_dir.mkdir(parents=True)
        (m_dir / "MISSION.yaml").write_text(
            "title: Test Mission\nstatus: active\npriority: HIGH\n"
            "description: A test\nlinked_projects:\n  - p1\n"
        )
        provider = _make_provider(tmp_path)
        result = provider.get_pai_missions()
        assert len(result) == 1
        assert result[0]["title"] == "Test Mission"
        assert result[0]["status"] == "active"
        assert result[0]["priority"] == "HIGH"
        assert "p1" in result[0]["linked_projects"]

    def test_merges_progress_json(self, tmp_path):
        """Test that progress.json is merged into mission data."""
        m_dir = tmp_path / "MEMORY" / "STATE" / "missions" / "m1"
        m_dir.mkdir(parents=True)
        (m_dir / "MISSION.yaml").write_text("title: M1\nstatus: active\npriority: MEDIUM\n")
        (m_dir / "progress.json").write_text(json.dumps({"completion_percentage": 75}))

        provider = _make_provider(tmp_path)
        result = provider.get_pai_missions()
        assert result[0]["completion_percentage"] == 75

    def test_skips_non_dict_yaml(self, tmp_path):
        """Test that YAML files that don't parse to dict are skipped."""
        missions_dir = tmp_path / "MEMORY" / "STATE" / "missions"
        bad = missions_dir / "bad"
        bad.mkdir(parents=True)
        # This parses as a string, not a dict — should be skipped
        (bad / "MISSION.yaml").write_text("just a plain string")

        good = missions_dir / "good"
        good.mkdir(parents=True)
        (good / "MISSION.yaml").write_text("title: Good\nstatus: active\npriority: LOW\n")

        provider = _make_provider(tmp_path)
        result = provider.get_pai_missions()
        assert len(result) == 1
        assert result[0]["title"] == "Good"

    def test_sorts_by_priority(self, tmp_path):
        """Test that missions are sorted HIGH > MEDIUM > LOW."""
        missions_dir = tmp_path / "MEMORY" / "STATE" / "missions"
        for name, prio in [("low", "LOW"), ("high", "HIGH"), ("med", "MEDIUM")]:
            d = missions_dir / name
            d.mkdir(parents=True)
            (d / "MISSION.yaml").write_text(f"title: {name}\nstatus: active\npriority: {prio}\n")

        provider = _make_provider(tmp_path)
        result = provider.get_pai_missions()
        priorities = [m["priority"] for m in result]
        assert priorities == ["HIGH", "MEDIUM", "LOW"]


@pytest.mark.unit
class TestGetPaiProjects:
    """Tests for get_pai_projects() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = _make_provider(tmp_path)
        assert isinstance(provider.get_pai_projects(), list)

    def test_empty_when_no_dir(self, tmp_path):
        """Test empty list when projects dir doesn't exist."""
        provider = _make_provider(tmp_path)
        assert provider.get_pai_projects() == []

    def test_reads_project_yaml(self, tmp_path):
        """Test that PROJECT.yaml is parsed correctly."""
        p_dir = tmp_path / "MEMORY" / "STATE" / "projects" / "p1"
        p_dir.mkdir(parents=True)
        (p_dir / "PROJECT.yaml").write_text(
            "title: Test Project\nstatus: in_progress\n"
            "goal: Build something\npriority: HIGH\nparent_mission: m1\ntags:\n  - python\n"
        )
        provider = _make_provider(tmp_path)
        result = provider.get_pai_projects()
        assert len(result) == 1
        assert result[0]["title"] == "Test Project"
        assert result[0]["parent_mission"] == "m1"
        assert "python" in result[0]["tags"]

    def test_merges_progress_json(self, tmp_path):
        """Test that progress.json is merged."""
        p_dir = tmp_path / "MEMORY" / "STATE" / "projects" / "p1"
        p_dir.mkdir(parents=True)
        (p_dir / "PROJECT.yaml").write_text("title: P1\nstatus: active\n")
        (p_dir / "progress.json").write_text(json.dumps({
            "completion_percentage": 50,
            "task_counts": {"completed": 5, "total": 10}
        }))

        provider = _make_provider(tmp_path)
        result = provider.get_pai_projects()
        assert result[0]["completion_percentage"] == 50
        assert result[0]["task_counts"]["completed"] == 5

    def test_skips_non_dict_yaml(self, tmp_path):
        """Test that YAML that doesn't parse to dict is skipped."""
        projects_dir = tmp_path / "MEMORY" / "STATE" / "projects"
        bad = projects_dir / "bad"
        bad.mkdir(parents=True)
        # This parses as a list, not a dict — should be skipped
        (bad / "PROJECT.yaml").write_text("- item1\n- item2\n")

        good = projects_dir / "good"
        good.mkdir(parents=True)
        (good / "PROJECT.yaml").write_text("title: Good\nstatus: active\n")

        provider = _make_provider(tmp_path)
        result = provider.get_pai_projects()
        assert len(result) == 1
        assert result[0]["title"] == "Good"


@pytest.mark.unit
class TestGetPaiTasks:
    """Tests for get_pai_tasks() method."""

    def test_rejects_traversal(self, tmp_path):
        """Test that .. in project_id raises ValueError."""
        provider = _make_provider(tmp_path)
        with pytest.raises(ValueError):
            provider.get_pai_tasks("../../../etc")

    def test_rejects_slash(self, tmp_path):
        """Test that / in project_id raises ValueError."""
        provider = _make_provider(tmp_path)
        with pytest.raises(ValueError):
            provider.get_pai_tasks("foo/bar")

    def test_parses_task_sections(self, tmp_path):
        """Test that - [ ] and - [x] lines are parsed."""
        p_dir = tmp_path / "MEMORY" / "STATE" / "projects" / "p1"
        p_dir.mkdir(parents=True)
        (p_dir / "TASKS.md").write_text(
            "# Tasks\n- [x] Done task\n- [ ] Todo task\n- [X] Also done\n"
        )
        provider = _make_provider(tmp_path)
        result = provider.get_pai_tasks("p1")
        assert result["done"] == 2
        assert result["total"] == 3
        assert "Done task" in result["completed"]
        assert "Todo task" in result["remaining"]

    def test_empty_for_missing_project(self, tmp_path):
        """Test empty dict for missing project."""
        provider = _make_provider(tmp_path)
        assert provider.get_pai_tasks("nonexistent") == {}


@pytest.mark.unit
class TestGetPaiTelos:
    """Tests for get_pai_telos() method."""

    def test_returns_list(self, tmp_path):
        """Test that a list is returned."""
        provider = _make_provider(tmp_path)
        assert isinstance(provider.get_pai_telos(), list)

    def test_empty_when_no_dir(self, tmp_path):
        """Test empty list when TELOS dir doesn't exist."""
        provider = _make_provider(tmp_path)
        assert provider.get_pai_telos() == []

    def test_reads_md_files_with_preview(self, tmp_path):
        """Test that .md files are read with 200-char preview."""
        telos_dir = tmp_path / "skills" / "PAI" / "USER" / "TELOS"
        telos_dir.mkdir(parents=True)
        (telos_dir / "goals.md").write_text("# My Goals\nBe awesome\n" + "x" * 300)
        (telos_dir / "notes.txt").write_text("not markdown")  # Should be skipped

        provider = _make_provider(tmp_path)
        result = provider.get_pai_telos()
        assert len(result) == 1
        assert result[0]["name"] == "goals"
        assert len(result[0]["preview"]) == 200

    def test_sorted_by_name(self, tmp_path):
        """Test that files are sorted by name."""
        telos_dir = tmp_path / "skills" / "PAI" / "USER" / "TELOS"
        telos_dir.mkdir(parents=True)
        (telos_dir / "zebra.md").write_text("Z")
        (telos_dir / "alpha.md").write_text("A")

        provider = _make_provider(tmp_path)
        result = provider.get_pai_telos()
        names = [t["name"] for t in result]
        assert names == ["alpha", "zebra"]


@pytest.mark.unit
class TestGetPaiMemoryOverview:
    """Tests for get_pai_memory_overview() method."""

    def test_returns_dict(self, tmp_path):
        """Test that a dict is returned."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_memory_overview()
        assert isinstance(result, dict)

    def test_empty_when_no_dir(self, tmp_path):
        """Test empty structure when MEMORY dir doesn't exist."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_memory_overview()
        assert result["directories"] == []
        assert result["total_files"] == 0

    def test_counts_subdirs_correctly(self, tmp_path):
        """Test that subdirectory counts are accurate."""
        mem_dir = tmp_path / "MEMORY"
        mem_dir.mkdir()
        work = mem_dir / "WORK"
        work.mkdir()
        (work / "session1").mkdir()
        (work / "session2").mkdir()
        (work / "notes.txt").write_text("hi")

        state = mem_dir / "STATE"
        state.mkdir()
        (state / "config.json").write_text("{}")

        provider = _make_provider(tmp_path)
        result = provider.get_pai_memory_overview()
        assert len(result["directories"]) == 2
        assert result["work_sessions_count"] == 2

        work_entry = next(d for d in result["directories"] if d["name"] == "WORK")
        assert work_entry["file_count"] == 1  # notes.txt
        assert work_entry["subdir_count"] == 2


@pytest.mark.unit
class TestGetPaiAwarenessData:
    """Tests for get_pai_awareness_data() method."""

    def test_returns_all_keys(self, tmp_path):
        """Test that all expected top-level keys are present."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_awareness_data()
        assert "missions" in result
        assert "projects" in result
        assert "telos" in result
        assert "memory" in result
        assert "metrics" in result
        assert "mermaid_graph" in result

    def test_metrics_computed(self, tmp_path):
        """Test that metrics are computed from data."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_awareness_data()
        assert result["metrics"]["mission_count"] == 0
        assert result["metrics"]["project_count"] == 0
        assert result["metrics"]["overall_completion"] == 0

    def test_includes_mermaid_graph(self, tmp_path):
        """Test that mermaid_graph is a string starting with graph TD."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_awareness_data()
        assert isinstance(result["mermaid_graph"], str)
        assert "graph TD" in result["mermaid_graph"]


@pytest.mark.unit
class TestBuildPaiMermaidGraph:
    """Tests for _build_pai_mermaid_graph() method."""

    def test_minimal_graph_for_empty_input(self, tmp_path):
        """Test that empty missions/projects produces valid graph."""
        provider = _make_provider(tmp_path)
        result = provider._build_pai_mermaid_graph([], [])
        assert "graph TD" in result

    def test_valid_syntax_with_data(self, tmp_path):
        """Test that graph with missions and projects has valid structure."""
        missions = [{"id": "m1", "title": "Mission 1", "status": "active", "linked_projects": ["p1"]}]
        projects = [{"id": "p1", "title": "Project 1", "status": "in_progress", "parent_mission": "m1"}]

        provider = _make_provider(tmp_path)
        result = provider._build_pai_mermaid_graph(missions, projects)
        assert "M_m1" in result
        assert "P_p1" in result
        assert "-->" in result

    def test_orphan_projects_handled(self, tmp_path):
        """Test that projects without mission links still appear."""
        projects = [{"id": "orphan", "title": "Orphan", "status": "active", "parent_mission": ""}]

        provider = _make_provider(tmp_path)
        result = provider._build_pai_mermaid_graph([], projects)
        assert "P_orphan" in result


@pytest.mark.unit
class TestGetPaiTasksSecurity:
    """Security tests for get_pai_tasks()."""

    def test_encoded_traversal(self, tmp_path):
        """Test that encoded path traversal chars are caught."""
        provider = _make_provider(tmp_path)
        with pytest.raises(ValueError):
            provider.get_pai_tasks("..%2F..%2Fetc")

    def test_empty_string_project_id(self, tmp_path):
        """Test that empty string returns empty dict (no crash)."""
        provider = _make_provider(tmp_path)
        result = provider.get_pai_tasks("")
        assert result == {}
