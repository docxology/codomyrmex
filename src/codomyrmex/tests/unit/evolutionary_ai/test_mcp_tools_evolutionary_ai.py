"""Tests for evolutionary_ai MCP tools.

Zero-mock policy: all tests exercise real implementations.
"""

from __future__ import annotations


class TestEvolutionaryAiListOperators:
    """Tests for evolutionary_ai_list_operators tool."""

    def test_list_operators_returns_all_categories(self):
        from codomyrmex.evolutionary_ai.mcp_tools import evolutionary_ai_list_operators

        result = evolutionary_ai_list_operators()
        assert result["status"] == "success"
        assert len(result["mutation_operators"]) == 4
        assert len(result["crossover_operators"]) == 4
        assert len(result["selection_operators"]) == 3

    def test_list_operators_has_descriptions(self):
        from codomyrmex.evolutionary_ai.mcp_tools import evolutionary_ai_list_operators

        result = evolutionary_ai_list_operators()
        assert result["status"] == "success"
        for op in result["mutation_operators"]:
            assert "name" in op
            assert "description" in op


class TestEvolutionaryAiRunEvolution:
    """Tests for evolutionary_ai_run_evolution tool."""

    def test_run_evolution_basic(self):
        from codomyrmex.evolutionary_ai.mcp_tools import evolutionary_ai_run_evolution

        result = evolutionary_ai_run_evolution(
            population_size=10,
            genome_length=5,
            generations=3,
        )
        assert result["status"] == "success"
        assert result["generations_run"] == 3
        assert result["best_fitness"] is not None
        assert result["best_fitness"] > 0
        assert len(result["history"]) == 3

    def test_run_evolution_zero_generations(self):
        from codomyrmex.evolutionary_ai.mcp_tools import evolutionary_ai_run_evolution

        result = evolutionary_ai_run_evolution(
            population_size=5,
            genome_length=3,
            generations=0,
        )
        assert result["status"] == "success"
        assert result["generations_run"] == 0
        assert result["best_fitness"] is not None

    def test_run_evolution_invalid_population(self):
        from codomyrmex.evolutionary_ai.mcp_tools import evolutionary_ai_run_evolution

        result = evolutionary_ai_run_evolution(population_size=1)
        assert result["status"] == "error"
        assert "population_size" in result["message"]

    def test_run_evolution_invalid_genome_length(self):
        from codomyrmex.evolutionary_ai.mcp_tools import evolutionary_ai_run_evolution

        result = evolutionary_ai_run_evolution(genome_length=0)
        assert result["status"] == "error"
        assert "genome_length" in result["message"]


class TestEvolutionaryAiGenomeStats:
    """Tests for evolutionary_ai_genome_stats tool."""

    def test_genome_stats_basic(self):
        from codomyrmex.evolutionary_ai.mcp_tools import evolutionary_ai_genome_stats

        result = evolutionary_ai_genome_stats(genome_length=20)
        assert result["status"] == "success"
        assert result["length"] == 20
        assert 0.0 <= result["mean"] <= 1.0
        assert len(result["genes"]) == 20

    def test_genome_stats_custom_bounds(self):
        from codomyrmex.evolutionary_ai.mcp_tools import evolutionary_ai_genome_stats

        result = evolutionary_ai_genome_stats(
            genome_length=10,
            gene_low=-5.0,
            gene_high=5.0,
        )
        assert result["status"] == "success"
        assert result["min_val"] >= -5.0
        assert result["max_val"] <= 5.0

    def test_genome_stats_invalid_length(self):
        from codomyrmex.evolutionary_ai.mcp_tools import evolutionary_ai_genome_stats

        result = evolutionary_ai_genome_stats(genome_length=0)
        assert result["status"] == "error"
        assert "genome_length" in result["message"]
