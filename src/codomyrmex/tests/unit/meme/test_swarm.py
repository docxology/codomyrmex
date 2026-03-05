"""Tests for meme.swarm -- zero-mock, real instances only.

Covers SwarmAgent, SwarmState, EmergentPattern, ConsensusState, SwarmEngine,
reach_consensus, and quorum_sensing with real numpy arrays and computation.
"""

from __future__ import annotations

import numpy as np
import pytest

from codomyrmex.meme.swarm.consensus import quorum_sensing, reach_consensus
from codomyrmex.meme.swarm.engine import SwarmEngine
from codomyrmex.meme.swarm.models import (
    ConsensusState,
    EmergentPattern,
    FlockingParams,
    SwarmAgent,
    SwarmState,
)

# ---------------------------------------------------------------------------
# SwarmAgent dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSwarmAgent:
    """Tests for the SwarmAgent dataclass."""

    def test_default_position_is_zeros(self) -> None:
        """Default position is a 3-element zero array."""
        agent = SwarmAgent()
        assert agent.position.shape == (3,)
        assert np.all(agent.position == 0.0)

    def test_default_velocity_is_zeros(self) -> None:
        """Default velocity is a 3-element zero array."""
        agent = SwarmAgent()
        assert agent.velocity.shape == (3,)
        assert np.all(agent.velocity == 0.0)

    def test_id_auto_generated(self) -> None:
        """ID is auto-generated as an 8-char string."""
        agent = SwarmAgent()
        assert isinstance(agent.id, str)
        assert len(agent.id) == 8

    def test_ids_are_unique(self) -> None:
        """Multiple agents receive unique IDs."""
        agents = [SwarmAgent() for _ in range(10)]
        ids = [a.id for a in agents]
        assert len(set(ids)) == 10

    def test_state_default_idle(self) -> None:
        """Default agent state is 'idle'."""
        agent = SwarmAgent()
        assert agent.state == "idle"

    def test_integrity_default_one(self) -> None:
        """Default integrity is 1.0 (full health)."""
        agent = SwarmAgent()
        assert agent.integrity == 1.0

    def test_list_position_converted_to_ndarray(self) -> None:
        """List position is converted to numpy array via __post_init__."""
        agent = SwarmAgent(position=[1.0, 2.0, 3.0])
        assert isinstance(agent.position, np.ndarray)
        assert agent.position[0] == 1.0

    def test_list_velocity_converted_to_ndarray(self) -> None:
        """List velocity is converted to numpy array via __post_init__."""
        agent = SwarmAgent(velocity=[0.5, 0.0, -0.5])
        assert isinstance(agent.velocity, np.ndarray)
        assert agent.velocity[2] == -0.5

    def test_explicit_state_stored(self) -> None:
        """Explicit state value is stored correctly."""
        agent = SwarmAgent(state="positive")
        assert agent.state == "positive"


# ---------------------------------------------------------------------------
# FlockingParams dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFlockingParams:
    """Tests for the FlockingParams configuration dataclass."""

    def test_defaults(self) -> None:
        """Default params have expected Reynolds values."""
        params = FlockingParams()
        assert params.separation_weight == pytest.approx(1.5)
        assert params.alignment_weight == pytest.approx(1.0)
        assert params.cohesion_weight == pytest.approx(1.0)
        assert params.max_speed == pytest.approx(5.0)
        assert params.max_force == pytest.approx(0.1)
        assert params.perception_radius == pytest.approx(10.0)

    def test_custom_values(self) -> None:
        """Custom values are stored correctly."""
        params = FlockingParams(separation_weight=2.0, max_speed=10.0)
        assert params.separation_weight == pytest.approx(2.0)
        assert params.max_speed == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# SwarmState dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSwarmState:
    """Tests for the SwarmState snapshot dataclass."""

    def test_empty_defaults(self) -> None:
        """Default SwarmState has empty agents list and zero coherence."""
        state = SwarmState()
        assert state.agents == []
        assert state.coherence == 0.0

    def test_centroid_default_zeros(self) -> None:
        """Default centroid is a 3-element zero array."""
        state = SwarmState()
        assert state.centroid.shape == (3,)
        assert np.all(state.centroid == 0.0)

    def test_agents_stored(self) -> None:
        """Agent list is stored correctly."""
        agents = [SwarmAgent(), SwarmAgent()]
        state = SwarmState(agents=agents)
        assert len(state.agents) == 2

    def test_coherence_stored(self) -> None:
        """Coherence value is stored correctly."""
        state = SwarmState(coherence=0.75)
        assert state.coherence == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# EmergentPattern dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestEmergentPattern:
    """Tests for the EmergentPattern dataclass."""

    def test_creation_stores_type(self) -> None:
        """pattern_type is stored correctly."""
        pattern = EmergentPattern(pattern_type="vortex")
        assert pattern.pattern_type == "vortex"

    def test_strength_default_zero(self) -> None:
        """Default strength is 0.0."""
        pattern = EmergentPattern(pattern_type="cluster")
        assert pattern.strength == 0.0

    def test_duration_default_zero(self) -> None:
        """Default duration is 0.0."""
        pattern = EmergentPattern(pattern_type="line")
        assert pattern.duration == 0.0

    def test_involved_agents_default_empty(self) -> None:
        """Default involved_agents is empty list."""
        pattern = EmergentPattern(pattern_type="vortex")
        assert pattern.involved_agents == []

    def test_explicit_values_stored(self) -> None:
        """Explicit values are stored correctly."""
        pattern = EmergentPattern(
            pattern_type="cluster",
            strength=0.9,
            duration=5.0,
            involved_agents=["a1", "a2", "a3"],
        )
        assert pattern.strength == pytest.approx(0.9)
        assert pattern.duration == pytest.approx(5.0)
        assert len(pattern.involved_agents) == 3


# ---------------------------------------------------------------------------
# ConsensusState dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestConsensusState:
    """Tests for the ConsensusState dataclass."""

    def test_proposal_id_stored(self) -> None:
        """proposal_id is stored correctly."""
        cs = ConsensusState(proposal_id="prop_001")
        assert cs.proposal_id == "prop_001"

    def test_round_default_zero(self) -> None:
        """Default round is 0."""
        cs = ConsensusState(proposal_id="x")
        assert cs.round == 0

    def test_agreed_ratio_default_zero(self) -> None:
        """Default agreed_ratio is 0.0."""
        cs = ConsensusState(proposal_id="x")
        assert cs.agreed_ratio == 0.0

    def test_status_default_pending(self) -> None:
        """Default status is 'pending'."""
        cs = ConsensusState(proposal_id="x")
        assert cs.status == "pending"

    def test_explicit_values_stored(self) -> None:
        """Explicit values are stored correctly."""
        cs = ConsensusState(
            proposal_id="p1",
            round=3,
            agreed_ratio=0.75,
            status="reached",
        )
        assert cs.round == 3
        assert cs.agreed_ratio == pytest.approx(0.75)
        assert cs.status == "reached"


# ---------------------------------------------------------------------------
# reach_consensus
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestReachConsensus:
    """Tests for the reach_consensus function."""

    def test_all_positive_reaches_consensus(self) -> None:
        """All agents in 'positive' state reach consensus."""
        agents = [SwarmAgent(state="positive") for _ in range(5)]
        assert reach_consensus(agents, "proposal_A") is True

    def test_all_idle_does_not_reach_consensus(self) -> None:
        """No positive agents fails to reach consensus."""
        agents = [SwarmAgent(state="idle") for _ in range(5)]
        assert reach_consensus(agents, "proposal_B") is False

    def test_majority_positive_reaches_consensus_at_default_threshold(self) -> None:
        """More than 60% positive reaches consensus at default 0.6 threshold."""
        # 7 out of 10 = 70% > 60%
        agents = [SwarmAgent(state="positive") for _ in range(7)]
        agents += [SwarmAgent(state="idle") for _ in range(3)]
        assert reach_consensus(agents, "p") is True

    def test_exactly_threshold_reaches_consensus(self) -> None:
        """Exactly at threshold (60%) should reach consensus."""
        # 3 out of 5 = exactly 60%
        agents = [SwarmAgent(state="positive") for _ in range(3)]
        agents += [SwarmAgent(state="idle") for _ in range(2)]
        assert reach_consensus(agents, "p", threshold=0.6) is True

    def test_below_threshold_fails(self) -> None:
        """Below threshold fails to reach consensus."""
        # 2 out of 5 = 40% < 60%
        agents = [SwarmAgent(state="positive") for _ in range(2)]
        agents += [SwarmAgent(state="idle") for _ in range(3)]
        assert reach_consensus(agents, "p", threshold=0.6) is False

    def test_empty_agents_returns_false(self) -> None:
        """Empty agent list cannot reach consensus (ratio = 0.0)."""
        assert reach_consensus([], "p") is False

    def test_custom_threshold_respected(self) -> None:
        """Custom threshold of 1.0 requires all agents positive."""
        agents = [SwarmAgent(state="positive") for _ in range(4)]
        agents.append(SwarmAgent(state="idle"))
        # 4/5 = 80% but threshold = 1.0
        assert reach_consensus(agents, "p", threshold=1.0) is False


# ---------------------------------------------------------------------------
# quorum_sensing
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestQuorumSensing:
    """Tests for the quorum_sensing function."""

    def test_empty_agents_returns_zero(self) -> None:
        """Empty agent list returns 0.0 density."""
        assert quorum_sensing([], radius=5.0) == 0.0

    def test_single_agent_returns_zero(self) -> None:
        """Single agent has no neighbors, returns 0."""
        agents = [SwarmAgent(position=np.array([0.0, 0.0, 0.0]))]
        density = quorum_sensing(agents, radius=5.0)
        assert density == 0.0

    def test_clustered_agents_have_high_density(self) -> None:
        """Agents clustered within radius report high local density."""
        # 5 agents all at origin — within any radius of each other
        agents = [SwarmAgent(position=np.zeros(3)) for _ in range(5)]
        density = quorum_sensing(agents, radius=1.0)
        assert density > 0.0

    def test_distant_agents_have_low_density(self) -> None:
        """Agents far apart with small radius have zero density."""
        agents = [
            SwarmAgent(position=np.array([float(i * 100), 0.0, 0.0])) for i in range(5)
        ]
        density = quorum_sensing(agents, radius=1.0)
        assert density == 0.0

    def test_density_increases_with_radius(self) -> None:
        """Larger radius captures more neighbors, increasing density."""
        agents = [
            SwarmAgent(position=np.array([float(i * 5), 0.0, 0.0])) for i in range(5)
        ]
        small_density = quorum_sensing(agents, radius=1.0)
        large_density = quorum_sensing(agents, radius=20.0)
        assert large_density >= small_density


# ---------------------------------------------------------------------------
# SwarmEngine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSwarmEngine:
    """Tests for the SwarmEngine orchestrator."""

    def test_default_num_agents(self) -> None:
        """Default engine has 50 agents."""
        engine = SwarmEngine(num_agents=50)
        assert len(engine.agents) == 50

    def test_custom_num_agents(self) -> None:
        """Custom num_agents is respected."""
        engine = SwarmEngine(num_agents=10)
        assert len(engine.agents) == 10

    def test_step_returns_swarm_state(self) -> None:
        """step() returns a SwarmState instance."""
        engine = SwarmEngine(num_agents=5)
        state = engine.step()
        assert isinstance(state, SwarmState)

    def test_step_centroid_shape(self) -> None:
        """step() centroid is a 3-element array."""
        engine = SwarmEngine(num_agents=5)
        state = engine.step()
        assert state.centroid.shape == (3,)

    def test_step_coherence_in_unit_range(self) -> None:
        """Coherence after step is in [0, 1]."""
        engine = SwarmEngine(num_agents=5)
        state = engine.step()
        assert 0.0 <= state.coherence <= 1.0

    def test_step_agents_list_populated(self) -> None:
        """SwarmState.agents contains the engine's agents."""
        engine = SwarmEngine(num_agents=8)
        state = engine.step()
        assert len(state.agents) == 8

    def test_multiple_steps_do_not_crash(self) -> None:
        """Running multiple simulation steps does not raise errors."""
        engine = SwarmEngine(num_agents=10)
        for _ in range(5):
            state = engine.step()
        assert isinstance(state, SwarmState)
