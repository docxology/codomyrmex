from codomyrmex.logging_monitoring import get_logger
"""Analyzer for FPF specifications.

"""Core functionality module

This module provides analyzer functionality including:
- 12 functions: __init__, calculate_pattern_importance, calculate_concept_centrality...
- 1 classes: FPFAnalyzer

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
This module provides intelligent analysis capabilities including
importance scoring, centrality analysis, and relationship strength calculation.
"""

from collections import defaultdict
from typing import Dict, List, Tuple

import networkx as nx

from .models import FPFSpec, Pattern, Concept, Relationship


class FPFAnalyzer:
    """Analyzer for FPF specifications."""

    def __init__(self, spec: FPFSpec):
        """Initialize the analyzer.

        Args:
            spec: The FPFSpec object to analyze
        """
        self.spec = spec
        self._dependency_graph = None
        self._concept_graph = None

    def calculate_pattern_importance(self) -> Dict[str, float]:
        """Calculate importance scores for patterns.

        Uses multiple metrics: degree centrality, betweenness centrality,
        and dependency depth.

        Returns:
            Dictionary mapping pattern IDs to importance scores
        """
        if not self._dependency_graph:
            self._build_dependency_graph()

        G = self._dependency_graph

        if len(G.nodes()) == 0:
            return {}

        # Calculate centrality metrics
        degree_centrality = nx.degree_centrality(G)
        betweenness_centrality = nx.betweenness_centrality(G)

        # Normalize and combine
        importance_scores = {}
        max_degree = max(degree_centrality.values()) if degree_centrality.values() else 1
        max_betweenness = max(betweenness_centrality.values()) if betweenness_centrality.values() else 1

        for pattern_id in G.nodes():
            degree_norm = degree_centrality.get(pattern_id, 0) / max_degree if max_degree > 0 else 0
            betweenness_norm = betweenness_centrality.get(pattern_id, 0) / max_betweenness if max_betweenness > 0 else 0
            # Combined score (weighted average)
            importance_scores[pattern_id] = 0.6 * degree_norm + 0.4 * betweenness_norm

        return importance_scores

    def calculate_concept_centrality(self) -> Dict[str, float]:
        """Calculate centrality scores for concepts.

        Returns:
            Dictionary mapping concept names to centrality scores
        """
        if not self._concept_graph:
            self._build_concept_graph()

        G = self._concept_graph

        if len(G.nodes()) == 0:
            return {}

        centrality = nx.degree_centrality(G)
        return centrality

    def calculate_relationship_strength(self) -> Dict[Tuple[str, str, str], float]:
        """Calculate strength scores for relationships.

        Returns:
            Dictionary mapping (source, target, type) tuples to strength scores
        """
        strengths = {}

        for relationship in self.spec.relationships:
            # Base strength from relationship type
            type_weights = {
                "builds_on": 1.0,
                "prerequisite_for": 0.9,
                "coordinates_with": 0.7,
                "constrains": 0.8,
                "refines": 0.6,
                "informs": 0.5,
            }
            base_strength = type_weights.get(relationship.type, 0.5)

            # Adjust based on pattern importance
            importance = self.calculate_pattern_importance()
            source_importance = importance.get(relationship.source, 0.5)
            target_importance = importance.get(relationship.target, 0.5)

            # Combined strength
            strength = base_strength * (0.5 + 0.5 * (source_importance + target_importance) / 2)
            strengths[(relationship.source, relationship.target, relationship.type)] = strength

        return strengths

    def analyze_dependency_depth(self) -> Dict[str, int]:
        """Analyze dependency depth for each pattern.

        Returns:
            Dictionary mapping pattern IDs to their maximum dependency depth
        """
        if not self._dependency_graph:
            self._build_dependency_graph()

        G = self._dependency_graph

        if len(G.nodes()) == 0:
            return {}

        depths = {}

        def calculate_depth(node: str, visited: set) -> int:
    """Brief description of calculate_depth.

Args:
    node : Description of node
    visited : Description of visited

    Returns: Description of return value (type: int)
"""
            if node in visited:
                return 0
            visited.add(node)

            predecessors = list(G.predecessors(node))
            if not predecessors:
                return 0

            max_pred_depth = max(
                [calculate_depth(pred, visited.copy()) for pred in predecessors], default=0
            )
            return max_pred_depth + 1

        for node in G.nodes():
            depths[node] = calculate_depth(node, set())

        return depths

    def get_critical_patterns(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Get the most critical patterns based on importance.

        Args:
            top_n: Number of top patterns to return

        Returns:
            List of tuples (pattern_id, importance_score)
        """
        importance = self.calculate_pattern_importance()
        sorted_patterns = sorted(
            importance.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_patterns[:top_n]

    def get_isolated_patterns(self) -> List[str]:
        """Get patterns that have no dependencies or dependents.

        Returns:
            List of isolated pattern IDs
        """
        if not self._dependency_graph:
            self._build_dependency_graph()

        G = self._dependency_graph

        isolated = [
            node
            for node in G.nodes()
            if G.in_degree(node) == 0 and G.out_degree(node) == 0
        ]

        return isolated

    def analyze_part_cohesion(self) -> Dict[str, float]:
        """Analyze cohesion within each part.

        Cohesion is measured as the ratio of internal relationships
        to total possible relationships.

        Returns:
            Dictionary mapping part IDs to cohesion scores
        """
        part_patterns: Dict[str, List[str]] = defaultdict(list)
        for pattern in self.spec.patterns:
            part = pattern.part or "Other"
            part_patterns[part].append(pattern.id)

        cohesion_scores = {}

        for part, pattern_ids in part_patterns.items():
            pattern_set = set(pattern_ids)

            # Count internal relationships
            internal_rels = sum(
                1
                for rel in self.spec.relationships
                if rel.source in pattern_set and rel.target in pattern_set
            )

            # Total possible relationships (n * (n-1))
            n = len(pattern_ids)
            total_possible = n * (n - 1) if n > 1 else 0

            cohesion = internal_rels / total_possible if total_possible > 0 else 0.0
            cohesion_scores[part] = cohesion

        return cohesion_scores

    def get_analysis_summary(self) -> Dict[str, any]:
        """Get comprehensive analysis summary.

        Returns:
            Dictionary with analysis results
        """
        importance = self.calculate_pattern_importance()
        centrality = self.calculate_concept_centrality()
        depths = self.analyze_dependency_depth()
        cohesion = self.analyze_part_cohesion()
        critical = self.get_critical_patterns(10)
        isolated = self.get_isolated_patterns()

        return {
            "pattern_importance": importance,
            "concept_centrality": centrality,
            "dependency_depths": depths,
            "part_cohesion": cohesion,
            "critical_patterns": critical,
            "isolated_patterns": isolated,
            "statistics": {
                "total_patterns": len(self.spec.patterns),
                "total_concepts": len(self.spec.concepts),
                "total_relationships": len(self.spec.relationships),
                "avg_importance": sum(importance.values()) / len(importance) if importance else 0,
                "avg_depth": sum(depths.values()) / len(depths) if depths else 0,
            },
        }

    def _build_dependency_graph(self) -> None:
        """Build dependency graph for analysis."""
        G = nx.DiGraph()

        # Add nodes
        for pattern in self.spec.patterns:
            G.add_node(pattern.id)

        # Add edges
        for relationship in self.spec.relationships:
            if relationship.type in ["builds_on", "prerequisite_for"]:
                G.add_edge(relationship.source, relationship.target)

        self._dependency_graph = G

    def _build_concept_graph(self) -> None:
        """Build concept relationship graph."""
        G = nx.Graph()

        # Add concept nodes
        for concept in self.spec.concepts:
            G.add_node(concept.name)

        # Add edges based on shared patterns
        concept_patterns: Dict[str, set] = defaultdict(set)
        for concept in self.spec.concepts:
            concept_patterns[concept.name].add(concept.pattern_id)
            concept_patterns[concept.name].update(concept.references)

        concepts_list = list(self.spec.concepts)
        for i, concept1 in enumerate(concepts_list):
            for concept2 in concepts_list[i + 1:]:
                patterns1 = concept_patterns.get(concept1.name, set())
                patterns2 = concept_patterns.get(concept2.name, set())
                if patterns1 & patterns2:
                    G.add_edge(concept1.name, concept2.name)

        self._concept_graph = G



