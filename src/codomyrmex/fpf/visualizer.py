from codomyrmex.logging_monitoring import get_logger
"""Visualizer for FPF specification.

"""Core functionality module

This module provides visualizer functionality including:
- 5 functions: __init__, visualize_pattern_hierarchy, visualize_dependencies...
- 1 classes: FPFVisualizer

Usage:
    # Example usage here
"""
logger = get_logger(__name__)
This module provides functionality to generate visualizations
and reports from FPF specifications.
"""

from pathlib import Path
from typing import List, Optional

from .models import FPFSpec, Pattern


class FPFVisualizer:
    """Visualizer for FPF specifications."""

    def __init__(self):
        """Initialize the visualizer."""
        self.config: dict[str, Any] = {}
        self.theme: str = "default"

    def visualize_pattern_hierarchy(self, patterns: List[Pattern]) -> str:
        """Generate a Mermaid diagram of the pattern hierarchy.

        Args:
            patterns: List of Pattern objects

        Returns:
            Mermaid diagram string
        """
        # Group patterns by part
        parts: dict[str, List[Pattern]] = {}
        for pattern in patterns:
            part = pattern.part or "Other"
            if part not in parts:
                parts[part] = []
            parts[part].append(pattern)

        mermaid_lines = ["graph TD"]
        node_ids = {}

        # Create nodes
        for i, pattern in enumerate(patterns):
            node_id = f"P{i}"
            node_ids[pattern.id] = node_id
            title_short = pattern.title[:30] + "..." if len(pattern.title) > 30 else pattern.title
            mermaid_lines.append(f'    {node_id}["{pattern.id}: {title_short}"]')

        # Create edges based on dependencies
        for pattern in patterns:
            source_id = node_ids[pattern.id]
            if "builds_on" in pattern.dependencies:
                for target in pattern.dependencies["builds_on"]:
                    if target in node_ids:
                        target_id = node_ids[target]
                        mermaid_lines.append(f"    {source_id} -->|builds_on| {target_id}")

        return "\n".join(mermaid_lines)

    def visualize_dependencies(self, patterns: List[Pattern]) -> str:
        """Generate a Mermaid diagram of pattern dependencies.

        Args:
            patterns: List of Pattern objects

        Returns:
            Mermaid diagram string
        """
        mermaid_lines = ["graph LR"]
        node_ids = {}

        # Create nodes
        for i, pattern in enumerate(patterns):
            node_id = f"P{i}"
            node_ids[pattern.id] = node_id
            mermaid_lines.append(f'    {node_id}["{pattern.id}"]')

        # Create edges for all dependency types
        for pattern in patterns:
            source_id = node_ids[pattern.id]
            for dep_type, deps in pattern.dependencies.items():
                for target in deps:
                    if target in node_ids:
                        target_id = node_ids[target]
                        # Use different arrow styles for different relationship types
                        arrow_style = "-->"
                        if dep_type == "prerequisite_for":
                            arrow_style = "-.->"
                        elif dep_type == "coordinates_with":
                            arrow_style = "==>"
                        mermaid_lines.append(f'    {source_id} {arrow_style}|{dep_type}| {target_id}')

        return "\n".join(mermaid_lines)

    def generate_report(self, spec: FPFSpec, output_path: Path) -> None:
        """Generate a comprehensive report of the FPF specification.

        Args:
            spec: The FPFSpec object
            output_path: Path to output report file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report_lines = [
            "# FPF Specification Report",
            "",
            f"**Version:** {spec.version or 'Unknown'}",
            f"**Source:** {spec.source_url or 'Unknown'}",
            f"**Total Patterns:** {len(spec.patterns)}",
            f"**Total Concepts:** {len(spec.concepts)}",
            f"**Total Relationships:** {len(spec.relationships)}",
            "",
            "## Patterns by Status",
            "",
        ]

        # Group patterns by status
        by_status: dict[str, List[Pattern]] = {}
        for pattern in spec.patterns:
            status = pattern.status
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(pattern)

        for status, patterns_list in sorted(by_status.items()):
            report_lines.append(f"### {status} ({len(patterns_list)})")
            for pattern in patterns_list:
                report_lines.append(f"- {pattern.id}: {pattern.title}")
            report_lines.append("")

        # Patterns by part
        report_lines.append("## Patterns by Part")
        report_lines.append("")
        by_part: dict[str, List[Pattern]] = {}
        for pattern in spec.patterns:
            part = pattern.part or "Other"
            if part not in by_part:
                by_part[part] = []
            by_part[part].append(pattern)

        for part, patterns_list in sorted(by_part.items()):
            report_lines.append(f"### Part {part} ({len(patterns_list)})")
            for pattern in patterns_list:
                report_lines.append(f"- {pattern.id}: {pattern.title}")
            report_lines.append("")

        # Top concepts
        report_lines.append("## Top Concepts")
        report_lines.append("")
        for concept in spec.concepts[:20]:  # Top 20
            report_lines.append(f"- **{concept.name}** ({concept.type}) - {concept.definition[:100]}...")
            report_lines.append("")

        output_path.write_text("\n".join(report_lines), encoding="utf-8")

    def create_pattern_card(self, pattern: Pattern) -> str:
        """Create a markdown card for a pattern.

        Args:
            pattern: Pattern object

        Returns:
            Markdown string representing the pattern card
        """
        card_lines = [
            f"## {pattern.id} - {pattern.title}",
            "",
            f"**Status:** {pattern.status}",
            "",
        ]

        if pattern.keywords:
            card_lines.append("**Keywords:** " + ", ".join(pattern.keywords))
            card_lines.append("")

        if pattern.dependencies:
            card_lines.append("### Dependencies")
            for dep_type, deps in pattern.dependencies.items():
                if deps:
                    card_lines.append(f"- **{dep_type.replace('_', ' ').title()}:** {', '.join(deps)}")
            card_lines.append("")

        if pattern.sections:
            card_lines.append("### Sections")
            for section_name, section_content in pattern.sections.items():
                if section_content:
                    preview = section_content[:200].replace("\n", " ")
                    card_lines.append(f"- **{section_name}:** {preview}...")
            card_lines.append("")

        return "\n".join(card_lines)



