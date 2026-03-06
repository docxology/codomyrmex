import sys

import pytest

from codomyrmex.logistics.orchestration.project import (
    ProjectType,
    Task,
    WorkflowStep,
    get_orchestration_engine,
    get_project_manager,
    get_resource_manager,
    get_task_orchestrator,
    get_workflow_manager,
)
from codomyrmex.performance.monitoring.performance_monitor import PerformanceMonitor

pytestmark = pytest.mark.integration

try:
    ORCHESTRATION_AVAILABLE = True
except ImportError:
    ORCHESTRATION_AVAILABLE = False


class TestOrchestrationIntegration:
    """Integration tests for orchestration components."""

    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set up test environment."""
        self.engine = get_orchestration_engine()
        self.wf_manager = get_workflow_manager()
        self.task_orchestrator = get_task_orchestrator()
        self.project_manager = get_project_manager()
        self.resource_manager = get_resource_manager()

        # Clean up any existing test data
        self._cleanup_test_data()
        yield
        self._cleanup_test_data()

    def _cleanup_test_data(self):
        """Clean up test data."""
        import shutil
        from pathlib import Path

        # Remove test workflows
        test_workflows = ["test_workflow", "integration_test_workflow", "perf_test_workflow", "error_test_workflow"]
        for i in range(3):
            test_workflows.append(f"concurrent_workflow_{i}")
            
        for wf_name in test_workflows:
            if hasattr(self.wf_manager, "workflows") and wf_name in self.wf_manager.workflows:
                del self.wf_manager.workflows[wf_name]

        # Remove test projects
        test_projects = ["test_project", "integration_test_project", "nonexistent_project"]
        for proj_name in test_projects:
            if hasattr(self.project_manager, "active_projects") and proj_name in self.project_manager.active_projects:
                del self.project_manager.active_projects[proj_name]
                
            # Clean up the physical folders
            proj_path = Path.cwd() / proj_name
            if proj_path.exists():
                shutil.rmtree(proj_path)

    def test_workflow_creation_and_execution(self):
        """Test workflow creation and execution."""
        steps = [
            WorkflowStep(
                name="test_step",
                module="environment_setup",
                action="check_environment",
                parameters={},
            )
        ]

        success = self.wf_manager.create_workflow("test_workflow", steps)
        assert success

        workflows = self.wf_manager.list_workflows()
        assert "test_workflow" in workflows

        result = self.wf_manager.execute_workflow("test_workflow")
        assert result is not None
        assert result.workflow_name == "test_workflow"

    def test_project_creation_and_management(self):
        """Test project creation and management."""
        project = self.project_manager.create_project(
            name="test_project",
            type=ProjectType.AI_ANALYSIS,
            description="Test project for integration testing",
        )

        assert project is not None
        assert project.name == "test_project"
        assert project.type == ProjectType.AI_ANALYSIS

        projects = [p.name for p in self.project_manager.list_projects()]
        assert "test_project" in projects

        # Test project status
        proj = self.project_manager.get_project("test_project")
        assert proj is not None
        assert proj.status.value == "active"

    def test_task_orchestration_with_dependencies(self):
        """Test task orchestration with dependencies."""
        task1 = Task(
            name="task1",
            module="environment_setup",
            action="check_environment",
            parameters={},
        )

        task2 = Task(
            name="task2",
            module="static_analysis",
            action="analyze_code_quality",
            parameters={"path": "."},
            dependencies=[task1.id],
        )

        task1_id = self.task_orchestrator.submit_task(task1)
        task2_id = self.task_orchestrator.submit_task(task2)

        assert task1_id is not None
        assert task2_id is not None

        tasks = self.task_orchestrator.list_tasks()
        assert len(tasks) >= 2

        self.task_orchestrator.start_processing()

        # Wait for completion
        import time
        from codomyrmex.logistics.orchestration.project.task_orchestrator import TaskStatus
        
        timeout = 10.0
        start = time.time()
        while time.time() - start < timeout:
            t1 = self.task_orchestrator.get_task(task1_id)
            t2 = self.task_orchestrator.get_task(task2_id)
            if t1 and t2 and t1.status in (TaskStatus.COMPLETED, TaskStatus.FAILED) and t2.status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                break
            time.sleep(0.1)

        t1 = self.task_orchestrator.get_task(task1_id)
        t2 = self.task_orchestrator.get_task(task2_id)
        assert t1.status == TaskStatus.COMPLETED or t1.status == TaskStatus.FAILED
        assert t2.status == TaskStatus.COMPLETED or t2.status == TaskStatus.FAILED

    def test_resource_allocation_and_deallocation(self):
        """Test resource allocation and deallocation."""
        user_id = "test_user"

        allocated = self.resource_manager.allocate(
            resource_id="sys-compute",
            requester_id=user_id,
            amount=1.0
        )
        assert allocated is not None

        res = self.resource_manager.get_resource("sys-compute")
        assert res is not None
        assert allocated.allocation_id in res.allocations

        deallocated = self.resource_manager.release(allocated.allocation_id)
        assert deallocated

        assert allocated.allocation_id not in res.allocations

    def test_orchestration_engine_session_management(self):
        """Test orchestration engine session management."""
        session_id = self.engine.create_session(
            user_id="test_user", mode="resource_aware"
        )
        assert session_id is not None

        session = self.engine.get_session(session_id)
        assert session is not None
        assert session.user_id == "test_user"

        closed = self.engine.close_session(session_id)
        assert closed

        session_after = self.engine.get_session(session_id)
        assert session_after is None

    def test_complex_workflow_execution(self):
        """Test complex workflow execution through orchestration engine."""
        workflow_definition = {
            "steps": [
                {
                    "name": "step1",
                    "module": "environment_setup",
                    "action": "check_environment",
                    "parameters": {},
                },
                {
                    "name": "step2",
                    "module": "static_analysis",
                    "action": "analyze_code_quality",
                    "parameters": {"path": "."},
                },
            ],
            "dependencies": {"step2": ["step1"]},
        }

        result = self.engine.execute_complex_workflow(workflow_definition)

        assert result is not None
        assert "success" in result
        assert "results" in result

    def test_system_health_check(self):
        """Test system health check."""
        health = self.engine.health_check()

        assert health is not None
        assert "overall_status" in health
        assert "components" in health
        assert "timestamp" in health

        expected_components = [
            "workflow_manager",
            "task_orchestrator",
            "project_manager",
            "resource_manager",
        ]
        for component in expected_components:
            assert component in health["components"]

    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration."""
        try:
            monitor = PerformanceMonitor()
            assert monitor is not None

            steps = [
                WorkflowStep(
                    name="perf_test_step",
                    module="environment_setup",
                    action="check_environment",
                    parameters={},
                )
            ]

            self.wf_manager.create_workflow("perf_test_workflow", steps)
            result = self.wf_manager.execute_workflow("perf_test_workflow")
            assert result is not None

            perf_summary = self.wf_manager.get_performance_summary()
            assert perf_summary is not None

        except ImportError:
            pytest.skip("Performance monitoring not available")

    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        steps = [
            WorkflowStep(
                name="invalid_step",
                module="nonexistent_module",
                action="nonexistent_action",
                parameters={},
            )
        ]

        self.wf_manager.create_workflow("error_test_workflow", steps)
        # Assuming workflow returns WorkflowExecution
        result = self.wf_manager.execute_workflow("error_test_workflow")

        # Wait for the task to actually fail in the background
        self.task_orchestrator.wait_for_completion(timeout=2.0)
        
        # Check task statuses since WorkflowExecution status isn't magically updated
        # if the task runner failed them in the background
        stats = self.task_orchestrator.get_execution_stats()

        assert result is not None
        # Either the workflow status was updated to failed, or tasks failed
        assert result.error is not None or result.status.value == "failed" or stats["failed"] > 0

    def test_concurrent_execution(self):
        """Test concurrent execution of multiple workflows."""
        workflows = []
        for i in range(3):
            steps = [
                WorkflowStep(
                    name=f"concurrent_step_{i}",
                    module="environment_setup",
                    action="check_environment",
                    parameters={},
                )
            ]
            wf_name = f"concurrent_workflow_{i}"
            self.wf_manager.create_workflow(wf_name, steps)
            workflows.append(wf_name)

        results = []
        for wf_name in workflows:
            result = self.wf_manager.execute_workflow(wf_name)
            results.append(result)

        assert len(results) == 3
        for result in results:
            assert result is not None

    def test_resource_contention_handling(self):
        """Test handling of resource contention."""
        user1 = "user1"
        user2 = "user2"

        res = self.resource_manager.get_resource("sys-compute")
        capacity = res.capacity

        allocated1 = self.resource_manager.allocate("sys-compute", user1, amount=capacity)
        assert allocated1 is not None

        allocated2 = self.resource_manager.allocate("sys-compute", user2, amount= capacity)
        assert allocated2 is None

        deallocated = self.resource_manager.release(allocated1.allocation_id)
        assert deallocated

        allocated2_retry = self.resource_manager.allocate("sys-compute", user2, amount=capacity)
        assert allocated2_retry is not None

        self.resource_manager.release(allocated2_retry.allocation_id)


class TestOrchestrationEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture(autouse=True)
    def setup_environment(self):
        """Set up test environment."""
        self.engine = get_orchestration_engine()
        self.wf_manager = get_workflow_manager()
        self.task_orchestrator = get_task_orchestrator()
        self.project_manager = get_project_manager()
        self.resource_manager = get_resource_manager()

    def test_nonexistent_workflow_execution(self):
        """Test execution of nonexistent workflow."""
        with pytest.raises(ValueError):
            self.wf_manager.execute_workflow("nonexistent_workflow")

    def test_nonexistent_project_operations(self):
        """Test operations on nonexistent project."""
        project = self.project_manager.get_project("nonexistent_project")
        assert project is None

    def test_invalid_task_creation(self):
        """Test creation of invalid tasks."""
        task = Task(
            name="invalid_task",
            module="nonexistent_module",
            action="nonexistent_action",
            parameters={},
        )
        assert task is not None

        task_id = self.task_orchestrator.submit_task(task)
        assert task_id is not None

    def test_resource_allocation_with_invalid_requirements(self):
        """Test resource allocation with invalid requirements."""
        user_id = "test_user"
        allocated = self.resource_manager.allocate("nonexistent-resource", user_id, 1.0)
        assert allocated is None

    def test_circular_dependencies(self):
        """Test handling of circular dependencies in tasks."""
        task1 = Task(
            name="task1",
            module="environment_setup",
            action="check_environment",
            parameters={},
            dependencies=["task2"],
        )

        task2 = Task(
            name="task2",
            module="static_analysis",
            action="analyze_code_quality",
            parameters={"path": "."},
            dependencies=["task1"],
        )

        # Note: In the new API dependencies are task.id, so let's fix that
        task1.dependencies = [task2.id]
        task2.dependencies = [task1.id]

        t1_id = self.task_orchestrator.submit_task(task1)
        t2_id = self.task_orchestrator.submit_task(task2)

        self.task_orchestrator.start_processing()

        import time
        from codomyrmex.logistics.orchestration.project.task_orchestrator import TaskStatus
        
        time.sleep(1.0)
        
        t1 = self.task_orchestrator.get_task(t1_id)
        t2 = self.task_orchestrator.get_task(t2_id)
        
        # They should be BLOCKED because of circular dependency
        assert t1.status == TaskStatus.BLOCKED
        assert t2.status == TaskStatus.BLOCKED


def run_integration_tests():
    """Run all integration tests."""
    print("Running Codomyrmex Orchestration Integration Tests")
    print("=" * 60)
    exit_code = pytest.main([__file__, "-v"])
    return exit_code == 0

if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
