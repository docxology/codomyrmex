"""UI components for data visualization."""

from dataclasses import dataclass
from typing import Any

from .layout import Grid
from .theme import DEFAULT_THEME, Theme


@dataclass
class Card:
    """Card component for highlighting information."""
    title: str = ""
    content: str = ""
    value: Any = None
    description: str = ""
    css_class: str = "card"

    def render(self) -> str:
        """render ."""
        parts = [f"<h3>{self.title}</h3>"]
        if self.value is not None:
             parts.append(f"<div class='value'>{self.value}</div>")
        if self.content:
            parts.append(f"<p>{self.content}</p>")
        if self.description:
            parts.append(f"<p class='description'>{self.description}</p>")

        inner = "".join(parts)
        return f"<div class='{self.css_class}'>{inner}</div>"

    def __str__(self) -> str:
        """str ."""
        return self.render()


class Table:
    """Table component for data display."""

    def __init__(self, headers: list[str] | None = None, rows: list[list] | None = None, **kwargs):
        """Initialize this instance."""
        self.headers = headers or []
        self.rows = rows or []

    def render(self) -> str:
        """render ."""
        header = "".join(f"<th>{h}</th>" for h in self.headers)
        body = "".join(
            "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
            for row in self.rows
        )
        return f"<table><thead><tr>{header}</tr></thead><tbody>{body}</tbody></table>"

    def __str__(self) -> str:
        """str ."""
        return self.render()


class Dashboard:
    """Dashboard container."""

    def __init__(self, title: str = "Dashboard", theme: Theme | None = None):
        """Initialize this instance."""
        self.title = title
        self.theme = theme or DEFAULT_THEME
        self.grid = Grid()
        self.sections: list[Any] = self.grid.sections

    def add_section(self, title: str, content: Any = None, **kwargs: Any) -> None:
        """add Section ."""
        self.grid.add_section(title, content, **kwargs)

    def render(self, output_path: str | None = None) -> str:
        """Render the dashboard as an HTML string.

        Args:
            output_path: If provided, write the HTML to this file path.

        Returns:
            Complete HTML string.
        """
        inner = self.grid.render()
        css = self.theme.css
        html = f"<html><head><style>{css}</style></head><body><h1>{self.title}</h1>{inner}</body></html>"
        if output_path:
            from pathlib import Path
            Path(output_path).write_text(html)
        return html

    def __str__(self) -> str:
        """str ."""
        return self.render()

    def __repr__(self) -> str:
        """repr ."""
        return f"Dashboard(title={self.title!r}, sections={len(self.sections)})"
