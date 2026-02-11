from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Theme:
    primary: str = "#2c3e50"
    secondary: str = "#95a5a6"
    accent: str = "#e74c3c"
    background: str = "#ecf0f1"
    text: str = "#2c3e50"
    font_family: str = "'Segoe UI', sans-serif"

    @property
    def css(self) -> str:
        return f"""
        body {{ font-family: {self.font_family}; background-color: {self.background}; color: {self.text}; margin: 0; padding: 20px; }}
        h1 {{ color: {self.primary}; border-bottom: 2px solid {self.accent}; padding-bottom: 10px; }}
        h2 {{ color: {self.primary}; margin-top: 30px; }}
        .dashboard-grid {{ display: flex; flex-wrap: wrap; gap: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .mermaid {{ background: white; padding: 10px; border-radius: 4px; }}
        """

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "background": self.background,
            "text": self.text,
            "font_family": self.font_family
        }

DEFAULT_THEME = Theme()
