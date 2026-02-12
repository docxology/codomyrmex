from dataclasses import dataclass
from typing import List, Any

@dataclass
class HeatmapTable:
    """
    Component to display a table with color-coded cells based on value.
    Assumes numeric data for coloring.
    """
    headers: List[str]
    rows: List[List[Any]] # Can be numbers or strings
    title: str = ""
    
    def __str__(self) -> str:
        # Find min/max for simple linear scaling (for numeric columns only)
        # For simplicity, we'll try to color all numeric cells
        all_numerics = []
        for row in self.rows:
            for cell in row:
                if isinstance(cell, (int, float)):
                    all_numerics.append(cell)
                    
        min_val = min(all_numerics) if all_numerics else 0
        max_val = max(all_numerics) if all_numerics else 1
        
        header_html = "".join([f'<th style="padding: 8px; border-bottom: 2px solid #ddd; text-align: left;">{h}</th>' for h in self.headers])
        
        rows_html = ""
        for row in self.rows:
            cells_html = ""
            for cell in row:
                bg_color = "transparent"
                text_color = "black"
                
                if isinstance(cell, (int, float)):
                    # Calculate intensity (0 to 1)
                    if max_val > min_val:
                        norm = (cell - min_val) / (max_val - min_val)
                    else:
                        norm = 0.5
                        
                    # Blue scale: light to dark
                    # Using rgba(0, 123, 255, alpha)
                    bg_color = f"rgba(0, 123, 255, {0.1 + norm * 0.9})"
                    text_color = "white" if norm > 0.6 else "black"
                    
                cells_html += f'<td style="padding: 8px; border-bottom: 1px solid #eee; background-color: {bg_color}; color: {text_color};">{cell}</td>'
                
            rows_html += f"<tr>{cells_html}</tr>"
            
        title_html = f'<h4 style="margin-bottom: 10px;">{self.title}</h4>' if self.title else ""
        
        return f"""
        <div class="component-heatmap-table" style="overflow-x: auto; margin-bottom: 20px;">
            {title_html}
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <thead>
                    <tr>{header_html}</tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """
