"""Tests for meme.hyperreality -- zero-mock, real instances only.

Covers SimulationLevel, OntologicalStatus, Simulacrum, RealityTunnel,
HyperrealityEngine, generate_simulacrum, and assess_reality_level.
"""

from __future__ import annotations

import pytest

from codomyrmex.meme.hyperreality.engine import HyperrealityEngine
from codomyrmex.meme.hyperreality.models import (
    OntologicalStatus,
    RealityTunnel,
    Simulacrum,
    SimulationLevel,
)
from codomyrmex.meme.hyperreality.simulation import (
    assess_reality_level,
    generate_simulacrum,
)

# ---------------------------------------------------------------------------
# SimulationLevel enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSimulationLevel:
    """Tests for the SimulationLevel enum."""

    def test_four_levels_present(self) -> None:
        """REFLECTION, MASK, ABSENCE, PURE are all present."""
        values = {sl.value for sl in SimulationLevel}
        assert values == {1, 2, 3, 4}

    def test_int_subclass(self) -> None:
        """SimulationLevel is an int enum."""
        assert isinstance(SimulationLevel.REFLECTION, int)
        assert SimulationLevel.PURE == 4

    def test_level_ordering(self) -> None:
        """Levels are ordered REFLECTION < MASK < ABSENCE < PURE."""
        assert SimulationLevel.REFLECTION < SimulationLevel.MASK
        assert SimulationLevel.MASK < SimulationLevel.ABSENCE
        assert SimulationLevel.ABSENCE < SimulationLevel.PURE


# ---------------------------------------------------------------------------
# OntologicalStatus enum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestOntologicalStatus:
    """Tests for the OntologicalStatus enum."""

    def test_four_statuses_present(self) -> None:
        """All four statuses are present."""
        expected = {"real", "virtual", "hyperreal", "fictional"}
        assert {s.value for s in OntologicalStatus} == expected

    def test_str_subclass(self) -> None:
        """OntologicalStatus is a StrEnum."""
        assert isinstance(OntologicalStatus.REAL, str)
        assert OntologicalStatus.HYPERREAL == "hyperreal"


# ---------------------------------------------------------------------------
# Simulacrum dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSimulacrum:
    """Tests for the Simulacrum dataclass."""

    def test_creation_stores_fields(self) -> None:
        """All Simulacrum fields are stored correctly."""
        sim = Simulacrum(
            referent="real_building",
            level=SimulationLevel.MASK,
            fidelity=0.8,
            autonomy=0.3,
        )
        assert sim.referent == "real_building"
        assert sim.level == SimulationLevel.MASK
        assert sim.fidelity == pytest.approx(0.8)
        assert sim.autonomy == pytest.approx(0.3)

    def test_id_auto_generated(self) -> None:
        """ID is auto-generated as an 8-char string."""
        sim = Simulacrum(referent="x", level=SimulationLevel.PURE)
        assert isinstance(sim.id, str)
        assert len(sim.id) == 8

    def test_default_fidelity(self) -> None:
        """Default fidelity is 1.0."""
        sim = Simulacrum(referent="x", level=SimulationLevel.REFLECTION)
        assert sim.fidelity == pytest.approx(1.0)

    def test_default_autonomy(self) -> None:
        """Default autonomy is 0.0."""
        sim = Simulacrum(referent="x", level=SimulationLevel.REFLECTION)
        assert sim.autonomy == pytest.approx(0.0)

    def test_metadata_default_empty(self) -> None:
        """Default metadata is empty dict."""
        sim = Simulacrum(referent="x", level=SimulationLevel.MASK)
        assert sim.metadata == {}


# ---------------------------------------------------------------------------
# RealityTunnel dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRealityTunnel:
    """Tests for the RealityTunnel dataclass."""

    def test_creation_stores_name(self) -> None:
        """name field is stored correctly."""
        tunnel = RealityTunnel(name="Materialist")
        assert tunnel.name == "Materialist"

    def test_filters_default_empty(self) -> None:
        """Default filters is empty list."""
        tunnel = RealityTunnel(name="x")
        assert tunnel.filters == []

    def test_distortion_default_zero(self) -> None:
        """Default distortion is 0.0."""
        tunnel = RealityTunnel(name="x")
        assert tunnel.distortion == pytest.approx(0.0)

    def test_active_simulacra_default_empty(self) -> None:
        """Default active_simulacra is empty list."""
        tunnel = RealityTunnel(name="x")
        assert tunnel.active_simulacra == []

    def test_explicit_fields_stored(self) -> None:
        """Explicit fields are stored correctly."""
        tunnel = RealityTunnel(
            name="Conspiratorial",
            filters=["everything is connected", "no coincidences"],
            distortion=0.9,
        )
        assert len(tunnel.filters) == 2
        assert tunnel.distortion == pytest.approx(0.9)


# ---------------------------------------------------------------------------
# generate_simulacrum
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGenerateSimulacrum:
    """Tests for the generate_simulacrum function."""

    def test_returns_simulacrum_type(self) -> None:
        """generate_simulacrum always returns a Simulacrum instance."""
        sim = generate_simulacrum("reality", SimulationLevel.REFLECTION)
        assert isinstance(sim, Simulacrum)

    def test_referent_stored(self) -> None:
        """The referent is stored in the generated simulacrum."""
        sim = generate_simulacrum("a painting", SimulationLevel.MASK)
        assert sim.referent == "a painting"

    def test_level_stored(self) -> None:
        """The simulation level is stored."""
        sim = generate_simulacrum("x", SimulationLevel.ABSENCE)
        assert sim.level == SimulationLevel.ABSENCE

    def test_reflection_level_high_fidelity(self) -> None:
        """REFLECTION level yields high fidelity (0.95)."""
        sim = generate_simulacrum("reality", SimulationLevel.REFLECTION)
        assert sim.fidelity == pytest.approx(0.95)

    def test_reflection_level_low_autonomy(self) -> None:
        """REFLECTION level yields low autonomy (0.1)."""
        sim = generate_simulacrum("reality", SimulationLevel.REFLECTION)
        assert sim.autonomy == pytest.approx(0.1)

    def test_mask_level_moderate_fidelity(self) -> None:
        """MASK level yields 0.8 fidelity."""
        sim = generate_simulacrum("icon", SimulationLevel.MASK)
        assert sim.fidelity == pytest.approx(0.8)

    def test_absence_level_moderate_autonomy(self) -> None:
        """ABSENCE level yields 0.6 autonomy."""
        sim = generate_simulacrum("ghost", SimulationLevel.ABSENCE)
        assert sim.autonomy == pytest.approx(0.6)

    def test_pure_level_full_autonomy(self) -> None:
        """PURE level yields full autonomy (1.0)."""
        sim = generate_simulacrum("pure_sign", SimulationLevel.PURE)
        assert sim.autonomy == pytest.approx(1.0)

    def test_pure_level_full_fidelity(self) -> None:
        """PURE level yields full fidelity (hyperreal: more real than real)."""
        sim = generate_simulacrum("pure_sign", SimulationLevel.PURE)
        assert sim.fidelity == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# assess_reality_level
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAssessRealityLevel:
    """Tests for the assess_reality_level function."""

    def test_no_provenance_returns_pure(self) -> None:
        """No provenance yields SimulationLevel.PURE."""
        result = assess_reality_level({"history": "some history"})
        assert result == SimulationLevel.PURE

    def test_copy_without_original_returns_absence(self) -> None:
        """History with 'copy' but no 'original' returns ABSENCE."""
        result = assess_reality_level({
            "history": "copy of a copy",
            "provenance": ["source_a"],
        })
        assert result == SimulationLevel.ABSENCE

    def test_high_distortion_returns_absence(self) -> None:
        """distortion > 0.8 returns ABSENCE."""
        result = assess_reality_level({
            "provenance": ["origin"],
            "distortion": 0.9,
        })
        assert result == SimulationLevel.ABSENCE

    def test_medium_distortion_returns_mask(self) -> None:
        """distortion between 0.4 and 0.8 returns MASK."""
        result = assess_reality_level({
            "provenance": ["origin"],
            "distortion": 0.6,
        })
        assert result == SimulationLevel.MASK

    def test_low_distortion_returns_reflection(self) -> None:
        """Low distortion and provenance returns REFLECTION."""
        result = assess_reality_level({
            "provenance": ["primary_source"],
            "distortion": 0.1,
        })
        assert result == SimulationLevel.REFLECTION

    def test_empty_dict_no_provenance_pure(self) -> None:
        """Empty dict has no provenance, returns PURE."""
        result = assess_reality_level({})
        assert result == SimulationLevel.PURE


# ---------------------------------------------------------------------------
# HyperrealityEngine
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHyperrealityEngineCreateTunnel:
    """Tests for HyperrealityEngine.create_tunnel."""

    def test_create_tunnel_returns_reality_tunnel(self) -> None:
        """create_tunnel returns a RealityTunnel instance."""
        engine = HyperrealityEngine()
        tunnel = engine.create_tunnel("Tech Utopian", ["AI solves everything"])
        assert isinstance(tunnel, RealityTunnel)

    def test_create_tunnel_name_stored(self) -> None:
        """Created tunnel has correct name."""
        engine = HyperrealityEngine()
        tunnel = engine.create_tunnel("Doomer", ["collapse imminent"])
        assert tunnel.name == "Doomer"

    def test_create_tunnel_filters_stored(self) -> None:
        """Created tunnel has the supplied filters."""
        engine = HyperrealityEngine()
        filters = ["filter_a", "filter_b"]
        tunnel = engine.create_tunnel("Test", filters)
        assert tunnel.filters == filters

    def test_create_tunnel_registered_in_engine(self) -> None:
        """Created tunnel is stored in engine.tunnels."""
        engine = HyperrealityEngine()
        engine.create_tunnel("Rationalist", ["evidence-based"])
        assert "Rationalist" in engine.tunnels

    def test_initial_tunnels_empty(self) -> None:
        """Fresh engine has no tunnels."""
        engine = HyperrealityEngine()
        assert engine.tunnels == {}


@pytest.mark.unit
class TestHyperrealityEngineGetTunnel:
    """Tests for HyperrealityEngine.get_tunnel."""

    def test_get_existing_tunnel(self) -> None:
        """get_tunnel returns the tunnel for a known name."""
        engine = HyperrealityEngine()
        engine.create_tunnel("Conspiratorial", [])
        result = engine.get_tunnel("Conspiratorial")
        assert result is not None
        assert result.name == "Conspiratorial"

    def test_get_nonexistent_tunnel_returns_none(self) -> None:
        """get_tunnel returns None for an unknown name."""
        engine = HyperrealityEngine()
        result = engine.get_tunnel("DoesNotExist")
        assert result is None


@pytest.mark.unit
class TestHyperrealityEngineInjectSimulacrum:
    """Tests for HyperrealityEngine.inject_simulacrum."""

    def test_inject_returns_simulacrum(self) -> None:
        """inject_simulacrum returns a Simulacrum instance."""
        engine = HyperrealityEngine()
        engine.create_tunnel("TestTunnel", [])
        sim = engine.inject_simulacrum("TestTunnel", "referent", SimulationLevel.MASK)
        assert isinstance(sim, Simulacrum)

    def test_inject_adds_to_tunnel_simulacra(self) -> None:
        """Injected simulacrum appears in tunnel's active_simulacra."""
        engine = HyperrealityEngine()
        engine.create_tunnel("T", [])
        engine.inject_simulacrum("T", "thing", SimulationLevel.REFLECTION)
        assert len(engine.tunnels["T"].active_simulacra) == 1

    def test_inject_increases_distortion(self) -> None:
        """Injecting simulacrum increases tunnel distortion."""
        engine = HyperrealityEngine()
        engine.create_tunnel("D", [])
        before = engine.tunnels["D"].distortion
        engine.inject_simulacrum("D", "thing", SimulationLevel.MASK)
        after = engine.tunnels["D"].distortion
        assert after > before

    def test_inject_auto_creates_missing_tunnel(self) -> None:
        """inject_simulacrum auto-creates the tunnel if it doesn't exist."""
        engine = HyperrealityEngine()
        engine.inject_simulacrum("AutoCreated", "thing", SimulationLevel.PURE)
        assert "AutoCreated" in engine.tunnels

    def test_inject_multiple_simulacra_caps_distortion(self) -> None:
        """Multiple injections cannot push distortion above 1.0."""
        engine = HyperrealityEngine()
        engine.create_tunnel("T", [])
        for _ in range(20):
            engine.inject_simulacrum("T", "x", SimulationLevel.PURE)
        assert engine.tunnels["T"].distortion <= 1.0

    def test_inject_simulacrum_referent_stored(self) -> None:
        """Returned simulacrum has the correct referent."""
        engine = HyperrealityEngine()
        engine.create_tunnel("TR", [])
        sim = engine.inject_simulacrum("TR", "specific_referent", SimulationLevel.ABSENCE)
        assert sim.referent == "specific_referent"
