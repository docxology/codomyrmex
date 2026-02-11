from typing import List, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Section:
    title: str
    content: Any  # Chart object, HTML string, or any renderable
    width: str = "100%"
    description: Optional[str] = None

@dataclass
class Grid:
    """Represents a grid layout for the dashboard."""
    columns: int = 2
    sections: List[Section] = field(default_factory=list)

    def add_section(self, title: str, content: Any, full_width: bool = False, description: Optional[str] = None):
        """
        Adds a section to the grid.
        
        Args:
            title: Title of the section.
            content: Content to render (HTML string, Plot object, etc.).
            full_width: If True, the section spans the full width of the container.
            description: Optional description text for the section.
        """
        width = "100%" if full_width else f"{int(100/self.columns)}%"
        self.sections.append(Section(title=title, content=content, width=width, description=description))
