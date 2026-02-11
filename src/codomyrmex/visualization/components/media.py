from dataclasses import dataclass
from typing import Optional

@dataclass
class Image:
    """
    Component to display an image.
    """
    src: str
    alt: str = ""
    width: str = "100%"
    caption: Optional[str] = None
    
    def __str__(self) -> str:
        caption_html = f"<figcaption>{self.caption}</figcaption>" if self.caption else ""
        return f"""
        <figure class="component-image">
            <img src="{self.src}" alt="{self.alt}" style="width: {self.width};">
            {caption_html}
        </figure>
        """

@dataclass
class Video:
    """
    Component to display a video.
    """
    src: str
    width: str = "100%"
    controls: bool = True
    autoplay: bool = False
    loop: bool = False
    
    def __str__(self) -> str:
        attrs = []
        if self.controls: attrs.append("controls")
        if self.autoplay: attrs.append("autoplay")
        if self.loop: attrs.append("loop")
        attr_str = " ".join(attrs)
        
        return f"""
        <div class="component-video">
            <video src="{self.src}" style="width: {self.width};" {attr_str}>
                Your browser does not support the video tag.
            </video>
        </div>
        """
