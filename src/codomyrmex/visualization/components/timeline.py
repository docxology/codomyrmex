from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class TimelineEvent:
    timestamp: str
    title: str
    description: str = ""
    icon: str = "•" 

@dataclass
class Timeline:
    """
    Component to display a vertical list of events.
    """
    events: List[TimelineEvent]
    
    def __str__(self) -> str:
        items_html = ""
        for event in self.events:
            items_html += f"""
            <div class="timeline-item" style="display: flex; gap: 10px; margin-bottom: 15px;">
                <div class="timeline-marker" style="min-width: 20px; text-align: center; color: #555;">{event.icon}</div>
                <div class="timeline-content">
                    <div style="font-size: 0.85em; color: #888;">{event.timestamp}</div>
                    <div style="font-weight: bold;">{event.title}</div>
                    <div>{event.description}</div>
                </div>
            </div>
            """
            
        return f"""
        <div class="component-timeline" style="border-left: 2px solid #ddd; padding-left: 10px;">
            {items_html}
        </div>
        """
