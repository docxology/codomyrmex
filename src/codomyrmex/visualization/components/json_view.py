from dataclasses import dataclass
import json
from typing import Any, Dict

@dataclass
class JsonView:
    """
    Component to display collapsible JSON data.
    """
    data: Any
    title: str = "Data View"
    expanded: bool = False
    
    def __str__(self) -> str:
        try:
            json_str = json.dumps(self.data, indent=2)
        except Exception:
            json_str = str(self.data)
            
        open_attr = "open" if self.expanded else ""
        
        return f"""
        <div class="component-json-view" style="font-family: monospace; background: #f8f9fa; border: 1px solid #ddd; border-radius: 4px; overflow: hidden;">
            <details {open_attr} style="padding: 0;">
                <summary style="padding: 10px; background: #e9ecef; cursor: pointer; outline: none;">{self.title}</summary>
                <div style="padding: 10px; overflow-x: auto;">
                    <pre style="margin: 0;">{json_str}</pre>
                </div>
            </details>
        </div>
        """
