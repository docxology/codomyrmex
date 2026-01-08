from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from enum import Enum
from pydantic import BaseModel, Field, field_validator
from pydantic import BaseModel, Field, validator as field_validator





























"""Data models for FPF specification parsing and analysis.

This module defines Pydantic models for representing the First Principles
Framework specification structure, including patterns, concepts, relationships,
and the overall specification.
"""


try:
except ImportError:
    # Fallback for older Pydantic versions


class PatternStatus(str, Enum):
    """Status values for FPF patterns."""

    STABLE = "Stable"
    DRAFT = "Draft"
    STUB = "Stub"
    NEW = "New"


class RelationshipType(str, Enum):
    """Types of relationships between patterns."""

    BUILDS_ON = "builds_on"
    PREREQUISITE_FOR = "prerequisite_for"
    COORDINATES_WITH = "coordinates_with"
    CONSTRAINS = "constrains"
    REFINES = "refines"
    INFORMS = "informs"
    USED_BY = "used_by"
    SPECIALIZED_BY = "specialized_by"
    INSTANCES = "instances"


class ConceptType(str, Enum):
    """Types of concepts in FPF."""

    U_TYPE = "U.Type"
    MECHANISM = "Mechanism"
    ARCHITHEORY = "Architheory"
    PRINCIPLE = "Principle"
    PATTERN = "Pattern"
    TERM = "Term"
    OPERATOR = "Operator"
    OTHER = "Other"


class Pattern(BaseModel):
    """Represents a single FPF pattern.

    Patterns are the core building blocks of FPF, each with a unique ID,
    title, status, and structured content sections.
    """

    id: str = Field(..., description="Pattern identifier (e.g., 'A.1', 'A.2.1')")
    title: str = Field(..., description="Pattern title")
    status: PatternStatus = Field(..., description="Pattern status")
    keywords: List[str] = Field(default_factory=list, description="Keywords for search")
    search_queries: List[str] = Field(
        default_factory=list, description="Example search queries"
    )
    dependencies: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Dependency relationships (builds_on, prerequisite_for, etc.)",
    )
    sections: Dict[str, str] = Field(
        default_factory=dict,
        description="Pattern sections (Problem, Solution, etc.)",
    )
    content: str = Field(..., description="Full markdown content of the pattern")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    part: Optional[str] = Field(None, description="Part identifier (A, B, C, etc.)")
    cluster: Optional[str] = Field(None, description="Cluster identifier if applicable")

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class Concept(BaseModel):
    """Represents a concept defined in FPF.

    Concepts are terms, types, mechanisms, or other defined entities
    that appear throughout the FPF specification.
    """

    name: str = Field(..., description="Concept name")
    definition: str = Field(..., description="Concept definition or description")
    pattern_id: str = Field(..., description="Pattern ID where concept is defined")
    type: ConceptType = Field(..., description="Type of concept")
    references: List[str] = Field(
        default_factory=list, description="Other patterns/concepts that reference this"
    )
    aliases: List[str] = Field(
        default_factory=list, description="Alternative names for the concept"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class Relationship(BaseModel):
    """Represents a relationship between patterns or concepts.

    Relationships capture how different parts of FPF relate to each other,
    such as dependencies, constraints, or coordination.
    """

    source: str = Field(..., description="Source pattern/concept ID")
    target: str = Field(..., description="Target pattern/concept ID")
    type: RelationshipType = Field(..., description="Type of relationship")
    strength: Optional[str] = Field(
        None, description="Relationship strength (optional)"
    )
    description: Optional[str] = Field(
        None, description="Human-readable description of the relationship"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class FPFSpec(BaseModel):
    """Represents the complete FPF specification.

    This is the root model containing all patterns, concepts, relationships,
    and metadata for the entire FPF specification.
    """

    version: Optional[str] = Field(None, description="FPF specification version")
    last_updated: Optional[Union[datetime, str]] = Field(
        None, description="Last update timestamp"
    )

    @field_validator("last_updated", mode="before")
    @classmethod
    def parse_last_updated(cls, v):
        """Parse last_updated from string if needed."""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                return None
        return v
    source_url: Optional[str] = Field(None, description="Source URL or path")
    source_hash: Optional[str] = Field(None, description="Content hash for versioning")
    patterns: List[Pattern] = Field(
        default_factory=list, description="All patterns in the specification"
    )
    concepts: List[Concept] = Field(
        default_factory=list, description="All concepts in the specification"
    )
    relationships: List[Relationship] = Field(
        default_factory=list, description="All relationships in the specification"
    )
    table_of_contents: Dict[str, Any] = Field(
        default_factory=dict, description="Table of contents structure"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional specification metadata"
    )

    def get_pattern_by_id(self, pattern_id: str) -> Optional[Pattern]:
        """Get a pattern by its ID."""
        for pattern in self.patterns:
            if pattern.id == pattern_id:
                return pattern
        return None

    def get_concepts_by_pattern(self, pattern_id: str) -> List[Concept]:
        """Get all concepts defined in a specific pattern."""
        return [c for c in self.concepts if c.pattern_id == pattern_id]

    def get_relationships_by_source(self, source_id: str) -> List[Relationship]:
        """Get all relationships where the given ID is the source."""
        return [r for r in self.relationships if r.source == source_id]

    def get_relationships_by_target(self, target_id: str) -> List[Relationship]:
        """Get all relationships where the given ID is the target."""
        return [r for r in self.relationships if r.target == target_id]


class FPFIndex(BaseModel):
    """Search index for FPF patterns and concepts.

    Provides fast lookup and search capabilities over the FPF specification.
    """

    pattern_index: Dict[str, Pattern] = Field(
        default_factory=dict, description="Pattern ID to Pattern mapping"
    )
    concept_index: Dict[str, List[Concept]] = Field(
        default_factory=dict, description="Concept name to Concepts mapping"
    )
    keyword_index: Dict[str, List[str]] = Field(
        default_factory=dict, description="Keyword to pattern IDs mapping"
    )
    title_index: Dict[str, List[str]] = Field(
        default_factory=dict, description="Title words to pattern IDs mapping"
    )
    relationship_graph: Dict[str, List[str]] = Field(
        default_factory=dict, description="Adjacency list for relationships"
    )

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get a pattern by ID."""
        return self.pattern_index.get(pattern_id)

    def search_patterns(
        self, query: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Pattern]:
        """Search patterns by query string."""
        query_lower = query.lower()
        matches = set()

        # Search in titles
        for pattern_id, pattern in self.pattern_index.items():
            if query_lower in pattern.title.lower():
                matches.add(pattern_id)

        # Search in keywords
        for keyword, pattern_ids in self.keyword_index.items():
            if query_lower in keyword.lower():
                matches.update(pattern_ids)

        # Search in content (basic)
        for pattern_id, pattern in self.pattern_index.items():
            if query_lower in pattern.content.lower()[:1000]:  # Limit search
                matches.add(pattern_id)

        # Apply filters
        results = [self.pattern_index[pid] for pid in matches if pid in self.pattern_index]
        if filters:
            if "status" in filters:
                results = [r for r in results if r.status == filters["status"]]
            if "part" in filters:
                results = [r for r in results if r.part == filters["part"]]

        return results

    def get_related_patterns(self, pattern_id: str, depth: int = 1) -> List[Pattern]:
        """Get patterns related to the given pattern through relationships."""
        visited = set()
        to_visit = [(pattern_id, 0)]
        related = []

        while to_visit:
            current_id, current_depth = to_visit.pop(0)
            if current_id in visited or current_depth > depth:
                continue

            visited.add(current_id)
            if current_id != pattern_id:
                pattern = self.get_pattern(current_id)
                if pattern:
                    related.append(pattern)

            # Add neighbors
            neighbors = self.relationship_graph.get(current_id, [])
            for neighbor in neighbors:
                if neighbor not in visited:
                    to_visit.append((neighbor, current_depth + 1))

        return related

