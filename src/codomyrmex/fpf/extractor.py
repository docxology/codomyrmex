"""Extractor for FPF patterns, concepts, and relationships.

This module provides functionality to extract structured information
from parsed FPF specifications.
"""

import re
from typing import Dict, List, Optional

from .models import Concept, ConceptType, FPFSpec, Pattern, Relationship, RelationshipType


class FPFExtractor:
    """Extractor for FPF patterns, concepts, and relationships."""

    def __init__(self):
        """Initialize the extractor."""
        # Patterns for extracting U.Types and concepts
        self.u_type_pattern = re.compile(r"`?U\.(\w+)`?")
        self.concept_pattern = re.compile(
            r"`?([A-Z][a-zA-Z0-9]*(?:\.[A-Z][a-zA-Z0-9]*)*)`?"
        )

    def extract_patterns(self, spec: FPFSpec) -> List[Pattern]:
        """Extract all patterns from the specification.

        Args:
            spec: The FPFSpec object containing parsed patterns

        Returns:
            List of Pattern objects (same as input, but with enhanced metadata)
        """
        # Patterns are already extracted by the parser
        # This method can be used for post-processing
        return spec.patterns

    def extract_concepts(self, spec: FPFSpec) -> List[Concept]:
        """Extract all concepts from the specification.

        Args:
            spec: The FPFSpec object

        Returns:
            List of Concept objects
        """
        concepts = []
        concept_names = set()

        for pattern in spec.patterns:
            # Extract U.Types
            u_types = self._extract_u_types(pattern)
            for u_type in u_types:
                if u_type not in concept_names:
                    concepts.append(
                        Concept(
                            name=f"U.{u_type}",
                            definition=self._extract_definition(pattern, f"U.{u_type}"),
                            pattern_id=pattern.id,
                            type=ConceptType.U_TYPE,
                            references=[],
                        )
                    )
                    concept_names.add(u_type)

            # Extract other concepts mentioned in titles and content
            other_concepts = self._extract_other_concepts(pattern)
            for concept_name, concept_type in other_concepts:
                if concept_name not in concept_names:
                    concepts.append(
                        Concept(
                            name=concept_name,
                            definition=self._extract_definition(pattern, concept_name),
                            pattern_id=pattern.id,
                            type=concept_type,
                            references=[],
                        )
                    )
                    concept_names.add(concept_name)

        # Update references
        for concept in concepts:
            concept.references = self._find_references(spec, concept.name)

        return concepts

    def extract_relationships(self, spec: FPFSpec) -> List[Relationship]:
        """Extract relationships between patterns.

        Args:
            spec: The FPFSpec object

        Returns:
            List of Relationship objects
        """
        relationships = []

        for pattern in spec.patterns:
            # Extract builds_on relationships
            if "builds_on" in pattern.dependencies:
                for target in pattern.dependencies["builds_on"]:
                    relationships.append(
                        Relationship(
                            source=pattern.id,
                            target=target,
                            type=RelationshipType.BUILDS_ON,
                        )
                    )

            # Extract prerequisite_for relationships
            if "prerequisite_for" in pattern.dependencies:
                for target in pattern.dependencies["prerequisite_for"]:
                    relationships.append(
                        Relationship(
                            source=pattern.id,
                            target=target,
                            type=RelationshipType.PREREQUISITE_FOR,
                        )
                    )

            # Extract coordinates_with relationships
            if "coordinates_with" in pattern.dependencies:
                for target in pattern.dependencies["coordinates_with"]:
                    relationships.append(
                        Relationship(
                            source=pattern.id,
                            target=target,
                            type=RelationshipType.COORDINATES_WITH,
                        )
                    )

            # Extract constrains relationships
            if "constrains" in pattern.dependencies:
                for target in pattern.dependencies["constrains"]:
                    relationships.append(
                        Relationship(
                            source=pattern.id,
                            target=target,
                            type=RelationshipType.CONSTRAINS,
                        )
                    )

            # Extract refines relationships
            if "refines" in pattern.dependencies:
                for target in pattern.dependencies["refines"]:
                    relationships.append(
                        Relationship(
                            source=pattern.id,
                            target=target,
                            type=RelationshipType.REFINES,
                        )
                    )

            # Extract informs relationships
            if "informs" in pattern.dependencies:
                for target in pattern.dependencies["informs"]:
                    relationships.append(
                        Relationship(
                            source=pattern.id,
                            target=target,
                            type=RelationshipType.INFORMS,
                        )
                    )

            # Extract used_by relationships (reverse of builds_on)
            if "used_by" in pattern.dependencies:
                for target in pattern.dependencies["used_by"]:
                    relationships.append(
                        Relationship(
                            source=target,
                            target=pattern.id,
                            type=RelationshipType.USED_BY,
                        )
                    )

        return relationships

    def extract_keywords(self, spec: FPFSpec) -> Dict[str, List[str]]:
        """Extract keywords indexed by pattern ID.

        Args:
            spec: The FPFSpec object

        Returns:
            Dictionary mapping pattern IDs to keyword lists
        """
        keywords = {}
        for pattern in spec.patterns:
            keywords[pattern.id] = pattern.keywords
        return keywords

    def extract_dependencies(self, spec: FPFSpec) -> Dict[str, Dict[str, List[str]]]:
        """Extract dependency graph.

        Args:
            spec: The FPFSpec object

        Returns:
            Dictionary mapping pattern IDs to dependency dictionaries
        """
        dependencies = {}
        for pattern in spec.patterns:
            dependencies[pattern.id] = pattern.dependencies
        return dependencies

    def _extract_u_types(self, pattern: Pattern) -> List[str]:
        """Extract U.Type names from a pattern.

        Args:
            pattern: Pattern to extract from

        Returns:
            List of U.Type names (without the U. prefix)
        """
        u_types = set()
        content = pattern.content + " " + pattern.title

        # Find all U.Type references
        matches = self.u_type_pattern.findall(content)
        u_types.update(matches)

        return list(u_types)

    def _extract_other_concepts(self, pattern: Pattern) -> List[tuple[str, ConceptType]]:
        """Extract other concepts (not U.Types) from a pattern.

        Args:
            pattern: Pattern to extract from

        Returns:
            List of tuples (concept_name, concept_type)
        """
        concepts = []
        content = pattern.content.lower()

        # Check for architheory mentions
        if "architheory" in content or "-cal" in content.lower() or "-chr" in content.lower():
            # Extract architheory names
            archi_matches = re.findall(r"([A-Z][a-z]*-[A-Z]+)", pattern.content)
            for match in archi_matches:
                concepts.append((match, ConceptType.ARCHITHEORY))

        # Check for mechanism mentions
        if "mechanism" in content:
            mech_matches = re.findall(r"([A-Z][a-zA-Z]*\s+[Mm]echanism)", pattern.content)
            for match in mech_matches:
                concepts.append((match.strip(), ConceptType.MECHANISM))

        # Check for principle mentions
        if "principle" in content or "pillar" in content:
            principle_matches = re.findall(
                r"([A-Z][a-zA-Z\s-]+(?:Principle|Pillar))", pattern.content
            )
            for match in principle_matches:
                concepts.append((match.strip(), ConceptType.PRINCIPLE))

        return concepts

    def _extract_definition(self, pattern: Pattern, concept_name: str) -> str:
        """Extract definition for a concept from a pattern.

        Args:
            pattern: Pattern containing the concept
            concept_name: Name of the concept

        Returns:
            Definition string (or empty if not found)
        """
        # Look in solution section first
        if "solution" in pattern.sections:
            solution = pattern.sections["solution"]
            # Try to find definition near the concept name
            lines = solution.split("\n")
            for i, line in enumerate(lines):
                if concept_name in line:
                    # Get next few lines as definition
                    definition_lines = lines[i : i + 3]
                    return "\n".join(definition_lines).strip()

        # Fallback to title or first section
        if pattern.title:
            return f"Defined in pattern {pattern.id}: {pattern.title}"

        return ""

    def _find_references(self, spec: FPFSpec, concept_name: str) -> List[str]:
        """Find patterns that reference a concept.

        Args:
            spec: The FPFSpec object
            concept_name: Name of the concept

        Returns:
            List of pattern IDs that reference the concept
        """
        references = []
        for pattern in spec.patterns:
            if concept_name in pattern.content or concept_name in pattern.title:
                if pattern.id not in references:
                    references.append(pattern.id)
        return references


