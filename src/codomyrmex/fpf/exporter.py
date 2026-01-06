"""Exporter for FPF specification to JSON and other formats.

This module provides functionality to export FPF specifications
to structured formats for use in context engineering.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import FPFSpec, Pattern


class FPFExporter:
    """Exporter for FPF specifications."""

    def __init__(self):
        """Initialize the exporter."""

    def export_json(self, spec: FPFSpec, output_path: Path) -> None:
        """Export the complete specification to JSON.

        Args:
            spec: The FPFSpec object to export
            output_path: Path to output JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            "version": spec.version,
            "last_updated": spec.last_updated.isoformat() if spec.last_updated else None,
            "source_url": spec.source_url,
            "source_hash": spec.source_hash,
            "metadata": spec.metadata,
            "patterns": [self._pattern_to_dict(p) for p in spec.patterns],
            "concepts": [self._concept_to_dict(c) for c in spec.concepts],
            "relationships": [self._relationship_to_dict(r) for r in spec.relationships],
            "table_of_contents": spec.table_of_contents,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def export_patterns_json(self, patterns: List[Pattern], output_path: Path) -> None:
        """Export patterns to JSON.

        Args:
            patterns: List of Pattern objects
            output_path: Path to output JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            "patterns": [self._pattern_to_dict(p) for p in patterns],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def export_concepts_json(
        self, concepts: List[Any], output_path: Path
    ) -> None:  # Using Any to avoid circular import
        """Export concepts to JSON.

        Args:
            concepts: List of Concept objects
            output_path: Path to output JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            "concepts": [self._concept_to_dict(c) for c in concepts],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def export_for_context(self, spec: FPFSpec, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export specification data optimized for context engineering.

        Args:
            spec: The FPFSpec object
            filters: Optional filters (part, status, pattern_ids, etc.)

        Returns:
            Dictionary optimized for prompt context
        """
        patterns = spec.patterns
        concepts = spec.concepts
        relationships = spec.relationships

        # Apply filters
        if filters:
            if "part" in filters:
                patterns = [p for p in patterns if p.part == filters["part"]]
            if "status" in filters:
                patterns = [p for p in patterns if p.status == filters["status"]]
            if "pattern_ids" in filters:
                pattern_ids = set(filters["pattern_ids"])
                patterns = [p for p in patterns if p.id in pattern_ids]
                # Filter relationships to only include filtered patterns
                relationships = [
                    r
                    for r in relationships
                    if r.source in pattern_ids and r.target in pattern_ids
                ]

        # Build context-optimized structure
        context_data = {
            "summary": {
                "total_patterns": len(patterns),
                "total_concepts": len(concepts),
                "total_relationships": len(relationships),
            },
            "patterns": [
                {
                    "id": p.id,
                    "title": p.title,
                    "status": p.status,
                    "keywords": p.keywords,
                    "dependencies": p.dependencies,
                    "sections": {
                        k: v[:500] for k, v in p.sections.items()
                    },  # Truncate sections
                }
                for p in patterns
            ],
            "concepts": [
                {
                    "name": c.name,
                    "type": c.type,
                    "pattern_id": c.pattern_id,
                    "definition": c.definition[:200],  # Truncate definition
                }
                for c in concepts
            ],
            "relationships": [
                {
                    "source": r.source,
                    "target": r.target,
                    "type": r.type,
                }
                for r in relationships
            ],
        }

        return context_data

    def _pattern_to_dict(self, pattern: Pattern) -> Dict[str, Any]:
        """Convert a Pattern to a dictionary.

        Args:
            pattern: Pattern object

        Returns:
            Dictionary representation
        """
        return {
            "id": pattern.id,
            "title": pattern.title,
            "status": pattern.status,
            "keywords": pattern.keywords,
            "search_queries": pattern.search_queries,
            "dependencies": pattern.dependencies,
            "sections": pattern.sections,
            "content": pattern.content,
            "metadata": pattern.metadata,
            "part": pattern.part,
            "cluster": pattern.cluster,
        }

    def _concept_to_dict(self, concept: Any) -> Dict[str, Any]:  # Using Any to avoid circular import
        """Convert a Concept to a dictionary.

        Args:
            concept: Concept object

        Returns:
            Dictionary representation
        """
        return {
            "name": concept.name,
            "definition": concept.definition,
            "pattern_id": concept.pattern_id,
            "type": concept.type,
            "references": concept.references,
            "aliases": concept.aliases,
            "metadata": concept.metadata,
        }

    def _relationship_to_dict(self, relationship: Any) -> Dict[str, Any]:  # Using Any to avoid circular import
        """Convert a Relationship to a dictionary.

        Args:
            relationship: Relationship object

        Returns:
            Dictionary representation
        """
        return {
            "source": relationship.source,
            "target": relationship.target,
            "type": relationship.type,
            "strength": relationship.strength,
            "description": relationship.description,
            "metadata": relationship.metadata,
        }

