"""Layout management for data visualization."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Section:
    """A section within a layout."""
    title: str = ""
    children: list[Any] = field(default_factory=list)
    css_class: str = ""
    width: str = "100%"

    def add(self, child: Any) -> None:
        self.children.append(child)

    def render(self) -> str:
        inner = "\n".join(
            getattr(c, "render", lambda: str(c))() for c in self.children
        )
        cls = f' class="{self.css_class}"' if self.css_class else ""
        title_html = f"<h2>{self.title}</h2>" if self.title else ""
        return f'<div{cls} style="width:{self.width}">{title_html}{inner}</div>'


@dataclass
class Grid:
    """Grid layout for dashboard-style visualization."""
    columns: int = 2
    gap: str = "16px"
    sections: list[Section] = field(default_factory=list)

    def add_section(self, section: Section) -> None:
        self.sections.append(section)

    def render(self) -> str:
        inner = "\n".join(s.render() for s in self.sections)
        return (
            f'<div style="display:grid;grid-template-columns:'
            f'repeat({self.columns},1fr);gap:{self.gap}">{inner}</div>'
        )
