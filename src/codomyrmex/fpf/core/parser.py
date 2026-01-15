from codomyrmex.logging_monitoring import get_logger
"""Parser for FPF specification markdown.


logger = get_logger(__name__)
This module provides functionality to parse the FPF specification markdown
file into structured data models.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .models import FPFSpec, Pattern, PatternStatus


class FPFParser:
    """Parser for FPF specification markdown files."""

    def __init__(self):
        """Initialize the parser."""
        self.pattern_regex = re.compile(
            r"^##\s+([A-Z]\.\d+(?:\.\d+)?(?:\.[A-Z])?)\s*[-–]\s*(.+)$"
        )
        self.section_regex = re.compile(r"^###\s+(.+)$")
        self.subsection_regex = re.compile(r"^####\s+(.+)$")
        self.subsubsection_regex = re.compile(r"^#####\s+(.+)$")

    def parse_spec(self, markdown_content: str, source_path: Optional[str] = None) -> FPFSpec:
        """Parse the complete FPF specification.

        Args:
            markdown_content: The markdown content of the FPF specification
            source_path: Optional path to the source file

        Returns:
            FPFSpec object containing all parsed patterns and metadata
        """
        lines = markdown_content.split("\n")
        table_of_contents = self.extract_table_of_contents(markdown_content)
        patterns = self.extract_patterns(markdown_content)

        # Extract version info if available
        version = None
        last_updated = None
        for line in lines[:100]:  # Check first 100 lines
            if "Version" in line or "version" in line:
                version_match = re.search(r"v?(\d+\.\d+\.\d+)", line)
                if version_match:
                    version = version_match.group(1)
            if "December" in line or "2025" in line:
                # Try to extract date
                date_match = re.search(r"(\d{4})", line)
                if date_match:
                    last_updated = date_match.group(1)

        return FPFSpec(
            version=version,
            source_url=source_path,
            patterns=patterns,
            table_of_contents=table_of_contents,
            metadata={"total_patterns": len(patterns)},
        )

    def extract_table_of_contents(self, content: str) -> Dict[str, any]:
        """Extract the table of contents from the FPF specification.

        Args:
            content: The markdown content

        Returns:
            Dictionary containing the table of contents structure
        """
        toc = {
            "preface": [],
            "parts": {},
            "sections": [],
        }

        lines = content.split("\n")
        in_toc = False
        current_part = None

        for i, line in enumerate(lines):
            # Detect start of TOC
            if "# Table of Content" in line or "Table of Content" in line:
                in_toc = True
                continue

            if not in_toc:
                continue

            # Detect end of TOC (start of actual content)
            if line.startswith("# **Preface**") or line.startswith("## FPF is"):
                break

            # Detect parts
            part_match = re.match(r"\*\*Part\s+([A-Z])\s*[-–]", line)
            if part_match:
                current_part = part_match.group(1)
                toc["parts"][current_part] = []
                continue

            # Detect sections within parts
            if current_part and "|" in line and "§" in line:
                # This is a table row in the TOC
                toc["parts"][current_part].append(line.strip())

        return toc

    def extract_patterns(self, content: str) -> List[Pattern]:
        """Extract all patterns from the FPF specification.

        Args:
            content: The markdown content

        Returns:
            List of Pattern objects
        """
        patterns = []
        lines = content.split("\n")

        current_pattern = None
        current_section = None
        current_content_lines = []
        pattern_start_line = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check for pattern header (## A.1 - Title)
            pattern_match = self.pattern_regex.match(line)
            if pattern_match:
                # Save previous pattern if exists
                if current_pattern:
                    current_pattern.content = "\n".join(current_content_lines)
                    current_pattern.sections[current_section] = "\n".join(
                        current_content_lines
                    )
                    patterns.append(current_pattern)

                # Start new pattern
                pattern_id = pattern_match.group(1)
                title = pattern_match.group(2).strip()
                status = self._extract_status(lines, i)

                # Extract part and cluster
                part = pattern_id.split(".")[0] if "." in pattern_id else None

                current_pattern = Pattern(
                    id=pattern_id,
                    title=title,
                    status=status,
                    part=part,
                    content="",
                    sections={},
                    keywords=[],
                    search_queries=[],
                    dependencies={},
                )
                current_content_lines = [line]
                pattern_start_line = i
                current_section = "header"
                i += 1
                continue

            # Check for section headers (### Section Name)
            if current_pattern:
                section_match = self.section_regex.match(line)
                if section_match:
                    # Save previous section
                    if current_section:
                        current_pattern.sections[current_section] = "\n".join(
                            current_content_lines
                        )

                    # Start new section
                    section_name = section_match.group(1).strip()
                    current_section = self._normalize_section_name(section_name)
                    current_content_lines = [line]
                    i += 1
                    continue

                # Collect content
                if current_pattern:
                    current_content_lines.append(line)

            i += 1

        # Save last pattern
        if current_pattern:
            current_pattern.content = "\n".join(current_content_lines)
            if current_section:
                current_pattern.sections[current_section] = "\n".join(
                    current_content_lines
                )
            patterns.append(current_pattern)

        # Post-process patterns to extract metadata
        for pattern in patterns:
            self._extract_pattern_metadata(pattern)

        return patterns

    def _extract_status(self, lines: List[str], pattern_line: int) -> PatternStatus:
        """Extract pattern status from surrounding lines.

        Args:
            lines: All lines of the document
            pattern_line: Line number of the pattern header

        Returns:
            PatternStatus enum value
        """
        # Check table of contents or pattern metadata
        # Look backwards and forwards for status indicators
        for i in range(max(0, pattern_line - 10), min(len(lines), pattern_line + 50)):
            line = lines[i]
            if "| Stable |" in line or '"Stable"' in line:
                return PatternStatus.STABLE
            if "| Draft |" in line or '"Draft"' in line:
                return PatternStatus.DRAFT
            if "| Stub |" in line or '"Stub"' in line:
                return PatternStatus.STUB
            if "| New |" in line or '"New"' in line:
                return PatternStatus.NEW

        # Default to Stable if not found
        return PatternStatus.STABLE

    def _normalize_section_name(self, section_name: str) -> str:
        """Normalize section names to standard keys.

        Args:
            section_name: Raw section name from markdown

        Returns:
            Normalized section name
        """
        section_name = section_name.strip()
        # Remove numbering and colons
        section_name = re.sub(r"^\d+\)\s*", "", section_name)
        section_name = re.sub(r"^[A-Z]\.\d+:\d+\s*[-–]\s*", "", section_name)
        section_name = section_name.strip(": -–")

        # Map common variations
        mappings = {
            "Problem frame": "problem",
            "Problem": "problem",
            "Forces": "forces",
            "Solution": "solution",
            "Archetypal Grounding": "archetypal_grounding",
            "Bias-Annotation": "bias_annotation",
            "Conformance Checklist": "conformance_checklist",
            "Common Anti-Patterns": "anti_patterns",
            "Consequences": "consequences",
            "Rationale": "rationale",
            "Relations": "relations",
            "SoTA-Echoing": "sota_echoing",
        }

        section_lower = section_name.lower()
        for key, value in mappings.items():
            if key.lower() in section_lower:
                return value

        # Default: lowercase and replace spaces with underscores
        return section_name.lower().replace(" ", "_").replace("-", "_")

    def _extract_pattern_metadata(self, pattern: Pattern) -> None:
        """Extract metadata from pattern content.

        Args:
            pattern: Pattern object to populate with metadata
        """
        content = pattern.content

        # Extract keywords
        keyword_matches = re.findall(r"\*Keywords:\*\s*(.+?)(?:\n|$)", content)
        if keyword_matches:
            keywords_str = keyword_matches[0]
            # Split by comma and clean
            keywords = [
                k.strip().strip("*")
                for k in keywords_str.split(",")
                if k.strip()
            ]
            pattern.keywords = keywords

        # Extract search queries
        query_matches = re.findall(
            r'\*Queries:\*\s*"(.+?)"', content, re.MULTILINE
        )
        if query_matches:
            pattern.search_queries = query_matches

        # Extract dependencies
        # Look for "Builds on:", "Prerequisite for:", etc.
        builds_on_match = re.search(
            r"\*\*Builds on:\*\*\s*(.+?)(?:\n|$)", content, re.IGNORECASE
        )
        if builds_on_match:
            deps = self._parse_dependency_list(builds_on_match.group(1))
            pattern.dependencies["builds_on"] = deps

        prerequisite_match = re.search(
            r"\*\*Prerequisite for:\*\*\s*(.+?)(?:\n|$)", content, re.IGNORECASE
        )
        if prerequisite_match:
            deps = self._parse_dependency_list(prerequisite_match.group(1))
            pattern.dependencies["prerequisite_for"] = deps

        coordinates_match = re.search(
            r"\*\*Coordinates with:\*\*\s*(.+?)(?:\n|$)", content, re.IGNORECASE
        )
        if coordinates_match:
            deps = self._parse_dependency_list(coordinates_match.group(1))
            pattern.dependencies["coordinates_with"] = deps

        constrains_match = re.search(
            r"\*\*Constrains:\*\*\s*(.+?)(?:\n|$)", content, re.IGNORECASE
        )
        if constrains_match:
            deps = self._parse_dependency_list(constrains_match.group(1))
            pattern.dependencies["constrains"] = deps

    def _parse_dependency_list(self, dep_string: str) -> List[str]:
        """Parse a dependency list string into individual pattern IDs.

        Args:
            dep_string: String containing dependency references

        Returns:
            List of pattern IDs
        """
        # Extract pattern IDs like A.1, A.2.1, B.3, etc.
        pattern_ids = re.findall(r"([A-Z]\.\d+(?:\.\d+)?(?:\.[A-Z])?)", dep_string)
        return pattern_ids

    def extract_sections(self, pattern_content: str) -> Dict[str, str]:
        """Extract sections from a pattern's content.

        Args:
            pattern_content: The markdown content of a single pattern

        Returns:
            Dictionary mapping section names to their content
        """
        sections = {}
        lines = pattern_content.split("\n")
        current_section = None
        current_lines = []

        for line in lines:
            section_match = self.section_regex.match(line)
            if section_match:
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_lines).strip()

                # Start new section
                section_name = section_match.group(1).strip()
                current_section = self._normalize_section_name(section_name)
                current_lines = [line]
            else:
                if current_section:
                    current_lines.append(line)

        # Save last section
        if current_section:
            sections[current_section] = "\n".join(current_lines).strip()

        return sections

