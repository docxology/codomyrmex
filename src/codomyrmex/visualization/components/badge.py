from dataclasses import dataclass

@dataclass
class Badge:
    """
    Component to display a small status badge.
    """
    text: str
    status: str = "primary" # primary, success, warning, danger, info
    
    def __str__(self) -> str:
        # Determine color based on status (simplified)
        colors = {
            "primary": "#337ab7",
            "success": "#5cb85c",
            "warning": "#f0ad4e",
            "danger": "#d9534f",
            "info": "#5bc0de"
        }
        color = colors.get(self.status, "#777")
        
        style = f"background-color: {color}; color: white; padding: 3px 7px; border-radius: 10px; font-size: 12px; font-weight: bold; vertical-align: middle;"
        
        return f'<span class="component-badge" style="{style}">{self.text}</span>'
