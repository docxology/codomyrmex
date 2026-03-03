"""Tests for bio_simulation MCP tools.

Strictly zero-mock tests that actually spin up simulations and
evolve populations.
"""

import pytest

from codomyrmex.bio_simulation.mcp_tools import (
    bio_analyze_genetics,
    bio_simulate_colony,
)


@pytest.mark.unit
def test_bio_simulate_colony_mcp_tool() -> None:
    """Verify bio_simulate_colony correctly simulates and returns stats."""
    # Run a small simulation: 5 ants, 1 hour
    stats = bio_simulate_colony(population=5, hours=1)

    assert isinstance(stats, dict)
    assert "tick" in stats
    assert stats["tick"] == 60  # 1 hour = 60 ticks
    assert "alive" in stats
    assert "dead" in stats
    assert "food_collected" in stats
    assert "state_distribution" in stats
    assert "avg_energy" in stats

    # Since it's zero-mock, verify constraints on real execution
    assert stats["alive"] + stats["dead"] == 5
    assert isinstance(stats["state_distribution"], dict)


@pytest.mark.unit
def test_bio_analyze_genetics_mcp_tool() -> None:
    """Verify bio_analyze_genetics evolves and returns distributions."""
    # Evolve a small population: 20 genomes, 3 generations
    distribution = bio_analyze_genetics(population_size=20, generations=3)

    assert isinstance(distribution, dict)
    # Ensure default traits from Genome.random() are present
    expected_traits = ["speed", "strength", "perception", "endurance"]
    for trait in expected_traits:
        assert trait in distribution
        stats = distribution[trait]
        assert "mean" in stats
        assert "std" in stats
        assert "min" in stats
        assert "max" in stats

        # Ensure values fall within expected Genome bounds [0, 1]
        assert 0.0 <= stats["mean"] <= 1.0
        assert 0.0 <= stats["min"] <= 1.0
        assert 0.0 <= stats["max"] <= 1.0


@pytest.mark.unit
def test_mcp_tool_metadata() -> None:
    """Verify the MCP tool metadata is correctly populated."""
    # Based on actual output and patterns in memory: The @mcp_tool decorator adds the metadata dict under _mcp_tool_meta,
    # but does NOT add an _is_mcp_tool attribute.
    colony_meta = getattr(bio_simulate_colony, "_mcp_tool_meta", {})
    assert colony_meta.get("category") == "bio_simulation"
    assert "name" in colony_meta
    # The decorator usually prepends codomyrmex. automatically
    assert colony_meta["name"].endswith("bio_simulate_colony")

    genetics_meta = getattr(bio_analyze_genetics, "_mcp_tool_meta", {})
    assert genetics_meta.get("category") == "bio_simulation"
    assert "name" in genetics_meta
    assert genetics_meta["name"].endswith("bio_analyze_genetics")
