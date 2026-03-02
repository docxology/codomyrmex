"""Theme management for data visualization."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Theme:
    """Visual theme configuration."""
    name: str = "default"
    primary_color: str = "#2c3e50"
    secondary_color: str = "#95a5a6"
    background_color: str = "#ecf0f1"
    text_color: str = "#2c3e50"
    font_family: str = "'Segoe UI', sans-serif"
    font_size: int = 14
    border_radius: int = 8
    custom: dict[str, Any] = field(default_factory=dict)

    def __init__(self, name: str = "default", **kwargs: Any) -> None:
        """Initialize this instance."""
        self.name = name
        self.primary_color = kwargs.get("primary", kwargs.get("primary_color", "#2c3e50"))
        # Map 'accent' to secondary if provided
        self.secondary_color = kwargs.get("accent", kwargs.get("secondary", kwargs.get("secondary_color", "#95a5a6")))
        self.background_color = kwargs.get("background", kwargs.get("background_color", "#ecf0f1"))
        self.text_color = kwargs.get("text", kwargs.get("text_color", "#2c3e50"))
        self.font_family = kwargs.get("font_family", "'Segoe UI', sans-serif")
        self.font_size = kwargs.get("font_size", 14)
        self.border_radius = kwargs.get("border_radius", 8)
        self.custom = kwargs.get("custom", {})

    @property
    def primary(self) -> str:
        """primary ."""
        return self.primary_color

    @property
    def secondary(self) -> str:
        """Alias for compatibility."""
        return self.secondary_color

    @property
    def background(self) -> str:
        """background ."""
        return self.background_color

    @property
    def css(self) -> str:
        """css ."""
        vars_dict = self.to_css_vars()
        css_lines = ["body {"]
        for k, v in vars_dict.items():
            css_lines.append(f"    {k}: {v};")
        css_lines.append("}")
        return "\n".join(css_lines)

    def to_css_vars(self) -> dict[str, str]:
        """to Css Vars ."""
        return {
            "--primary": self.primary_color,
            "--secondary": self.secondary_color,
            "--bg": self.background_color,
            "--text": self.text_color,
            "--font": self.font_family,
            "--font-size": f"{self.font_size}px",
            "--radius": f"{self.border_radius}px",
        }

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "name": self.name,
            "primary": self.primary_color,
            "secondary": self.secondary_color,
            "background": self.background_color,
            "text": self.text_color,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "border_radius": self.border_radius,
            "custom": self.custom,
        }


DEFAULT_THEME = Theme()
DARK_THEME = Theme(
    name="dark",
    primary_color="#60A5FA",
    secondary_color="#34D399",
    background_color="#111827",
    text_color="#F9FAFB",
)
