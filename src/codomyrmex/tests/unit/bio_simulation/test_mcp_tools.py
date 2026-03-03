"""Strictly zero-mock tests for bio_simulation MCP tools."""

import pytest

from codomyrmex.bio_simulation.mcp_tools import (
    bio_simulation_evolve_population,
    bio_simulation_run_colony,
)


@pytest.mark.unit
def test_bio_simulation_run_colony() -> None:
    """Testing running an ant colony simulation via the MCP tool."""
    stats = bio_simulation_run_colony(population=10, hours=1)

    assert isinstance(stats, dict)
    assert "tick" in stats
    assert "alive" in stats
    assert "dead" in stats
    assert "food_collected" in stats

    assert stats["tick"] == 60  # 1 hour = 60 ticks
    assert stats["alive"] + stats["dead"] == 10  # Population constraint


@pytest.mark.unit
def test_bio_simulation_evolve_population() -> None:
    """Testing evolving a population via the MCP tool."""
    traits_dist = bio_simulation_evolve_population(generations=5, size=20)

    assert isinstance(traits_dist, dict)

    expected_traits = {"speed", "strength", "perception", "endurance"}
    for trait in expected_traits:
        assert trait in traits_dist

        trait_stats = traits_dist[trait]
        assert "mean" in trait_stats
        assert "std" in trait_stats
        assert "min" in trait_stats
        assert "max" in trait_stats

        # Verify basic range sanity checks for genomes created with random values
        assert 0.0 <= trait_stats["min"] <= trait_stats["max"] <= 1.0
        assert 0.0 <= trait_stats["mean"] <= 1.0
