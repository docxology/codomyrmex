"""Rule file loader.

Parses .cursorrules files into Rule objects, inferring priority from
their directory location in the rules hierarchy.
"""

from __future__ import annotations

import re
from pathlib import Path

from .models import Rule, RulePriority, RuleSection

# Matches section headings like "## 0. Preamble" or "## 3. Coding Standards & Practices for X"
_SECTION_RE = re.compile(r"^#{1,3}\s+(\d+)\.\s+(.+)$", re.MULTILINE)


class RuleLoader:
    """Loads and parses a single .cursorrules file into a Rule object."""

    @classmethod
    def load(cls, path: Path) -> Rule:
        """Parse *path* and return a Rule.

        Raises:
            FileNotFoundError: if *path* does not exist.
            ValueError: if *path* is not a .cursorrules file.
        """
        if not path.exists():
            raise FileNotFoundError(f"cursorrules file not found: {path}")
        if not path.name.endswith(".cursorrules"):
            raise ValueError(f"Expected a .cursorrules file, got: {path}")

        raw = path.read_text(encoding="utf-8")
        priority = cls._infer_priority(path)
        name = cls._infer_name(path)
        sections = cls._parse_sections(raw)
        return Rule(
            name=name,
            priority=priority,
            file_path=path,
            sections=sections,
            raw_content=raw,
        )

    @classmethod
    def _infer_priority(cls, path: Path) -> RulePriority:
        """Infer RulePriority from the file's location in the hierarchy."""
        parts = set(path.parts)
        if "file-specific" in parts:
            return RulePriority.FILE_SPECIFIC
        if "modules" in parts:
            return RulePriority.MODULE
        if "cross-module" in parts:
            return RulePriority.CROSS_MODULE
        return RulePriority.GENERAL

    @classmethod
    def _infer_name(cls, path: Path) -> str:
        """Strip the .cursorrules suffix to get the rule name.

        Examples:
            "python.cursorrules"      → "python"
            "README.md.cursorrules"   → "README.md"
            "general.cursorrules"     → "general"
        """
        filename = path.name
        suffix = ".cursorrules"
        if filename.endswith(suffix):
            return filename[: -len(suffix)]
        return filename

    @classmethod
    def _parse_sections(cls, raw: str) -> list[RuleSection]:
        """Split *raw* into numbered sections based on ## N. heading markers."""
        matches = list(_SECTION_RE.finditer(raw))
        if not matches:
            # No numbered sections — return whole file as section 0
            return [RuleSection(number=0, title="Content", content=raw.strip())]

        sections: list[RuleSection] = []
        for i, m in enumerate(matches):
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
            sections.append(
                RuleSection(
                    number=int(m.group(1)),
                    title=m.group(2).strip(),
                    content=raw[start:end].strip(),
                )
            )
        return sections
