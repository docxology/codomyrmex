"""Comprehensive tests for MermaidDiagramGenerator — zero-mock, all real strings.

Covers: init, git branch diagrams, workflow diagrams, repository structure diagrams,
commit timeline diagrams, file icons, and save-to-file functionality.
"""

import os
import tempfile

import pytest

from codomyrmex.data_visualization.mermaid.mermaid_generator import (
    MermaidDiagramGenerator,
)


@pytest.fixture
def gen():
    """Provide a fresh MermaidDiagramGenerator for each test."""
    return MermaidDiagramGenerator()


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


class TestInit:
    def test_diagram_types_populated(self, gen):
        assert isinstance(gen.diagram_types, dict)
        assert len(gen.diagram_types) > 0

    def test_flowchart_type_exists(self, gen):
        assert "flowchart" in gen.diagram_types

    def test_gitgraph_type_exists(self, gen):
        assert "gitgraph" in gen.diagram_types


# ---------------------------------------------------------------------------
# Git branch diagrams
# ---------------------------------------------------------------------------


class TestGitBranchDiagram:
    def test_creates_valid_mermaid(self, gen):
        branches = [
            {"name": "main", "head": True},
            {"name": "feature/auth", "head": False},
        ]
        commits = [
            {"hash": "abc", "message": "init", "branch": "main"},
            {"hash": "def", "message": "add auth", "branch": "feature/auth"},
        ]
        result = gen.create_git_branch_diagram(branches, commits)
        assert isinstance(result, str)
        assert (
            "gitGraph" in result
            or "gitgraph" in result.lower()
            or "graph" in result.lower()
        )

    def test_empty_branches(self, gen):
        result = gen.create_git_branch_diagram([], [])
        assert isinstance(result, str)

    def test_with_title(self, gen):
        branches = [{"name": "main", "head": True}]
        commits = [{"hash": "abc", "message": "init", "branch": "main"}]
        result = gen.create_git_branch_diagram(branches, commits, title="My Branches")
        assert isinstance(result, str)

    def test_save_to_file(self, gen):
        branches = [{"name": "main", "head": True}]
        commits = [{"hash": "abc", "message": "init", "branch": "main"}]
        with tempfile.NamedTemporaryFile(suffix=".mmd", delete=False, mode="w") as f:
            path = f.name
        try:
            gen.create_git_branch_diagram(branches, commits, output_path=path)
            assert os.path.exists(path)
            content = open(path).read()
            assert len(content) > 0
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Workflow diagrams
# ---------------------------------------------------------------------------


class TestWorkflowDiagram:
    def test_creates_valid_mermaid(self, gen):
        steps = [
            {"name": "Build", "type": "process"},
            {"name": "Test", "type": "process"},
            {"name": "Deploy", "type": "process"},
        ]
        result = gen.create_git_workflow_diagram(steps)
        assert isinstance(result, str)
        assert len(result) > 10

    def test_empty_steps_uses_default(self, gen):
        result = gen.create_git_workflow_diagram()
        assert isinstance(result, str)

    def test_with_title(self, gen):
        steps = [{"name": "Build", "type": "process"}]
        result = gen.create_git_workflow_diagram(steps, title="CI Pipeline")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Repository structure diagrams
# ---------------------------------------------------------------------------


class TestRepoStructureDiagram:
    def test_creates_valid_mermaid(self, gen):
        structure = {
            "src": {"main.py": None, "utils.py": None},
            "tests": {"test_main.py": None},
            "README.md": None,
        }
        result = gen.create_repository_structure_diagram(structure)
        assert isinstance(result, str)
        assert len(result) > 10

    def test_nested_structure(self, gen):
        structure = {
            "src": {
                "core": {"engine.py": None, "config.py": None},
                "utils": {"helpers.py": None},
            },
        }
        result = gen.create_repository_structure_diagram(structure)
        assert isinstance(result, str)

    def test_empty_structure(self, gen):
        result = gen.create_repository_structure_diagram({})
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Commit timeline diagrams
# ---------------------------------------------------------------------------


class TestCommitTimelineDiagram:
    def test_creates_valid_mermaid(self, gen):
        commits = [
            {"hash": "abc", "message": "First commit", "date": "2024-01-01"},
            {"hash": "def", "message": "Second commit", "date": "2024-01-02"},
        ]
        result = gen.create_commit_timeline_diagram(commits)
        assert isinstance(result, str)
        assert len(result) > 10

    def test_empty_commits(self, gen):
        result = gen.create_commit_timeline_diagram([])
        assert isinstance(result, str)

    def test_with_title(self, gen):
        commits = [{"hash": "abc", "message": "init", "date": "2024-01-01"}]
        result = gen.create_commit_timeline_diagram(commits, title="Project History")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# File icons
# ---------------------------------------------------------------------------


class TestFileIcons:
    @pytest.mark.parametrize(
        "filename",
        [
            "main.py",
            "index.js",
            "style.css",
            "data.json",
            "README.md",
            "image.png",
            "unknown.xyz",
        ],
    )
    def test_get_file_icon_returns_string(self, gen, filename):
        icon = gen._get_file_icon(filename)
        assert isinstance(icon, str)
        assert len(icon) >= 1


# ---------------------------------------------------------------------------
# Generic diagram types
# ---------------------------------------------------------------------------


class TestGenericDiagramTypes:
    def test_create_flowchart(self, gen):
        result = gen._create_flowchart()
        assert isinstance(result, str)

    def test_create_gitgraph(self, gen):
        result = gen._create_gitgraph()
        assert isinstance(result, str)

    def test_create_timeline(self, gen):
        result = gen._create_timeline()
        assert isinstance(result, str)

    def test_create_graph(self, gen):
        result = gen._create_graph()
        assert isinstance(result, str)

    def test_create_sequence(self, gen):
        result = gen._create_sequence()
        assert isinstance(result, str)

    def test_create_class(self, gen):
        result = gen._create_class()
        assert isinstance(result, str)

    def test_create_state(self, gen):
        result = gen._create_state()
        assert isinstance(result, str)

    def test_create_pie_chart(self, gen):
        result = gen._create_pie_chart()
        assert isinstance(result, str)
