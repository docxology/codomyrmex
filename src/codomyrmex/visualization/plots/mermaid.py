from .base import Plot

class MermaidDiagram(Plot):
    """
    Wraps a Mermaid diagram definition.
    """
    def __init__(self, title: str, definition: str):
        super().__init__(title, definition)
        
    def render(self) -> str:
        return self.data
    
    def to_html(self) -> str:
        return f'<div class="mermaid">{self.data}</div>'
