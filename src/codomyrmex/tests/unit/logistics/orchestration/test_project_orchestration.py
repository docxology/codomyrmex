"""Unit tests for project_orchestration module."""

import os
import sys

import pytest


@pytest.mark.unit
class TestProjectOrchestration:
    """Test cases for project orchestration functionality."""

    def test_project_orchestration_import(self, code_dir):
        """Test that we can import project_orchestration module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex import logistics
            assert logistics is not None
        except ImportError as e:
            pytest.fail(f"Failed to import logistics: {e}")

    def test_project_orchestration_module_exists(self, code_dir):
        """Test that project_orchestration module directory exists."""
        po_path = code_dir / "codomyrmex" / "logistics" / "orchestration" / "project"
        assert po_path.exists()
        assert po_path.is_dir()

    def test_project_orchestration_init_file(self, code_dir):
        """Test that project_orchestration has __init__.py."""
        init_path = code_dir / "codomyrmex" / "logistics" / "orchestration" / "project" / "__init__.py"
        assert init_path.exists()

    def test_workflow_manager_module_exists(self, code_dir):
        """Test that workflow_manager module exists."""
        wm_path = code_dir / "codomyrmex" / "logistics" / "orchestration" / "project" / "workflow_manager.py"
        assert wm_path.exists()

    def test_task_orchestrator_module_exists(self, code_dir):
        """Test that task_orchestrator module exists."""
        to_path = code_dir / "codomyrmex" / "logistics" / "orchestration" / "project" / "task_orchestrator.py"
        assert to_path.exists()

    def test_project_manager_module_exists(self, code_dir):
        """Test that project_manager module exists."""
        pm_path = code_dir / "codomyrmex" / "logistics" / "orchestration" / "project" / "project_manager.py"
        assert pm_path.exists()

    def test_resource_manager_module_exists(self, code_dir):
        """Test that resource_manager module exists."""
        rm_path = code_dir / "codomyrmex" / "logistics" / "orchestration" / "project" / "resource_manager.py"
        assert rm_path.exists()

    def test_orchestration_engine_module_exists(self, code_dir):
        """Test that orchestration_engine module exists."""
        oe_path = code_dir / "codomyrmex" / "logistics" / "orchestration" / "project" / "orchestration_engine.py"
        assert oe_path.exists()

    def test_workflow_manager_import(self, code_dir):
        """Test that WorkflowManager class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logistics.orchestration.project import WorkflowManager
            assert WorkflowManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import WorkflowManager: {e}")

    def test_task_orchestrator_import(self, code_dir):
        """Test that TaskOrchestrator class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logistics.orchestration.project import TaskOrchestrator
            assert TaskOrchestrator is not None
        except ImportError as e:
            pytest.fail(f"Failed to import TaskOrchestrator: {e}")

    def test_project_manager_import(self, code_dir):
        """Test that ProjectManager class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logistics.orchestration.project import ProjectManager
            assert ProjectManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ProjectManager: {e}")

    def test_resource_manager_import(self, code_dir):
        """Test that ResourceManager class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logistics.orchestration.project import ResourceManager
            assert ResourceManager is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ResourceManager: {e}")

    def test_orchestration_engine_import(self, code_dir):
        """Test that OrchestrationEngine class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logistics.orchestration.project import OrchestrationEngine
            assert OrchestrationEngine is not None
        except ImportError as e:
            pytest.fail(f"Failed to import OrchestrationEngine: {e}")

    def test_workflow_step_import(self, code_dir):
        """Test that WorkflowStep class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logistics.orchestration.project import WorkflowStep
            assert WorkflowStep is not None
        except ImportError as e:
            pytest.fail(f"Failed to import WorkflowStep: {e}")

    def test_task_import(self, code_dir):
        """Test that Task class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logistics.orchestration.project import Task
            assert Task is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Task: {e}")

    def test_project_import(self, code_dir):
        """Test that Project class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logistics.orchestration.project import Project
            assert Project is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Project: {e}")

    def test_resource_import(self, code_dir):
        """Test that Resource class can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logistics.orchestration.project import Resource
            assert Resource is not None
        except ImportError as e:
            pytest.fail(f"Failed to import Resource: {e}")

    def test_status_enums_import(self, code_dir):
        """Test that status enums can be imported."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from codomyrmex.logistics.orchestration.project import (
                ProjectStatus,
                ResourceStatus,
                SessionStatus,
                TaskStatus,
                WorkflowStatus,
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
            from codomyrmex.logistics.orchestration.project import (
                execute_mcp_tool,
                get_mcp_tool_definitions,
                get_mcp_tools,
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
            from codomyrmex.logistics.orchestration.project import (
                DocumentationGenerator,
            )
            assert DocumentationGenerator is not None
        except ImportError as e:
            pytest.fail(f"Failed to import DocumentationGenerator: {e}")

    def test_project_orchestration_version(self, code_dir):
        """Test that project_orchestration has version defined."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.logistics.orchestration.project import __version__
        assert __version__ == "0.1.0"

    def test_project_orchestration_all_exports(self, code_dir):
        """Test that project_orchestration exports all expected symbols."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from codomyrmex.logistics.orchestration.project import __all__

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
            assert export in __all__, f"Missing export: {export}"

    def test_agents_md_exists(self, code_dir):
        """Test that AGENTS.md exists for project_orchestration module."""
        agents_path = code_dir / "codomyrmex" / "logistics" / "orchestration" / "project" / "AGENTS.md"
        assert agents_path.exists()

    def test_readme_exists(self, code_dir):
        """Test that README.md exists for project_orchestration module."""
        readme_path = code_dir / "codomyrmex" / "logistics" / "orchestration" / "project" / "README.md"
        assert readme_path.exists()

    def test_templates_directory_exists(self, code_dir):
        """Test that templates directory exists for project_orchestration module."""
        templates_path = code_dir / "codomyrmex" / "logistics" / "orchestration" / "project" / "templates"
        assert templates_path.exists()
        assert templates_path.is_dir()


@pytest.mark.unit
class TestWorkflowDAG:
    """Test cases for WorkflowDAG functionality."""

    def test_workflow_dag_creation(self):
        """Test creating a basic workflow DAG."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_dag import (
                WorkflowDAG,
            )
        except ImportError:
            pytest.skip("WorkflowDAG not available")

        # Create a simple DAG
        tasks = [
            {"name": "task1", "module": "test", "action": "run", "dependencies": []},
            {"name": "task2", "module": "test", "action": "run", "dependencies": ["task1"]},
        ]

        dag = WorkflowDAG(tasks)

        assert len(dag.tasks) == 2
        assert "task1" in dag.tasks
        assert "task2" in dag.tasks
        assert dag.tasks["task2"].dependencies == ["task1"]

    def test_dag_validation_valid(self):
        """Test DAG validation with valid DAG."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_dag import (
                WorkflowDAG,
            )
        except ImportError:
            pytest.skip("WorkflowDAG not available")

        tasks = [
            {"name": "task1", "module": "test", "action": "run", "dependencies": []},
            {"name": "task2", "module": "test", "action": "run", "dependencies": ["task1"]},
            {"name": "task3", "module": "test", "action": "run", "dependencies": ["task1"]},
            {"name": "task4", "module": "test", "action": "run", "dependencies": ["task2", "task3"]},
        ]

        dag = WorkflowDAG(tasks)
        is_valid, errors = dag.validate_dag()

        assert is_valid
        assert len(errors) == 0

    def test_dag_validation_cycle(self):
        """Test DAG validation with cycle detection."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_dag import (
                WorkflowDAG,
            )
        except ImportError:
            pytest.skip("WorkflowDAG not available")

        tasks = [
            {"name": "task1", "module": "test", "action": "run", "dependencies": ["task3"]},
            {"name": "task2", "module": "test", "action": "run", "dependencies": ["task1"]},
            {"name": "task3", "module": "test", "action": "run", "dependencies": ["task2"]},
        ]

        dag = WorkflowDAG(tasks)
        is_valid, errors = dag.validate_dag()

        assert not is_valid
        assert len(errors) > 0
        assert any("cycle" in error.lower() for error in errors)

    def test_dag_execution_order(self):
        """Test getting execution order from DAG."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_dag import (
                WorkflowDAG,
            )
        except ImportError:
            pytest.skip("WorkflowDAG not available")

        tasks = [
            {"name": "task1", "module": "test", "action": "run", "dependencies": []},
            {"name": "task2", "module": "test", "action": "run", "dependencies": ["task1"]},
            {"name": "task3", "module": "test", "action": "run", "dependencies": ["task1"]},
            {"name": "task4", "module": "test", "action": "run", "dependencies": ["task2", "task3"]},
        ]

        dag = WorkflowDAG(tasks)
        execution_order = dag.get_execution_order()

        # Should have 3 levels
        assert len(execution_order) == 3

        # Level 0: task1
        assert execution_order[0] == ["task1"]

        # Level 1: task2 and task3 (can run in parallel)
        assert set(execution_order[1]) == {"task2", "task3"}

        # Level 2: task4
        assert execution_order[2] == ["task4"]

    def test_dag_dependency_queries(self):
        """Test dependency query methods."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_dag import (
                WorkflowDAG,
            )
        except ImportError:
            pytest.skip("WorkflowDAG not available")

        tasks = [
            {"name": "task1", "module": "test", "action": "run", "dependencies": []},
            {"name": "task2", "module": "test", "action": "run", "dependencies": ["task1"]},
            {"name": "task3", "module": "test", "action": "run", "dependencies": ["task2"]},
        ]

        dag = WorkflowDAG(tasks)

        # Test direct dependencies
        deps = dag.get_task_dependencies("task3")
        assert set(deps) == {"task1", "task2"}

        # Test dependents
        dependents = dag.get_dependent_tasks("task1")
        assert set(dependents) == {"task2", "task3"}

    def test_dag_visualization(self):
        """Test DAG visualization generation."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_dag import (
                WorkflowDAG,
            )
        except ImportError:
            pytest.skip("WorkflowDAG not available")

        tasks = [
            {"name": "task1", "module": "test", "action": "run", "dependencies": []},
            {"name": "task2", "module": "test", "action": "run", "dependencies": ["task1"]},
        ]

        dag = WorkflowDAG(tasks)
        mermaid_diagram = dag.visualize()

        assert isinstance(mermaid_diagram, str)
        assert "graph TD" in mermaid_diagram
        assert "task1" in mermaid_diagram
        assert "task2" in mermaid_diagram
        assert "task1 --> task2" in mermaid_diagram


@pytest.mark.unit
class TestParallelExecutor:
    """Test cases for ParallelExecutor functionality."""

    def test_parallel_executor_creation(self):
        """Test creating a parallel executor."""
        try:
            from codomyrmex.logistics.orchestration.project.parallel_executor import (
                ParallelExecutor,
            )
        except ImportError:
            pytest.skip("ParallelExecutor not available")

        executor = ParallelExecutor(max_workers=2)
        assert executor.max_workers == 2
        assert executor.default_timeout == 300.0

        executor.shutdown()

    def test_execute_task_group(self):
        """Test executing a group of independent tasks."""
        try:
            from codomyrmex.logistics.orchestration.project.parallel_executor import (
                ParallelExecutor,
            )
        except ImportError:
            pytest.skip("ParallelExecutor not available")

        tasks = [
            {"name": "task1", "module": "test", "action": "run"},
            {"name": "task2", "module": "test", "action": "run"},
        ]

        with ParallelExecutor(max_workers=2) as executor:
            results = executor.execute_task_group(tasks, timeout=10)

        assert len(results) == 2
        for result in results:
            assert result.status.name == "COMPLETED"
            assert result.task_name in ["task1", "task2"]
            assert result.duration > 0

    def test_dependency_management(self):
        """Test dependency checking in executor."""
        try:
            from codomyrmex.logistics.orchestration.project.parallel_executor import (
                ParallelExecutor,
            )
        except ImportError:
            pytest.skip("ParallelExecutor not available")

        executor = ParallelExecutor()

        # Task with dependencies
        task = {"name": "task1", "dependencies": ["dep1", "dep2"]}
        completed = {"dep1"}  # Only one dependency completed

        # Should not be ready
        ready = executor.wait_for_dependencies(task, completed)
        assert not ready

        # Complete all dependencies
        completed.add("dep2")
        ready = executor.wait_for_dependencies(task, completed)
        assert ready

        executor.shutdown()

    def test_workflow_validation_functions(self):
        """Test workflow validation utility functions."""
        try:
            from codomyrmex.logistics.orchestration.project.parallel_executor import (
                get_workflow_execution_order,
                validate_workflow_dependencies,
            )
        except ImportError:
            pytest.skip("Parallel executor utilities not available")

        # Test validation
        tasks = [
            {"name": "task1", "dependencies": []},
            {"name": "task2", "dependencies": ["task1"]},
        ]

        errors = validate_workflow_dependencies(tasks)
        assert len(errors) == 0

        # Test invalid dependencies
        invalid_tasks = [
            {"name": "task1", "dependencies": ["missing_task"]},
        ]

        errors = validate_workflow_dependencies(invalid_tasks)
        assert len(errors) > 0
        assert "missing_task" in errors[0]

        # Test execution order
        execution_order = get_workflow_execution_order(tasks)
        assert isinstance(execution_order, list)
        assert len(execution_order) > 0


@pytest.mark.unit
class TestWorkflowManagerEnhancements:
    """Test cases for enhanced WorkflowManager functionality."""

    def test_create_workflow_dag(self):
        """Test creating workflow DAG through manager."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_manager import (
                WorkflowManager,
            )
        except ImportError:
            pytest.skip("WorkflowManager not available")

        manager = WorkflowManager()

        tasks = [
            {"name": "task1", "module": "test", "action": "run", "dependencies": []},
            {"name": "task2", "module": "test", "action": "run", "dependencies": ["task1"]},
        ]

        dag = manager.create_workflow_dag(tasks)

        assert dag is not None
        assert len(dag.tasks) == 2

    def test_validate_workflow_dependencies(self):
        """Test workflow dependency validation through manager."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_manager import (
                WorkflowManager,
            )
        except ImportError:
            pytest.skip("WorkflowManager not available")

        manager = WorkflowManager()

        # Valid tasks
        valid_tasks = [
            {"name": "task1", "dependencies": []},
            {"name": "task2", "dependencies": ["task1"]},
        ]

        errors = manager.validate_workflow_dependencies(valid_tasks)
        assert len(errors) == 0

        # Invalid tasks (missing dependency)
        invalid_tasks = [
            {"name": "task1", "dependencies": ["missing"]},
        ]

        errors = manager.validate_workflow_dependencies(invalid_tasks)
        assert len(errors) > 0

    def test_get_workflow_execution_order(self):
        """Test getting workflow execution order through manager."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_manager import (
                WorkflowManager,
            )
        except ImportError:
            pytest.skip("WorkflowManager not available")

        manager = WorkflowManager()

        tasks = [
            {"name": "task1", "module": "test", "action": "run", "dependencies": []},
            {"name": "task2", "module": "test", "action": "run", "dependencies": ["task1"]},
            {"name": "task3", "module": "test", "action": "run", "dependencies": ["task1"]},
        ]

        execution_order = manager.get_workflow_execution_order(tasks)

        assert isinstance(execution_order, list)
        assert len(execution_order) >= 2  # At least 2 levels
        assert execution_order[0] == ["task1"]  # First task has no dependencies

    def test_execute_parallel_workflow(self):
        """Test parallel workflow execution through manager with real ParallelExecutor."""
        try:
            from codomyrmex.logistics.orchestration.project.parallel_executor import (
                ParallelExecutor,
            )
            from codomyrmex.logistics.orchestration.project.workflow_manager import (
                WorkflowManager,
            )
        except ImportError:
            pytest.skip("WorkflowManager not available")

        manager = WorkflowManager()

        workflow = {
            "tasks": [
                {"name": "task1", "module": "test", "action": "run"}
            ],
            "dependencies": {},
            "max_parallel": 2
        }

        # Use real ParallelExecutor
        result = manager.execute_parallel_workflow(workflow)

        # Should return a result dict
        assert isinstance(result, dict)
        assert result["status"] in ["completed", "partial_failure", "failed"]
        assert "total_tasks" in result
        assert "completed_tasks" in result
        assert "task_results" in result

    def test_workflow_dag_integration(self):
        """Test integration between WorkflowManager and WorkflowDAG."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_dag import (
                WorkflowDAG,
            )
            from codomyrmex.logistics.orchestration.project.workflow_manager import (
                WorkflowManager,
            )
        except ImportError:
            pytest.skip("Required modules not available")

        manager = WorkflowManager()

        # Create complex workflow with dependencies
        tasks = [
            {"name": "data_ingest", "module": "data", "action": "ingest", "dependencies": []},
            {"name": "data_validate", "module": "data", "action": "validate", "dependencies": ["data_ingest"]},
            {"name": "analysis", "module": "analysis", "action": "run", "dependencies": ["data_validate"]},
            {"name": "report", "module": "reporting", "action": "generate", "dependencies": ["analysis"]},
            {"name": "notify", "module": "notification", "action": "send", "dependencies": ["report"]},
        ]

        # Create DAG through manager
        dag = manager.create_workflow_dag(tasks)

        # Validate DAG
        is_valid, errors = dag.validate_dag()
        assert is_valid, f"DAG validation failed: {errors}"

        # Get execution order
        execution_order = dag.get_execution_order()
        assert len(execution_order) == 5  # 5 levels for sequential dependencies

        # Verify topological ordering
        task_levels = {}
        for level_idx, level_tasks in enumerate(execution_order):
            for task in level_tasks:
                task_levels[task] = level_idx

        # Verify dependency constraints
        assert task_levels["data_ingest"] < task_levels["data_validate"]
        assert task_levels["data_validate"] < task_levels["analysis"]
        assert task_levels["analysis"] < task_levels["report"]
        assert task_levels["report"] < task_levels["notify"]


@pytest.mark.unit
class TestWorkflowManagerLocation:
    """Test cases for WorkflowManager directory location."""

    def test_default_location(self, tmp_path):
        """Test that WorkflowManager defaults to config/workflows/production."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_manager import (
                WorkflowManager,
            )
        except ImportError:
            pytest.skip("WorkflowManager not available")

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            manager = WorkflowManager()

            expected_location = tmp_path / "config" / "workflows" / "production"
            assert manager.config_dir == expected_location
            assert manager.config_dir.exists()
        finally:
            os.chdir(original_cwd)

    def test_custom_config_dir(self, tmp_path):
        """Test that custom config_dir parameter is respected."""
        try:
            from codomyrmex.logistics.orchestration.project.workflow_manager import (
                WorkflowManager,
            )
        except ImportError:
            pytest.skip("WorkflowManager not available")

        custom_dir = tmp_path / "custom" / "workflows"
        manager = WorkflowManager(config_dir=custom_dir)

        # Should use custom directory
        assert manager.config_dir == custom_dir
        assert manager.config_dir.exists()

    def test_load_workflows_from_production(self, tmp_path):
        """Test loading workflows from production directory."""
        try:
            import json

            from codomyrmex.logistics.orchestration.project.workflow_manager import (
                WorkflowManager,
            )
        except ImportError:
            pytest.skip("WorkflowManager not available")

        production_location = tmp_path / "config" / "workflows" / "production"
        production_location.mkdir(parents=True, exist_ok=True)

        test_workflow = {
            "name": "test_workflow",
            "steps": [
                {
                    "name": "test_step",
                    "module": "environment_setup",
                    "action": "check_environment",
                    "parameters": {},
                    "dependencies": [],
                    "timeout": 60,
                    "max_retries": 3
                }
            ]
        }

        workflow_file = production_location / "test_workflow.json"
        with open(workflow_file, "w") as f:
            json.dump(test_workflow, f)

        original_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            manager = WorkflowManager()

            workflows = manager.list_workflows()
            assert "test_workflow" in workflows
        finally:
            os.chdir(original_cwd)

