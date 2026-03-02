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
        # Remove test workflows
        test_workflows = ["test_workflow", "integration_test_workflow"]
        for wf_name in test_workflows:
            if wf_name in self.wf_manager.workflows:
                del self.wf_manager.workflows[wf_name]

        # Remove test projects
        test_projects = ["test_project", "integration_test_project"]
        for proj_name in test_projects:
            if proj_name in self.project_manager.projects:
                del self.project_manager.projects[proj_name]

    def test_workflow_creation_and_execution(self):
        """Test workflow creation and execution."""
        # Create a test workflow
        steps = [
            WorkflowStep(
                name="test_step",
                module="environment_setup",
                action="check_environment",
                parameters={}
            )
        ]

        success = self.wf_manager.create_workflow("test_workflow", steps)
        assert success

        # Verify workflow exists
        workflows = self.wf_manager.list_workflows()
        assert "test_workflow" in workflows

        # Test workflow execution
        result = self.wf_manager.execute_workflow("test_workflow")
        assert result is not None
        assert result.workflow_name == "test_workflow"

    def test_project_creation_and_management(self):
        """Test project creation and management."""
        # Create a test project
        project = self.project_manager.create_project(
            name="test_project",
            template_name="ai_analysis",
            description="Test project for integration testing"
        )

        assert project is not None
        assert project.name == "test_project"
        assert project.type == ProjectType.AI_ANALYSIS

        # Verify project exists
        projects = self.project_manager.list_projects()
        assert "test_project" in projects

        # Test project status
        status = self.project_manager.get_project_status("test_project")
        assert status is not None
        assert status['name'] == "test_project"

    def test_task_orchestration_with_dependencies(self):
        """Test task orchestration with dependencies."""
        # Create tasks with dependencies
        task1 = Task(
            name="task1",
            module="environment_setup",
            action="check_environment",
            parameters={}
        )

        task2 = Task(
            name="task2",
            module="static_analysis",
            action="analyze_code_quality",
            parameters={"path": "."},
            dependencies=[task1.id]
        )

        # Add tasks to orchestrator
        task1_id = self.task_orchestrator.add_task(task1)
        task2_id = self.task_orchestrator.add_task(task2)

        assert task1_id is not None
        assert task2_id is not None

        # Verify tasks are in queue
        tasks = self.task_orchestrator.list_tasks()
        assert len(tasks) == 2

        # Test task execution
        self.task_orchestrator.start_execution()

        # Wait for completion
        completed = self.task_orchestrator.wait_for_completion(timeout=10.0)
        assert completed

        # Verify task results
        task1_result = self.task_orchestrator.get_task_result(task1_id)
        task2_result = self.task_orchestrator.get_task_result(task2_id)

        assert task1_result is not None
        assert task2_result is not None

    def test_resource_allocation_and_deallocation(self):
        """Test resource allocation and deallocation."""
        user_id = "test_user"
        requirements = {
            "cpu": {"cores": 1},
            "memory": {"gb": 1}
        }

        # Allocate resources
        allocated = self.resource_manager.allocate_resources(user_id, requirements)
        assert allocated is not None

        # Verify allocation
        user_allocations = self.resource_manager.get_user_allocations(user_id)
        assert len(user_allocations) > 0

        # Deallocate resources
        deallocated = self.resource_manager.deallocate_resources(user_id)
        assert deallocated

        # Verify deallocation
        user_allocations_after = self.resource_manager.get_user_allocations(user_id)
        assert len(user_allocations_after) == 0

    def test_orchestration_engine_session_management(self):
        """Test orchestration engine session management."""
        # Create session
        session_id = self.engine.create_session(
            user_id="test_user",
            mode="resource_aware"
        )

        assert session_id is not None

        # Verify session exists
        session = self.engine.get_session(session_id)
        assert session is not None
        assert session.user_id == "test_user"

        # Close session
        closed = self.engine.close_session(session_id)
        assert closed

        # Verify session is closed
        session_after = self.engine.get_session(session_id)
        assert session_after is None

    def test_complex_workflow_execution(self):
        """Test complex workflow execution through orchestration engine."""
        # Define complex workflow
        workflow_definition = {
            "steps": [
                {
                    "name": "step1",
                    "module": "environment_setup",
                    "action": "check_environment",
                    "parameters": {}
                },
                {
                    "name": "step2",
                    "module": "static_analysis",
                    "action": "analyze_code_quality",
                    "parameters": {"path": "."}
                }
            ],
            "dependencies": {
                "step2": ["step1"]
            }
        }

        # Execute workflow
        result = self.engine.execute_complex_workflow(workflow_definition)

        assert result is not None
        assert 'success' in result
        assert 'results' in result

    def test_system_health_check(self):
        """Test system health check."""
        health = self.engine.health_check()

        assert health is not None
        assert 'overall_status' in health
        assert 'components' in health
        assert 'timestamp' in health

        # Verify expected components are checked
        expected_components = [
            'workflow_manager',
            'task_orchestrator',
            'project_manager',
            'resource_manager'
        ]

        for component in expected_components:
            assert component in health['components']

    def test_performance_monitoring_integration(self):
        """Test performance monitoring integration."""
        try:

            # Create performance monitor
            monitor = PerformanceMonitor()
            assert monitor is not None

            # Test workflow with performance monitoring
            steps = [
                WorkflowStep(
                    name="perf_test_step",
                    module="environment_setup",
                    action="check_environment",
                    parameters={}
                )
            ]

            self.wf_manager.create_workflow("perf_test_workflow", steps)
            result = self.wf_manager.execute_workflow("perf_test_workflow")

            assert result is not None

            # Get performance summary
            perf_summary = self.wf_manager.get_performance_summary()
            assert perf_summary is not None

        except ImportError:
            pytest.skip("Performance monitoring not available")

    def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms."""
        # Test workflow with invalid module
        steps = [
            WorkflowStep(
                name="invalid_step",
                module="nonexistent_module",
                action="nonexistent_action",
                parameters={}
            )
        ]

        self.wf_manager.create_workflow("error_test_workflow", steps)
        result = self.wf_manager.execute_workflow("error_test_workflow")

        # Should handle error gracefully
        assert result is not None
        assert 'errors' in result.__dict__

    def test_concurrent_execution(self):
        """Test concurrent execution of multiple workflows."""
        # Create multiple workflows
        workflows = []
        for i in range(3):
            steps = [
                WorkflowStep(
                    name=f"concurrent_step_{i}",
                    module="environment_setup",
                    action="check_environment",
                    parameters={}
                )
            ]
            wf_name = f"concurrent_workflow_{i}"
            self.wf_manager.create_workflow(wf_name, steps)
            workflows.append(wf_name)

        # Execute workflows concurrently
        results = []
        for wf_name in workflows:
            result = self.wf_manager.execute_workflow(wf_name)
            results.append(result)

        # Verify all workflows completed
        assert len(results) == 3
        for result in results:
            assert result is not None

    def test_resource_contention_handling(self):
        """Test handling of resource contention."""
        user1 = "user1"
        user2 = "user2"

        # Both users request exclusive access to same resource
        requirements = {
            "cpu": {"cores": 4}  # Request all available cores
        }

        # First user should get resources
        allocated1 = self.resource_manager.allocate_resources(user1, requirements)
        assert allocated1 is not None

        # Second user should fail to get resources
        allocated2 = self.resource_manager.allocate_resources(user2, requirements)
        assert allocated2 is None

        # Release first user's resources
        deallocated = self.resource_manager.deallocate_resources(user1)
        assert deallocated

        # Now second user should be able to get resources
        allocated2_retry = self.resource_manager.allocate_resources(user2, requirements)
        assert allocated2_retry is not None

        # Clean up
        self.resource_manager.deallocate_resources(user2)


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
        yield

    def test_nonexistent_workflow_execution(self):
        """Test execution of nonexistent workflow."""
        with pytest.raises(ValueError):
            self.wf_manager.execute_workflow("nonexistent_workflow")

    def test_nonexistent_project_operations(self):
        """Test operations on nonexistent project."""
        # Test getting nonexistent project
        project = self.project_manager.get_project("nonexistent_project")
        assert project is None

        # Test project status for nonexistent project
        status = self.project_manager.get_project_status("nonexistent_project")
        assert status is None

    def test_invalid_task_creation(self):
        """Test creation of invalid tasks."""
        # Test task with invalid module
        task = Task(
            name="invalid_task",
            module="nonexistent_module",
            action="nonexistent_action",
            parameters={}
        )

        # Should not raise exception during creation
        assert task is not None

        # But execution should fail gracefully
        task_id = self.task_orchestrator.add_task(task)
        assert task_id is not None

    def test_resource_allocation_with_invalid_requirements(self):
        """Test resource allocation with invalid requirements."""
        user_id = "test_user"

        # Test with invalid resource type
        invalid_requirements = {
            "invalid_resource": {"amount": 1}
        }

        allocated = self.resource_manager.allocate_resources(user_id, invalid_requirements)
        assert allocated is None

    def test_circular_dependencies(self):
        """Test handling of circular dependencies in tasks."""
        # Create tasks with circular dependencies
        task1 = Task(
            name="task1",
            module="environment_setup",
            action="check_environment",
            parameters={},
            dependencies=["task2"]  # Depends on task2
        )

        task2 = Task(
            name="task2",
            module="static_analysis",
            action="analyze_code_quality",
            parameters={"path": "."},
            dependencies=["task1"]  # Depends on task1
        )

        # Add tasks to orchestrator
        self.task_orchestrator.add_task(task1)
        self.task_orchestrator.add_task(task2)

        # Start execution
        self.task_orchestrator.start_execution()

        # Wait for completion (should timeout due to circular dependency)
        completed = self.task_orchestrator.wait_for_completion(timeout=5.0)
        assert not completed  # Should not complete due to circular dependency


def run_integration_tests():
    """Run all integration tests."""
    print("Running Codomyrmex Orchestration Integration Tests")
    print("=" * 60)

    # Use pytest programmatic API
    exit_code = pytest.main([__file__, "-v"])

    return exit_code == 0


if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
