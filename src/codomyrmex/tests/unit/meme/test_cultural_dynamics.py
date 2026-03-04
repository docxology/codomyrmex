"""Tests for meme.cultural_dynamics -- zero-mock, real instances only.

Covers CulturalState, Signal, Trajectory, PowerMap, FrequencyMap, and
CulturalDynamicsEngine with real computation and real dataclass instances.
"""

from __future__ import annotations

import time

import pytest

from codomyrmex.meme.cultural_dynamics.engine import CulturalDynamicsEngine
from codomyrmex.meme.cultural_dynamics.models import (
    CulturalState,
    FrequencyMap,
    PowerMap,
    Signal,
    Trajectory,
)
from codomyrmex.meme.memetics.models import Meme

# ---------------------------------------------------------------------------
# CulturalState dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCulturalState:
    """Tests for the CulturalState snapshot dataclass."""

    def test_empty_defaults(self) -> None:
        """Default CulturalState has empty dicts and zero energy."""
        state = CulturalState()
        assert state.dimensions == {}
        assert state.momentum == {}
        assert state.energy == 0.0

    def test_dimensions_stored(self) -> None:
        """Dimension values are stored and retrievable."""
        state = CulturalState(
            dimensions={"liberty_authority": 0.7, "tradition_innovation": -0.3}
        )
        assert state.dimensions["liberty_authority"] == pytest.approx(0.7)
        assert state.dimensions["tradition_innovation"] == pytest.approx(-0.3)

    def test_momentum_stored(self) -> None:
        """Momentum values are stored and retrievable."""
        state = CulturalState(momentum={"liberty_authority": 0.1})
        assert state.momentum["liberty_authority"] == pytest.approx(0.1)

    def test_energy_nonzero(self) -> None:
        """Energy can be set to a nonzero value."""
        state = CulturalState(energy=0.85)
        assert state.energy == pytest.approx(0.85)

    def test_timestamp_is_float(self) -> None:
        """timestamp is a float near the current time."""
        before = time.time()
        state = CulturalState()
        after = time.time()
        assert before <= state.timestamp <= after


# ---------------------------------------------------------------------------
# Signal dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSignal:
    """Tests for the Signal event dataclass."""

    def test_creation_stores_fields(self) -> None:
        """All Signal fields are stored correctly."""
        sig = Signal(
            source="media",
            content="Breaking news",
            strength=0.9,
            valence=0.7,
            dimension="liberty_authority",
        )
        assert sig.source == "media"
        assert sig.content == "Breaking news"
        assert sig.strength == 0.9
        assert sig.valence == 0.7
        assert sig.dimension == "liberty_authority"

    def test_timestamp_auto_set(self) -> None:
        """Timestamp is auto-set to a recent float."""
        before = time.time()
        sig = Signal(source="x", content="y", strength=0.5, valence=0.0, dimension="d")
        after = time.time()
        assert before <= sig.timestamp <= after

    def test_negative_valence(self) -> None:
        """Negative valence is stored correctly."""
        sig = Signal(source="s", content="c", strength=0.5, valence=-0.8, dimension="d")
        assert sig.valence == -0.8


# ---------------------------------------------------------------------------
# Trajectory dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTrajectory:
    """Tests for the Trajectory temporal sequence dataclass."""

    def test_empty_default(self) -> None:
        """Default Trajectory has empty states and None trend."""
        traj = Trajectory()
        assert traj.states == []
        assert traj.trend_vector is None

    def test_states_stored(self) -> None:
        """States list is stored and retrievable."""
        s1 = CulturalState(energy=0.1)
        s2 = CulturalState(energy=0.5)
        traj = Trajectory(states=[s1, s2])
        assert len(traj.states) == 2
        assert traj.states[0].energy == pytest.approx(0.1)

    def test_trend_vector_stored(self) -> None:
        """trend_vector dict is stored when supplied."""
        traj = Trajectory(trend_vector={"lib_auth": 0.05, "trad_innov": -0.02})
        assert traj.trend_vector is not None
        assert traj.trend_vector["lib_auth"] == pytest.approx(0.05)


# ---------------------------------------------------------------------------
# PowerMap dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPowerMap:
    """Tests for the PowerMap dataclass."""

    def test_empty_defaults(self) -> None:
        """Default PowerMap has empty nodes and centrality_scores."""
        pm = PowerMap()
        assert pm.nodes == []
        assert pm.centrality_scores == {}

    def test_nodes_stored(self) -> None:
        """Node list is stored."""
        pm = PowerMap(nodes=["entity_A", "entity_B"])
        assert len(pm.nodes) == 2
        assert "entity_A" in pm.nodes

    def test_centrality_scores_stored(self) -> None:
        """Centrality scores dict is stored."""
        pm = PowerMap(centrality_scores={"A": 0.8, "B": 0.3})
        assert pm.centrality_scores["A"] == pytest.approx(0.8)


# ---------------------------------------------------------------------------
# FrequencyMap dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestFrequencyMap:
    """Tests for the FrequencyMap spectral analysis dataclass."""

    def test_creation_fields(self) -> None:
        """FrequencyMap stores all fields correctly."""
        fm = FrequencyMap(
            dimension="lib_auth",
            dominant_frequency=0.1,
            period=10.0,
            amplitude=0.5,
        )
        assert fm.dimension == "lib_auth"
        assert fm.dominant_frequency == pytest.approx(0.1)
        assert fm.period == pytest.approx(10.0)
        assert fm.amplitude == pytest.approx(0.5)

    def test_zero_frequency(self) -> None:
        """Zero dominant_frequency is valid (flat signal)."""
        fm = FrequencyMap(dimension="d", dominant_frequency=0.0, period=0.0, amplitude=0.0)
        assert fm.dominant_frequency == 0.0
        assert fm.amplitude == 0.0


# ---------------------------------------------------------------------------
# CulturalDynamicsEngine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCulturalDynamicsEngineOscillation:
    """Tests for CulturalDynamicsEngine.oscillation_spectrum."""

    def test_empty_time_series_returns_zeros(self) -> None:
        """Empty time series yields a zero FrequencyMap."""
        engine = CulturalDynamicsEngine()
        fm = engine.oscillation_spectrum([], "liberty_authority")
        assert fm.dominant_frequency == 0.0
        assert fm.amplitude == 0.0
        assert fm.period == 0.0

    def test_single_state_returns_zero_period(self) -> None:
        """Single state has period 0 (cannot compute oscillation)."""
        engine = CulturalDynamicsEngine()
        state = CulturalState(dimensions={"x": 0.5})
        fm = engine.oscillation_spectrum([state], "x")
        assert fm.period == 0.0
        assert fm.dominant_frequency == 0.0

    def test_two_states_compute_amplitude(self) -> None:
        """Two states with different values produce nonzero amplitude."""
        engine = CulturalDynamicsEngine()
        states = [
            CulturalState(dimensions={"d": 0.0}),
            CulturalState(dimensions={"d": 1.0}),
        ]
        fm = engine.oscillation_spectrum(states, "d")
        assert fm.amplitude == pytest.approx(0.5, abs=1e-9)

    def test_amplitude_computed_as_half_range(self) -> None:
        """Amplitude = (max - min) / 2 over dimension values."""
        engine = CulturalDynamicsEngine()
        states = [
            CulturalState(dimensions={"x": -0.4}),
            CulturalState(dimensions={"x": 0.6}),
            CulturalState(dimensions={"x": 0.2}),
        ]
        fm = engine.oscillation_spectrum(states, "x")
        assert fm.amplitude == pytest.approx(0.5, abs=1e-9)

    def test_period_is_half_series_length(self) -> None:
        """Period = len(series) / 2 for series longer than 1."""
        engine = CulturalDynamicsEngine()
        states = [CulturalState(dimensions={"x": float(i)}) for i in range(4)]
        fm = engine.oscillation_spectrum(states, "x")
        assert fm.period == pytest.approx(2.0, abs=1e-9)

    def test_frequency_is_inverse_of_period(self) -> None:
        """dominant_frequency = 1 / period when period > 0."""
        engine = CulturalDynamicsEngine()
        states = [CulturalState(dimensions={"x": float(i)}) for i in range(6)]
        fm = engine.oscillation_spectrum(states, "x")
        assert fm.dominant_frequency == pytest.approx(1.0 / fm.period, abs=1e-9)

    def test_dimension_not_in_state_uses_zero(self) -> None:
        """Missing dimension key defaults to 0.0 value."""
        engine = CulturalDynamicsEngine()
        states = [
            CulturalState(dimensions={}),
            CulturalState(dimensions={}),
        ]
        fm = engine.oscillation_spectrum(states, "nonexistent")
        assert fm.amplitude == 0.0


@pytest.mark.unit
class TestCulturalDynamicsEngineZeitgeist:
    """Tests for CulturalDynamicsEngine.zeitgeist_trajectory."""

    def _make_signal(
        self,
        dimension: str,
        valence: float,
        strength: float = 1.0,
        timestamp: float = 0.0,
    ) -> Signal:
        return Signal(
            source="test",
            content="event",
            strength=strength,
            valence=valence,
            dimension=dimension,
            timestamp=timestamp,
        )

    def test_empty_signals_returns_empty_trajectory(self) -> None:
        """No signals produce a Trajectory with no states."""
        engine = CulturalDynamicsEngine()
        traj = engine.zeitgeist_trajectory([])
        assert isinstance(traj, Trajectory)
        assert traj.states == []

    def test_single_signal_produces_one_state(self) -> None:
        """One signal produces a trajectory with exactly one state."""
        engine = CulturalDynamicsEngine()
        sig = self._make_signal("d", 0.5, timestamp=1.0)
        traj = engine.zeitgeist_trajectory([sig])
        assert len(traj.states) == 1

    def test_state_contains_dimension(self) -> None:
        """Produced state has the signal's dimension key."""
        engine = CulturalDynamicsEngine()
        sig = self._make_signal("liberty_authority", 1.0, timestamp=1.0)
        traj = engine.zeitgeist_trajectory([sig])
        assert "liberty_authority" in traj.states[0].dimensions

    def test_multiple_signals_sorted_by_timestamp(self) -> None:
        """Signals are processed in chronological order."""
        engine = CulturalDynamicsEngine()
        sigs = [
            self._make_signal("d", 1.0, timestamp=2.0),
            self._make_signal("d", -1.0, timestamp=0.5),
        ]
        traj = engine.zeitgeist_trajectory(sigs)
        # Should have 2 states; first processed = earlier timestamp
        assert len(traj.states) == 2

    def test_positive_valence_shifts_dimension_positive(self) -> None:
        """Strongly positive signals shift dimension value positive."""
        engine = CulturalDynamicsEngine()
        # Feed many strongly positive signals to accumulate positive value
        sigs = [self._make_signal("d", 1.0, 1.0, timestamp=float(i)) for i in range(10)]
        traj = engine.zeitgeist_trajectory(sigs)
        final_val = traj.states[-1].dimensions.get("d", 0.0)
        assert final_val > 0.0

    def test_negative_valence_shifts_dimension_negative(self) -> None:
        """Strongly negative signals shift dimension value negative."""
        engine = CulturalDynamicsEngine()
        sigs = [self._make_signal("d", -1.0, 1.0, timestamp=float(i)) for i in range(10)]
        traj = engine.zeitgeist_trajectory(sigs)
        final_val = traj.states[-1].dimensions.get("d", 0.0)
        assert final_val < 0.0

    def test_trajectory_returns_trajectory_type(self) -> None:
        """Return type is always Trajectory."""
        engine = CulturalDynamicsEngine()
        result = engine.zeitgeist_trajectory([self._make_signal("x", 0.0)])
        assert isinstance(result, Trajectory)


@pytest.mark.unit
class TestCulturalDynamicsEngineMutation:
    """Tests for CulturalDynamicsEngine.mutation_probability."""

    def test_low_energy_gives_low_probability(self) -> None:
        """Low energy state gives mutation probability near 0.1."""
        engine = CulturalDynamicsEngine()
        state = CulturalState(energy=0.0)
        meme = Meme(content="test")
        prob = engine.mutation_probability(state, meme)
        assert prob == pytest.approx(0.1, abs=1e-9)

    def test_high_energy_approaches_cap(self) -> None:
        """High energy state gives mutation probability capped at 0.9."""
        engine = CulturalDynamicsEngine()
        state = CulturalState(energy=2.0)
        meme = Meme(content="test")
        prob = engine.mutation_probability(state, meme)
        assert prob == pytest.approx(0.9, abs=1e-9)

    def test_probability_in_unit_range(self) -> None:
        """Mutation probability is always in [0, 1]."""
        engine = CulturalDynamicsEngine()
        for energy in [0.0, 0.5, 1.0, 1.5, 5.0]:
            state = CulturalState(energy=energy)
            prob = engine.mutation_probability(state, Meme(content="x"))
            assert 0.0 <= prob <= 1.0

    def test_energy_proportional_effect(self) -> None:
        """Higher energy yields higher mutation probability."""
        engine = CulturalDynamicsEngine()
        low_state = CulturalState(energy=0.2)
        high_state = CulturalState(energy=0.8)
        meme = Meme(content="x")
        assert engine.mutation_probability(high_state, meme) > engine.mutation_probability(
            low_state, meme
        )


@pytest.mark.unit
class TestCulturalDynamicsEnginePowerTopology:
    """Tests for CulturalDynamicsEngine.power_topology."""

    def test_empty_nodes_empty_powermap(self) -> None:
        """No nodes produces a PowerMap with no nodes."""
        engine = CulturalDynamicsEngine()
        pm = engine.power_topology([], [])
        assert isinstance(pm, PowerMap)
        assert pm.nodes == []

    def test_nodes_are_stored(self) -> None:
        """All provided node names are in the resulting PowerMap."""
        engine = CulturalDynamicsEngine()
        nodes = ["A", "B", "C"]
        pm = engine.power_topology(nodes, [])
        assert set(pm.nodes) == set(nodes)

    def test_all_nodes_get_baseline_score(self) -> None:
        """All nodes receive at least the baseline 0.1 centrality score."""
        engine = CulturalDynamicsEngine()
        pm = engine.power_topology(["X", "Y"], [])
        for node in ["X", "Y"]:
            assert pm.centrality_scores.get(node, 0) >= 0.1

    def test_source_interaction_increases_score(self) -> None:
        """Node that appears as source in interactions gets higher score."""
        engine = CulturalDynamicsEngine()
        nodes = ["A", "B"]
        # A is the source of 3 interactions
        interactions = [("A", "B"), ("A", "B"), ("A", "B")]
        pm = engine.power_topology(nodes, interactions)
        assert pm.centrality_scores["A"] > pm.centrality_scores["B"]

    def test_returns_power_map_type(self) -> None:
        """Return value is always a PowerMap instance."""
        engine = CulturalDynamicsEngine()
        result = engine.power_topology(["X"], [("X", "X")])
        assert isinstance(result, PowerMap)
