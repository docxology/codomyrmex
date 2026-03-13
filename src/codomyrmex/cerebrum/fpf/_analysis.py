from collections import defaultdict
from typing import Any

from codomyrmex.cerebrum import Case
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class FPFCombinatoricsAnalysisMixin:
    """Mixin for FPF structural combinatorics analysis."""

    def analyze_pattern_pairs(self) -> dict[str, Any]:
        """Analyze all pairs of patterns for relationships.

        Returns:
            Dictionary with pair analysis results
        """
        self.logger.info("Analyzing pattern pairs")

        pairs_analysis = []
        patterns = self.spec.patterns

        # Analyze all pairs (limit to first 50 patterns for performance)
        for i, pattern1 in enumerate(patterns[:50]):
            for pattern2 in patterns[i + 1 : 50]:
                # Create cases for both patterns
                case1 = self._pattern_to_case(pattern1)
                case2 = self._pattern_to_case(pattern2)

                # Compute similarity
                similarity = self.cerebrum.case_base.compute_similarity(case1, case2)

                # Check for explicit relationships
                has_relationship = any(
                    (rel.source == pattern1.id and rel.target == pattern2.id)
                    or (rel.source == pattern2.id and rel.target == pattern1.id)
                    for rel in self.spec.relationships
                )

                # Get relationship types
                relationship_types = []
                for rel in self.spec.relationships:
                    if (rel.source == pattern1.id and rel.target == pattern2.id) or (
                        rel.source == pattern2.id and rel.target == pattern1.id
                    ):
                        relationship_types.append(rel.type)

                pairs_analysis.append(
                    {
                        "pattern1": pattern1.id,
                        "pattern2": pattern2.id,
                        "similarity": similarity,
                        "has_relationship": has_relationship,
                        "relationship_types": relationship_types,
                        "shared_keywords": list(
                            set(pattern1.keywords) & set(pattern2.keywords)
                        ),
                        "shared_concepts": self._find_shared_concepts(
                            pattern1, pattern2
                        ),
                    }
                )

        # Sort by similarity
        pairs_analysis.sort(key=lambda x: x["similarity"], reverse=True)

        self.logger.info("Analyzed %s pattern pairs", len(pairs_analysis))
        return {
            "total_pairs": len(pairs_analysis),
            "high_similarity_pairs": [
                p for p in pairs_analysis if p["similarity"] > 0.7
            ][:20],
            "related_pairs": [p for p in pairs_analysis if p["has_relationship"]][:20],
            "all_pairs": pairs_analysis[:100],  # Top 100
        }

    def analyze_dependency_chains(self) -> dict[str, Any]:
        """Analyze dependency chains in FPF patterns.

        Returns:
            Dictionary with chain analysis
        """
        self.logger.info("Analyzing dependency chains")

        chains = []
        visited = set()

        def build_chain(
            pattern_id: str, current_chain: list[str], depth: int, max_depth: int = 5
        ):
            """Recursively build dependency chains."""
            if depth > max_depth or pattern_id in visited:
                return

            visited.add(pattern_id)
            current_chain.append(pattern_id)

            pattern = self.spec.get_pattern_by_id(pattern_id)
            if not pattern:
                return

            # Get dependencies
            dependencies = []
            for deps in pattern.dependencies.values():
                dependencies.extend(deps)

            if dependencies:
                for dep in dependencies[:3]:  # Limit branching
                    build_chain(dep, current_chain.copy(), depth + 1, max_depth)
            # End of chain
            elif len(current_chain) > 1:
                chains.append(current_chain.copy())

            visited.remove(pattern_id)

        # Build chains from all patterns
        for pattern in self.spec.patterns[:30]:  # Limit for performance
            build_chain(pattern.id, [], 0)

        # Analyze chains
        chain_analysis = []
        for chain in chains[:50]:  # Top 50 chains
            chain_patterns = [
                self.spec.get_pattern_by_id(pid)
                for pid in chain
                if self.spec.get_pattern_by_id(pid)
            ]
            if chain_patterns:
                importance_scores = self.fpf_analyzer.calculate_pattern_importance()
                chain_importance = sum(
                    importance_scores.get(pid, 0) for pid in chain
                ) / len(chain)

                chain_analysis.append(
                    {
                        "chain": chain,
                        "length": len(chain),
                        "avg_importance": chain_importance,
                        "parts": list({p.part for p in chain_patterns if p.part}),
                    }
                )

        chain_analysis.sort(key=lambda x: x["avg_importance"], reverse=True)

        self.logger.info("Found %s dependency chains", len(chains))
        return {
            "total_chains": len(chains),
            "longest_chains": sorted(chains, key=len, reverse=True)[:10],
            "most_important_chains": chain_analysis[:20],
        }

    def analyze_concept_cooccurrence(self) -> dict[str, Any]:
        """Analyze concept co-occurrence across patterns.

        Returns:
            Dictionary with co-occurrence analysis
        """
        self.logger.info("Analyzing concept co-occurrence")

        # Get co-occurrence matrix
        cooccurrence = self.term_analyzer.build_term_cooccurrence_matrix(self.spec)

        # Find strongest co-occurrences
        strong_pairs = []
        for term1, neighbors in cooccurrence.items():
            for term2, weight in neighbors.items():
                if weight >= 3:  # Minimum co-occurrence threshold
                    strong_pairs.append(
                        {
                            "term1": term1,
                            "term2": term2,
                            "cooccurrence_count": weight,
                        }
                    )

        strong_pairs.sort(key=lambda x: x["cooccurrence_count"], reverse=True)

        # Analyze concept clusters
        concept_clusters = self._find_concept_clusters(cooccurrence, min_weight=3)

        self.logger.info("Found %s strong concept co-occurrences", len(strong_pairs))
        return {
            "cooccurrence_matrix": {
                k: dict(v) for k, v in list(cooccurrence.items())[:50]
            },
            "strong_pairs": strong_pairs[:50],
            "concept_clusters": concept_clusters,
        }

    def analyze_cross_part_relationships(self) -> dict[str, Any]:
        """Analyze relationships between patterns in different parts.

        Returns:
            Dictionary with cross-part analysis
        """
        self.logger.info("Analyzing cross-part relationships")

        cross_part_rels = []
        part_patterns = defaultdict(list)

        # Group patterns by part
        for pattern in self.spec.patterns:
            part = pattern.part or "Other"
            part_patterns[part].append(pattern.id)

        # Find relationships across parts
        for relationship in self.spec.relationships:
            source_pattern = self.spec.get_pattern_by_id(relationship.source)
            target_pattern = self.spec.get_pattern_by_id(relationship.target)

            if source_pattern and target_pattern:
                source_part = source_pattern.part or "Other"
                target_part = target_pattern.part or "Other"

                if source_part != target_part:
                    cross_part_rels.append(
                        {
                            "source_part": source_part,
                            "target_part": target_part,
                            "source_pattern": relationship.source,
                            "target_pattern": relationship.target,
                            "relationship_type": relationship.type,
                        }
                    )

        # Group by part pairs
        part_pair_counts = defaultdict(int)
        for rel in cross_part_rels:
            pair = tuple(sorted([rel["source_part"], rel["target_part"]]))
            part_pair_counts[pair] += 1

        self.logger.info("Found %s cross-part relationships", len(cross_part_rels))
        return {
            "total_cross_part_relationships": len(cross_part_rels),
            "relationships": cross_part_rels[:50],
            "part_pair_counts": dict(
                sorted(part_pair_counts.items(), key=lambda x: x[1], reverse=True)
            ),
        }

    def _pattern_to_case(self, pattern) -> Case:
        """Convert FPF pattern to CEREBRUM case."""
        features = {
            "status": pattern.status,
            "part": pattern.part or "Other",
            "num_keywords": len(pattern.keywords),
            "num_dependencies": sum(
                len(deps) for deps in pattern.dependencies.values()
            ),
        }
        return Case(
            case_id=f"pattern_{pattern.id}",
            features=features,
            context={"pattern_id": pattern.id, "title": pattern.title},
        )

    def _find_shared_concepts(self, pattern1, pattern2) -> list[str]:
        """Find shared concepts between two patterns."""
        concepts1 = self.spec.get_concepts_by_pattern(pattern1.id)
        concepts2 = self.spec.get_concepts_by_pattern(pattern2.id)

        names1 = {c.name for c in concepts1}
        names2 = {c.name for c in concepts2}

        return list(names1 & names2)

    def _find_concept_clusters(
        self, cooccurrence: dict[str, dict[str, int]], min_weight: int = 3
    ) -> list[list[str]]:
        """Find clusters of co-occurring concepts."""
        try:
            import networkx as nx

            G = nx.Graph()

            for term1, neighbors in cooccurrence.items():
                for term2, weight in neighbors.items():
                    if weight >= min_weight:
                        G.add_edge(term1, term2, weight=weight)

            # Find connected components (clusters)
            clusters = list(nx.connected_components(G))

            return [sorted(cluster) for cluster in clusters if len(cluster) > 2]
        except ImportError as e:
            logger.debug("Optional networkx graph clustering unavailable: %s", e)
            return []
