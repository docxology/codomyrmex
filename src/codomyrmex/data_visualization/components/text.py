"""Component module."""
from dataclasses import dataclass

from ._base import BaseComponent


@dataclass
class TextBlock(BaseComponent):
    """Text block component."""
    content: str = ""
    is_markdown: bool = False

    def render(self) -> str:
        """Render."""
        text = self.content.replace("\n", "<br>")
        md_class = " markdown" if self.is_markdown else ""
        cls = f"component-text{md_class}"
        return f"<div class='{cls}'>{text}</div>"

    def __str__(self) -> str:
        """Return human-readable string."""
        return self.render()

@dataclass
class CodeBlock(BaseComponent):
    """Code block component."""
    code: str = ""
    language: str = "python"

    def render(self) -> str:
        """Render."""
        return f'<pre><code class="language-{self.language}">{self.code}</code></pre>'

    def __str__(self) -> str:
        """Return human-readable string."""
        return self.render()
