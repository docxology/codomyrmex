"""Base class for all reports."""
from dataclasses import dataclass, field
from typing import Any

@dataclass
class BaseReport:
    """Base class for report generators."""
    title: str = ""
    sections: list[Any] = field(default_factory=list)

    def add_section(self, section: Any) -> None:
        self.sections.append(section)

    def render(self) -> str:
        inner = "\n".join(
            getattr(s, "render", lambda: str(s))() for s in self.sections
        )
        return f"<article><h1>{self.title}</h1>{inner}</article>"

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "section_count": len(self.sections)}
