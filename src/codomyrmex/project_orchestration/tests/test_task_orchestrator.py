"""
Comprehensive unit tests for TaskOrchestrator.

This module contains extensive unit tests for the TaskOrchestrator class,
covering all public methods, error conditions, and edge cases.
"""

import pytest
import time
import threading
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

from codomyrmex.project_orchestration.task_orchestrator import (
    TaskOrchestrator,
    Task,
    TaskStatus,
    TaskPriority,
    TaskResult,
)
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)
from codomyrmex.project_orchestration.task_orchestrator import (
    TaskResource,
    ResourceType,
    ResourceManager,
    TaskQueue,
)


class TestTaskResource:
    """Test cases for TaskResource dataclass."""

    def test_task_resource_creation(self):
        """Test basic TaskResource creation."""
        resource = TaskResource(
            type=ResourceType.CPU, identifier="cpu_1", mode="exclusive", timeout=300
        )

        assert resource.type == ResourceType.CPU
        assert resource.identifier == "cpu_1"
        assert resource.mode == "exclusive"
        assert resource.timeout == 300

    def test_task_resource_defaults(self):
        """Test TaskResource with default values."""
        resource = TaskResource(type=ResourceType.MEMORY, identifier="mem_1")

        assert resource.type == ResourceType.MEMORY
        assert resource.identifier == "mem_1"
        assert resource.mode == "read"
        assert resource.timeout is None


class TestTaskResult:
    """Test cases for TaskResult dataclass."""

    def test_task_result_creation(self):
        """Test basic TaskResult creation."""
        result = TaskResult(
            success=True,
            data={"output": "test_data"},
            execution_time=1.5,
            memory_usage=1024.0,
            metadata={"key": "value"},
        )

        assert result.success is True
        assert result.data == {"output": "test_data"}
        assert result.error_message is None
        assert result.error_type is None
        assert result.execution_time == 1.5
        assert result.memory_usage == 1024.0
        assert result.metadata == {"key": "value"}

    def test_task_result_failure(self):
        """Test TaskResult for failed task."""
        result = TaskResult(
            success=False,
            error_message="Task failed",
            error_type="RuntimeError",
            execution_time=0.5,
        )

        assert result.success is False
        assert result.error_message == "Task failed"
        assert result.error_type == "RuntimeError"
        assert result.data is None
        assert result.execution_time == 0.5

    def test_task_result_to_dict(self):
        """Test TaskResult serialization to dictionary."""
        result = TaskResult(success=True, data={"test": "data"}, execution_time=2.0)

        data_dict = result.to_dict()

        assert data_dict["success"] is True
        assert data_dict["data"] == {"test": "data"}
        assert data_dict["execution_time"] == 2.0
        assert data_dict["memory_usage"] == 0.0

    def test_task_result_from_dict(self):
        """Test TaskResult creation from dictionary."""
        data_dict = {
            "success": True,
            "data": {"test": "data"},
            "execution_time": 2.0,
            "memory_usage": 512.0,
        }

        result = TaskResult.from_dict(data_dict)

        assert result.success is True
        assert result.data == {"test": "data"}
        assert result.execution_time == 2.0
        assert result.memory_usage == 512.0


class TestTask:
    """Test cases for Task dataclass."""

    def test_task_creation(self):
        """Test basic Task creation."""
        task = Task(
            name="test_task",
            description="A test task",
            module="test_module",
            action="test_action",
            parameters={"param1": "value1"},
            priority=TaskPriority.HIGH,
            timeout=300,
            max_retries=5,
        )

        assert task.name == "test_task"
        assert task.description == "A test_task"
        assert task.module == "test_module"
        assert task.action == "test_action"
        assert task.parameters == {"param1": "value1"}
        assert task.priority == TaskPriority.HIGH
        assert task.timeout == 300
        assert task.max_retries == 5
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 0
        assert task.created_at is not None

    def test_task_auto_name_generation(self):
        """Test automatic task name generation."""
        task = Task(module="test_module", action="test_action")

        assert task.name == "test_module.test_action"
        assert task.module == "test_module"
        assert task.action == "test_action"

    def test_task_execution_time_property(self):
        """Test task execution time calculation."""
        task = Task(name="test_task", module="module", action="action")

        # No execution time initially
        assert task.execution_time is None

        # Set start and end times
        task.started_at = datetime.now(timezone.utc)
        time.sleep(0.1)  # Small delay
        task.completed_at = datetime.now(timezone.utc)

        # Should have execution time now
        assert task.execution_time is not None
        assert task.execution_time > 0

    def test_task_can_retry(self):
        """Test task retry capability check."""
        task = Task(name="test_task", module="module", action="action", max_retries=3)

        # Initially can retry
        assert task.can_retry() is False  # Not failed yet

        # Set as failed
        task.status = TaskStatus.FAILED
        assert task.can_retry() is True

        # After max retries
        task.retry_count = 3
        assert task.can_retry() is False

    def test_task_is_ready(self):
        """Test task readiness check."""
        task = Task(
            name="test_task",
            module="module",
            action="action",
            dependencies=["dep1", "dep2"],
        )

        # Not ready initially (dependencies not satisfied)
        assert task.is_ready(set()) is False
        assert task.is_ready({"dep1"}) is False

        # Ready when all dependencies satisfied
        assert task.is_ready({"dep1", "dep2"}) is True

        # Task with no dependencies is always ready
        simple_task = Task(name="simple", module="module", action="action")
        assert simple_task.is_ready(set()) is True

    def test_task_serialization(self):
        """Test task serialization to/from dictionary."""
        task = Task(
            name="test_task",
            module="test_module",
            action="test_action",
            parameters={"param": "value"},
            priority=TaskPriority.HIGH,
            dependencies=["dep1"],
            resources=[TaskResource(type=ResourceType.CPU, identifier="cpu_1")],
            tags=["test", "unit"],
            metadata={"key": "value"},
        )

        # Test to_dict
        task_dict = task.to_dict()
        assert task_dict["name"] == "test_task"
        assert task_dict["module"] == "test_module"
        assert task_dict["priority"] == TaskPriority.HIGH.value
        assert task_dict["status"] == TaskStatus.PENDING.value
        assert len(task_dict["resources"]) == 1

        # Test from_dict
        restored_task = Task.from_dict(task_dict)
        assert restored_task.name == "test_task"
        assert restored_task.module == "test_module"
        assert restored_task.priority == TaskPriority.HIGH
        assert restored_task.status == TaskStatus.PENDING
        assert len(restored_task.resources) == 1


class TestResourceManager:
    """Test cases for ResourceManager class."""

    def test_resource_manager_initialization(self):
        """Test ResourceManager initialization."""
        manager = ResourceManager()

        assert manager.resource_locks == {}
        assert manager.resource_users == {}
        assert manager.lock is not None

    def test_acquire_resources_success(self):
        """Test successful resource acquisition."""
        manager = ResourceManager()

        task = Task(
            name="test_task",
            module="module",
            action="action",
            resources=[
                TaskResource(
                    type=ResourceType.CPU, identifier="cpu_1", mode="exclusive"
                ),
                TaskResource(type=ResourceType.MEMORY, identifier="mem_1", mode="read"),
            ],
        )

        result = manager.acquire_resources(task)

        assert result is True
        assert "cpu:cpu_1" in manager.resource_users
        assert "memory:mem_1" in manager.resource_users
        assert task.id in manager.resource_users["cpu:cpu_1"]
        assert task.id in manager.resource_users["memory:mem_1"]

    def test_acquire_resources_exclusive_conflict(self):
        """Test resource acquisition with exclusive mode conflict."""
        manager = ResourceManager()

        # First task acquires exclusive resource
        task1 = Task(
            name="task1",
            module="module",
            action="action",
            resources=[
                TaskResource(
                    type=ResourceType.CPU, identifier="cpu_1", mode="exclusive"
                )
            ],
        )

        task2 = Task(
            name="task2",
            module="module",
            action="action",
            resources=[
                TaskResource(
                    type=ResourceType.CPU, identifier="cpu_1", mode="exclusive"
                )
            ],
        )

        # First task succeeds
        assert manager.acquire_resources(task1) is True

        # Second task fails due to exclusive conflict
        assert manager.acquire_resources(task2) is False

    def test_acquire_resources_write_conflict(self):
        """Test resource acquisition with write mode conflict."""
        manager = ResourceManager()

        # First task acquires resource for reading
        task1 = Task(
            name="task1",
            module="module",
            action="action",
            resources=[
                TaskResource(type=ResourceType.CPU, identifier="cpu_1", mode="read")
            ],
        )

        task2 = Task(
            name="task2",
            module="module",
            action="action",
            resources=[
                TaskResource(type=ResourceType.CPU, identifier="cpu_1", mode="write")
            ],
        )

        # First task succeeds
        assert manager.acquire_resources(task1) is True

        # Second task fails due to write conflict
        assert manager.acquire_resources(task2) is False

    def test_release_resources(self):
        """Test resource release."""
        manager = ResourceManager()

        task = Task(
            name="test_task",
            module="module",
            action="action",
            resources=[TaskResource(type=ResourceType.CPU, identifier="cpu_1")],
        )

        # Acquire resources
        assert manager.acquire_resources(task) is True
        assert task.id in manager.resource_users["cpu:cpu_1"]

        # Release resources
        manager.release_resources(task)
        assert task.id not in manager.resource_users["cpu:cpu_1"]


class TestTaskQueue:
    """Test cases for TaskQueue class."""

    def test_task_queue_initialization(self):
        """Test TaskQueue initialization."""
        queue = TaskQueue()

        assert queue.queue is not None
        assert queue.tasks == {}
        assert queue.lock is not None

    def test_add_task(self):
        """Test adding task to queue."""
        queue = TaskQueue()

        task = Task(name="test_task", module="module", action="action")

        queue.add_task(task)

        assert task.id in queue.tasks
        assert queue.tasks[task.id] == task

    def test_get_next_ready_task(self):
        """Test getting next ready task from queue."""
        queue = TaskQueue()

        # Add tasks with dependencies
        task1 = Task(name="task1", module="module", action="action")
        task2 = Task(
            name="task2", module="module", action="action", dependencies=["task1"]
        )

        queue.add_task(task1)
        queue.add_task(task2)

        # Initially only task1 should be ready
        ready_task = queue.get_next_ready_task(set())
        assert ready_task is not None
        assert ready_task.name == "task1"

        # After task1 completes, task2 should be ready
        ready_task = queue.get_next_ready_task({"task1"})
        assert ready_task is not None
        assert ready_task.name == "task2"

    def test_remove_task(self):
        """Test removing task from queue."""
        queue = TaskQueue()

        task = Task(name="test_task", module="module", action="action")
        queue.add_task(task)

        assert task.id in queue.tasks

        result = queue.remove_task(task.id)
        assert result is True
        assert task.id not in queue.tasks

    def test_get_task(self):
        """Test getting task by ID."""
        queue = TaskQueue()

        task = Task(name="test_task", module="module", action="action")
        queue.add_task(task)

        retrieved_task = queue.get_task(task.id)
        assert retrieved_task == task

        # Test non-existent task
        non_existent = queue.get_task("non_existent")
        assert non_existent is None


class TestTaskOrchestrator:
    """Test cases for TaskOrchestrator class."""

    @pytest.fixture
    def orchestrator(self):
        """Create a TaskOrchestrator instance for testing."""
        return TaskOrchestrator(max_workers=2)

    def test_orchestrator_initialization(self):
        """Test TaskOrchestrator initialization."""
        orchestrator = TaskOrchestrator(max_workers=4)

        assert orchestrator.max_workers == 4
        assert orchestrator.executor is not None
        assert orchestrator.resource_manager is not None
        assert orchestrator.task_queue is not None
        assert orchestrator.completed_tasks == set()
        assert orchestrator.running_tasks == {}
        assert orchestrator.task_results == {}
        assert orchestrator.shutdown_requested is False

    def test_add_task(self, orchestrator):
        """Test adding task to orchestrator."""
        task = Task(name="test_task", module="module", action="action")

        task_id = orchestrator.add_task(task)

        assert task_id == task.id
        assert task.id in orchestrator.task_queue.tasks

    def test_create_task(self, orchestrator):
        """Test creating task through orchestrator."""
        task = orchestrator.create_task(
            name="test_task",
            module="test_module",
            action="test_action",
            parameters={"param": "value"},
            priority=TaskPriority.HIGH,
            timeout=300,
        )

        assert task.name == "test_task"
        assert task.module == "test_module"
        assert task.action == "test_action"
        assert task.parameters == {"param": "value"}
        assert task.priority == TaskPriority.HIGH
        assert task.timeout == 300
        assert task.id in orchestrator.task_queue.tasks

    def test_get_task(self, orchestrator):
        """Test getting task by ID."""
        task = Task(name="test_task", module="module", action="action")
        orchestrator.add_task(task)

        retrieved_task = orchestrator.get_task(task.id)
        assert retrieved_task == task

        # Test non-existent task
        non_existent = orchestrator.get_task("non_existent")
        assert non_existent is None

    def test_list_tasks(self, orchestrator):
        """Test listing tasks."""
        # Add tasks with different statuses
        task1 = Task(name="task1", module="module", action="action")
        task1.status = TaskStatus.PENDING

        task2 = Task(name="task2", module="module", action="action")
        task2.status = TaskStatus.RUNNING

        orchestrator.add_task(task1)
        orchestrator.add_task(task2)

        # List all tasks
        all_tasks = orchestrator.list_tasks()
        assert len(all_tasks) == 2

        # List tasks by status
        pending_tasks = orchestrator.list_tasks(TaskStatus.PENDING)
        assert len(pending_tasks) == 1
        assert pending_tasks[0].name == "task1"

        running_tasks = orchestrator.list_tasks(TaskStatus.RUNNING)
        assert len(running_tasks) == 1
        assert running_tasks[0].name == "task2"

    def test_start_stop_execution(self, orchestrator):
        """Test starting and stopping execution engine."""
        # Start execution
        orchestrator.start_execution()
        assert orchestrator.execution_thread is not None
        assert orchestrator.execution_thread.is_alive()

        # Stop execution
        orchestrator.stop_execution()
        assert orchestrator.shutdown_requested is True

    def test_task_execution_flow(self, orchestrator):
        """Test complete task execution flow."""
        # Create a simple task
        task = Task(
            name="test_task",
            module="module",
            action="action",
            parameters={"test": "value"},
        )

        orchestrator.add_task(task)

        # Start execution
        orchestrator.start_execution()

        # Wait for task to complete
        time.sleep(1)

        # Stop execution
        orchestrator.stop_execution()

        # Check that task was processed
        assert (
            task.id in orchestrator.completed_tasks
            or task.id in orchestrator.task_results
        )

    def test_task_with_dependencies(self, orchestrator):
        """Test task execution with dependencies."""
        # Create tasks with dependencies
        task1 = Task(name="task1", module="module", action="action")
        task2 = Task(
            name="task2", module="module", action="action", dependencies=["task1"]
        )

        orchestrator.add_task(task1)
        orchestrator.add_task(task2)

        # Start execution
        orchestrator.start_execution()

        # Wait for tasks to complete
        time.sleep(2)

        # Stop execution
        orchestrator.stop_execution()

        # Both tasks should be completed
        assert "task1" in orchestrator.completed_tasks
        assert "task2" in orchestrator.completed_tasks

    def test_task_with_resources(self, orchestrator):
        """Test task execution with resource requirements."""
        # Create task with resource requirements
        task = Task(
            name="resource_task",
            module="module",
            action="action",
            resources=[
                TaskResource(
                    type=ResourceType.CPU, identifier="cpu_1", mode="exclusive"
                )
            ],
        )

        orchestrator.add_task(task)

        # Start execution
        orchestrator.start_execution()

        # Wait for task to complete
        time.sleep(1)

        # Stop execution
        orchestrator.stop_execution()

        # Task should be completed
        assert (
            task.id in orchestrator.completed_tasks
            or task.id in orchestrator.task_results
        )

    def test_task_retry_logic(self, orchestrator):
        """Test task retry logic for failed tasks."""
        # Create task that will fail
        task = Task(
            name="failing_task", module="module", action="action", max_retries=2
        )

        orchestrator.add_task(task)

        # Start execution
        orchestrator.start_execution()

        # Wait for retries
        time.sleep(3)

        # Stop execution
        orchestrator.stop_execution()

        # Task should have been retried
        assert task.retry_count > 0 or task.id in orchestrator.completed_tasks


class TestTaskOrchestratorIntegration:
    """Integration tests for TaskOrchestrator."""

    def test_complex_workflow_execution(self):
        """Test execution of complex workflow with multiple tasks and dependencies."""
        orchestrator = TaskOrchestrator(max_workers=3)

        # Create complex workflow
        tasks = [
            Task(name="setup", module="module", action="action"),
            Task(
                name="analyze", module="module", action="action", dependencies=["setup"]
            ),
            Task(
                name="process",
                module="module",
                action="action",
                dependencies=["analyze"],
            ),
            Task(
                name="validate",
                module="module",
                action="action",
                dependencies=["process"],
            ),
            Task(
                name="report",
                module="module",
                action="action",
                dependencies=["validate"],
            ),
        ]

        # Add all tasks
        for task in tasks:
            orchestrator.add_task(task)

        # Start execution
        orchestrator.start_execution()

        # Wait for all tasks to complete
        time.sleep(5)

        # Stop execution
        orchestrator.stop_execution()

        # All tasks should be completed
        for task in tasks:
            assert (
                task.id in orchestrator.completed_tasks
                or task.id in orchestrator.task_results
            )

    def test_concurrent_task_execution(self):
        """Test concurrent execution of independent tasks."""
        orchestrator = TaskOrchestrator(max_workers=4)

        # Create independent tasks
        tasks = [
            Task(name=f"task_{i}", module="module", action="action") for i in range(5)
        ]

        # Add all tasks
        for task in tasks:
            orchestrator.add_task(task)

        # Start execution
        orchestrator.start_execution()

        # Wait for tasks to complete
        time.sleep(3)

        # Stop execution
        orchestrator.stop_execution()

        # Most tasks should be completed
        completed_count = len(orchestrator.completed_tasks)
        assert completed_count >= 3  # At least 3 should complete with 4 workers


if __name__ == "__main__":
    pytest.main([__file__])
