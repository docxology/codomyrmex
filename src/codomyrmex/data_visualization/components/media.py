"""Component module."""
from dataclasses import dataclass, field
from typing import Any

from ._base import BaseComponent

@dataclass
class Image(BaseComponent):
    """Image component."""
    src: str = ""
    alt: str = ""
    caption: str = ""

    def render(self) -> str:
        cap = f"<figcaption>{self.caption}</figcaption>" if self.caption else ""
        return f'<figure><img src="{self.src}" alt="{self.alt}" />{cap}</figure>'

    def __str__(self) -> str:
        return self.render()

@dataclass
class Video(BaseComponent):
    """Video component."""
    src: str = ""
    autoplay: bool = False
    controls: bool = True

    def render(self) -> str:
        attrs = [f'src="{self.src}"']
        if self.controls:
            attrs.append("controls")
        if self.autoplay:
            attrs.append("autoplay")
        return f'<video {" ".join(attrs)}></video>'

    def __str__(self) -> str:
        return self.render()
