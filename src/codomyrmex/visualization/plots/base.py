from abc import ABC, abstractmethod
from typing import Any, Dict

class Plot(ABC):
    """
    Abstract base class for all visualization plots.
    """
    
    def __init__(self, title: str, data: Any):
        self.title = title
        self.data = data
        
    @abstractmethod
    def render(self) -> Any:
        """
        Renders the plot. 
        
        Returns:
            The rendered object (matplotlib Figure, HTML string, etc.)
        """
        pass
        
    def to_html(self) -> str:
        """
        Returns an HTML representation of the plot.
        Useful for embedding in reports.
        """
        # Default fallback: string representation of the render result
        return str(self.render())
        
    def __str__(self) -> str:
        """
        Returns the HTML representation of the plot when converted to string.
        """
        try:
            return self.to_html()
        except Exception as e:
            return f"<div>Error rendering plot: {str(e)}</div>"
