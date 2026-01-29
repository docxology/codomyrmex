#!/usr/bin/env python3
"""
Export visualizations to various formats (PNG, SVG, PDF, HTML).

Usage:
    python export_chart.py <data_file> --output OUTPUT [--format FORMAT]
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
import csv


def load_data(file_path: str) -> tuple:
    """Load data from CSV or JSON file."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == ".csv":
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            headers = list(rows[0].keys()) if rows else []
            return headers, rows
    elif suffix == ".json":
        with open(path, "r") as f:
            data = json.load(f)
            if isinstance(data, list) and data:
                return list(data[0].keys()), data
            raise ValueError("JSON must be an array of objects")
    else:
        raise ValueError(f"Unsupported: {suffix}")


def create_svg_bar_chart(data: list, x_col: str, y_col: str, width: int = 600, height: int = 400) -> str:
    """Generate an SVG bar chart."""
    y_values = [float(row.get(y_col, 0)) for row in data]
    x_values = [str(row.get(x_col, "")) for row in data]
    
    max_y = max(y_values) if y_values else 1
    bar_width = (width - 100) / len(data) - 5
    
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
        '<style>',
        '  .bar { fill: #4f46e5; }',
        '  .bar:hover { fill: #6366f1; }',
        '  .label { font-family: sans-serif; font-size: 12px; fill: #374151; }',
        '  .title { font-family: sans-serif; font-size: 16px; font-weight: bold; fill: #111827; }',
        '  .axis { stroke: #9ca3af; stroke-width: 1; }',
        '</style>',
        f'<text x="{width/2}" y="25" text-anchor="middle" class="title">{y_col} by {x_col}</text>',
        f'<line x1="50" y1="50" x2="50" y2="{height-50}" class="axis"/>',
        f'<line x1="50" y1="{height-50}" x2="{width-30}" y2="{height-50}" class="axis"/>',
    ]
    
    for i, (x, y) in enumerate(zip(x_values, y_values)):
        bar_height = (y / max_y) * (height - 120) if max_y > 0 else 0
        x_pos = 60 + i * (bar_width + 5)
        y_pos = height - 50 - bar_height
        
        svg_parts.append(f'<rect x="{x_pos}" y="{y_pos}" width="{bar_width}" height="{bar_height}" class="bar"/>')
        svg_parts.append(f'<text x="{x_pos + bar_width/2}" y="{height-35}" text-anchor="middle" class="label">{x[:8]}</text>')
        svg_parts.append(f'<text x="{x_pos + bar_width/2}" y="{y_pos-5}" text-anchor="middle" class="label">{y:.1f}</text>')
    
    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)


def create_html_chart(data: list, x_col: str, y_col: str, chart_type: str = "bar") -> str:
    """Generate an HTML page with Chart.js visualization."""
    labels = [str(row.get(x_col, "")) for row in data]
    values = [float(row.get(y_col, 0)) for row in data]
    
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>{y_col} by {x_col}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: sans-serif; padding: 20px; background: #f9fafb; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="container">
        <canvas id="chart"></canvas>
    </div>
    <script>
        new Chart(document.getElementById('chart'), {{
            type: '{chart_type}',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{{
                    label: '{y_col}',
                    data: {json.dumps(values)},
                    backgroundColor: 'rgba(79, 70, 229, 0.7)',
                    borderColor: 'rgb(79, 70, 229)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    title: {{ display: true, text: '{y_col} by {x_col}' }}
                }}
            }}
        }});
    </script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description="Export data visualizations")
    parser.add_argument("data_file", help="CSV or JSON data file")
    parser.add_argument("--output", "-o", required=True, help="Output file path")
    parser.add_argument("--format", "-f", choices=["svg", "html"], default=None,
                        help="Output format (auto-detected from extension)")
    parser.add_argument("--type", "-t", choices=["bar", "line", "pie"], default="bar",
                        help="Chart type (default: bar)")
    parser.add_argument("--x", default=None, help="X-axis column")
    parser.add_argument("--y", default=None, help="Y-axis column")
    args = parser.parse_args()
    
    try:
        headers, data = load_data(args.data_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    x_col = args.x or headers[0]
    y_col = args.y or (headers[1] if len(headers) > 1 else headers[0])
    
    output_path = Path(args.output)
    format_type = args.format or output_path.suffix.lstrip(".").lower()
    
    if format_type == "svg":
        content = create_svg_bar_chart(data, x_col, y_col)
    elif format_type == "html":
        content = create_html_chart(data, x_col, y_col, args.type)
    else:
        print(f"❌ Unsupported format: {format_type}")
        print("   Supported: svg, html")
        return 1
    
    output_path.write_text(content)
    print(f"✅ Chart exported to: {output_path}")
    print(f"   Format: {format_type.upper()}")
    print(f"   Type: {args.type}")
    print(f"   Data: {x_col} vs {y_col} ({len(data)} points)")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
