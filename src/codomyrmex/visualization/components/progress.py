from dataclasses import dataclass

@dataclass
class ProgressBar:
    """
    Component to display a progress bar.
    """
    value: float # 0 to 100
    max_value: float = 100
    label: str = ""
    color: str = "#337ab7"
    
    def __str__(self) -> str:
        percentage = min(100, max(0, (self.value / self.max_value) * 100))
        
        container_style = "background-color: #f5f5f5; border-radius: 4px; box-shadow: inset 0 1px 2px rgba(0,0,0,.1); height: 20px; margin-bottom: 20px;"
        bar_style = f"width: {percentage}%; background-color: {self.color}; height: 100%; border-radius: 4px; text-align: center; color: white; line-height: 20px; font-size: 12px; transition: width .6s ease;"
        
        display_label = self.label if self.label else f"{int(percentage)}%"
        
        return f"""
        <div class="component-progress" style="{container_style}">
            <div style="{bar_style}">
                {display_label}
            </div>
        </div>
        """
