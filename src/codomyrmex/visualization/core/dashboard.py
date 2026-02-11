from typing import List, Any
from pathlib import Path
from .layout import Grid
from .export import render_html
from .theme import Theme, DEFAULT_THEME

class Dashboard:
    """
    Base class for creating dashboards.
    """
    def __init__(self, title: str = "Codomyrmex Dashboard", theme: Theme = DEFAULT_THEME):
        self.title = title
        self.theme = theme
        self.grid = Grid()
        
    def add_section(self, title: str, content: Any, full_width: bool = False, description: str = None):
        """Adds a section to the dashboard's grid."""
        self.grid.add_section(title, content, full_width, description)
        
    def render(self, output_path: str) -> str:
        """
        Renders the dashboard to an HTML file.
        
        Args:
            output_path: The path (file) to save the dashboard to.
            
        Returns:
            Absolute path to the rendered file.
        """
        path = Path(output_path)
        return render_html(self.grid, self.title, path, self.theme)
