from dataclasses import dataclass

@dataclass
class Alert:
    """
    Component to display a contextual alert message.
    """
    message: str
    level: str = "info" # info, success, warning, danger
    
    def __str__(self) -> str:
        colors = {
            "info": ("#d9edf7", "#31708f"),
            "success": ("#dff0d8", "#3c763d"),
            "warning": ("#fcf8e3", "#8a6d3b"),
            "danger": ("#f2dede", "#a94442")
        }
        bg, text = colors.get(self.level, colors["info"])
        
        style = f"background-color: {bg}; color: {text}; padding: 15px; margin-bottom: 20px; border: 1px solid transparent; border-radius: 4px;"
        
        return f'<div class="component-alert" style="{style}">{self.message}</div>'
