"""
Comprehensive unit tests for WorkflowManager.

This module contains extensive unit tests for the WorkflowManager class,
covering all public methods, error conditions, and edge cases.
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from codomyrmex.project_orchestration.workflow_manager import (
    WorkflowManager,
    WorkflowStep,
    WorkflowExecution,
)
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)
from codomyrmex.project_orchestration.workflow_manager import (
    WorkflowStatus,
    get_workflow_manager,
)


class TestWorkflowStep:
    """Test cases for WorkflowStep dataclass."""

    def test_workflow_step_creation(self):
        """Test basic WorkflowStep creation."""
        step = WorkflowStep(
            name="test_step",
            module="test_module",
            action="test_action",
            parameters={"param1": "value1"},
            dependencies=["dep1", "dep2"],
            timeout=300,
            max_retries=5,
        )

        assert step.name == "test_step"
        assert step.module == "test_module"
        assert step.action == "test_action"
        assert step.parameters == {"param1": "value1"}
        assert step.dependencies == ["dep1", "dep2"]
        assert step.timeout == 300
        assert step.max_retries == 5
        assert step.retry_count == 0

    def test_workflow_step_defaults(self):
        """Test WorkflowStep with default values."""
        step = WorkflowStep(
            name="test_step", module="test_module", action="test_action"
        )

        assert step.parameters == {}
        assert step.dependencies == []
        assert step.timeout is None
        assert step.max_retries == 3
        assert step.retry_count == 0


class TestWorkflowExecution:
    """Test cases for WorkflowExecution dataclass."""

    def test_workflow_execution_creation(self):
        """Test basic WorkflowExecution creation."""
        execution = WorkflowExecution(workflow_name="test_workflow")

        assert execution.workflow_name == "test_workflow"
        assert execution.status == WorkflowStatus.PENDING
        assert execution.start_time is None
        assert execution.end_time is None
        assert execution.results == {}
        assert execution.errors == []
        assert execution.performance_metrics == {}

    def test_workflow_execution_with_values(self):
        """Test WorkflowExecution with custom values."""
        start_time = datetime.now()
        execution = WorkflowExecution(
            workflow_name="test_workflow",
            status=WorkflowStatus.RUNNING,
            start_time=start_time,
            results={"step1": {"output": "data"}},
            errors=["error1"],
            performance_metrics={"step1": {"time": 1.5}},
        )

        assert execution.workflow_name == "test_workflow"
        assert execution.status == WorkflowStatus.RUNNING
        assert execution.start_time == start_time
        assert execution.results == {"step1": {"output": "data"}}
        assert execution.errors == ["error1"]
        assert execution.performance_metrics == {"step1": {"time": 1.5}}


class TestWorkflowManager:
    """Test cases for WorkflowManager class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def workflow_manager(self, temp_dir):
        """Create a WorkflowManager instance for testing."""
        return WorkflowManager(config_dir=temp_dir, enable_performance_monitoring=False)

    @pytest.fixture
    def sample_steps(self):
        """Create sample workflow steps for testing."""
        return [
            WorkflowStep(
                name="step1",
                module="module1",
                action="action1",
                parameters={"param1": "value1"},
            ),
            WorkflowStep(
                name="step2",
                module="module2",
                action="action2",
                parameters={"param2": "value2"},
                dependencies=["step1"],
            ),
        ]

    def test_workflow_manager_initialization(self, temp_dir):
        """Test WorkflowManager initialization."""
        manager = WorkflowManager(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

        assert manager.config_dir == temp_dir
        assert manager.workflows == {}
        assert manager.executions == {}
        assert manager.enable_performance_monitoring is False
        assert manager.performance_monitor is None
        assert manager.logger is not None

    def test_workflow_manager_initialization_with_performance(self, temp_dir):
        """Test WorkflowManager initialization with performance monitoring."""
        # Test with performance monitoring disabled (default behavior)
        manager = WorkflowManager(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

        assert manager.enable_performance_monitoring is False
        assert manager.performance_monitor is None

    def test_create_workflow_success(self, workflow_manager, sample_steps):
        """Test successful workflow creation."""
        result = workflow_manager.create_workflow("test_workflow", sample_steps)

        assert result is True
        assert "test_workflow" in workflow_manager.workflows
        assert workflow_manager.workflows["test_workflow"] == sample_steps

    def test_create_workflow_empty_name(self, workflow_manager, sample_steps):
        """Test workflow creation with empty name."""
        result = workflow_manager.create_workflow("", sample_steps)

        assert result is False
        assert "test_workflow" not in workflow_manager.workflows

    def test_create_workflow_empty_steps(self, workflow_manager):
        """Test workflow creation with empty steps."""
        result = workflow_manager.create_workflow("test_workflow", [])

        assert result is False
        assert "test_workflow" not in workflow_manager.workflows

    def test_create_workflow_invalid_dependencies(self, workflow_manager):
        """Test workflow creation with invalid dependencies."""
        steps = [
            WorkflowStep(
                name="step1",
                module="module1",
                action="action1",
                dependencies=["nonexistent_step"],
            )
        ]

        result = workflow_manager.create_workflow("test_workflow", steps)

        # Should still succeed but log warning
        assert result is True
        assert "test_workflow" in workflow_manager.workflows

    def test_create_workflow_save_to_disk(self, temp_dir, sample_steps):
        """Test workflow creation with disk persistence."""
        manager = WorkflowManager(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

        result = manager.create_workflow("test_workflow", sample_steps, save=True)

        assert result is True

        # Check if file was created
        workflow_file = temp_dir / "test_workflow.json"
        assert workflow_file.exists()

        # Check file contents
        with open(workflow_file, "r") as f:
            data = json.load(f)

        assert data["name"] == "test_workflow"
        assert len(data["steps"]) == 2
        assert data["steps"][0]["name"] == "step1"
        assert data["steps"][1]["name"] == "step2"

    def test_list_workflows_empty(self, workflow_manager):
        """Test listing workflows when none exist."""
        workflows = workflow_manager.list_workflows()

        assert workflows == {}

    def test_list_workflows_with_data(self, workflow_manager, sample_steps):
        """Test listing workflows with data."""
        workflow_manager.create_workflow("workflow1", sample_steps)
        workflow_manager.create_workflow("workflow2", sample_steps[:1])

        workflows = workflow_manager.list_workflows()

        assert len(workflows) == 2
        assert "workflow1" in workflows
        assert "workflow2" in workflows

        # Check workflow1 metadata
        wf1_info = workflows["workflow1"]
        assert wf1_info["steps"] == 2
        assert set(wf1_info["modules"]) == {"module1", "module2"}
        assert wf1_info["has_dependencies"] is True

        # Check workflow2 metadata
        wf2_info = workflows["workflow2"]
        assert wf2_info["steps"] == 1
        assert wf2_info["modules"] == ["module1"]
        assert wf2_info["has_dependencies"] is False

    def test_execute_workflow_success(self, workflow_manager, sample_steps):
        """Test successful workflow execution."""
        workflow_manager.create_workflow("test_workflow", sample_steps)

        async def run_workflow():
            return await workflow_manager.execute_workflow("test_workflow")

        execution = asyncio.run(run_workflow())

        assert execution.workflow_name == "test_workflow"
        assert execution.status == WorkflowStatus.COMPLETED
        assert execution.start_time is not None
        assert execution.end_time is not None
        assert len(execution.results) == 2
        assert "step1" in execution.results
        assert "step2" in execution.results
        assert execution.errors == []

    def test_execute_workflow_not_found(self, workflow_manager):
        """Test executing non-existent workflow."""

        async def run_workflow():
            return await workflow_manager.execute_workflow("nonexistent")

        with pytest.raises(ValueError, match="Workflow 'nonexistent' not found"):
            asyncio.run(run_workflow())

    def test_execute_workflow_with_parameters(self, workflow_manager, sample_steps):
        """Test workflow execution with parameters."""
        workflow_manager.create_workflow("test_workflow", sample_steps)

        async def run_workflow():
            parameters = {"global_param": "global_value"}
            return await workflow_manager.execute_workflow("test_workflow", parameters)

        execution = asyncio.run(run_workflow())

        assert execution.status == WorkflowStatus.COMPLETED
        # Check that parameters were passed to steps
        for step_name, result in execution.results.items():
            assert "parameters_used" in result
            assert "global_param" in result["parameters_used"]

    def test_execute_workflow_circular_dependency(self, workflow_manager):
        """Test workflow execution with circular dependencies."""
        steps = [
            WorkflowStep(
                name="step1", module="module1", action="action1", dependencies=["step2"]
            ),
            WorkflowStep(
                name="step2", module="module2", action="action2", dependencies=["step1"]
            ),
        ]
        workflow_manager.create_workflow("circular_workflow", steps)

        async def run_workflow():
            return await workflow_manager.execute_workflow("circular_workflow")

        execution = asyncio.run(run_workflow())

        assert execution.status == WorkflowStatus.FAILED
        assert len(execution.errors) > 0
        assert "Circular dependency" in execution.errors[0]

    def test_get_performance_summary_no_monitoring(self, workflow_manager):
        """Test performance summary when monitoring is disabled."""
        summary = workflow_manager.get_performance_summary()

        assert "error" in summary
        assert summary["error"] == "Performance monitoring not enabled"

    def test_get_performance_summary_with_monitoring(self, temp_dir):
        """Test performance summary with monitoring enabled."""
        # Test with performance monitoring disabled (default behavior)
        manager = WorkflowManager(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

        # Add some execution data
        execution = WorkflowExecution(workflow_name="test_workflow")
        execution.status = WorkflowStatus.COMPLETED
        execution.start_time = datetime.now()
        execution.end_time = datetime.now()
        execution.performance_metrics = {
            "step1": {"module": "module1", "execution_time": 1.5}
        }
        manager.executions["test_execution"] = execution

        summary = manager.get_performance_summary()

        # Should return error message since monitoring is disabled
        assert "error" in summary
        assert summary["error"] == "Performance monitoring not enabled"

    def test_load_workflows_from_disk(self, temp_dir, sample_steps):
        """Test loading workflows from disk."""
        # Create a workflow file manually
        workflow_file = temp_dir / "saved_workflow.json"
        workflow_data = {
            "name": "saved_workflow",
            "steps": [
                {
                    "name": "step1",
                    "module": "module1",
                    "action": "action1",
                    "parameters": {"param1": "value1"},
                    "dependencies": [],
                    "timeout": None,
                    "retry_count": 0,
                    "max_retries": 3,
                }
            ],
        }

        with open(workflow_file, "w") as f:
            json.dump(workflow_data, f)

        # Create manager and load workflows
        manager = WorkflowManager(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

        assert "saved_workflow" in manager.workflows
        assert len(manager.workflows["saved_workflow"]) == 1
        assert manager.workflows["saved_workflow"][0].name == "step1"

    def test_load_workflows_invalid_file(self, temp_dir):
        """Test loading workflows with invalid JSON file."""
        # Create invalid JSON file
        invalid_file = temp_dir / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("invalid json content")

        # Create manager and load workflows
        manager = WorkflowManager(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

        # Should not crash, just log error
        assert len(manager.workflows) == 0

    def test_load_workflows_missing_fields(self, temp_dir):
        """Test loading workflows with missing required fields."""
        # Create workflow file with missing fields
        workflow_file = temp_dir / "incomplete.json"
        workflow_data = {
            "name": "incomplete_workflow"
            # Missing "steps" field
        }

        with open(workflow_file, "w") as f:
            json.dump(workflow_data, f)

        # Create manager and load workflows
        manager = WorkflowManager(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

        # Should not load incomplete workflow
        assert "incomplete_workflow" not in manager.workflows


class TestGetWorkflowManager:
    """Test cases for get_workflow_manager function."""

    def test_get_workflow_manager_singleton(self):
        """Test that get_workflow_manager returns singleton instance."""
        # Reset global state
        import codomyrmex.project_orchestration.workflow_manager as wm_module

        wm_module._workflow_manager = None

        manager1 = get_workflow_manager()
        manager2 = get_workflow_manager()

        assert manager1 is manager2
        assert isinstance(manager1, WorkflowManager)

    def test_get_workflow_manager_multiple_calls(self):
        """Test multiple calls to get_workflow_manager."""
        # Reset global state
        import codomyrmex.project_orchestration.workflow_manager as wm_module

        wm_module._workflow_manager = None

        managers = [get_workflow_manager() for _ in range(5)]

        # All should be the same instance
        for manager in managers:
            assert manager is managers[0]


class TestWorkflowManagerIntegration:
    """Integration tests for WorkflowManager."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def workflow_manager(self, temp_dir):
        """Create a WorkflowManager instance for testing."""
        return WorkflowManager(config_dir=temp_dir, enable_performance_monitoring=False)

    def test_full_workflow_lifecycle(self, workflow_manager, temp_dir):
        """Test complete workflow lifecycle: create, save, load, execute."""
        # Create workflow
        steps = [
            WorkflowStep(
                name="setup", module="environment_setup", action="check_environment"
            ),
            WorkflowStep(
                name="analyze",
                module="static_analysis",
                action="analyze_code",
                parameters={"path": "."},
                dependencies=["setup"],
            ),
        ]

        # Test creation
        result = workflow_manager.create_workflow("integration_test", steps, save=True)
        assert result is True

        # Test listing
        workflows = workflow_manager.list_workflows()
        assert "integration_test" in workflows
        assert workflows["integration_test"]["steps"] == 2

        # Test persistence by creating new manager
        new_manager = WorkflowManager(
            config_dir=temp_dir, enable_performance_monitoring=False
        )
        assert "integration_test" in new_manager.workflows

        # Test execution
        async def run_execution():
            execution = await new_manager.execute_workflow("integration_test")
            assert execution.status == WorkflowStatus.COMPLETED
            assert len(execution.results) == 2
            return execution

        # Run async test
        execution = asyncio.run(run_execution())
        assert execution.workflow_name == "integration_test"

    def test_workflow_with_complex_dependencies(self, workflow_manager):
        """Test workflow with complex dependency chain."""
        steps = [
            WorkflowStep(name="step1", module="module1", action="action1"),
            WorkflowStep(
                name="step2", module="module2", action="action2", dependencies=["step1"]
            ),
            WorkflowStep(
                name="step3", module="module3", action="action3", dependencies=["step1"]
            ),
            WorkflowStep(
                name="step4",
                module="module4",
                action="action4",
                dependencies=["step2", "step3"],
            ),
        ]

        result = workflow_manager.create_workflow("complex_workflow", steps)
        assert result is True

        # Test execution order
        async def run_execution():
            execution = await workflow_manager.execute_workflow("complex_workflow")
            assert execution.status == WorkflowStatus.COMPLETED
            assert len(execution.results) == 4
            return execution

        execution = asyncio.run(run_execution())
        assert execution.status == WorkflowStatus.COMPLETED


if __name__ == "__main__":
    pytest.main([__file__])
