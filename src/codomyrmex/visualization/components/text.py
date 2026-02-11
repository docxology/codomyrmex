from dataclasses import dataclass
from typing import Optional

@dataclass
class TextBlock:
    """
    Component to display a block of text, optionally interpreted as Markdown (basic HTML support).
    """
    content: str
    is_markdown: bool = False # In a real system, we'd use a markdown parser
    
    def __str__(self) -> str:
        # Placeholder for Markdown parsing
        # For now, we assume simple text or pre-formatted HTML
        if self.is_markdown:
             # Very basic conversion for demo
            html = self.content.replace("\n", "<br>")
            return f'<div class="component-text markdown">{html}</div>'
        return f'<div class="component-text">{self.content}</div>'

@dataclass
class CodeBlock:
    """
    Component to display code with syntax highlighting (handled by CSS/JS).
    """
    code: str
    language: str = "python"
    
    def __str__(self) -> str:
        return f"""
        <pre><code class="language-{self.language}">{self.code}</code></pre>
        """
