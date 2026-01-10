from codomyrmex.logging_monitoring import get_logger
"""Section manager for extracting and managing FPF sections.

This module provides functionality to extract individual parts, pattern groups,
and concept clusters from FPF specifications.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Set

from .models import FPFSpec, Pattern, Concept, Relationship


class SectionManager:
    """Manager for FPF section extraction and management."""

    def __init__(self, spec: FPFSpec):
        """Initialize the section manager.

        Args:
            spec: The FPFSpec object to manage
        """
        self.spec = spec

    def extract_part(self, part_id: str) -> Dict[str, any]:
        """Extract all patterns, concepts, and relationships for a specific part.

        Args:
            part_id: Part identifier (A, B, C, etc.)

        Returns:
            Dictionary containing patterns, concepts, and relationships for the part
        """
        # Filter patterns by part
        part_patterns = [p for p in self.spec.patterns if p.part == part_id]

        # Get pattern IDs
        pattern_ids = {p.id for p in part_patterns}

        # Filter concepts by pattern IDs
        part_concepts = [
            c for c in self.spec.concepts if c.pattern_id in pattern_ids
        ]

        # Filter relationships where both source and target are in this part
        part_relationships = [
            r
            for r in self.spec.relationships
            if r.source in pattern_ids and r.target in pattern_ids
        ]

        return {
            "part": part_id,
            "patterns": part_patterns,
            "concepts": part_concepts,
            "relationships": part_relationships,
            "metadata": {
                "pattern_count": len(part_patterns),
                "concept_count": len(part_concepts),
                "relationship_count": len(part_relationships),
            },
        }

    def extract_pattern_group(
        self, pattern_ids: List[str], include_dependencies: bool = True
    ) -> Dict[str, any]:
        """Extract a group of patterns and their related content.

        Args:
            pattern_ids: List of pattern IDs to extract
            include_dependencies: Whether to include dependent patterns

        Returns:
            Dictionary containing patterns, concepts, and relationships
        """
        pattern_id_set = set(pattern_ids)

        # Add dependencies if requested
        if include_dependencies:
            for relationship in self.spec.relationships:
                if relationship.source in pattern_id_set:
                    pattern_id_set.add(relationship.target)
                if relationship.target in pattern_id_set:
                    pattern_id_set.add(relationship.source)

        # Filter patterns
        group_patterns = [p for p in self.spec.patterns if p.id in pattern_id_set]

        # Filter concepts
        group_concepts = [
            c for c in self.spec.concepts if c.pattern_id in pattern_id_set
        ]

        # Filter relationships
        group_relationships = [
            r
            for r in self.spec.relationships
            if r.source in pattern_id_set and r.target in pattern_id_set
        ]

        return {
            "pattern_ids": sorted(list(pattern_id_set)),
            "patterns": group_patterns,
            "concepts": group_concepts,
            "relationships": group_relationships,
            "metadata": {
                "pattern_count": len(group_patterns),
                "concept_count": len(group_concepts),
                "relationship_count": len(group_relationships),
            },
        }

    def extract_concept_cluster(
        self, concept_names: List[str], include_related_patterns: bool = True
    ) -> Dict[str, any]:
        """Extract a cluster of concepts and their related patterns.

        Args:
            concept_names: List of concept names to extract
            include_related_patterns: Whether to include patterns that define/use these concepts

        Returns:
            Dictionary containing concepts, patterns, and relationships
        """
        concept_name_set = set(concept_names)

        # Filter concepts
        cluster_concepts = [
            c for c in self.spec.concepts if c.name in concept_name_set
        ]

        # Get related pattern IDs
        pattern_ids = {c.pattern_id for c in cluster_concepts}
        if include_related_patterns:
            # Add patterns that reference these concepts
            for concept in cluster_concepts:
                pattern_ids.update(concept.references)

        # Filter patterns
        cluster_patterns = [p for p in self.spec.patterns if p.id in pattern_ids]

        # Filter relationships
        cluster_relationships = [
            r
            for r in self.spec.relationships
            if r.source in pattern_ids and r.target in pattern_ids
        ]

        return {
            "concept_names": sorted(list(concept_name_set)),
            "concepts": cluster_concepts,
            "patterns": cluster_patterns,
            "relationships": cluster_relationships,
            "metadata": {
                "concept_count": len(cluster_concepts),
                "pattern_count": len(cluster_patterns),
                "relationship_count": len(cluster_relationships),
            },
        }

    def extract_relationship_subset(
        self, relationship_types: List[str], include_patterns: bool = True
    ) -> Dict[str, any]:
        """Extract relationships of specific types.

        Args:
            relationship_types: List of relationship types to extract
            include_patterns: Whether to include related patterns

        Returns:
            Dictionary containing relationships and optionally patterns
        """
        relationship_type_set = set(relationship_types)

        # Filter relationships
        subset_relationships = [
            r for r in self.spec.relationships if r.type in relationship_type_set
        ]

        result = {
            "relationship_types": sorted(list(relationship_type_set)),
            "relationships": subset_relationships,
        }

        if include_patterns:
            # Get pattern IDs from relationships
            pattern_ids = set()
            for rel in subset_relationships:
                pattern_ids.add(rel.source)
                pattern_ids.add(rel.target)

            # Filter patterns
            subset_patterns = [p for p in self.spec.patterns if p.id in pattern_ids]
            result["patterns"] = subset_patterns
            result["metadata"] = {
                "relationship_count": len(subset_relationships),
                "pattern_count": len(subset_patterns),
            }
        else:
            result["metadata"] = {
                "relationship_count": len(subset_relationships),
            }

        return result

    def list_parts(self) -> List[str]:
        """List all part identifiers in the specification.

        Returns:
            List of part identifiers
        """
        parts = {p.part for p in self.spec.patterns if p.part}
        return sorted(list(parts))

    def list_pattern_groups(self, by_part: bool = False) -> Dict[str, List[str]]:
        """List pattern groups.

        Args:
            by_part: If True, group by part; if False, return flat list

        Returns:
            Dictionary mapping group names to pattern ID lists
        """
        if by_part:
            groups: Dict[str, List[str]] = {}
            for pattern in self.spec.patterns:
                part = pattern.part or "Other"
                if part not in groups:
                    groups[part] = []
                groups[part].append(pattern.id)
            return groups
        else:
            return {"all": [p.id for p in self.spec.patterns]}

    def get_section_statistics(self) -> Dict[str, any]:
        """Get statistics about sections in the specification.

        Returns:
            Dictionary with section statistics
        """
        parts = self.list_parts()
        part_stats = {}

        for part in parts:
            part_data = self.extract_part(part)
            part_stats[part] = part_data["metadata"]

        return {
            "total_parts": len(parts),
            "total_patterns": len(self.spec.patterns),
            "total_concepts": len(self.spec.concepts),
            "total_relationships": len(self.spec.relationships),
            "part_statistics": part_stats,
        }

