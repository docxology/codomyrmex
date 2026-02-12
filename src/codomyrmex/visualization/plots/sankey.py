from typing import List, Tuple
from .mermaid import MermaidDiagram

class SankeyDiagram(MermaidDiagram):
    """
    Generates a Sankey diagram using Mermaid's sankey-beta syntax.
    Useful for flow visualization.
    """
    def __init__(self, title: str, links: List[Tuple[str, str, float]]):
        """
        Args:
            links: List of tuples (source, target, value)
        """
        self.links = links
        diagram_code = self._generate_code()
        super().__init__(title, diagram_code)
        
    def _generate_code(self) -> str:
        code = "sankey-beta\n"
        for source, target, value in self.links:
            # Simple sanitization
            s = source.replace('"', '').strip()
            t = target.replace('"', '').strip()
            code += f'{s}, {t}, {value}\n'
        return code
