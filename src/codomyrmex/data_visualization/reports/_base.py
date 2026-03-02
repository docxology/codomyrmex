"""Base class for all reports."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class BaseReport:
    """Base class for report generators.

    Attributes:
        title: Report title.
        sections: List of content sections.
    """
    title: str = ""
    sections: list[Any] = field(default_factory=list)

    def add_section(self, section: Any) -> None:
        """Append a section to the report."""
        self.sections.append(section)

    def render(self) -> str:
        """Render the report as an HTML string."""
        inner = "\n".join(
            getattr(s, "render", lambda s=s: str(s))() for s in self.sections
        )
        return f"<article><h1>{self.title}</h1>{inner}</article>"

    def save(self, output_path: str) -> str:
        """Save the rendered report to a file.

        Args:
            output_path: File path to save the HTML report.

        Returns:
            The *output_path* for chaining convenience.
        """
        html = self.render()
        Path(output_path).write_text(html)
        return str(output_path)

    def to_dict(self) -> dict[str, Any]:
        """Serialize report metadata to a dictionary."""
        return {"title": self.title, "section_count": len(self.sections)}

    def __str__(self) -> str:
        """str ."""
        return self.render()

    def __repr__(self) -> str:
        """repr ."""
        return f"{self.__class__.__name__}(title={self.title!r}, sections={len(self.sections)})"
