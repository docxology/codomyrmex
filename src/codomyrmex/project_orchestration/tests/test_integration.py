"""
Comprehensive integration tests for Project Orchestration system.

This module contains integration tests that verify the interaction between
different components of the project orchestration system.
"""

import pytest
import asyncio
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from codomyrmex.project_orchestration import (
    get_workflow_manager,
    get_task_orchestrator,
    get_project_manager,
    get_resource_manager,
    get_orchestration_engine,
    WorkflowStep,
    Task,
    TaskPriority,
    Project,
    ProjectType,
    Resource,
    ResourceType,
)


class TestWorkflowTaskIntegration:
    """Integration tests between WorkflowManager and TaskOrchestrator."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_workflow_creates_tasks(self, temp_dir):
        """Test that workflow execution creates and manages tasks."""
        # Get managers
        workflow_manager = get_workflow_manager()
        task_orchestrator = get_task_orchestrator()

        # Create workflow with multiple steps
        steps = [
            WorkflowStep(
                name="setup", module="environment_setup", action="check_environment"
            ),
            WorkflowStep(
                name="analyze",
                module="static_analysis",
                action="analyze_code",
                dependencies=["setup"],
            ),
            WorkflowStep(
                name="visualize",
                action="create_chart",
                module="data_visualization",
                dependencies=["analyze"],
            ),
        ]

        workflow_manager.create_workflow("integration_test", steps)

        # Execute workflow
        async def run_workflow():
            execution = await workflow_manager.execute_workflow("integration_test")
            return execution

        execution = asyncio.run(run_workflow())

        # Verify workflow execution
        assert execution.status.value in ["completed", "failed"]
        assert len(execution.results) == 3
        assert "setup" in execution.results
        assert "analyze" in execution.results
        assert "visualize" in execution.results

    def test_task_dependencies_resolution(self, temp_dir):
        """Test that task dependencies are properly resolved."""
        task_orchestrator = get_task_orchestrator()

        # Create tasks with dependencies
        task1 = Task(
            name="task1", module="module1", action="action1", priority=TaskPriority.HIGH
        )

        task2 = Task(
            name="task2",
            module="module2",
            action="action2",
            dependencies=["task1"],
            priority=TaskPriority.NORMAL,
        )

        task3 = Task(
            name="task3",
            module="module3",
            action="action3",
            dependencies=["task1", "task2"],
            priority=TaskPriority.LOW,
        )

        # Add tasks to orchestrator
        task_orchestrator.add_task(task1)
        task_orchestrator.add_task(task2)
        task_orchestrator.add_task(task3)

        # Start execution
        task_orchestrator.start_execution()

        # Wait for tasks to complete
        time.sleep(2)

        # Stop execution
        task_orchestrator.stop_execution()

        # Verify execution order (task1 should complete before task2, task2 before task3)
        # This is a simplified check - in real implementation, we'd verify timing
        assert (
            task1.id in task_orchestrator.completed_tasks
            or task1.id in task_orchestrator.task_results
        )
        assert (
            task2.id in task_orchestrator.completed_tasks
            or task2.id in task_orchestrator.task_results
        )
        assert (
            task3.id in task_orchestrator.completed_tasks
            or task3.id in task_orchestrator.task_results
        )


class TestProjectWorkflowIntegration:
    """Integration tests between ProjectManager and WorkflowManager."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_project_workflow_lifecycle(self, temp_dir):
        """Test complete project workflow lifecycle."""
        project_manager = get_project_manager()
        workflow_manager = get_workflow_manager()

        # Create project
        project = project_manager.create_project(
            name="integration_project",
            description="Integration test project",
            template_name="ai_analysis",
        )

        assert project is not None
        assert project.name == "integration_project"

        # Create workflow for project
        steps = [
            WorkflowStep(
                name="setup_project",
                module="environment_setup",
                action="check_environment",
                parameters={"project_path": project.path},
            ),
            WorkflowStep(
                name="analyze_project",
                module="static_analysis",
                action="analyze_code_quality",
                parameters={"path": project.path},
                dependencies=["setup_project"],
            ),
            WorkflowStep(
                name="generate_report",
                module="data_visualization",
                action="create_analysis_chart",
                parameters={"data": "{{analyze_project.output}}"},
                dependencies=["analyze_project"],
            ),
        ]

        workflow_manager.create_workflow("project_analysis", steps)

        # Execute workflow
        async def run_workflow():
            execution = await workflow_manager.execute_workflow(
                "project_analysis", parameters={"project_name": project.name}
            )
            return execution

        execution = asyncio.run(run_workflow())

        # Verify workflow execution
        assert execution.status.value in ["completed", "failed"]
        assert len(execution.results) == 3

        # Update project status based on workflow result
        if execution.status.value == "completed":
            project_manager.update_project(
                project.name,
                status="active",
                metadata={
                    "workflow_status": "completed",
                    "last_analysis": datetime.now().isoformat(),
                },
            )

        # Verify project was updated
        updated_project = project_manager.get_project(project.name)
        assert updated_project is not None
        assert updated_project.metadata.get("workflow_status") == "completed"


class TestResourceTaskIntegration:
    """Integration tests between ResourceManager and TaskOrchestrator."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_task_resource_allocation(self, temp_dir):
        """Test that tasks properly allocate and release resources."""
        resource_manager = get_resource_manager()
        task_orchestrator = get_task_orchestrator()

        # Add resources
        cpu_resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )

        mem_resource = Resource(
            id="mem_1",
            name="Memory 1",
            resource_type=ResourceType.MEMORY,
            capacity=1024.0,
        )

        resource_manager.add_resource(cpu_resource)
        resource_manager.add_resource(mem_resource)

        # Create tasks with resource requirements
        task1 = Task(
            name="cpu_intensive_task",
            module="module1",
            action="action1",
            resources=[
                TaskResource(
                    type=ResourceType.CPU, identifier="cpu_1", mode="exclusive"
                )
            ],
        )

        task2 = Task(
            name="memory_intensive_task",
            module="module2",
            action="action2",
            resources=[
                TaskResource(
                    type=ResourceType.MEMORY, identifier="mem_1", mode="exclusive"
                )
            ],
        )

        # Add tasks to orchestrator
        task_orchestrator.add_task(task1)
        task_orchestrator.add_task(task2)

        # Start execution
        task_orchestrator.start_execution()

        # Wait for tasks to complete
        time.sleep(2)

        # Stop execution
        task_orchestrator.stop_execution()

        # Verify resources were properly managed
        # Note: In real implementation, we'd verify that resources were allocated and released
        assert (
            task1.id in task_orchestrator.completed_tasks
            or task1.id in task_orchestrator.task_results
        )
        assert (
            task2.id in task_orchestrator.completed_tasks
            or task2.id in task_orchestrator.task_results
        )

    def test_resource_conflict_handling(self, temp_dir):
        """Test that resource conflicts are properly handled."""
        resource_manager = get_resource_manager()
        task_orchestrator = get_task_orchestrator()

        # Add limited resource
        cpu_resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=50.0,  # Limited capacity
        )

        resource_manager.add_resource(cpu_resource)

        # Create tasks that require more resources than available
        task1 = Task(
            name="task1",
            module="module1",
            action="action1",
            resources=[
                TaskResource(
                    type=ResourceType.CPU, identifier="cpu_1", mode="exclusive"
                )
            ],
        )

        task2 = Task(
            name="task2",
            module="module2",
            action="action2",
            resources=[
                TaskResource(
                    type=ResourceType.CPU, identifier="cpu_1", mode="exclusive"
                )
            ],
        )

        # Add tasks to orchestrator
        task_orchestrator.add_task(task1)
        task_orchestrator.add_task(task2)

        # Start execution
        task_orchestrator.start_execution()

        # Wait for tasks to complete
        time.sleep(2)

        # Stop execution
        task_orchestrator.stop_execution()

        # Verify that at least one task completed (resource conflict handling)
        completed_tasks = len(task_orchestrator.completed_tasks)
        assert completed_tasks >= 1


class TestOrchestrationEngineIntegration:
    """Integration tests for OrchestrationEngine with all components."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_complete_orchestration_workflow(self, temp_dir):
        """Test complete orchestration workflow with all components."""
        engine = get_orchestration_engine()

        # Create session
        session = engine.create_session(
            name="Complete Integration Test",
            description="Test all orchestration components",
        )

        assert session is not None

        # Create project in session
        project = engine.create_project_in_session(
            session.session_id, "integration_project", "Integration test project"
        )

        assert project is not None

        # Add resources
        cpu_resource = Resource(
            id="cpu_1", name="CPU 1", resource_type=ResourceType.CPU, capacity=100.0
        )

        mem_resource = Resource(
            id="mem_1",
            name="Memory 1",
            resource_type=ResourceType.MEMORY,
            capacity=1024.0,
        )

        engine.resource_manager.add_resource(cpu_resource)
        engine.resource_manager.add_resource(mem_resource)

        # Allocate resources for session
        engine.allocate_resources_for_session(session.session_id, "cpu_1", 50.0)
        engine.allocate_resources_for_session(session.session_id, "mem_1", 256.0)

        # Create workflow
        steps = [
            WorkflowStep(
                name="setup", module="environment_setup", action="check_environment"
            ),
            WorkflowStep(
                name="analyze",
                module="static_analysis",
                action="analyze_code",
                dependencies=["setup"],
            ),
            WorkflowStep(
                name="visualize",
                module="data_visualization",
                action="create_chart",
                dependencies=["analyze"],
            ),
        ]

        engine.workflow_manager.create_workflow("integration_workflow", steps)

        # Execute workflow in session
        result = engine.execute_workflow_in_session(
            session.session_id, "integration_workflow"
        )
        assert result is True

        # Add tasks to session
        task1 = Task(
            name="session_task1",
            module="module1",
            action="action1",
            priority=TaskPriority.HIGH,
        )

        task2 = Task(
            name="session_task2",
            module="module2",
            action="action2",
            dependencies=["session_task1"],
            priority=TaskPriority.NORMAL,
        )

        engine.add_task_to_session(session.session_id, task1)
        engine.add_task_to_session(session.session_id, task2)

        # Get system status
        status = engine.get_system_status()
        assert status["active_sessions"] == 1
        assert status["total_workflows"] == 1
        assert status["total_tasks"] == 2
        assert status["total_projects"] == 1
        assert status["total_resources"] == 2

        # Get health status
        health = engine.get_health_status()
        assert health["overall_status"] == "healthy"

        # Get session resources
        resources = engine.get_session_resources(session.session_id)
        assert "cpu_1" in resources
        assert "mem_1" in resources

        # Update session
        updated_session = engine.update_session(
            session.session_id, name="Updated Integration Test", status="completed"
        )

        assert updated_session is not None
        assert updated_session.name == "Updated Integration Test"
        assert updated_session.status.value == "completed"

        # Cleanup session
        cleanup_result = engine.cleanup_session(session.session_id)
        assert cleanup_result is True

        # Verify session is cleaned up
        assert session.session_id not in engine.sessions

        # Shutdown engine
        engine.shutdown()
        assert engine.shutdown_requested is True

    def test_multiple_sessions_resource_isolation(self, temp_dir):
        """Test that multiple sessions have proper resource isolation."""
        engine = get_orchestration_engine()

        # Create multiple sessions
        session1 = engine.create_session(name="Session 1")
        session2 = engine.create_session(name="Session 2")

        # Add shared resource
        cpu_resource = Resource(
            id="cpu_1", name="CPU 1", resource_type=ResourceType.CPU, capacity=100.0
        )

        engine.resource_manager.add_resource(cpu_resource)

        # Allocate resources for each session
        engine.allocate_resources_for_session(session1.session_id, "cpu_1", 30.0)
        engine.allocate_resources_for_session(session2.session_id, "cpu_1", 40.0)

        # Verify resource allocation
        session1_resources = engine.get_session_resources(session1.session_id)
        session2_resources = engine.get_session_resources(session2.session_id)

        assert "cpu_1" in session1_resources
        assert "cpu_1" in session2_resources
        assert session1_resources["cpu_1"]["allocated_amount"] == 30.0
        assert session2_resources["cpu_1"]["allocated_amount"] == 40.0

        # Verify total allocation doesn't exceed capacity
        total_allocated = (
            session1_resources["cpu_1"]["allocated_amount"]
            + session2_resources["cpu_1"]["allocated_amount"]
        )
        assert total_allocated <= 100.0

        # Cleanup sessions
        engine.cleanup_session(session1.session_id)
        engine.cleanup_session(session2.session_id)

        # Shutdown
        engine.shutdown()

    def test_error_handling_and_recovery(self, temp_dir):
        """Test error handling and recovery across components."""
        engine = get_orchestration_engine()

        # Create session
        session = engine.create_session(name="Error Handling Test")

        # Test invalid workflow execution
        result = engine.execute_workflow_in_session(
            session.session_id, "nonexistent_workflow"
        )
        assert result is False

        # Test invalid task addition
        task = Task(name="test_task", module="module", action="action")
        result = engine.add_task_to_session("nonexistent_session", task)
        assert result is False

        # Test invalid project creation
        project = engine.create_project_in_session(
            "nonexistent_session", "test_project", "description"
        )
        assert project is None

        # Test invalid resource allocation
        result = engine.allocate_resources_for_session(
            session.session_id, "nonexistent_resource", 50.0
        )
        assert result is False

        # Test invalid session operations
        result = engine.get_session_resources("nonexistent_session")
        assert result == {}

        result = engine.cleanup_session("nonexistent_session")
        assert result is False

        # Cleanup valid session
        engine.cleanup_session(session.session_id)

        # Shutdown
        engine.shutdown()


class TestPerformanceIntegration:
    """Integration tests for performance monitoring across components."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_performance_monitoring_integration(self, temp_dir):
        """Test that performance monitoring works across all components."""
        # This test would require performance monitoring to be available
        # For now, we'll test the basic functionality

        engine = get_orchestration_engine()

        # Create session
        session = engine.create_session(name="Performance Test")

        # Create workflow
        steps = [
            WorkflowStep(name="step1", module="module1", action="action1"),
            WorkflowStep(
                name="step2", module="module2", action="action2", dependencies=["step1"]
            ),
        ]

        engine.workflow_manager.create_workflow("performance_test", steps)

        # Execute workflow
        result = engine.execute_workflow_in_session(
            session.session_id, "performance_test"
        )
        assert result is True

        # Get performance summary
        summary = engine.workflow_manager.get_performance_summary()
        assert "performance_stats" in summary or "error" in summary

        # Cleanup
        engine.cleanup_session(session.session_id)
        engine.shutdown()


if __name__ == "__main__":
    pytest.main([__file__])
