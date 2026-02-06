
"""Section exporter for FPF sections.


logger = get_logger(__name__)
This module provides functionality to export individual parts, pattern groups,
and concept clusters to separate JSON files.
"""

import json
from pathlib import Path

from ..core.models import Concept, Pattern, Relationship
from .section_manager import SectionManager


class SectionExporter:
    """Exporter for FPF sections."""

    def __init__(self, section_manager: SectionManager):
        """Initialize the section exporter.

        Args:
            section_manager: SectionManager instance
        """
        self.section_manager = section_manager

    def export_part(
        self, part_id: str, output_path: Path, include_metadata: bool = True
    ) -> None:
        """Export a part to JSON.

        Args:
            part_id: Part identifier
            output_path: Path to output JSON file
            include_metadata: Whether to include metadata
        """
        part_data = self.section_manager.extract_part(part_id)

        export_data = {
            "part": part_id,
            "patterns": [self._pattern_to_dict(p) for p in part_data["patterns"]],
            "concepts": [self._concept_to_dict(c) for c in part_data["concepts"]],
            "relationships": [
                self._relationship_to_dict(r) for r in part_data["relationships"]
            ],
        }

        if include_metadata:
            export_data["metadata"] = part_data["metadata"]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def export_pattern_group(
        self,
        pattern_ids: list[str],
        output_path: Path,
        include_dependencies: bool = True,
        include_metadata: bool = True,
    ) -> None:
        """Export a pattern group to JSON.

        Args:
            pattern_ids: List of pattern IDs
            output_path: Path to output JSON file
            include_dependencies: Whether to include dependent patterns
            include_metadata: Whether to include metadata
        """
        group_data = self.section_manager.extract_pattern_group(
            pattern_ids, include_dependencies=include_dependencies
        )

        export_data = {
            "pattern_ids": group_data["pattern_ids"],
            "patterns": [self._pattern_to_dict(p) for p in group_data["patterns"]],
            "concepts": [self._concept_to_dict(c) for c in group_data["concepts"]],
            "relationships": [
                self._relationship_to_dict(r) for r in group_data["relationships"]
            ],
        }

        if include_metadata:
            export_data["metadata"] = group_data["metadata"]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def export_single_pattern(
        self, pattern_id: str, output_path: Path, include_related: bool = False
    ) -> None:
        """Export a single pattern to JSON.

        Args:
            pattern_id: Pattern identifier
            output_path: Path to output JSON file
            include_related: Whether to include related patterns
        """
        pattern_ids = [pattern_id]
        if include_related:
            # Get related patterns
            pattern = next(
                (p for p in self.section_manager.spec.patterns if p.id == pattern_id),
                None,
            )
            if pattern:
                for dep_type, deps in pattern.dependencies.items():
                    pattern_ids.extend(deps)

        self.export_pattern_group(
            pattern_ids, output_path, include_dependencies=False, include_metadata=True
        )

    def export_concept_cluster(
        self,
        concept_names: list[str],
        output_path: Path,
        include_related_patterns: bool = True,
        include_metadata: bool = True,
    ) -> None:
        """Export a concept cluster to JSON.

        Args:
            concept_names: List of concept names
            output_path: Path to output JSON file
            include_related_patterns: Whether to include related patterns
            include_metadata: Whether to include metadata
        """
        cluster_data = self.section_manager.extract_concept_cluster(
            concept_names, include_related_patterns=include_related_patterns
        )

        export_data = {
            "concept_names": cluster_data["concept_names"],
            "concepts": [self._concept_to_dict(c) for c in cluster_data["concepts"]],
            "patterns": [self._pattern_to_dict(p) for p in cluster_data["patterns"]],
            "relationships": [
                self._relationship_to_dict(r) for r in cluster_data["relationships"]
            ],
        }

        if include_metadata:
            export_data["metadata"] = cluster_data["metadata"]

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def export_all_parts(self, output_dir: Path, include_metadata: bool = True) -> list[Path]:
        """Export all parts to separate JSON files.

        Args:
            output_dir: Directory to save JSON files
            include_metadata: Whether to include metadata

        Returns:
            List of exported file paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        exported_paths = []

        for part_id in self.section_manager.list_parts():
            output_path = output_dir / f"part-{part_id.lower()}.json"
            self.export_part(part_id, output_path, include_metadata=include_metadata)
            exported_paths.append(output_path)

        return exported_paths

    def _pattern_to_dict(self, pattern: Pattern) -> dict[str, any]:
        """Convert Pattern to dictionary."""
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

    def _concept_to_dict(self, concept: Concept) -> dict[str, any]:
        """Convert Concept to dictionary."""
        return {
            "name": concept.name,
            "definition": concept.definition,
            "pattern_id": concept.pattern_id,
            "type": concept.type,
            "references": concept.references,
            "aliases": concept.aliases,
            "metadata": concept.metadata,
        }

    def _relationship_to_dict(self, relationship: Relationship) -> dict[str, any]:
        """Convert Relationship to dictionary."""
        return {
            "source": relationship.source,
            "target": relationship.target,
            "type": relationship.type,
            "strength": relationship.strength,
            "description": relationship.description,
            "metadata": relationship.metadata,
        }

