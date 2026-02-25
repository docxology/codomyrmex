"""
Tests for collaboration module data models.
"""

from datetime import datetime

from codomyrmex.collaboration.models import (
    AgentStatus,
    SwarmStatus,
    Task,
    TaskPriority,
    TaskResult,
    TaskStatus,
)


class TestTask:
    """Tests for Task dataclass."""

    def test_task_creation_minimal(self):
        """Test creating a task with minimal arguments."""
        task = Task(name="Test Task")

        assert task.name == "Test Task"
        assert task.description == ""
        assert task.id is not None
        assert task.priority == 5
        assert task.status == TaskStatus.PENDING
        assert task.required_capabilities == []
        assert task.dependencies == []

    def test_task_creation_full(self):
        """Test creating a task with all arguments."""
        task = Task(
            name="Full Task",
            description="A complete task",
            id="task-123",
            required_capabilities=["coding", "testing"],
            priority=8,
            dependencies=["task-000"],
            metadata={"source": "test"},
        )

        assert task.name == "Full Task"
        assert task.description == "A complete task"
        assert task.id == "task-123"
        assert task.required_capabilities == ["coding", "testing"]
        assert task.priority == 8
        assert task.dependencies == ["task-000"]
        assert task.metadata == {"source": "test"}

    def test_task_to_dict(self):
        """Test task serialization."""
        task = Task(
            name="Serialize Test",
            id="task-456",
            priority=7,
        )

        data = task.to_dict()

        assert data["name"] == "Serialize Test"
        assert data["id"] == "task-456"
        assert data["priority"] == 7
        assert data["status"] == "pending"
        assert "created_at" in data

    def test_task_from_dict(self):
        """Test task deserialization."""
        data = {
            "name": "Deserialize Test",
            "id": "task-789",
            "description": "Test description",
            "priority": 3,
            "status": "running",
            "required_capabilities": ["analysis"],
            "dependencies": [],
            "metadata": {},
            "created_at": datetime.now().isoformat(),
        }

        task = Task.from_dict(data)

        assert task.name == "Deserialize Test"
        assert task.id == "task-789"
        assert task.priority == 3
        assert task.status == TaskStatus.RUNNING

    def test_task_is_ready_no_dependencies(self):
        """Test is_ready with no dependencies."""
        task = Task(name="No Deps")

        assert task.is_ready([]) is True
        assert task.is_ready(["other-task"]) is True

    def test_task_is_ready_with_dependencies(self):
        """Test is_ready with dependencies."""
        task = Task(
            name="With Deps",
            dependencies=["dep-1", "dep-2"],
        )

        assert task.is_ready([]) is False
        assert task.is_ready(["dep-1"]) is False
        assert task.is_ready(["dep-1", "dep-2"]) is True
        assert task.is_ready(["dep-1", "dep-2", "dep-3"]) is True


class TestTaskResult:
    """Tests for TaskResult dataclass."""

    def test_result_success(self):
        """Test creating a successful result."""
        result = TaskResult(
            task_id="task-123",
            success=True,
            output={"data": [1, 2, 3]},
            duration=1.5,
            agent_id="agent-1",
        )

        assert result.task_id == "task-123"
        assert result.success is True
        assert result.output == {"data": [1, 2, 3]}
        assert result.error is None
        assert result.duration == 1.5
        assert result.agent_id == "agent-1"

    def test_result_failure(self):
        """Test creating a failed result."""
        result = TaskResult(
            task_id="task-456",
            success=False,
            error="Task failed due to timeout",
            duration=30.0,
            agent_id="agent-2",
        )

        assert result.success is False
        assert result.error == "Task failed due to timeout"
        assert result.output is None

    def test_result_to_dict(self):
        """Test result serialization."""
        result = TaskResult(
            task_id="task-789",
            success=True,
            output="completed",
            duration=2.5,
            agent_id="agent-3",
        )

        data = result.to_dict()

        assert data["task_id"] == "task-789"
        assert data["success"] is True
        assert data["output"] == "completed"
        assert data["duration"] == 2.5
        assert "completed_at" in data

    def test_result_from_dict(self):
        """Test result deserialization."""
        data = {
            "task_id": "task-999",
            "success": False,
            "error": "Network error",
            "duration": 5.0,
            "agent_id": "agent-4",
            "completed_at": datetime.now().isoformat(),
        }

        result = TaskResult.from_dict(data)

        assert result.task_id == "task-999"
        assert result.success is False
        assert result.error == "Network error"


class TestSwarmStatus:
    """Tests for SwarmStatus dataclass."""

    def test_swarm_status_default(self):
        """Test default swarm status."""
        status = SwarmStatus()

        assert status.total_agents == 0
        assert status.active_agents == 0
        assert status.idle_agents == 0
        assert status.pending_tasks == 0
        assert status.running_tasks == 0
        assert status.completed_tasks == 0
        assert status.failed_tasks == 0

    def test_swarm_status_with_values(self):
        """Test swarm status with values."""
        status = SwarmStatus(
            total_agents=10,
            active_agents=3,
            idle_agents=7,
            pending_tasks=5,
            running_tasks=3,
            completed_tasks=20,
            failed_tasks=2,
            uptime_seconds=3600.0,
        )

        assert status.total_agents == 10
        assert status.active_agents == 3
        assert status.uptime_seconds == 3600.0

    def test_swarm_status_to_dict(self):
        """Test swarm status serialization."""
        status = SwarmStatus(total_agents=5, active_agents=2)

        data = status.to_dict()

        assert data["total_agents"] == 5
        assert data["active_agents"] == 2
        assert "uptime_seconds" in data


class TestAgentStatus:
    """Tests for AgentStatus dataclass."""

    def test_agent_status_creation(self):
        """Test creating agent status."""
        status = AgentStatus(
            agent_id="agent-123",
            name="Test Agent",
            status="busy",
            current_task_id="task-456",
            capabilities=["coding", "testing"],
        )

        assert status.agent_id == "agent-123"
        assert status.name == "Test Agent"
        assert status.status == "busy"
        assert status.current_task_id == "task-456"
        assert status.capabilities == ["coding", "testing"]

    def test_agent_status_to_dict(self):
        """Test agent status serialization."""
        status = AgentStatus(
            agent_id="agent-789",
            name="Serialize Agent",
            capabilities=["analysis"],
        )

        data = status.to_dict()

        assert data["agent_id"] == "agent-789"
        assert data["name"] == "Serialize Agent"
        assert data["capabilities"] == ["analysis"]
        assert "last_heartbeat" in data

    def test_agent_status_from_dict(self):
        """Test agent status deserialization."""
        data = {
            "agent_id": "agent-999",
            "name": "Deserialize Agent",
            "status": "idle",
            "capabilities": ["coding"],
            "tasks_completed": 10,
            "tasks_failed": 1,
            "last_heartbeat": datetime.now().isoformat(),
        }

        status = AgentStatus.from_dict(data)

        assert status.agent_id == "agent-999"
        assert status.name == "Deserialize Agent"
        assert status.tasks_completed == 10
        assert status.tasks_failed == 1


class TestTaskPriority:
    """Tests for TaskPriority enum."""

    def test_priority_values(self):
        """Test priority enum values."""
        assert TaskPriority.LOW.value == 1
        assert TaskPriority.NORMAL.value == 5
        assert TaskPriority.HIGH.value == 8
        assert TaskPriority.CRITICAL.value == 10


class TestTaskStatus:
    """Tests for TaskStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.QUEUED.value == "queued"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
