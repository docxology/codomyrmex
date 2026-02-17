"""HTML export utilities for data visualization."""

from pathlib import Path

from .theme import DEFAULT_THEME, Theme


def render_html(
    content: str,
    *,
    title: str = "Codomyrmex Report",
    theme: Theme | None = None,
    output_path: str | Path | None = None,
) -> str:
    """Render content into a full HTML document.

    Args:
        content: HTML body content.
        title: Page title.
        theme: Theme to apply (defaults to DEFAULT_THEME).
        output_path: If provided, write HTML to this file.

    Returns:
        Complete HTML string.
    """
    theme = theme or DEFAULT_THEME
    css_vars = "; ".join(f"{k}:{v}" for k, v in theme.to_css_vars().items())
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{ {css_vars} }}
        body {{ font-family: var(--font); color: var(--text); background: var(--bg); margin: 2rem; }}
    </style>
</head>
<body>
{content}
</body>
</html>"""
    if output_path:
        Path(output_path).write_text(html)
    return html
