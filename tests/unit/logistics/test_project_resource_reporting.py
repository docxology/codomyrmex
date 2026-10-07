"""Tests for project/resource reporting and the orchestration MCP adapter.

Covers ProjectManager.get_projects_summary / update_project_metrics /
add_project_milestone / create_project(path=...), ResourceManager
.get_resource_usage, the package-level ``create_project`` helper, and the
class-based OrchestrationMCPTools project and workflow tools.

Zero-mock policy: real managers on ``tmp_path``.
"""

from __future__ import annotations

import pytest

import codomyrmex.logistics.orchestration.project as project_pkg
from codomyrmex.logistics.orchestration.project.project_manager import (
    ProjectManager,
    ProjectStatus,
    ProjectType,
)
from codomyrmex.logistics.orchestration.project.resource_manager import (
    ResourceManager,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def pm(tmp_path) -> ProjectManager:
    return ProjectManager(projects_root=tmp_path)


class TestProjectManagerReporting:
    def test_summary_of_empty_manager(self, pm):
        assert pm.get_projects_summary() == {
            "total_projects": 0,
            "by_status": {},
            "by_type": {},
            "recent_activity": [],
        }

    def test_summary_counts_real_projects(self, pm):
        pm.create_project("a", ProjectType.RESEARCH)
        pm.create_project("b", ProjectType.RESEARCH)
        pm.create_project("c", ProjectType.ML_MODEL)
        pm.update_project_status("a", ProjectStatus.PAUSED)

        summary = pm.get_projects_summary()

        assert summary["total_projects"] == 3
        assert summary["by_type"] == {"research": 2, "ml_model": 1}
        assert summary["by_status"] == {"paused": 1, "active": 2}
        assert summary["recent_activity"][0]["name"] == "a"  # most recently updated

    def test_metrics_merge(self, pm):
        pm.create_project("a", ProjectType.CUSTOM)
        assert pm.update_project_metrics("a", {"x": 1}) is True
        assert pm.update_project_metrics("a", {"y": 2}) is True
        assert pm.get_project("a").metrics == {"x": 1, "y": 2}
        assert pm.update_project_metrics("missing", {"x": 1}) is False

    def test_milestones_recorded_with_timestamp(self, pm):
        pm.create_project("a", ProjectType.CUSTOM)
        assert pm.add_project_milestone("a", "m1", {"score": 3}) is True
        milestone = pm.get_project("a").milestones["m1"]
        assert milestone["score"] == 3
        assert "recorded_at" in milestone
        assert pm.add_project_milestone("missing", "m1") is False
        assert pm.get_project("a").to_dict()["milestones"]["m1"]["score"] == 3

    def test_create_project_honours_explicit_path(self, pm, tmp_path):
        target = tmp_path / "elsewhere" / "proj"
        project = pm.create_project("p", ProjectType.CUSTOM, path=target)
        assert project is not None
        assert project.path == target
        assert (target / "src").is_dir()

    def test_create_project_rejects_registered_name(self, pm, tmp_path):
        assert pm.create_project("p", ProjectType.CUSTOM) is not None
        assert (
            pm.create_project("p", ProjectType.CUSTOM, path=tmp_path / "other") is None
        )

    def test_string_projects_root_is_accepted(self, tmp_path):
        manager = ProjectManager(projects_root=str(tmp_path))
        assert manager.create_project("p", ProjectType.CUSTOM) is not None


class TestResourceUsage:
    def test_usage_reflects_allocations(self):
        rm = ResourceManager()
        allocation = rm.allocate("sys-compute", "user", 25.0)
        assert allocation is not None

        usage = rm.get_resource_usage()

        assert usage["total_resources"] == 3
        assert usage["total_allocations"] == 1
        assert usage["lifetime_allocations"] == 1
        assert usage["resources_by_type"] == {
            "compute": 1,
            "memory": 1,
            "api_quota": 1,
        }
        assert usage["utilization_summary"]["compute"] == pytest.approx(25.0)
        compute = usage["resources"]["sys-compute"]
        assert compute["allocated"] == 25.0
        assert compute["available"] == 75.0
        assert compute["allocation_count"] == 1

        rm.release(allocation.allocation_id)
        usage = rm.get_resource_usage()
        assert usage["total_allocations"] == 0
        assert usage["lifetime_allocations"] == 1


class TestPackageCreateProject:
    def test_create_project_builds_instance(self):
        """Regression: the helper raised TypeError (missing path and type)."""
        project = project_pkg.create_project("demo", "d", template="web_application")
        assert project.name == "demo"
        assert project.type is ProjectType.WEB_APPLICATION
        assert project.path.name == "demo"
        assert project.description == "d"

    def test_create_project_default_type(self):
        assert project_pkg.create_project("demo").type is ProjectType.CUSTOM

    def test_create_project_unknown_template(self):
        with pytest.raises(ValueError):
            project_pkg.create_project("demo", template="nope")


class TestOrchestrationMCPTools:
    @pytest.fixture
    def tools(self):
        from codomyrmex.logistics.orchestration.project.mcp_tools import (
            OrchestrationMCPTools,
        )

        tools = OrchestrationMCPTools()
        created_projects: list[str] = []
        created_workflows: list[str] = []
        yield tools, created_projects, created_workflows
        for name in created_projects:
            tools.project_manager.active_projects.pop(name, None)
        for name in created_workflows:
            tools.wf_manager.workflows.pop(name, None)
        tools.task_orchestrator.actions.unregister("mcp_test", "echo")

    def test_tools_share_the_engine_components(self, tools):
        mcp, _, _ = tools
        assert mcp.wf_manager is mcp.engine.workflow_manager
        assert mcp.task_orchestrator is mcp.engine.task_orchestrator
        assert mcp.project_manager is mcp.engine.project_manager
        assert mcp.resource_manager is mcp.engine.resource_manager

    def test_create_and_list_projects(self, tools, tmp_path):
        """Regression: create_project imported a nonexistent ``models`` module
        and list_projects iterated Project objects as names."""
        mcp, created, _ = tools
        result = mcp.execute_tool(
            "create_project",
            {
                "name": "mcp_tool_project",
                "template": "research",
                "path": str(tmp_path / "mcp_tool_project"),
            },
        )
        created.append("mcp_tool_project")
        assert result.status == "success", result.error
        assert result.data["data"]["project_type"] == "research"
        assert result.data["data"]["project_path"] == str(tmp_path / "mcp_tool_project")

        listed = mcp.execute_tool("list_projects", {})
        assert listed.status == "success", listed.error
        names = [p["name"] for p in listed.data["data"]["projects"]]
        assert "mcp_tool_project" in names

    def test_create_project_failure_is_reported(self, tools, tmp_path):
        mcp, created, _ = tools
        args = {"name": "mcp_dup_project", "path": str(tmp_path / "dup")}
        assert mcp.execute_tool("create_project", args).status == "success"
        created.append("mcp_dup_project")
        again = mcp.execute_tool("create_project", args)
        assert again.status == "failure"
        assert "could not be created" in again.error.error_message

    def test_create_project_unknown_template_fails(self, tools, tmp_path):
        mcp, _, _ = tools
        result = mcp.execute_tool(
            "create_project",
            {"name": "x", "template": "nope", "path": str(tmp_path / "x")},
        )
        assert result.status == "failure"
        assert result.error.error_type == "ValueError"

    def test_created_workflow_is_executable(self, tools):
        """create_workflow and execute_workflow used different WorkflowManagers."""
        mcp, _, created_workflows = tools
        mcp.task_orchestrator.register_action(
            "mcp_test", "echo", lambda message: message
        )
        created = mcp.execute_tool(
            "create_workflow",
            {
                "name": "mcp_test_workflow",
                "steps": [
                    {
                        "name": "s",
                        "module": "mcp_test",
                        "action": "echo",
                        "parameters": {"message": "hi"},
                    }
                ],
            },
        )
        created_workflows.append("mcp_test_workflow")
        assert created.status == "success"

        result = mcp.execute_tool(
            "execute_workflow", {"workflow_name": "mcp_test_workflow"}
        )
        assert result.status == "success", result.data
        assert result.data["data"]["result"]["s"]["result"] == "hi"

    def test_system_status_tool_succeeds(self, tools):
        mcp, _, _ = tools
        result = mcp.execute_tool("get_system_status", {})
        assert result.status == "success"
        assert "project_manager" in result.data["data"]
