from codomyrmex.logging_monitoring import get_logger
"""Context builder for prompt engineering.

logger = get_logger(__name__)
This module provides functionality to build context strings
from FPF specifications for use in prompt engineering.
"""

from typing import Dict, List, Optional

from .models import FPFSpec, Pattern


class ContextBuilder:
    """Builder for prompt engineering contexts from FPF specifications."""

    def __init__(self, spec: FPFSpec):
        """Initialize the context builder.

        Args:
            spec: The FPFSpec object to build contexts from
        """
        self.spec = spec

    def build_context_for_pattern(
        self, pattern_id: str, depth: int = 1, include_related: bool = True
    ) -> str:
        """Build context string for a specific pattern.

        Args:
            pattern_id: Pattern identifier
            depth: Depth of related patterns to include
            include_related: Whether to include related patterns

        Returns:
            Context string for prompt engineering
        """
        pattern = self.spec.get_pattern_by_id(pattern_id)
        if not pattern:
            return f"Pattern {pattern_id} not found."

        context_lines = [
            f"# FPF Pattern: {pattern.id} - {pattern.title}",
            f"Status: {pattern.status}",
            "",
        ]

        if pattern.keywords:
            context_lines.append(f"Keywords: {', '.join(pattern.keywords)}")
            context_lines.append("")

        if pattern.dependencies:
            context_lines.append("## Dependencies")
            for dep_type, deps in pattern.dependencies.items():
                if deps:
                    context_lines.append(f"- {dep_type}: {', '.join(deps)}")
            context_lines.append("")

        # Include main sections
        if "problem" in pattern.sections:
            context_lines.append("## Problem")
            context_lines.append(pattern.sections["problem"][:500])
            context_lines.append("")

        if "solution" in pattern.sections:
            context_lines.append("## Solution")
            context_lines.append(pattern.sections["solution"][:1000])
            context_lines.append("")

        # Include related patterns if requested
        if include_related and depth > 0:
            related = self._get_related_patterns(pattern_id, depth)
            if related:
                context_lines.append("## Related Patterns")
                for related_pattern in related[:5]:  # Limit to 5
                    context_lines.append(f"- {related_pattern.id}: {related_pattern.title}")
                context_lines.append("")

        return "\n".join(context_lines)

    def build_context_for_concept(self, concept: str) -> str:
        """Build context string for a specific concept.

        Args:
            concept: Concept name

        Returns:
            Context string for prompt engineering
        """
        # Find concept
        matching_concepts = [c for c in self.spec.concepts if concept.lower() in c.name.lower()]

        if not matching_concepts:
            return f"Concept '{concept}' not found."

        context_lines = [
            f"# FPF Concept: {concept}",
            "",
        ]

        for concept_obj in matching_concepts[:3]:  # Limit to 3 matches
            context_lines.append(f"## {concept_obj.name}")
            context_lines.append(f"Type: {concept_obj.type}")
            context_lines.append(f"Defined in: {concept_obj.pattern_id}")
            context_lines.append("")
            context_lines.append(f"Definition: {concept_obj.definition}")
            context_lines.append("")

            # Include pattern context
            pattern = self.spec.get_pattern_by_id(concept_obj.pattern_id)
            if pattern:
                context_lines.append(f"From Pattern {pattern.id}: {pattern.title}")
                context_lines.append("")

        return "\n".join(context_lines)

    def build_minimal_context(self, filters: Optional[Dict[str, any]] = None) -> str:
        """Build a minimal context with only essential information.

        Args:
            filters: Optional filters (part, status, pattern_ids)

        Returns:
            Minimal context string
        """
        patterns = self.spec.patterns

        # Apply filters
        if filters:
            if "part" in filters:
                patterns = [p for p in patterns if p.part == filters["part"]]
            if "status" in filters:
                patterns = [p for p in patterns if p.status == filters["status"]]
            if "pattern_ids" in filters:
                pattern_ids = set(filters["pattern_ids"])
                patterns = [p for p in patterns if p.id in pattern_ids]

        context_lines = [
            "# FPF Minimal Context",
            f"Patterns: {len(patterns)}",
            "",
        ]

        for pattern in patterns[:20]:  # Limit to 20 patterns
            context_lines.append(f"## {pattern.id}: {pattern.title}")
            context_lines.append(f"Status: {pattern.status}")
            if pattern.keywords:
                context_lines.append(f"Keywords: {', '.join(pattern.keywords[:5])}")
            context_lines.append("")

        return "\n".join(context_lines)

    def build_full_context(self) -> str:
        """Build a full context with all patterns and concepts.

        Returns:
            Full context string
        """
        context_lines = [
            "# FPF Full Specification Context",
            f"Version: {self.spec.version or 'Unknown'}",
            f"Total Patterns: {len(self.spec.patterns)}",
            f"Total Concepts: {len(self.spec.concepts)}",
            "",
            "## Patterns",
            "",
        ]

        for pattern in self.spec.patterns:
            context_lines.append(f"### {pattern.id}: {pattern.title}")
            context_lines.append(f"Status: {pattern.status}")
            if pattern.keywords:
                context_lines.append(f"Keywords: {', '.join(pattern.keywords)}")
            if pattern.dependencies:
                context_lines.append("Dependencies:")
                for dep_type, deps in pattern.dependencies.items():
                    if deps:
                        context_lines.append(f"  - {dep_type}: {', '.join(deps)}")
            context_lines.append("")

        context_lines.append("## Concepts")
        context_lines.append("")
        for concept in self.spec.concepts[:50]:  # Limit to 50 concepts
            context_lines.append(f"- **{concept.name}** ({concept.type}): {concept.definition[:100]}...")
            context_lines.append("")

        return "\n".join(context_lines)

    def _get_related_patterns(self, pattern_id: str, depth: int) -> List[Pattern]:
        """Get patterns related to the given pattern.

        Args:
            pattern_id: Pattern identifier
            depth: Relationship depth

        Returns:
            List of related Pattern objects
        """
        pattern = self.spec.get_pattern_by_id(pattern_id)
        if not pattern:
            return []

        related_ids = set()
        related_patterns = []

        # Collect related pattern IDs
        for dep_type, deps in pattern.dependencies.items():
            related_ids.update(deps)

        # Get related patterns
        for related_id in related_ids:
            related_pattern = self.spec.get_pattern_by_id(related_id)
            if related_pattern:
                related_patterns.append(related_pattern)

        return related_patterns[:10]  # Limit to 10

