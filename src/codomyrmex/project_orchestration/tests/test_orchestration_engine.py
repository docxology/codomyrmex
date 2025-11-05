"""
Comprehensive unit tests for OrchestrationEngine.

This module contains extensive unit tests for the OrchestrationEngine class,
covering all public methods, error conditions, and edge cases.
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from codomyrmex.logging_monitoring.logger_config import get_logger
from codomyrmex.project_orchestration.orchestration_engine import (
    OrchestrationEngine,
    OrchestrationSession,
    SessionStatus,
)

logger = get_logger(__name__)
from codomyrmex.project_orchestration.project_manager import (
    Project,
)
from codomyrmex.project_orchestration.resource_manager import (
    Resource,
    ResourceType,
)
from codomyrmex.project_orchestration.task_orchestrator import (
    Task,
)
from codomyrmex.project_orchestration.workflow_manager import (
    WorkflowStep,
)


class TestOrchestrationSession:
    """Test cases for OrchestrationSession dataclass."""

    def test_session_creation(self):
        """Test basic OrchestrationSession creation."""
        session = OrchestrationSession(
            session_id="test_session",
            name="Test Session",
            description="A test orchestration session",
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
        )

        assert session.session_id == "test_session"
        assert session.name == "Test Session"
        assert session.description == "A test orchestration session"
        assert session.status == SessionStatus.ACTIVE
        assert session.created_at is not None

    def test_session_defaults(self):
        """Test OrchestrationSession with default values."""
        session = OrchestrationSession(session_id="test_session")

        assert session.session_id == "test_session"
        assert session.name == ""
        assert session.description == ""
        assert session.status == SessionStatus.PENDING
        assert session.created_at is not None

    def test_session_serialization(self):
        """Test OrchestrationSession serialization to/from dictionary."""
        session = OrchestrationSession(
            session_id="test_session",
            name="Test Session",
            description="Test description",
            status=SessionStatus.ACTIVE,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            metadata={"key": "value"},
        )

        # Test to_dict
        session_dict = session.to_dict()
        assert session_dict["session_id"] == "test_session"
        assert session_dict["name"] == "Test Session"
        assert session_dict["description"] == "Test description"
        assert session_dict["status"] == SessionStatus.ACTIVE.value
        assert session_dict["metadata"] == {"key": "value"}

        # Test from_dict
        restored_session = OrchestrationSession.from_dict(session_dict)
        assert restored_session.session_id == "test_session"
        assert restored_session.name == "Test Session"
        assert restored_session.description == "Test description"
        assert restored_session.status == SessionStatus.ACTIVE
        assert restored_session.metadata == {"key": "value"}


class TestOrchestrationEngine:
    """Test cases for OrchestrationEngine class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def orchestration_engine(self, temp_dir):
        """Create an OrchestrationEngine instance for testing."""
        return OrchestrationEngine(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

    def test_orchestration_engine_initialization(self, temp_dir):
        """Test OrchestrationEngine initialization."""
        engine = OrchestrationEngine(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

        assert engine.config_dir == temp_dir
        assert engine.sessions == {}
        assert engine.workflow_manager is not None
        assert engine.task_orchestrator is not None
        assert engine.project_manager is not None
        assert engine.resource_manager is not None
        assert engine.logger is not None
        assert engine.enable_performance_monitoring is False

    def test_orchestration_engine_default_initialization(self):
        """Test OrchestrationEngine with default initialization."""
        engine = OrchestrationEngine()

        assert engine.config_dir is not None
        assert engine.sessions == {}
        assert engine.workflow_manager is not None
        assert engine.task_orchestrator is not None
        assert engine.project_manager is not None
        assert engine.resource_manager is not None

    def test_create_session_success(self, orchestration_engine):
        """Test successful session creation."""
        session = orchestration_engine.create_session(
            name="Test Session", description="A test session"
        )

        assert session is not None
        assert session.name == "Test Session"
        assert session.description == "A test session"
        assert session.status == SessionStatus.ACTIVE
        assert session.session_id in orchestration_engine.sessions

    def test_create_session_with_metadata(self, orchestration_engine):
        """Test session creation with metadata."""
        metadata = {"project": "test_project", "environment": "development"}

        session = orchestration_engine.create_session(
            name="Test Session", description="A test session", metadata=metadata
        )

        assert session is not None
        assert session.metadata == metadata

    def test_get_session_existing(self, orchestration_engine):
        """Test getting existing session."""
        session = orchestration_engine.create_session(name="Test Session")

        retrieved_session = orchestration_engine.get_session(session.session_id)

        assert retrieved_session is not None
        assert retrieved_session.session_id == session.session_id
        assert retrieved_session.name == "Test Session"

    def test_get_session_nonexistent(self, orchestration_engine):
        """Test getting non-existent session."""
        retrieved_session = orchestration_engine.get_session("nonexistent")

        assert retrieved_session is None

    def test_list_sessions(self, orchestration_engine):
        """Test listing sessions."""
        # Create multiple sessions
        session1 = orchestration_engine.create_session(name="Session 1")
        session2 = orchestration_engine.create_session(name="Session 2")

        sessions = orchestration_engine.list_sessions()

        assert len(sessions) == 2
        assert session1.session_id in sessions
        assert session2.session_id in sessions

    def test_list_sessions_by_status(self, orchestration_engine):
        """Test listing sessions by status."""
        # Create sessions with different statuses
        session1 = orchestration_engine.create_session(name="Active Session")
        session1.status = SessionStatus.ACTIVE

        session2 = orchestration_engine.create_session(name="Completed Session")
        session2.status = SessionStatus.COMPLETED

        # List all sessions
        all_sessions = orchestration_engine.list_sessions()
        assert len(all_sessions) == 2

        # List active sessions
        active_sessions = orchestration_engine.list_sessions(
            status=SessionStatus.ACTIVE
        )
        assert len(active_sessions) == 1
        assert active_sessions[0].name == "Active Session"

        # List completed sessions
        completed_sessions = orchestration_engine.list_sessions(
            status=SessionStatus.COMPLETED
        )
        assert len(completed_sessions) == 1
        assert completed_sessions[0].name == "Completed Session"

    def test_update_session(self, orchestration_engine):
        """Test updating session."""
        session = orchestration_engine.create_session(name="Test Session")

        # Update session
        updated_session = orchestration_engine.update_session(
            session.session_id,
            name="Updated Session",
            description="Updated description",
            status=SessionStatus.COMPLETED,
            metadata={"key": "value"},
        )

        assert updated_session is not None
        assert updated_session.name == "Updated Session"
        assert updated_session.description == "Updated description"
        assert updated_session.status == SessionStatus.COMPLETED
        assert updated_session.metadata == {"key": "value"}

    def test_update_session_nonexistent(self, orchestration_engine):
        """Test updating non-existent session."""
        updated_session = orchestration_engine.update_session("nonexistent")

        assert updated_session is None

    def test_delete_session(self, orchestration_engine):
        """Test deleting session."""
        session = orchestration_engine.create_session(name="Test Session")

        result = orchestration_engine.delete_session(session.session_id)

        assert result is True
        assert session.session_id not in orchestration_engine.sessions

    def test_delete_session_nonexistent(self, orchestration_engine):
        """Test deleting non-existent session."""
        result = orchestration_engine.delete_session("nonexistent")

        assert result is False

    def test_get_system_status(self, orchestration_engine):
        """Test getting system status."""
        # Create some test data
        orchestration_engine.create_session(name="Test Session")

        # Add some workflows
        steps = [WorkflowStep(name="step1", module="module1", action="action1")]
        orchestration_engine.workflow_manager.create_workflow("test_workflow", steps)

        # Add some tasks
        task = Task(name="test_task", module="module", action="action")
        orchestration_engine.task_orchestrator.add_task(task)

        # Add some projects
        project = Project(name="test_project")
        orchestration_engine.project_manager.projects["test_project"] = project

        # Add some resources
        resource = Resource(
            id="cpu_1", name="CPU 1", resource_type=ResourceType.CPU, capacity=100.0
        )
        orchestration_engine.resource_manager.add_resource(resource)

        # Get system status
        status = orchestration_engine.get_system_status()

        assert "active_sessions" in status
        assert "total_workflows" in status
        assert "running_workflows" in status
        assert "total_tasks" in status
        assert "completed_tasks" in status
        assert "failed_tasks" in status
        assert "total_projects" in status
        assert "total_resources" in status
        assert "active_allocations" in status

        assert status["active_sessions"] == 1
        assert status["total_workflows"] == 1
        assert status["total_tasks"] == 1
        assert status["total_projects"] == 1
        assert status["total_resources"] == 1

    def test_get_health_status(self, orchestration_engine):
        """Test getting health status."""
        health = orchestration_engine.get_health_status()

        assert "overall_status" in health
        assert "workflow_manager" in health
        assert "task_orchestrator" in health
        assert "project_manager" in health
        assert "resource_manager" in health

        assert health["overall_status"] == "healthy"
        assert health["workflow_manager"] == "healthy"
        assert health["task_orchestrator"] == "healthy"
        assert health["project_manager"] == "healthy"
        assert health["resource_manager"] == "healthy"

    def test_execute_workflow_in_session(self, orchestration_engine):
        """Test executing workflow in session."""
        # Create session
        session = orchestration_engine.create_session(name="Test Session")

        # Create workflow
        steps = [WorkflowStep(name="step1", module="module1", action="action1")]
        orchestration_engine.workflow_manager.create_workflow("test_workflow", steps)

        # Execute workflow in session
        result = orchestration_engine.execute_workflow_in_session(
            session.session_id, "test_workflow"
        )

        assert result is True

    def test_execute_workflow_in_session_invalid_session(self, orchestration_engine):
        """Test executing workflow in invalid session."""
        result = orchestration_engine.execute_workflow_in_session(
            "nonexistent", "test_workflow"
        )

        assert result is False

    def test_execute_workflow_in_session_invalid_workflow(self, orchestration_engine):
        """Test executing invalid workflow in session."""
        session = orchestration_engine.create_session(name="Test Session")

        result = orchestration_engine.execute_workflow_in_session(
            session.session_id, "nonexistent_workflow"
        )

        assert result is False

    def test_add_task_to_session(self, orchestration_engine):
        """Test adding task to session."""
        session = orchestration_engine.create_session(name="Test Session")

        task = Task(name="test_task", module="module", action="action")

        result = orchestration_engine.add_task_to_session(session.session_id, task)

        assert result is True
        assert task.id in orchestration_engine.task_orchestrator.task_queue.tasks

    def test_add_task_to_session_invalid_session(self, orchestration_engine):
        """Test adding task to invalid session."""
        task = Task(name="test_task", module="module", action="action")

        result = orchestration_engine.add_task_to_session("nonexistent", task)

        assert result is False

    def test_create_project_in_session(self, orchestration_engine):
        """Test creating project in session."""
        session = orchestration_engine.create_session(name="Test Session")

        project = orchestration_engine.create_project_in_session(
            session.session_id, "test_project", "Test project description"
        )

        assert project is not None
        assert project.name == "test_project"
        assert project.description == "Test project description"
        assert "test_project" in orchestration_engine.project_manager.projects

    def test_create_project_in_session_invalid_session(self, orchestration_engine):
        """Test creating project in invalid session."""
        project = orchestration_engine.create_project_in_session(
            "nonexistent", "test_project", "Test project description"
        )

        assert project is None

    def test_allocate_resources_for_session(self, orchestration_engine):
        """Test allocating resources for session."""
        session = orchestration_engine.create_session(name="Test Session")

        # Add resource first
        resource = Resource(
            id="cpu_1", name="CPU 1", resource_type=ResourceType.CPU, capacity=100.0
        )
        orchestration_engine.resource_manager.add_resource(resource)

        # Allocate resources
        result = orchestration_engine.allocate_resources_for_session(
            session.session_id, "cpu_1", 50.0
        )

        assert result is True

    def test_allocate_resources_for_session_invalid_session(self, orchestration_engine):
        """Test allocating resources for invalid session."""
        result = orchestration_engine.allocate_resources_for_session(
            "nonexistent", "cpu_1", 50.0
        )

        assert result is False

    def test_release_resources_for_session(self, orchestration_engine):
        """Test releasing resources for session."""
        session = orchestration_engine.create_session(name="Test Session")

        # Add and allocate resource first
        resource = Resource(
            id="cpu_1", name="CPU 1", resource_type=ResourceType.CPU, capacity=100.0
        )
        orchestration_engine.resource_manager.add_resource(resource)
        orchestration_engine.allocate_resources_for_session(
            session.session_id, "cpu_1", 50.0
        )

        # Release resources
        result = orchestration_engine.release_resources_for_session(
            session.session_id, "cpu_1"
        )

        assert result is True

    def test_release_resources_for_session_invalid_session(self, orchestration_engine):
        """Test releasing resources for invalid session."""
        result = orchestration_engine.release_resources_for_session(
            "nonexistent", "cpu_1"
        )

        assert result is False

    def test_get_session_resources(self, orchestration_engine):
        """Test getting session resources."""
        session = orchestration_engine.create_session(name="Test Session")

        # Add and allocate resource
        resource = Resource(
            id="cpu_1", name="CPU 1", resource_type=ResourceType.CPU, capacity=100.0
        )
        orchestration_engine.resource_manager.add_resource(resource)
        orchestration_engine.allocate_resources_for_session(
            session.session_id, "cpu_1", 50.0
        )

        # Get session resources
        resources = orchestration_engine.get_session_resources(session.session_id)

        assert "cpu_1" in resources
        assert resources["cpu_1"]["allocated_amount"] == 50.0

    def test_get_session_resources_invalid_session(self, orchestration_engine):
        """Test getting resources for invalid session."""
        resources = orchestration_engine.get_session_resources("nonexistent")

        assert resources == {}

    def test_cleanup_session(self, orchestration_engine):
        """Test cleaning up session."""
        session = orchestration_engine.create_session(name="Test Session")

        # Add some data to session
        task = Task(name="test_task", module="module", action="action")
        orchestration_engine.add_task_to_session(session.session_id, task)

        # Allocate some resources
        resource = Resource(
            id="cpu_1", name="CPU 1", resource_type=ResourceType.CPU, capacity=100.0
        )
        orchestration_engine.resource_manager.add_resource(resource)
        orchestration_engine.allocate_resources_for_session(
            session.session_id, "cpu_1", 50.0
        )

        # Cleanup session
        result = orchestration_engine.cleanup_session(session.session_id)

        assert result is True
        assert session.session_id not in orchestration_engine.sessions

    def test_cleanup_session_invalid_session(self, orchestration_engine):
        """Test cleaning up invalid session."""
        result = orchestration_engine.cleanup_session("nonexistent")

        assert result is False

    def test_shutdown(self, orchestration_engine):
        """Test orchestration engine shutdown."""
        # Create some sessions
        orchestration_engine.create_session(name="Session 1")
        orchestration_engine.create_session(name="Session 2")

        # Shutdown engine
        orchestration_engine.shutdown()

        # Verify shutdown
        assert orchestration_engine.shutdown_requested is True


class TestOrchestrationEngineIntegration:
    """Integration tests for OrchestrationEngine."""

    def test_complete_workflow_session(self, temp_dir):
        """Test complete workflow session lifecycle."""
        engine = OrchestrationEngine(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

        # Create session
        session = engine.create_session(
            name="Complete Workflow Session", description="Test complete workflow"
        )

        assert session is not None
        assert session.session_id in engine.sessions

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

        engine.workflow_manager.create_workflow("complete_workflow", steps)

        # Execute workflow in session
        result = engine.execute_workflow_in_session(
            session.session_id, "complete_workflow"
        )
        assert result is True

        # Add tasks to session
        task1 = Task(name="task1", module="module1", action="action1")
        task2 = Task(
            name="task2", module="module2", action="action2", dependencies=["task1"]
        )

        engine.add_task_to_session(session.session_id, task1)
        engine.add_task_to_session(session.session_id, task2)

        # Create project in session
        project = engine.create_project_in_session(
            session.session_id, "test_project", "Test project for session"
        )

        assert project is not None

        # Allocate resources for session
        resource = Resource(
            id="cpu_1", name="CPU 1", resource_type=ResourceType.CPU, capacity=100.0
        )
        engine.resource_manager.add_resource(resource)

        engine.allocate_resources_for_session(session.session_id, "cpu_1", 50.0)

        # Get session resources
        resources = engine.get_session_resources(session.session_id)
        assert "cpu_1" in resources

        # Update session
        updated_session = engine.update_session(
            session.session_id, name="Updated Session", status=SessionStatus.COMPLETED
        )

        assert updated_session is not None
        assert updated_session.name == "Updated Session"
        assert updated_session.status == SessionStatus.COMPLETED

        # Get system status
        status = engine.get_system_status()
        assert status["active_sessions"] == 1

        # Cleanup session
        cleanup_result = engine.cleanup_session(session.session_id)
        assert cleanup_result is True
        assert session.session_id not in engine.sessions

        # Shutdown engine
        engine.shutdown()
        assert engine.shutdown_requested is True

    def test_multiple_sessions_isolation(self, temp_dir):
        """Test isolation between multiple sessions."""
        engine = OrchestrationEngine(
            config_dir=temp_dir, enable_performance_monitoring=False
        )

        # Create multiple sessions
        session1 = engine.create_session(name="Session 1")
        session2 = engine.create_session(name="Session 2")

        # Add different tasks to each session
        task1 = Task(name="session1_task", module="module1", action="action1")
        task2 = Task(name="session2_task", module="module2", action="action2")

        engine.add_task_to_session(session1.session_id, task1)
        engine.add_task_to_session(session2.session_id, task2)

        # Create different projects in each session
        engine.create_project_in_session(
            session1.session_id, "project1", "Project 1"
        )

        engine.create_project_in_session(
            session2.session_id, "project2", "Project 2"
        )

        # Allocate different resources for each session
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

        engine.allocate_resources_for_session(session1.session_id, "cpu_1", 50.0)
        engine.allocate_resources_for_session(session2.session_id, "mem_1", 256.0)

        # Verify isolation
        session1_resources = engine.get_session_resources(session1.session_id)
        session2_resources = engine.get_session_resources(session2.session_id)

        assert "cpu_1" in session1_resources
        assert "mem_1" not in session1_resources
        assert "mem_1" in session2_resources
        assert "cpu_1" not in session2_resources

        # Cleanup one session
        engine.cleanup_session(session1.session_id)

        # Verify other session is unaffected
        assert session2.session_id in engine.sessions
        session2_resources_after = engine.get_session_resources(session2.session_id)
        assert "mem_1" in session2_resources_after

        # Shutdown
        engine.shutdown()


if __name__ == "__main__":
    pytest.main([__file__])
