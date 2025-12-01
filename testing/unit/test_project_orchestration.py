"""Unit tests for project_orchestration module."""

import sys
import pytest
from pathlib import Path


class TestProjectOrchestration:
    """Test cases for project orchestration functionality."""

    def test_project_orchestration_import(self, code_dir):
        """Test that we can import project_orchestration module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex import project_orchestration
            assert project_orchestration is not None
        except ImportError as e:
            pytest.fail(f"Failed to import project_orchestration: {e}")

    def test_project_orchestration_module_exists(self, code_dir):
        """Test that project_orchestration module directory exists."""
        po_path = code_dir / "codomyrmex" / "project_orchestration"
        assert po_path.exists()
        assert po_path.is_dir()

    def test_project_orchestration_init_file(self, code_dir):
        """Test that project_orchestration has __init__.py."""
        init_path = code_dir / "codomyrmex" / "project_orchestration" / "__init__.py"
        assert init_path.exists()

    def test_workflow_manager_module_exists(self, code_dir):
        """Test that workflow_manager module exists."""
        wm_path = code_dir / "codomyrmex" / "project_orchestration" / "workflow_manager.py"
        assert wm_path.exists()

    def test_task_orchestrator_module_exists(self, code_dir):
        """Test that task_orchestrator module exists."""
        to_path = code_dir / "codomyrmex" / "project_orchestration" / "task_orchestrator.py"
        assert to_path.exists()

    def test_project_manager_module_exists(self, code_dir):
        """Test that project_manager module exists."""
        pm_path = code_dir / "codomyrmex" / "project_orchestration" / "project_manager.py"
        assert pm_path.exists()

    def test_resource_manager_module_exists(self, code_dir):
        """Test that resource_manager module exists."""
        rm_path = code_dir / "codomyrmex" / "project_orchestration" / "resource_manager.py"
        assert rm_path.exists()

    def test_orchestration_engine_module_exists(self, code_dir):
        """Test that orchestration_engine module exists."""
        oe_path = code_dir / "codomyrmex" / "project_orchestration" / "orchestration_engine.py"
        assert oe_path.exists()

    def test_workflow_manager_import(self, code_dir):
        """Test that WorkflowManager class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import WorkflowManager
            assert WorkflowManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import WorkflowManager: {e}")

    def test_task_orchestrator_import(self, code_dir):
        """Test that TaskOrchestrator class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import TaskOrchestrator
            assert TaskOrchestrator is not None
        except ImportError as e:
            pytest.fail(f"Failed to import TaskOrchestrator: {e}")

    def test_project_manager_import(self, code_dir):
        """Test that ProjectManager class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import ProjectManager
            assert ProjectManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ProjectManager: {e}")

    def test_resource_manager_import(self, code_dir):
        """Test that ResourceManager class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import ResourceManager
            assert ResourceManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ResourceManager: {e}")

    def test_orchestration_engine_import(self, code_dir):
        """Test that OrchestrationEngine class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import OrchestrationEngine
            assert OrchestrationEngine is not None
        except ImportError as e:
            pytest.fail(f"Failed to import OrchestrationEngine: {e}")

    def test_workflow_step_import(self, code_dir):
        """Test that WorkflowStep class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import WorkflowStep
            assert WorkflowStep is not None
        except ImportError as e:
            pytest.fail(f"Failed to import WorkflowStep: {e}")

    def test_task_import(self, code_dir):
        """Test that Task class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import Task
            assert Task is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Task: {e}")

    def test_project_import(self, code_dir):
        """Test that Project class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import Project
            assert Project is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Project: {e}")

    def test_resource_import(self, code_dir):
        """Test that Resource class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import Resource
            assert Resource is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Resource: {e}")

    def test_status_enums_import(self, code_dir):
        """Test that status enums can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import (
                WorkflowStatus,
                TaskStatus,
                ProjectStatus,
                ResourceStatus,
                SessionStatus,
            )
            assert WorkflowStatus is not None
            assert TaskStatus is not None
            assert ProjectStatus is not None
            assert ResourceStatus is not None
            assert SessionStatus is not None
        except ImportError as e:
            pytest.fail(f"Failed to import status enums: {e}")

    def test_mcp_tools_import(self, code_dir):
        """Test that MCP tools can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import (
                get_mcp_tools,
                get_mcp_tool_definitions,
                execute_mcp_tool,
            )
            assert callable(get_mcp_tools)
            assert callable(get_mcp_tool_definitions)
            assert callable(execute_mcp_tool)
        except ImportError as e:
            pytest.fail(f"Failed to import MCP tools: {e}")

    def test_documentation_generator_import(self, code_dir):
        """Test that DocumentationGenerator class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.project_orchestration import DocumentationGenerator
            assert DocumentationGenerator is not None
        except ImportError as e:
            pytest.fail(f"Failed to import DocumentationGenerator: {e}")

    def test_project_orchestration_version(self, code_dir):
        """Test that project_orchestration has version defined."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex import project_orchestration
        assert hasattr(project_orchestration, "__version__")
        assert project_orchestration.__version__ == "0.1.0"

    def test_project_orchestration_all_exports(self, code_dir):
        """Test that project_orchestration exports all expected symbols."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex import project_orchestration

        expected_exports = [
            "WorkflowManager",
            "TaskOrchestrator",
            "ProjectManager",
            "ResourceManager",
            "OrchestrationEngine",
            "DocumentationGenerator",
            "WorkflowStep",
            "WorkflowStatus",
            "Task",
            "TaskStatus",
            "Project",
            "Resource",
        ]

        for export in expected_exports:
            assert hasattr(project_orchestration, export), f"Missing export: {export}"

    def test_agents_md_exists(self, code_dir):
        """Test that AGENTS.md exists for project_orchestration module."""
        agents_path = code_dir / "codomyrmex" / "project_orchestration" / "AGENTS.md"
        assert agents_path.exists()

    def test_readme_exists(self, code_dir):
        """Test that README.md exists for project_orchestration module."""
        readme_path = code_dir / "codomyrmex" / "project_orchestration" / "README.md"
        assert readme_path.exists()

    def test_templates_directory_exists(self, code_dir):
        """Test that templates directory exists for project_orchestration module."""
        templates_path = code_dir / "codomyrmex" / "project_orchestration" / "templates"
        assert templates_path.exists()
        assert templates_path.is_dir()

