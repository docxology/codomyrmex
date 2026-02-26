"""
Tests for collaboration agents submodule.
"""


import pytest

from codomyrmex.collaboration.agents import (
    AgentRegistry,
    CollaborativeAgent,
    SpecializedWorker,
    SupervisorAgent,
    WorkerAgent,
    get_registry,
)
from codomyrmex.collaboration.exceptions import (
    AgentNotFoundError,
)
from codomyrmex.collaboration.models import Task
from codomyrmex.collaboration.protocols import AgentCapability, AgentState


class TestCollaborativeAgent:
    """Tests for CollaborativeAgent."""

    def test_agent_creation(self):
        """Test creating a collaborative agent."""
        agent = CollaborativeAgent(
            agent_id="agent-123",
            name="Test Agent",
        )

        assert agent.agent_id == "agent-123"
        assert agent.name == "Test Agent"
        assert agent.state == AgentState.IDLE

    def test_agent_auto_id(self):
        """Test agent with auto-generated ID."""
        agent = CollaborativeAgent(name="Auto ID Agent")

        assert isinstance(agent.agent_id, str)
        assert len(agent.agent_id) > 0

    def test_agent_capabilities(self):
        """Test agent capability management."""
        agent = CollaborativeAgent(
            name="Capable Agent",
            capabilities=[
                AgentCapability(name="coding", description="Write code"),
                AgentCapability(name="testing", description="Run tests"),
            ],
        )

        assert agent.has_capability("coding") is True
        assert agent.has_capability("testing") is True
        assert agent.has_capability("unknown") is False
        assert set(agent.get_capabilities()) == {"coding", "testing"}

    def test_agent_add_capability(self):
        """Test adding capability to agent."""
        agent = CollaborativeAgent(name="Learning Agent")

        assert agent.has_capability("new_skill") is False

        agent.add_capability(AgentCapability(name="new_skill", description="A new skill"))

        assert agent.has_capability("new_skill") is True

    def test_agent_get_status(self):
        """Test getting agent status."""
        agent = CollaborativeAgent(
            agent_id="status-agent",
            name="Status Agent",
            capabilities=[AgentCapability(name="coding", description="")],
        )

        status = agent.get_status()

        assert status.agent_id == "status-agent"
        assert status.name == "Status Agent"
        assert status.status == "idle"
        assert "coding" in status.capabilities


class TestWorkerAgent:
    """Tests for WorkerAgent."""

    def test_worker_creation(self):
        """Test creating a worker agent."""
        worker = WorkerAgent(
            agent_id="worker-1",
            name="Test Worker",
        )

        assert worker.agent_id == "worker-1"
        assert worker.name == "Test Worker"

    def test_worker_register_handler(self):
        """Test registering a task handler."""
        worker = WorkerAgent(name="Handler Worker")

        def my_handler(task: Task):
            return f"Processed: {task.name}"

        worker.register_handler("coding", my_handler, "Coding tasks")

        assert worker.has_capability("coding") is True

    def test_worker_can_handle_task(self):
        """Test checking if worker can handle a task."""
        worker = WorkerAgent(
            name="Capable Worker",
            capabilities=[AgentCapability(name="coding", description="")],
        )

        task_with_cap = Task(name="Code Task", required_capabilities=["coding"])
        task_without_cap = Task(name="Design Task", required_capabilities=["design"])
        task_no_cap = Task(name="Simple Task")

        assert worker.can_handle_task(task_with_cap) is True
        assert worker.can_handle_task(task_without_cap) is False
        assert worker.can_handle_task(task_no_cap) is True

    @pytest.mark.asyncio
    async def test_worker_execute_task(self):
        """Test executing a task."""
        worker = WorkerAgent(name="Execute Worker")

        async def async_handler(task: Task):
            return {"result": f"Completed: {task.name}"}

        worker.register_handler("coding", async_handler, "Coding tasks")

        task = Task(name="Test Task", required_capabilities=["coding"])
        result = await worker.process_task(task)

        assert result.success is True
        assert result.output == {"result": "Completed: Test Task"}
        assert result.agent_id == worker.agent_id


class TestSpecializedWorker:
    """Tests for SpecializedWorker."""

    def test_specialized_worker_creation(self):
        """Test creating a specialized worker."""
        def handler(task):
            return "done"

        worker = SpecializedWorker(
            capability_name="analysis",
            handler=handler,
            name="Analysis Worker",
            description="Performs analysis",
        )

        assert worker.name == "Analysis Worker"
        assert worker.has_capability("analysis") is True


class TestSupervisorAgent:
    """Tests for SupervisorAgent."""

    def test_supervisor_creation(self):
        """Test creating a supervisor agent."""
        supervisor = SupervisorAgent(
            agent_id="supervisor-1",
            name="Test Supervisor",
        )

        assert supervisor.agent_id == "supervisor-1"
        assert supervisor.name == "Test Supervisor"
        assert supervisor.has_capability("supervision") is True

    def test_supervisor_add_worker(self):
        """Test adding workers to supervisor."""
        supervisor = SupervisorAgent(name="Boss")
        worker1 = WorkerAgent(name="Worker 1")
        worker2 = WorkerAgent(name="Worker 2")

        supervisor.add_worker(worker1)
        supervisor.add_worker(worker2)

        workers = supervisor.get_workers()
        assert len(workers) == 2

    def test_supervisor_remove_worker(self):
        """Test removing workers from supervisor."""
        supervisor = SupervisorAgent(name="Boss")
        worker = WorkerAgent(name="Worker")

        supervisor.add_worker(worker)
        assert len(supervisor.get_workers()) == 1

        supervisor.remove_worker(worker.agent_id)
        assert len(supervisor.get_workers()) == 0

    def test_supervisor_find_capable_workers(self):
        """Test finding workers with capabilities."""
        supervisor = SupervisorAgent(name="Boss")

        worker1 = WorkerAgent(
            name="Coder",
            capabilities=[AgentCapability(name="coding", description="")],
        )
        worker2 = WorkerAgent(
            name="Tester",
            capabilities=[AgentCapability(name="testing", description="")],
        )

        supervisor.add_worker(worker1)
        supervisor.add_worker(worker2)

        task = Task(name="Code Task", required_capabilities=["coding"])
        capable = supervisor.find_capable_workers(task)

        assert len(capable) == 1
        assert capable[0].name == "Coder"


class TestAgentRegistry:
    """Tests for AgentRegistry."""

    def setup_method(self):
        """Reset registry before each test."""
        AgentRegistry.reset()

    def test_registry_singleton(self):
        """Test registry is a singleton."""
        registry1 = AgentRegistry.get_instance()
        registry2 = AgentRegistry.get_instance()

        assert registry1 is registry2

    def test_registry_register(self):
        """Test registering an agent."""
        registry = AgentRegistry.get_instance()
        agent = CollaborativeAgent(name="Test Agent")

        agent_id = registry.register(agent)

        assert agent_id == agent.agent_id
        assert registry.get(agent_id) is agent

    def test_registry_unregister(self):
        """Test unregistering an agent."""
        registry = AgentRegistry.get_instance()
        agent = CollaborativeAgent(name="Test Agent")

        registry.register(agent)
        result = registry.unregister(agent.agent_id)

        assert result is True
        with pytest.raises(AgentNotFoundError):
            registry.get(agent.agent_id)

    def test_registry_find_by_capability(self):
        """Test finding agents by capability."""
        registry = AgentRegistry.get_instance()

        agent1 = CollaborativeAgent(
            name="Agent 1",
            capabilities=[AgentCapability(name="coding", description="")],
        )
        agent2 = CollaborativeAgent(
            name="Agent 2",
            capabilities=[AgentCapability(name="testing", description="")],
        )

        registry.register(agent1)
        registry.register(agent2)

        coders = registry.find_by_capability("coding")
        assert len(coders) == 1
        assert coders[0].name == "Agent 1"

    def test_registry_get_swarm_status(self):
        """Test getting swarm status."""
        registry = AgentRegistry.get_instance()

        agent1 = CollaborativeAgent(name="Agent 1")
        agent2 = CollaborativeAgent(name="Agent 2")

        registry.register(agent1)
        registry.register(agent2)

        status = registry.get_swarm_status()

        assert status.total_agents == 2
        assert status.idle_agents == 2

    def test_get_registry_function(self):
        """Test get_registry convenience function."""
        registry = get_registry()

        assert isinstance(registry, AgentRegistry)
