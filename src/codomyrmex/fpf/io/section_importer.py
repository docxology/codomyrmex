
"""Section importer for merging FPF sections.


logger = get_logger(__name__)
This module provides functionality to import and merge sections
from separate JSON files into a unified FPF specification.
"""

import json
from pathlib import Path

from ..core.models import (
    Concept,
    ConceptType,
    FPFSpec,
    Pattern,
    PatternStatus,
    Relationship,
    RelationshipType,
)


class SectionImporter:
    """Importer for FPF sections."""

    def __init__(self, base_spec: FPFSpec | None = None):
        """Initialize the section importer.

        Args:
            base_spec: Optional base specification to merge into
        """
        self.base_spec = base_spec or FPFSpec()

    def import_part(self, json_path: Path) -> FPFSpec:
        """Import a part from JSON and merge into specification.

        Args:
            json_path: Path to JSON file containing part data

        Returns:
            Updated FPFSpec with imported part
        """
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        # Import patterns
        patterns = [self._dict_to_pattern(p) for p in data.get("patterns", [])]

        # Import concepts
        concepts = [self._dict_to_concept(c) for c in data.get("concepts", [])]

        # Import relationships
        relationships = [
            self._dict_to_relationship(r) for r in data.get("relationships", [])
        ]

        # Merge into base spec
        return self._merge_into_spec(patterns, concepts, relationships)

    def import_pattern_group(self, json_path: Path) -> FPFSpec:
        """Import a pattern group from JSON.

        Args:
            json_path: Path to JSON file

        Returns:
            Updated FPFSpec
        """
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        patterns = [self._dict_to_pattern(p) for p in data.get("patterns", [])]
        concepts = [self._dict_to_concept(c) for c in data.get("concepts", [])]
        relationships = [
            self._dict_to_relationship(r) for r in data.get("relationships", [])
        ]

        return self._merge_into_spec(patterns, concepts, relationships)

    def import_single_pattern(self, json_path: Path) -> FPFSpec:
        """Import a single pattern from JSON.

        Args:
            json_path: Path to JSON file

        Returns:
            Updated FPFSpec
        """
        return self.import_pattern_group(json_path)

    def merge_specs(self, *specs: FPFSpec) -> FPFSpec:
        """Merge multiple specifications into one.

        Args:
            *specs: Variable number of FPFSpec objects to merge

        Returns:
            Merged FPFSpec
        """
        merged = FPFSpec()

        for spec in specs:
            # Merge patterns (avoid duplicates)
            existing_ids = {p.id for p in merged.patterns}
            merged.patterns.extend(
                [p for p in spec.patterns if p.id not in existing_ids]
            )

            # Merge concepts (avoid duplicates)
            existing_names = {c.name for c in merged.concepts}
            merged.concepts.extend(
                [c for c in spec.concepts if c.name not in existing_names]
            )

            # Merge relationships (avoid duplicates)
            existing_rels = {
                (r.source, r.target, r.type) for r in merged.relationships
            }
            merged.relationships.extend(
                [
                    r
                    for r in spec.relationships
                    if (r.source, r.target, r.type) not in existing_rels
                ]
            )

        return merged

    def _merge_into_spec(
        self, patterns: list[Pattern], concepts: list[Concept], relationships: list[Relationship]
    ) -> FPFSpec:
        """Merge data into base specification.

        Args:
            patterns: Patterns to merge
            concepts: Concepts to merge
            relationships: Relationships to merge

        Returns:
            Updated FPFSpec
        """
        # Create new spec from base
        merged = FPFSpec(
            version=self.base_spec.version,
            source_url=self.base_spec.source_url,
            patterns=list(self.base_spec.patterns),
            concepts=list(self.base_spec.concepts),
            relationships=list(self.base_spec.relationships),
        )

        # Merge patterns
        existing_ids = {p.id for p in merged.patterns}
        merged.patterns.extend([p for p in patterns if p.id not in existing_ids])

        # Merge concepts
        existing_names = {c.name for c in merged.concepts}
        merged.concepts.extend([c for c in concepts if c.name not in existing_names])

        # Merge relationships
        existing_rels = {(r.source, r.target, r.type) for r in merged.relationships}
        merged.relationships.extend(
            [r for r in relationships if (r.source, r.target, r.type) not in existing_rels]
        )

        return merged

    def _dict_to_pattern(self, data: dict) -> Pattern:
        """Convert dictionary to Pattern object."""
        return Pattern(
            id=data["id"],
            title=data["title"],
            status=PatternStatus(data.get("status", "Stable")),
            keywords=data.get("keywords", []),
            search_queries=data.get("search_queries", []),
            dependencies=data.get("dependencies", {}),
            sections=data.get("sections", {}),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            part=data.get("part"),
            cluster=data.get("cluster"),
        )

    def _dict_to_concept(self, data: dict) -> Concept:
        """Convert dictionary to Concept object."""
        return Concept(
            name=data["name"],
            definition=data.get("definition", ""),
            pattern_id=data["pattern_id"],
            type=ConceptType(data.get("type", "Other")),
            references=data.get("references", []),
            aliases=data.get("aliases", []),
            metadata=data.get("metadata", {}),
        )

    def _dict_to_relationship(self, data: dict) -> Relationship:
        """Convert dictionary to Relationship object."""
        return Relationship(
            source=data["source"],
            target=data["target"],
            type=RelationshipType(data.get("type", "builds_on")),
            strength=data.get("strength"),
            description=data.get("description"),
            metadata=data.get("metadata", {}),
        )

