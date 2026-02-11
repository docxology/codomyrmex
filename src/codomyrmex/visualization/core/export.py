from pathlib import Path
from .layout import Grid
from .theme import Theme, DEFAULT_THEME

def render_html(grid: Grid, title: str, output_path: Path, theme: Theme = DEFAULT_THEME) -> str:
    """
    Renders a Grid layout to an HTML file.
    
    Args:
        grid: The Grid object containing sections to render.
        title: The title of the dashboard/report.
        output_path: Path to write the HTML file to.
        theme: Theme object for styling.
        
    Returns:
        The absolute path to the generated HTML file as a string.
    """
    
    cards_html = ""
    for section in grid.sections:
        # Determine content type
        # For now, we assume content is a string (HTML) or has a __str__ representation
        # Future: Check for specific plot types and call their render methods
        content_html = str(section.content)
        
        description_html = f"<p><em>{section.description}</em></p>" if section.description else ""
        
        # Calculate width with gap consideration (simplistic)
        # In a real grid system (CSS Grid), this would be handled by classes
        if section.width == "100%":
             width_style = "width: 100%;"
        else:
             width_style = f"width: calc({section.width} - 20px);" # Adjust for gap

        cards_html += f"""
        <div class="card" style="{width_style}">
            <h3>{section.title}</h3>
            {description_html}
            {content_html}
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>{theme.css}</style>
    </head>
    <body>
        <h1>{title}</h1>
        <div class="dashboard-grid">
            {cards_html}
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
    </body>
    </html>
    """
    
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding='utf-8')
    return str(output_path.absolute())
