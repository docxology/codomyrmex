"""Unit tests for codomyrmex.cerebrum.fpf.combinatorics module.

Tests the FPFCombinatoricsAnalyzer class covering pattern pair analysis,
dependency chain analysis, concept co-occurrence analysis, cross-part
relationships, visualization generation, and helper methods.

Zero-mock policy: all objects are real. Network access is required for
FPF spec fetching.
"""

import csv
import json
import os

import pytest

# Guard: the module requires network to fetch FPF spec and several optional libs
_SKIP_REASON = "Requires network access and matplotlib/networkx/numpy"

try:
    from codomyrmex.cerebrum import Case, CerebrumEngine
    from codomyrmex.cerebrum.fpf.combinatorics import FPFCombinatoricsAnalyzer
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
def analyzer(tmp_path_factory):
    """Create a shared FPFCombinatoricsAnalyzer instance for the module.

    Uses a temporary output directory so tests don't pollute the workspace.
    """
    out = tmp_path_factory.mktemp("combinatorics_output")
    return FPFCombinatoricsAnalyzer(output_dir=str(out))


@pytest.fixture(scope="module")
def spec(analyzer):
    """Return the FPF spec loaded by the analyzer."""
    return analyzer.spec


# ---------------------------------------------------------------------------
# Constructor / initialization
# ---------------------------------------------------------------------------


class TestFPFCombinatoricsAnalyzerInit:
    """Tests for FPFCombinatoricsAnalyzer construction."""

    def test_init_creates_output_dir(self, tmp_path):
        out = tmp_path / "new_output"
        FPFCombinatoricsAnalyzer(output_dir=str(out))
        assert out.exists()
        assert out.is_dir()

    def test_init_loads_spec(self, analyzer):
        assert analyzer.spec is not None
        assert len(analyzer.spec.patterns) > 0

    def test_init_creates_engines(self, analyzer):
        assert analyzer.cerebrum is not None
        assert isinstance(analyzer.cerebrum, CerebrumEngine)
        assert analyzer.fpf_analyzer is not None
        assert analyzer.term_analyzer is not None

    def test_init_with_custom_output_dir(self, tmp_path):
        custom = tmp_path / "custom"
        a = FPFCombinatoricsAnalyzer(output_dir=str(custom))
        assert a.output_dir == custom


# ---------------------------------------------------------------------------
# _pattern_to_case helper
# ---------------------------------------------------------------------------


class TestPatternToCase:
    """Tests for the _pattern_to_case helper method."""

    def test_returns_case_object(self, analyzer):
        pattern = analyzer.spec.patterns[0]
        case = analyzer._pattern_to_case(pattern)
        assert isinstance(case, Case)

    def test_case_id_contains_pattern_id(self, analyzer):
        pattern = analyzer.spec.patterns[0]
        case = analyzer._pattern_to_case(pattern)
        assert pattern.id in case.case_id

    def test_case_features_contain_status(self, analyzer):
        pattern = analyzer.spec.patterns[0]
        case = analyzer._pattern_to_case(pattern)
        assert "status" in case.features
        assert case.features["status"] == pattern.status

    def test_case_features_contain_part(self, analyzer):
        pattern = analyzer.spec.patterns[0]
        case = analyzer._pattern_to_case(pattern)
        assert "part" in case.features

    def test_case_features_contain_num_keywords(self, analyzer):
        pattern = analyzer.spec.patterns[0]
        case = analyzer._pattern_to_case(pattern)
        assert "num_keywords" in case.features
        assert case.features["num_keywords"] == len(pattern.keywords)

    def test_case_features_contain_num_dependencies(self, analyzer):
        pattern = analyzer.spec.patterns[0]
        case = analyzer._pattern_to_case(pattern)
        assert "num_dependencies" in case.features

    def test_case_context_has_pattern_id(self, analyzer):
        pattern = analyzer.spec.patterns[0]
        case = analyzer._pattern_to_case(pattern)
        assert case.context["pattern_id"] == pattern.id

    def test_case_context_has_title(self, analyzer):
        pattern = analyzer.spec.patterns[0]
        case = analyzer._pattern_to_case(pattern)
        assert case.context["title"] == pattern.title


# ---------------------------------------------------------------------------
# _find_shared_concepts helper
# ---------------------------------------------------------------------------


class TestFindSharedConcepts:
    """Tests for _find_shared_concepts helper."""

    def test_returns_list(self, analyzer):
        p1 = analyzer.spec.patterns[0]
        p2 = analyzer.spec.patterns[1]
        result = analyzer._find_shared_concepts(p1, p2)
        assert isinstance(result, list)

    def test_shared_concepts_are_strings(self, analyzer):
        p1 = analyzer.spec.patterns[0]
        p2 = analyzer.spec.patterns[1]
        result = analyzer._find_shared_concepts(p1, p2)
        for item in result:
            assert isinstance(item, str)


# ---------------------------------------------------------------------------
# _find_concept_clusters helper
# ---------------------------------------------------------------------------


class TestFindConceptClusters:
    """Tests for _find_concept_clusters helper."""

    def test_returns_list(self, analyzer):
        cooc = {"a": {"b": 5, "c": 4}, "b": {"a": 5, "d": 3}, "c": {"a": 4}, "d": {"b": 3}}
        result = analyzer._find_concept_clusters(cooc, min_weight=3)
        assert isinstance(result, list)

    def test_clusters_are_sorted_lists(self, analyzer):
        cooc = {"a": {"b": 5, "c": 4}, "b": {"a": 5}, "c": {"a": 4}}
        result = analyzer._find_concept_clusters(cooc, min_weight=3)
        for cluster in result:
            assert isinstance(cluster, list)
            assert cluster == sorted(cluster)

    def test_empty_cooccurrence(self, analyzer):
        result = analyzer._find_concept_clusters({}, min_weight=3)
        assert result == []

    def test_no_clusters_below_threshold(self, analyzer):
        cooc = {"a": {"b": 1}, "b": {"a": 1}}
        result = analyzer._find_concept_clusters(cooc, min_weight=5)
        assert result == []

    def test_filters_small_clusters(self, analyzer):
        # Clusters of size <= 2 should be excluded
        cooc = {"x": {"y": 10}, "y": {"x": 10}}
        result = analyzer._find_concept_clusters(cooc, min_weight=3)
        # Only a pair (size 2) -- should be excluded since filter is len > 2
        assert all(len(c) > 2 for c in result)


# ---------------------------------------------------------------------------
# analyze_pattern_pairs
# ---------------------------------------------------------------------------


class TestAnalyzePatternPairs:
    """Tests for analyze_pattern_pairs method."""

    @pytest.fixture(scope="class")
    def pairs_result(self, analyzer):
        return analyzer.analyze_pattern_pairs()

    def test_returns_dict(self, pairs_result):
        assert isinstance(pairs_result, dict)

    def test_has_total_pairs(self, pairs_result):
        assert "total_pairs" in pairs_result
        assert isinstance(pairs_result["total_pairs"], int)

    def test_has_high_similarity_pairs(self, pairs_result):
        assert "high_similarity_pairs" in pairs_result
        assert isinstance(pairs_result["high_similarity_pairs"], list)

    def test_has_related_pairs(self, pairs_result):
        assert "related_pairs" in pairs_result
        assert isinstance(pairs_result["related_pairs"], list)

    def test_has_all_pairs(self, pairs_result):
        assert "all_pairs" in pairs_result
        assert isinstance(pairs_result["all_pairs"], list)

    def test_pair_entry_structure(self, pairs_result):
        if pairs_result["all_pairs"]:
            pair = pairs_result["all_pairs"][0]
            assert "pattern1" in pair
            assert "pattern2" in pair
            assert "similarity" in pair
            assert "has_relationship" in pair
            assert "relationship_types" in pair
            assert "shared_keywords" in pair
            assert "shared_concepts" in pair

    def test_pairs_sorted_by_similarity_descending(self, pairs_result):
        all_pairs = pairs_result["all_pairs"]
        if len(all_pairs) > 1:
            sims = [p["similarity"] for p in all_pairs]
            assert sims == sorted(sims, reverse=True)

    def test_total_pairs_is_positive(self, pairs_result):
        # With 145 patterns, there should be many pairs
        assert pairs_result["total_pairs"] > 0


# ---------------------------------------------------------------------------
# analyze_dependency_chains
# ---------------------------------------------------------------------------


class TestAnalyzeDependencyChains:
    """Tests for analyze_dependency_chains method."""

    @pytest.fixture(scope="class")
    def chains_result(self, analyzer):
        return analyzer.analyze_dependency_chains()

    def test_returns_dict(self, chains_result):
        assert isinstance(chains_result, dict)

    def test_has_total_chains(self, chains_result):
        assert "total_chains" in chains_result
        assert isinstance(chains_result["total_chains"], int)

    def test_has_longest_chains(self, chains_result):
        assert "longest_chains" in chains_result
        assert isinstance(chains_result["longest_chains"], list)

    def test_has_most_important_chains(self, chains_result):
        assert "most_important_chains" in chains_result
        assert isinstance(chains_result["most_important_chains"], list)

    def test_chain_entry_structure(self, chains_result):
        for chain_info in chains_result["most_important_chains"]:
            assert "chain" in chain_info
            assert "length" in chain_info
            assert "avg_importance" in chain_info
            assert "parts" in chain_info


# ---------------------------------------------------------------------------
# analyze_concept_cooccurrence
# ---------------------------------------------------------------------------


class TestAnalyzeConceptCooccurrence:
    """Tests for analyze_concept_cooccurrence method."""

    @pytest.fixture(scope="class")
    def cooccurrence_result(self, analyzer):
        return analyzer.analyze_concept_cooccurrence()

    def test_returns_dict(self, cooccurrence_result):
        assert isinstance(cooccurrence_result, dict)

    def test_has_cooccurrence_matrix(self, cooccurrence_result):
        assert "cooccurrence_matrix" in cooccurrence_result
        assert isinstance(cooccurrence_result["cooccurrence_matrix"], dict)

    def test_has_strong_pairs(self, cooccurrence_result):
        assert "strong_pairs" in cooccurrence_result
        assert isinstance(cooccurrence_result["strong_pairs"], list)

    def test_has_concept_clusters(self, cooccurrence_result):
        assert "concept_clusters" in cooccurrence_result
        assert isinstance(cooccurrence_result["concept_clusters"], list)

    def test_strong_pairs_sorted_descending(self, cooccurrence_result):
        pairs = cooccurrence_result["strong_pairs"]
        if len(pairs) > 1:
            counts = [p["cooccurrence_count"] for p in pairs]
            assert counts == sorted(counts, reverse=True)

    def test_strong_pair_entry_structure(self, cooccurrence_result):
        for pair in cooccurrence_result["strong_pairs"]:
            assert "term1" in pair
            assert "term2" in pair
            assert "cooccurrence_count" in pair
            assert pair["cooccurrence_count"] >= 3


# ---------------------------------------------------------------------------
# analyze_cross_part_relationships
# ---------------------------------------------------------------------------


class TestAnalyzeCrossPartRelationships:
    """Tests for analyze_cross_part_relationships method."""

    @pytest.fixture(scope="class")
    def cross_part_result(self, analyzer):
        return analyzer.analyze_cross_part_relationships()

    def test_returns_dict(self, cross_part_result):
        assert isinstance(cross_part_result, dict)

    def test_has_total_cross_part_relationships(self, cross_part_result):
        assert "total_cross_part_relationships" in cross_part_result
        assert isinstance(cross_part_result["total_cross_part_relationships"], int)

    def test_has_relationships_list(self, cross_part_result):
        assert "relationships" in cross_part_result
        assert isinstance(cross_part_result["relationships"], list)

    def test_has_part_pair_counts(self, cross_part_result):
        assert "part_pair_counts" in cross_part_result
        assert isinstance(cross_part_result["part_pair_counts"], dict)


# ---------------------------------------------------------------------------
# generate_all_visualizations
# ---------------------------------------------------------------------------


class TestGenerateAllVisualizations:
    """Tests for generate_all_visualizations method."""

    def test_empty_results_no_crash(self, analyzer):
        # Should handle empty results gracefully
        empty_results = {
            "pattern_pairs": {},
            "dependency_chains": {},
            "concept_cooccurrence": {},
            "cross_part_relationships": {},
        }
        analyzer.generate_all_visualizations(empty_results)

    def test_creates_visualization_dir(self, analyzer):
        empty_results = {
            "pattern_pairs": {},
            "dependency_chains": {},
            "concept_cooccurrence": {},
            "cross_part_relationships": {},
        }
        analyzer.generate_all_visualizations(empty_results)
        viz_dir = analyzer.output_dir / "visualizations"
        assert viz_dir.exists()


# ---------------------------------------------------------------------------
# _visualize_pair_similarity
# ---------------------------------------------------------------------------


class TestVisualizePairSimilarity:
    """Tests for _visualize_pair_similarity method."""

    def test_empty_pairs_exports_csv(self, analyzer, tmp_path):
        viz_dir = tmp_path / "viz_pairs"
        viz_dir.mkdir()
        analyzer._visualize_pair_similarity({}, viz_dir)
        csv_path = viz_dir / "pair_similarity_heatmap.csv"
        assert csv_path.exists()

    def test_empty_pairs_csv_has_header(self, analyzer, tmp_path):
        viz_dir = tmp_path / "viz_pairs_header"
        viz_dir.mkdir()
        analyzer._visualize_pair_similarity({}, viz_dir)
        csv_path = viz_dir / "pair_similarity_heatmap.csv"
        with open(csv_path) as f:
            reader = csv.reader(f)
            header = next(reader)
        assert "pattern1" in header
        assert "similarity" in header

    def test_with_pair_data(self, analyzer, tmp_path):
        viz_dir = tmp_path / "viz_pairs_data"
        viz_dir.mkdir()
        pairs_data = {
            "all_pairs": [
                {
                    "pattern1": "A.0",
                    "pattern2": "A.1",
                    "similarity": 0.85,
                    "has_relationship": False,
                    "relationship_types": [],
                    "shared_keywords": ["test"],
                    "shared_concepts": [],
                },
            ],
        }
        analyzer._visualize_pair_similarity(pairs_data, viz_dir)
        # Check CSV was written with data
        csv_path = viz_dir / "pair_similarity_heatmap.csv"
        assert csv_path.exists()
        with open(csv_path) as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["pattern1"] == "A.0"


# ---------------------------------------------------------------------------
# _visualize_dependency_chains
# ---------------------------------------------------------------------------


class TestVisualizeDependencyChains:
    """Tests for _visualize_dependency_chains method."""

    def test_empty_chains_exports_json(self, analyzer, tmp_path):
        viz_dir = tmp_path / "viz_chains"
        viz_dir.mkdir()
        analyzer._visualize_dependency_chains({}, viz_dir)
        json_path = viz_dir / "dependency_chains.json"
        assert json_path.exists()

    def test_empty_chains_json_structure(self, analyzer, tmp_path):
        viz_dir = tmp_path / "viz_chains_struct"
        viz_dir.mkdir()
        analyzer._visualize_dependency_chains({}, viz_dir)
        json_path = viz_dir / "dependency_chains.json"
        with open(json_path) as f:
            data = json.load(f)
        assert "chains" in data
        assert "total_chains" in data


# ---------------------------------------------------------------------------
# _visualize_concept_cooccurrence
# ---------------------------------------------------------------------------


class TestVisualizeConceptCooccurrence:
    """Tests for _visualize_concept_cooccurrence method."""

    def test_empty_cooccurrence_exports_json_and_csv(self, analyzer, tmp_path):
        viz_dir = tmp_path / "viz_cooc"
        viz_dir.mkdir()
        analyzer._visualize_concept_cooccurrence({}, viz_dir)
        assert (viz_dir / "concept_cooccurrence_network.json").exists()
        assert (viz_dir / "concept_cooccurrence_network.csv").exists()

    def test_json_has_nodes_and_edges(self, analyzer, tmp_path):
        viz_dir = tmp_path / "viz_cooc_struct"
        viz_dir.mkdir()
        analyzer._visualize_concept_cooccurrence({}, viz_dir)
        with open(viz_dir / "concept_cooccurrence_network.json") as f:
            data = json.load(f)
        assert "nodes" in data
        assert "edges" in data


# ---------------------------------------------------------------------------
# _visualize_cross_part_relationships
# ---------------------------------------------------------------------------


class TestVisualizeCrossPartRelationships:
    """Tests for _visualize_cross_part_relationships method."""

    def test_empty_cross_part_exports_csv(self, analyzer, tmp_path):
        viz_dir = tmp_path / "viz_crosspart"
        viz_dir.mkdir()
        analyzer._visualize_cross_part_relationships({}, viz_dir)
        csv_path = viz_dir / "cross_part_relationships.csv"
        assert csv_path.exists()

    def test_csv_has_header(self, analyzer, tmp_path):
        viz_dir = tmp_path / "viz_crosspart_h"
        viz_dir.mkdir()
        analyzer._visualize_cross_part_relationships({}, viz_dir)
        csv_path = viz_dir / "cross_part_relationships.csv"
        with open(csv_path) as f:
            reader = csv.reader(f)
            header = next(reader)
        assert "part1" in header
        assert "relationship_count" in header


# ---------------------------------------------------------------------------
# run_comprehensive_combinatorics
# ---------------------------------------------------------------------------


class TestRunComprehensiveCombinatorics:
    """Tests for run_comprehensive_combinatorics method."""

    @pytest.fixture(scope="class")
    def comprehensive_result(self, analyzer):
        return analyzer.run_comprehensive_combinatorics()

    def test_returns_dict(self, comprehensive_result):
        assert isinstance(comprehensive_result, dict)

    def test_has_all_analysis_keys(self, comprehensive_result):
        assert "pattern_pairs" in comprehensive_result
        assert "dependency_chains" in comprehensive_result
        assert "concept_cooccurrence" in comprehensive_result
        assert "cross_part_relationships" in comprehensive_result

    def test_exports_json_file(self, analyzer, comprehensive_result):
        json_path = analyzer.output_dir / "combinatorics_analysis.json"
        assert json_path.exists()

    def test_exported_json_is_valid(self, analyzer, comprehensive_result):
        json_path = analyzer.output_dir / "combinatorics_analysis.json"
        with open(json_path) as f:
            data = json.load(f)
        assert "pattern_pairs" in data
