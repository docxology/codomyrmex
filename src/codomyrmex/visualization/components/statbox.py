from dataclasses import dataclass
from typing import Optional

@dataclass
class StatBox:
    """
    Component to display a primary metric with a trend indicator.
    """
    label: str
    value: str
    trend: Optional[str] = None # e.g., "+10%", "-5%"
    trend_direction: str = "neutral" # up, down, neutral
    
    def __str__(self) -> str:
        colors = {
            "up": "green",
            "down": "red",
            "neutral": "gray"
        }
        trend_color = colors.get(self.trend_direction, "gray")
        trend_html = ""
        
        if self.trend:
            arrow = "↑" if self.trend_direction == "up" else "↓" if self.trend_direction == "down" else "-"
            trend_html = f'<div style="color: {trend_color}; font-size: 0.9em; margin-top: 5px;">{arrow} {self.trend}</div>'
            
        return f"""
        <div class="component-statbox" style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; min-width: 150px;">
            <div style="color: #666; font-size: 0.9em; text-transform: uppercase;">{self.label}</div>
            <div style="font-size: 2em; font-weight: bold; margin: 10px 0;">{self.value}</div>
            {trend_html}
        </div>
        """
