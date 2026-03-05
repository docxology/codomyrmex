"""Tests for bio_simulation MCP tools."""

from codomyrmex.bio_simulation.mcp_tools import (
    bio_simulation_colony_stats,
    bio_simulation_evolve_population,
    bio_simulation_run_colony,
)


class TestBioSimulationRunColony:
    def test_returns_dict_with_status(self):
        result = bio_simulation_run_colony(population=5, hours=1, seed=42)
        assert isinstance(result, dict)
        assert "status" in result

    def test_success_contains_step_summary(self):
        result = bio_simulation_run_colony(population=5, hours=1, seed=42)
        assert result["status"] == "success"
        assert "step_summary" in result
        assert "colony_stats" in result

    def test_step_summary_has_ticks_elapsed(self):
        result = bio_simulation_run_colony(population=5, hours=2, seed=42)
        assert result["step_summary"]["ticks_elapsed"] == 120

    def test_with_food_sources(self):
        food = [{"position": [30, 30], "amount": 200.0}]
        result = bio_simulation_run_colony(
            population=5, hours=1, seed=42, food_sources=food
        )
        assert result["status"] == "success"

    def test_negative_population_returns_error(self):
        result = bio_simulation_run_colony(population=-1, seed=42)
        assert result["status"] == "error"
        assert "message" in result


class TestBioSimulationColonyStats:
    def test_returns_dict_with_status(self):
        result = bio_simulation_colony_stats(population=5, seed=42)
        assert isinstance(result, dict)
        assert result["status"] == "success"

    def test_stats_keys(self):
        result = bio_simulation_colony_stats(population=5, seed=42)
        stats = result["stats"]
        assert "alive" in stats
        assert "food_collected" in stats
        assert stats["alive"] == 5

    def test_zero_population(self):
        result = bio_simulation_colony_stats(population=0, seed=42)
        assert result["status"] == "success"
        assert result["stats"]["alive"] == 0


class TestBioSimulationEvolvePopulation:
    def test_returns_dict_with_status(self):
        result = bio_simulation_evolve_population(population_size=10, generations=2)
        assert isinstance(result, dict)
        assert result["status"] == "success"

    def test_contains_fitness_data(self):
        result = bio_simulation_evolve_population(population_size=10, generations=3)
        assert "best_fitness" in result
        assert "average_fitness" in result
        assert isinstance(result["best_fitness"], float)
        assert isinstance(result["average_fitness"], float)

    def test_history_length_matches_generations(self):
        result = bio_simulation_evolve_population(population_size=10, generations=5)
        assert len(result["history"]) == 5

    def test_trait_distribution_present(self):
        result = bio_simulation_evolve_population(population_size=10, generations=2)
        dist = result["trait_distribution"]
        assert isinstance(dist, dict)
        assert "speed" in dist
