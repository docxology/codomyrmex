"""Unit tests for codomyrmex.cerebrum.fpf.orchestration module.

Tests the FPFOrchestrator class covering case creation, Bayesian network
building, case-based reasoning, Bayesian inference, active inference,
comprehensive analysis, visualization generation, result export, and
markdown report generation.

Zero-mock policy: all objects are real. Network access is required for
FPF spec fetching.
"""

import json
import os

import pytest

_SKIP_REASON = "Requires network access and cerebrum/fpf dependencies"

try:
    from codomyrmex.cerebrum import (
        ActiveInferenceAgent,
        BayesianNetwork,
        Case,
        CerebrumConfig,
        CerebrumEngine,
        InferenceEngine,
    )
    from codomyrmex.cerebrum.fpf.orchestration import FPFOrchestrator, main
    from codomyrmex.cerebrum.inference.bayesian import Distribution
    from codomyrmex.fpf import FPFClient

    _HAS_DEPS = True
except ImportError:
    _HAS_DEPS = False

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(not _HAS_DEPS, reason=_SKIP_REASON),
    pytest.mark.skipif(
        os.getenv("CI") == "true" and not os.getenv("ALLOW_NETWORK"),
        reason="Skipping network-dependent test in CI without ALLOW_NETWORK",
    ),
]


@pytest.fixture(scope="module")
def orchestrator(tmp_path_factory):
    """Create a shared FPFOrchestrator instance for the module."""
    out = tmp_path_factory.mktemp("orchestration_output")
    return FPFOrchestrator(output_dir=str(out))


@pytest.fixture(scope="module")
def spec(orchestrator):
    """Return the FPF spec loaded by the orchestrator."""
    return orchestrator.spec


# ---------------------------------------------------------------------------
# Constructor / initialization
# ---------------------------------------------------------------------------


class TestFPFOrchestratorInit:
    """Tests for FPFOrchestrator construction."""

    def test_init_creates_output_dir(self, tmp_path):
        out = tmp_path / "orch_output"
        o = FPFOrchestrator(output_dir=str(out))
        assert out.exists()

    def test_init_loads_spec(self, orchestrator):
        assert orchestrator.spec is not None
        assert len(orchestrator.spec.patterns) > 0

    def test_init_creates_cerebrum_engine(self, orchestrator):
        assert orchestrator.cerebrum is not None
        assert isinstance(orchestrator.cerebrum, CerebrumEngine)

    def test_init_creates_fpf_analyzer(self, orchestrator):
        assert orchestrator.fpf_analyzer is not None

    def test_init_creates_term_analyzer(self, orchestrator):
        assert orchestrator.term_analyzer is not None

    def test_init_configures_cerebrum_with_custom_config(self, orchestrator):
        # The orchestrator sets a custom config in __init__
        config = orchestrator.cerebrum.config
        assert config.case_similarity_threshold == 0.6
        assert config.max_retrieved_cases == 20
        assert config.inference_method == "variable_elimination"
        assert config.adaptation_rate == 0.1


# ---------------------------------------------------------------------------
# create_pattern_cases
# ---------------------------------------------------------------------------


class TestCreatePatternCases:
    """Tests for create_pattern_cases method."""

    @pytest.fixture(scope="class")
    def cases(self, orchestrator):
        return orchestrator.create_pattern_cases()

    def test_returns_list(self, cases):
        assert isinstance(cases, list)

    def test_returns_case_objects(self, cases):
        for case in cases:
            assert isinstance(case, Case)

    def test_case_count_matches_patterns(self, cases, orchestrator):
        assert len(cases) == len(orchestrator.spec.patterns)

    def test_case_id_format(self, cases, orchestrator):
        first_pattern = orchestrator.spec.patterns[0]
        assert cases[0].case_id == f"pattern_{first_pattern.id}"

    def test_case_features_have_status(self, cases):
        assert "status" in cases[0].features

    def test_case_features_have_part(self, cases):
        assert "part" in cases[0].features

    def test_case_features_have_num_keywords(self, cases):
        assert "num_keywords" in cases[0].features

    def test_case_features_have_num_dependencies(self, cases):
        assert "num_dependencies" in cases[0].features

    def test_case_features_have_bool_deps(self, cases):
        assert "has_builds_on" in cases[0].features
        assert "has_prerequisite" in cases[0].features

    def test_case_context_has_pattern_id(self, cases, orchestrator):
        first_pattern = orchestrator.spec.patterns[0]
        assert cases[0].context["pattern_id"] == first_pattern.id

    def test_case_context_has_title(self, cases, orchestrator):
        first_pattern = orchestrator.spec.patterns[0]
        assert cases[0].context["title"] == first_pattern.title

    def test_case_outcome_is_none(self, cases):
        # Outcome is set to None initially
        for case in cases:
            assert case.outcome is None

    def test_case_metadata_has_pattern_info(self, cases, orchestrator):
        first_pattern = orchestrator.spec.patterns[0]
        assert cases[0].metadata["pattern_id"] == first_pattern.id
        assert cases[0].metadata["title"] == first_pattern.title


# ---------------------------------------------------------------------------
# build_bayesian_network_from_fpf
# ---------------------------------------------------------------------------


class TestBuildBayesianNetworkFromFPF:
    """Tests for build_bayesian_network_from_fpf method."""

    @pytest.fixture(scope="class")
    def network(self, orchestrator):
        return orchestrator.build_bayesian_network_from_fpf()

    def test_returns_bayesian_network(self, network):
        assert isinstance(network, BayesianNetwork)

    def test_network_has_name(self, network):
        assert network.name == "fpf_pattern_network"

    def test_network_has_pattern_status_node(self, network):
        assert "pattern_status" in network.nodes

    def test_network_has_dependency_node(self, network):
        assert "has_dependencies" in network.nodes

    def test_network_has_importance_node(self, network):
        assert "pattern_importance" in network.nodes

    def test_network_has_edges(self, network):
        # pattern_status -> pattern_importance
        assert "pattern_importance" in network.edges.get("pattern_status", [])

    def test_network_has_multiple_nodes(self, network):
        # Should have pattern_status + has_dependencies + pattern_importance + part nodes + concept nodes
        assert len(network.nodes) >= 3

    def test_importance_node_has_three_values(self, network):
        importance_info = network.nodes["pattern_importance"]
        assert set(importance_info["values"]) == {"high", "medium", "low"}


# ---------------------------------------------------------------------------
# analyze_with_case_based_reasoning
# ---------------------------------------------------------------------------


class TestAnalyzeWithCaseBasedReasoning:
    """Tests for analyze_with_case_based_reasoning method."""

    @pytest.fixture(scope="class")
    def cbr_result(self, orchestrator):
        return orchestrator.analyze_with_case_based_reasoning()

    def test_returns_dict(self, cbr_result):
        assert isinstance(cbr_result, dict)

    def test_has_similarity_analysis(self, cbr_result):
        assert "similarity_analysis" in cbr_result
        assert isinstance(cbr_result["similarity_analysis"], dict)

    def test_has_total_cases(self, cbr_result):
        assert "total_cases" in cbr_result
        assert cbr_result["total_cases"] > 0

    def test_has_case_base_size(self, cbr_result):
        assert "case_base_size" in cbr_result
        assert cbr_result["case_base_size"] > 0

    def test_similarity_entry_structure(self, cbr_result):
        for pattern_id, data in cbr_result["similarity_analysis"].items():
            assert "prediction" in data
            assert "confidence" in data
            assert "retrieved_count" in data
            assert "similar_patterns" in data

    def test_analyzes_up_to_20_patterns(self, cbr_result):
        assert len(cbr_result["similarity_analysis"]) <= 20


# ---------------------------------------------------------------------------
# analyze_with_bayesian_inference
# ---------------------------------------------------------------------------


class TestAnalyzeWithBayesianInference:
    """Tests for analyze_with_bayesian_inference method."""

    @pytest.fixture(scope="class")
    def bayesian_result(self, orchestrator):
        return orchestrator.analyze_with_bayesian_inference()

    def test_returns_dict(self, bayesian_result):
        assert isinstance(bayesian_result, dict)

    def test_has_inference_results(self, bayesian_result):
        assert "inference_results" in bayesian_result

    def test_has_network_nodes(self, bayesian_result):
        assert "network_nodes" in bayesian_result
        assert bayesian_result["network_nodes"] > 0

    def test_has_network_edges(self, bayesian_result):
        assert "network_edges" in bayesian_result

    def test_inference_results_structure(self, bayesian_result):
        for pattern_id, data in bayesian_result["inference_results"].items():
            if "error" not in data:
                assert "importance_distribution" in data
                assert "most_likely" in data
                assert "evidence" in data
                dist = data["importance_distribution"]
                assert "high" in dist
                assert "medium" in dist
                assert "low" in dist

    def test_analyzes_up_to_20_patterns(self, bayesian_result):
        assert len(bayesian_result["inference_results"]) <= 20

    def test_importance_probabilities_sum_near_one(self, bayesian_result):
        for pattern_id, data in bayesian_result["inference_results"].items():
            if "importance_distribution" in data:
                dist = data["importance_distribution"]
                total = dist["high"] + dist["medium"] + dist["low"]
                assert abs(total - 1.0) < 0.01


# ---------------------------------------------------------------------------
# analyze_with_active_inference
# ---------------------------------------------------------------------------


class TestAnalyzeWithActiveInference:
    """Tests for analyze_with_active_inference method."""

    @pytest.fixture(scope="class")
    def ai_result(self, orchestrator):
        return orchestrator.analyze_with_active_inference()

    def test_returns_dict(self, ai_result):
        assert isinstance(ai_result, dict)

    def test_has_exploration_path(self, ai_result):
        assert "exploration_path" in ai_result
        assert isinstance(ai_result["exploration_path"], list)

    def test_has_final_beliefs(self, ai_result):
        assert "final_beliefs" in ai_result
        assert isinstance(ai_result["final_beliefs"], dict)

    def test_exploration_path_entry_structure(self, ai_result):
        for step in ai_result["exploration_path"]:
            assert "pattern_id" in step
            assert "action" in step
            assert "free_energy" in step
            assert "importance" in step

    def test_exploration_path_length(self, ai_result):
        # Should explore up to 10 patterns
        assert len(ai_result["exploration_path"]) <= 10

    def test_actions_are_valid(self, ai_result):
        valid_actions = {"analyze_pattern", "explore_dependencies", "analyze_concepts", "skip"}
        for step in ai_result["exploration_path"]:
            assert step["action"] in valid_actions

    def test_free_energy_is_numeric(self, ai_result):
        for step in ai_result["exploration_path"]:
            assert isinstance(step["free_energy"], (int, float))

    def test_final_beliefs_has_states(self, ai_result):
        assert "states" in ai_result["final_beliefs"]


# ---------------------------------------------------------------------------
# generate_comprehensive_analysis
# ---------------------------------------------------------------------------


class TestGenerateComprehensiveAnalysis:
    """Tests for generate_comprehensive_analysis method."""

    @pytest.fixture(scope="class")
    def comprehensive_result(self, orchestrator):
        return orchestrator.generate_comprehensive_analysis()

    def test_returns_dict(self, comprehensive_result):
        assert isinstance(comprehensive_result, dict)

    def test_has_fpf_statistics(self, comprehensive_result):
        stats = comprehensive_result["fpf_statistics"]
        assert "total_patterns" in stats
        assert "total_concepts" in stats
        assert "total_relationships" in stats

    def test_has_case_based_reasoning(self, comprehensive_result):
        assert "case_based_reasoning" in comprehensive_result

    def test_has_bayesian_inference(self, comprehensive_result):
        assert "bayesian_inference" in comprehensive_result

    def test_has_active_inference(self, comprehensive_result):
        assert "active_inference" in comprehensive_result

    def test_has_fpf_analysis(self, comprehensive_result):
        fpf = comprehensive_result["fpf_analysis"]
        assert "pattern_importance" in fpf
        assert "critical_patterns" in fpf
        assert "isolated_patterns" in fpf
        assert "part_cohesion" in fpf

    def test_has_term_analysis(self, comprehensive_result):
        terms = comprehensive_result["term_analysis"]
        assert "shared_terms" in terms
        assert "important_terms" in terms

    def test_pattern_count_is_positive(self, comprehensive_result):
        assert comprehensive_result["fpf_statistics"]["total_patterns"] > 0


# ---------------------------------------------------------------------------
# export_results
# ---------------------------------------------------------------------------


class TestExportResults:
    """Tests for export_results method."""

    @pytest.fixture(scope="class")
    def exported(self, orchestrator):
        results = {
            "fpf_statistics": {"total_patterns": 10, "total_concepts": 5, "total_relationships": 3},
            "case_based_reasoning": {
                "similarity_analysis": {
                    "P1": {"prediction": 0.7, "confidence": 0.8, "retrieved_count": 3, "similar_patterns": []},
                },
                "total_cases": 10,
                "case_base_size": 10,
            },
            "bayesian_inference": {
                "inference_results": {
                    "P1": {
                        "importance_distribution": {"high": 0.5, "medium": 0.3, "low": 0.2},
                        "most_likely": "high",
                        "evidence": {},
                    },
                },
                "network_nodes": 5,
                "network_edges": 3,
            },
            "active_inference": {
                "exploration_path": [
                    {"pattern_id": "P1", "action": "analyze_pattern", "free_energy": 0.5, "importance": 0.8},
                ],
                "final_beliefs": {"states": {"s1": 0.5}},
            },
            "fpf_analysis": {
                "pattern_importance": {"P1": 0.8},
                "critical_patterns": [("P1", 0.8)],
                "isolated_patterns": [],
                "part_cohesion": {"A": 0.9},
            },
            "term_analysis": {
                "shared_terms": [("term1", 5, ["P1", "P2"])],
                "important_terms": [("concept1", 0.9, 4)],
            },
        }
        orchestrator.export_results(results)
        return results

    def test_json_file_created(self, orchestrator, exported):
        json_path = orchestrator.output_dir / "comprehensive_analysis.json"
        assert json_path.exists()

    def test_json_file_is_valid(self, orchestrator, exported):
        json_path = orchestrator.output_dir / "comprehensive_analysis.json"
        with open(json_path) as f:
            data = json.load(f)
        assert "fpf_statistics" in data

    def test_markdown_file_created(self, orchestrator, exported):
        md_path = orchestrator.output_dir / "comprehensive_analysis.md"
        assert md_path.exists()

    def test_markdown_contains_header(self, orchestrator, exported):
        md_path = orchestrator.output_dir / "comprehensive_analysis.md"
        content = md_path.read_text()
        assert "# CEREBRUM Analysis" in content

    def test_markdown_contains_statistics(self, orchestrator, exported):
        md_path = orchestrator.output_dir / "comprehensive_analysis.md"
        content = md_path.read_text()
        assert "Total Patterns" in content


# ---------------------------------------------------------------------------
# _generate_markdown_report
# ---------------------------------------------------------------------------


class TestGenerateMarkdownReport:
    """Tests for _generate_markdown_report method."""

    def test_report_sections(self, orchestrator, tmp_path):
        output_path = tmp_path / "report.md"
        results = {
            "fpf_statistics": {"total_patterns": 5, "total_concepts": 2, "total_relationships": 1},
            "case_based_reasoning": {
                "similarity_analysis": {},
                "total_cases": 5,
                "case_base_size": 5,
            },
            "bayesian_inference": {
                "inference_results": {},
                "network_nodes": 3,
                "network_edges": 2,
            },
            "active_inference": {
                "exploration_path": [],
                "final_beliefs": {},
            },
            "fpf_analysis": {
                "critical_patterns": [],
                "part_cohesion": {},
            },
            "term_analysis": {
                "shared_terms": [],
            },
        }
        orchestrator._generate_markdown_report(results, output_path)
        content = output_path.read_text()
        assert "## Overview" in content
        assert "## Case-Based Reasoning" in content
        assert "## Bayesian Inference" in content
        assert "## Active Inference" in content
        assert "## FPF Analysis" in content
        assert "## Term Analysis" in content


# ---------------------------------------------------------------------------
# generate_visualizations (smoke test)
# ---------------------------------------------------------------------------


class TestGenerateVisualizations:
    """Smoke tests for generate_visualizations method."""

    def test_no_crash_with_minimal_results(self, orchestrator):
        minimal = {
            "case_based_reasoning": {"similarity_analysis": {}},
            "bayesian_inference": {"inference_results": {}},
        }
        # Should not raise even with minimal data
        orchestrator.generate_visualizations(minimal)

    def test_creates_viz_directory(self, orchestrator):
        minimal = {
            "case_based_reasoning": {"similarity_analysis": {}},
            "bayesian_inference": {"inference_results": {}},
        }
        orchestrator.generate_visualizations(minimal)
        viz_dir = orchestrator.output_dir / "visualizations"
        assert viz_dir.exists()


# ---------------------------------------------------------------------------
# _generate_concordance_visualizations (smoke)
# ---------------------------------------------------------------------------


class TestGenerateConcordanceVisualizations:
    """Tests for _generate_concordance_visualizations method."""

    def test_no_crash_with_empty_data(self, orchestrator, tmp_path):
        viz_dir = tmp_path / "concordance_viz"
        viz_dir.mkdir()
        analysis_results = {
            "case_based_reasoning": {"similarity_analysis": {}},
            "bayesian_inference": {"inference_results": {}},
        }
        orchestrator._generate_concordance_visualizations(analysis_results, viz_dir)


# ---------------------------------------------------------------------------
# _generate_composition_visualizations (smoke)
# ---------------------------------------------------------------------------


class TestGenerateCompositionVisualizations:
    """Tests for _generate_composition_visualizations method."""

    def test_no_crash_with_empty_data(self, orchestrator, tmp_path):
        viz_dir = tmp_path / "composition_viz"
        viz_dir.mkdir()
        analysis_results = {
            "case_based_reasoning": {"similarity_analysis": {}},
            "bayesian_inference": {"inference_results": {}},
        }
        orchestrator._generate_composition_visualizations(analysis_results, viz_dir)


# ---------------------------------------------------------------------------
# run_comprehensive_analysis (integration-level)
# ---------------------------------------------------------------------------


class TestRunComprehensiveAnalysis:
    """Tests for run_comprehensive_analysis end-to-end method."""

    @pytest.fixture(scope="class")
    def full_result(self, orchestrator):
        return orchestrator.run_comprehensive_analysis()

    def test_returns_dict(self, full_result):
        assert isinstance(full_result, dict)

    def test_has_all_top_level_keys(self, full_result):
        assert "fpf_statistics" in full_result
        assert "case_based_reasoning" in full_result
        assert "bayesian_inference" in full_result
        assert "active_inference" in full_result
        assert "fpf_analysis" in full_result
        assert "term_analysis" in full_result

    def test_json_export_exists(self, orchestrator, full_result):
        assert (orchestrator.output_dir / "comprehensive_analysis.json").exists()

    def test_markdown_export_exists(self, orchestrator, full_result):
        assert (orchestrator.output_dir / "comprehensive_analysis.md").exists()
