from dataclasses import dataclass
from typing import Any

@dataclass
class Card:
    """
    A simple card component to display a value and a label.
    """
    title: str
    value: Any
    description: str = ""
    
    def __str__(self) -> str:
        return f"""
        <div class="component-card">
            <h4>{self.title}</h4>
            <div class="value">{self.value}</div>
            <div class="description">{self.description}</div>
        </div>
        """
        
@dataclass
class Table:
    """
    A simple HTML table component.
    """
    headers: list[str]
    rows: list[list[Any]]
    
    def __str__(self) -> str:
        header_html = "".join([f"<th>{h}</th>" for h in self.headers])
        rows_html = ""
        for row in self.rows:
            row_html = "".join([f"<td>{cell}</td>" for cell in row])
            rows_html += f"<tr>{row_html}</tr>"
            
        return f"""
        <table class="component-table">
            <thead>
                <tr>{header_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        """
