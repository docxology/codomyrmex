"""
Tests for collaboration coordination submodule.
"""


import pytest

from codomyrmex.collaboration.agents import CollaborativeAgent
from codomyrmex.collaboration.coordination import (
    BullyElection,
    ConsensusBuilder,
    DependencyGraph,
    ElectionState,
    RandomElection,
    RingElection,
    RotatingLeadership,
    SchedulingStrategy,
    TaskManager,
    TaskQueue,
    VoteType,
    VotingMechanism,
)
from codomyrmex.collaboration.models import Task, TaskResult, TaskStatus


class TestTaskQueue:
    """Tests for TaskQueue."""

    def test_queue_creation(self):
        """Test creating a task queue."""
        queue = TaskQueue()

        assert len(queue) == 0
        assert bool(queue) is False

    def test_queue_push_pop(self):
        """Test pushing and popping tasks."""
        queue = TaskQueue()

        task1 = Task(name="Low Priority", priority=1)
        task2 = Task(name="High Priority", priority=10)

        queue.push(task1)
        queue.push(task2)

        assert len(queue) == 2

        # Higher priority should come first
        popped = queue.pop()
        assert popped.name == "High Priority"

        popped = queue.pop()
        assert popped.name == "Low Priority"

        assert queue.pop() is None

    def test_queue_peek(self):
        """Test peeking at the queue."""
        queue = TaskQueue()
        task = Task(name="Peek Task", priority=5)

        queue.push(task)
        peeked = queue.peek()

        assert peeked.name == "Peek Task"
        assert len(queue) == 1  # Still in queue

    def test_queue_remove(self):
        """Test removing a task by ID."""
        queue = TaskQueue()
        task = Task(name="Remove Me")

        queue.push(task)
        result = queue.remove(task.id)

        assert result is True
        assert queue.pop() is None

    def test_queue_get(self):
        """Test getting a task by ID."""
        queue = TaskQueue()
        task = Task(name="Get Me")

        queue.push(task)
        retrieved = queue.get(task.id)

        assert retrieved.name == "Get Me"


class TestDependencyGraph:
    """Tests for DependencyGraph."""

    def test_graph_creation(self):
        """Test creating a dependency graph."""
        graph = DependencyGraph()

        assert graph is not None

    def test_graph_add_task(self):
        """Test adding tasks to graph."""
        graph = DependencyGraph()

        task1 = Task(name="Task 1", id="t1")
        task2 = Task(name="Task 2", id="t2", dependencies=["t1"])

        graph.add_task(task1)
        graph.add_task(task2)

        deps = graph.get_dependencies("t2")
        assert "t1" in deps

    def test_graph_get_ready_tasks(self):
        """Test getting ready tasks."""
        graph = DependencyGraph()

        task1 = Task(name="Task 1", id="t1")
        task2 = Task(name="Task 2", id="t2", dependencies=["t1"])

        graph.add_task(task1)
        graph.add_task(task2)

        # Initially only t1 is ready
        ready = graph.get_ready_tasks(set())
        assert "t1" in ready
        assert "t2" not in ready

        # After t1 completes, t2 is ready
        ready = graph.get_ready_tasks({"t1"})
        assert "t2" in ready

    def test_graph_remove_task(self):
        """Test removing a task."""
        graph = DependencyGraph()
        task = Task(name="Remove", id="t1")

        graph.add_task(task)
        graph.remove_task("t1")

        assert graph.get_dependencies("t1") == set()


class TestTaskManager:
    """Tests for TaskManager."""

    def test_manager_creation(self):
        """Test creating a task manager."""
        manager = TaskManager(strategy=SchedulingStrategy.PRIORITY)

        assert manager.get_pending_count() == 0
        assert manager.get_running_count() == 0

    def test_manager_submit(self):
        """Test submitting a task."""
        manager = TaskManager()
        task = Task(name="Submit Task")

        task_id = manager.submit(task)

        assert task_id is not None
        assert manager.get_pending_count() == 1
        assert manager.get_task_status(task_id) == TaskStatus.QUEUED

    def test_manager_submit_batch(self):
        """Test submitting multiple tasks."""
        manager = TaskManager()
        tasks = [
            Task(name="Task 1"),
            Task(name="Task 2"),
            Task(name="Task 3"),
        ]

        ids = manager.submit_batch(tasks)

        assert len(ids) == 3
        assert manager.get_pending_count() == 3

    def test_manager_cancel(self):
        """Test cancelling a task."""
        manager = TaskManager()
        task = Task(name="Cancel Me")

        task_id = manager.submit(task)
        result = manager.cancel(task_id)

        assert result is True
        assert manager.get_pending_count() == 0

    def test_manager_get_next_task(self):
        """Test getting next task for an agent."""
        manager = TaskManager()
        task = Task(name="Next Task")
        agent = CollaborativeAgent(name="Worker")

        manager.submit(task)
        next_task = manager.get_next_task(agent)

        assert next_task is not None
        assert next_task.name == "Next Task"
        assert manager.get_running_count() == 1

    def test_manager_complete_task(self):
        """Test completing a task."""
        manager = TaskManager()
        task = Task(name="Complete Me")
        agent = CollaborativeAgent(name="Worker")

        manager.submit(task)
        assigned = manager.get_next_task(agent)

        result = TaskResult(
            task_id=assigned.id,
            success=True,
            output="Done",
            agent_id=agent.agent_id,
        )
        manager.complete_task(result)

        assert manager.get_completed_count() == 1
        assert manager.get_task_status(assigned.id) == TaskStatus.COMPLETED


class TestVotingMechanism:
    """Tests for VotingMechanism."""

    def test_voting_creation(self):
        """Test creating a voting mechanism."""
        voting = VotingMechanism(quorum=0.5, threshold=0.5)

        assert voting is not None

    def test_voting_create_proposal(self):
        """Test creating a proposal."""
        voting = VotingMechanism()

        proposal = voting.create_proposal(
            title="Test Proposal",
            description="A test",
            proposer_id="agent-1",
        )

        assert proposal.proposal_id is not None
        assert proposal.title == "Test Proposal"

    def test_voting_cast_vote(self):
        """Test casting a vote."""
        voting = VotingMechanism()
        proposal = voting.create_proposal(
            title="Vote Test",
            description="",
            proposer_id="agent-1",
        )

        vote = voting.cast_vote(
            proposal.proposal_id,
            "voter-1",
            VoteType.YES,
            reason="I agree",
        )

        assert vote.vote == VoteType.YES
        assert vote.reason == "I agree"

    def test_voting_tally_passed(self):
        """Test tallying votes - passed."""
        voting = VotingMechanism(quorum=0.5, threshold=0.5)

        proposal = voting.create_proposal("Pass Test", "", "agent-1")

        voting.cast_vote(proposal.proposal_id, "v1", VoteType.YES)
        voting.cast_vote(proposal.proposal_id, "v2", VoteType.YES)
        voting.cast_vote(proposal.proposal_id, "v3", VoteType.NO)

        result = voting.tally_votes(proposal.proposal_id, total_voters=4)

        assert result.passed is True
        assert result.votes_for == 2
        assert result.votes_against == 1
        assert result.quorum_met is True

    def test_voting_tally_failed(self):
        """Test tallying votes - failed."""
        voting = VotingMechanism(quorum=0.5, threshold=0.6)

        proposal = voting.create_proposal("Fail Test", "", "agent-1")

        voting.cast_vote(proposal.proposal_id, "v1", VoteType.YES)
        voting.cast_vote(proposal.proposal_id, "v2", VoteType.NO)
        voting.cast_vote(proposal.proposal_id, "v3", VoteType.NO)

        result = voting.tally_votes(proposal.proposal_id, total_voters=4)

        assert result.passed is False
        assert result.votes_against == 2


class TestConsensusBuilder:
    """Tests for ConsensusBuilder."""

    def test_consensus_creation(self):
        """Test creating a consensus builder."""
        builder = ConsensusBuilder(convergence_threshold=0.8)

        assert builder is not None

    def test_consensus_propose_value(self):
        """Test proposing values."""
        builder = ConsensusBuilder()

        builder.propose_value("config.timeout", "agent-1", 30)
        builder.propose_value("config.timeout", "agent-2", 30)
        builder.propose_value("config.timeout", "agent-3", 60)

        proposals = builder.get_proposals("config.timeout")
        assert len(proposals) == 3

    def test_consensus_check_reached(self):
        """Test checking consensus - reached."""
        builder = ConsensusBuilder(convergence_threshold=0.6)

        builder.propose_value("key", "a1", "value")
        builder.propose_value("key", "a2", "value")
        builder.propose_value("key", "a3", "value")
        builder.propose_value("key", "a4", "other")

        result = builder.check_consensus("key", total_agents=4)

        assert result == "value"

    def test_consensus_check_not_reached(self):
        """Test checking consensus - not reached."""
        builder = ConsensusBuilder(convergence_threshold=0.9)

        builder.propose_value("key", "a1", "value1")
        builder.propose_value("key", "a2", "value2")

        result = builder.check_consensus("key", total_agents=2)

        assert result is None

    def test_consensus_clear(self):
        """Test clearing proposals."""
        builder = ConsensusBuilder()
        builder.propose_value("key", "agent", "value")

        builder.clear("key")

        assert builder.get_proposals("key") == {}


class TestBullyElection:
    """Tests for BullyElection."""

    def test_bully_creation(self):
        """Test creating a bully election."""
        election = BullyElection()

        assert election.state == ElectionState.IDLE
        assert election.current_leader is None

    @pytest.mark.asyncio
    async def test_bully_elect(self):
        """Test running bully election."""
        election = BullyElection(
            priority_fn=lambda a: hash(a.agent_id)
        )

        agents = [
            CollaborativeAgent(agent_id="a1", name="Agent 1"),
            CollaborativeAgent(agent_id="a2", name="Agent 2"),
            CollaborativeAgent(agent_id="a3", name="Agent 3"),
        ]

        result = await election.elect(agents)

        assert result.success is True
        assert result.leader_id is not None
        assert result.leader_id in ["a1", "a2", "a3"]

    @pytest.mark.asyncio
    async def test_bully_elect_no_agents(self):
        """Test election with no agents."""
        election = BullyElection()

        result = await election.elect([])

        assert result.success is False
        assert result.leader_id is None


class TestRingElection:
    """Tests for RingElection."""

    @pytest.mark.asyncio
    async def test_ring_elect(self):
        """Test running ring election."""
        election = RingElection()

        agents = [
            CollaborativeAgent(agent_id="a1", name="Agent 1"),
            CollaborativeAgent(agent_id="a2", name="Agent 2"),
        ]

        result = await election.elect(agents)

        assert result.success is True
        assert result.leader_id is not None


class TestRandomElection:
    """Tests for RandomElection."""

    @pytest.mark.asyncio
    async def test_random_elect(self):
        """Test running random election."""
        election = RandomElection()

        agents = [
            CollaborativeAgent(agent_id="a1", name="Agent 1"),
            CollaborativeAgent(agent_id="a2", name="Agent 2"),
            CollaborativeAgent(agent_id="a3", name="Agent 3"),
        ]

        result = await election.elect(agents)

        assert result.success is True
        assert result.leader_id in ["a1", "a2", "a3"]


class TestRotatingLeadership:
    """Tests for RotatingLeadership."""

    def test_rotating_creation(self):
        """Test creating rotating leadership."""
        rotation = RotatingLeadership()

        assert rotation.get_current_leader() is None

    def test_rotating_add_agent(self):
        """Test adding agents to rotation."""
        rotation = RotatingLeadership()
        agent = CollaborativeAgent(name="Agent 1")

        rotation.add_agent(agent)

        assert rotation.get_current_leader() is agent

    def test_rotating_rotate(self):
        """Test rotating leadership."""
        agent1 = CollaborativeAgent(name="Agent 1")
        agent2 = CollaborativeAgent(name="Agent 2")
        rotation = RotatingLeadership([agent1, agent2])

        assert rotation.get_current_leader() is agent1

        rotation.rotate()
        assert rotation.get_current_leader() is agent2

        rotation.rotate()
        assert rotation.get_current_leader() is agent1

    def test_rotating_remove_agent(self):
        """Test removing agent from rotation."""
        agent1 = CollaborativeAgent(name="Agent 1")
        agent2 = CollaborativeAgent(name="Agent 2")
        rotation = RotatingLeadership([agent1, agent2])

        result = rotation.remove_agent(agent1.agent_id)

        assert result is True
        assert rotation.get_current_leader() is agent2

    def test_rotating_term_count(self):
        """Test term count tracking."""
        agent = CollaborativeAgent(name="Agent")
        rotation = RotatingLeadership([agent])

        assert rotation.get_term_count() == 0

        rotation.rotate()
        assert rotation.get_term_count() == 1
