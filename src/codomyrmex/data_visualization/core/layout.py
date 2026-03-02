"""Layout management for data visualization."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Section:
    """A section within a layout."""
    title: str = ""
    description: str = ""
    children: list[Any] = field(default_factory=list)
    css_class: str = ""
    width: str = "100%"

    def add(self, child: Any) -> None:
        """add ."""
        self.children.append(child)

    def render(self) -> str:
        """render ."""
        inner = "\n".join(
            getattr(c, "render", lambda: str(c))() for c in self.children
        )
        cls = f' class="{self.css_class}"' if self.css_class else ""
        title_html = f"<h2>{self.title}</h2>" if self.title else ""
        desc_html = f"<p>{self.description}</p>" if self.description else ""
        return f'<div{cls} style="width:{self.width}">{title_html}{desc_html}{inner}</div>'


@dataclass
class Grid:
    """Grid layout for dashboard-style visualization."""
    columns: int = 2
    gap: str = "16px"
    sections: list[Section] = field(default_factory=list)

    def add_section(self, title: str, content: Any = None, **kwargs: Any) -> None:
        description = kwargs.get("description", "")
        full_width = kwargs.get("full_width", False)
        width = "100%" if full_width else f"{100/self.columns}%" # Simplistic width

        section = Section(title=title, description=description, width=width)
        if content:
            section.add(content)
        self.sections.append(section)

    def render(self) -> str:
        """render ."""
        inner = "\n".join(s.render() for s in self.sections)
        return (
            f'<div style="display:grid;grid-template-columns:'
            f'repeat({self.columns},1fr);gap:{self.gap}">{inner}</div>'
        )
