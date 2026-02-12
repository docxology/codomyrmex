from dataclasses import dataclass

@dataclass
class ChatBubble:
    """
    Component to display a chat message.
    """
    message: str
    sender: str # "user" or "agent" or "system"
    timestamp: str = ""
    
    def __str__(self) -> str:
        # Styles
        base_style = "max-width: 70%; padding: 10px 15px; border-radius: 15px; margin-bottom: 10px; position: relative; clear: both;"
        
        if self.sender.lower() == "user":
            style = f"{base_style} background-color: #007bff; color: white; float: right; border-bottom-right-radius: 5px;"
            align = "right"
            meta_color = "#ccc"
        elif self.sender.lower() == "system":
            style = f"{base_style} background-color: #eee; color: #555; margin: 0 auto; float: none; text-align: center; font-style: italic;"
            align = "center"
            meta_color = "#999"
        else: # agent
            style = f"{base_style} background-color: #f1f0f0; color: #333; float: left; border-bottom-left-radius: 5px;"
            align = "left"
            meta_color = "#999"
            
        timestamp_html = f'<div style="font-size: 0.7em; color: {meta_color}; text-align: {align}; margin-top: 5px;">{self.timestamp}</div>' if self.timestamp else ""
        
        return f"""
        <div class="component-chat-wrapper" style="overflow: hidden; width: 100%;">
            <div class="component-chat-bubble" style="{style}">
                <div style="font-weight: bold; font-size: 0.8em; margin-bottom: 3px;">{self.sender.title()}</div>
                <div>{self.message}</div>
                {timestamp_html}
            </div>
        </div>
        """
