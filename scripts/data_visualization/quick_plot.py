#!/usr/bin/env python3
"""
Create quick plots from CSV/JSON data files.

Usage:
    python quick_plot.py <data_file> [--type TYPE] [--x X] [--y Y] [--output OUTPUT]
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
import csv


def load_data(file_path: str) -> tuple:
    """Load data from CSV or JSON file. Returns (headers, rows)."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    suffix = path.suffix.lower()
    
    if suffix == ".csv":
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                return [], []
            headers = list(rows[0].keys())
            return headers, rows
    
    elif suffix == ".json":
        with open(path, "r") as f:
            data = json.load(f)
            if isinstance(data, list) and data:
                headers = list(data[0].keys())
                return headers, data
            raise ValueError("JSON must be an array of objects")
    
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def create_text_plot(data: list, x_col: str, y_col: str, plot_type: str, width: int = 60, height: int = 15) -> str:
    """Create a simple ASCII visualization."""
    x_values = [row.get(x_col, "") for row in data]
    y_values = []
    for row in data:
        try:
            y_values.append(float(row.get(y_col, 0)))
        except (ValueError, TypeError):
            y_values.append(0)
    
    if not y_values:
        return "No data to plot"
    
    max_y = max(y_values) if max(y_values) > 0 else 1
    min_y = min(y_values)
    y_range = max_y - min_y if max_y != min_y else 1
    
    output = []
    output.append(f"\n📊 {plot_type.upper()} Plot: {y_col} by {x_col}\n")
    output.append(f"   Max: {max_y:.2f}")
    
    if plot_type == "bar":
        # Horizontal bar chart
        max_label_len = min(15, max(len(str(x)) for x in x_values))
        bar_width = width - max_label_len - 10
        
        for x, y in zip(x_values, y_values):
            bar_len = int((y - min_y) / y_range * bar_width) if y_range > 0 else 0
            bar = "█" * bar_len
            label = str(x)[:max_label_len].ljust(max_label_len)
            output.append(f"   {label} │{bar} {y:.1f}")
    
    elif plot_type == "line":
        # ASCII line chart
        chart = [[" " for _ in range(len(y_values))] for _ in range(height)]
        
        for i, y in enumerate(y_values):
            row = int((1 - (y - min_y) / y_range) * (height - 1)) if y_range > 0 else height // 2
            row = max(0, min(height - 1, row))
            chart[row][i] = "●"
        
        for row_idx, row in enumerate(chart):
            y_label = f"{max_y - (row_idx / (height - 1)) * y_range:.1f}".rjust(8)
            output.append(f"{y_label} │{''.join(row)}")
        
        output.append(" " * 9 + "└" + "─" * len(y_values))
    
    elif plot_type == "scatter":
        # ASCII scatter plot
        chart = [[" " for _ in range(width)] for _ in range(height)]
        
        try:
            x_nums = [float(x) for x in x_values]
            x_min, x_max = min(x_nums), max(x_nums)
            x_range = x_max - x_min if x_max != x_min else 1
            
            for x, y in zip(x_nums, y_values):
                col = int((x - x_min) / x_range * (width - 1)) if x_range > 0 else width // 2
                row = int((1 - (y - min_y) / y_range) * (height - 1)) if y_range > 0 else height // 2
                col = max(0, min(width - 1, col))
                row = max(0, min(height - 1, row))
                chart[row][col] = "●"
            
            for row in chart:
                output.append("   │" + "".join(row))
            output.append("   └" + "─" * width)
        except ValueError:
            output.append("   (Scatter requires numeric X values)")
    
    output.append(f"\n   Data points: {len(data)}")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Create quick plots from data files")
    parser.add_argument("data_file", help="CSV or JSON data file")
    parser.add_argument("--type", "-t", choices=["line", "bar", "scatter"], default="bar",
                        help="Plot type (default: bar)")
    parser.add_argument("--x", default=None, help="X-axis column name")
    parser.add_argument("--y", default=None, help="Y-axis column name")
    parser.add_argument("--list-columns", "-l", action="store_true",
                        help="List available columns")
    args = parser.parse_args()
    
    try:
        headers, data = load_data(args.data_file)
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return 1
    
    if args.list_columns or not headers:
        print(f"📋 Available columns in {args.data_file}:")
        for h in headers:
            sample = data[0].get(h, "") if data else ""
            print(f"   - {h}: {str(sample)[:30]}...")
        return 0
    
    # Auto-select columns if not specified
    x_col = args.x or headers[0]
    y_col = args.y or (headers[1] if len(headers) > 1 else headers[0])
    
    if x_col not in headers:
        print(f"❌ Column not found: {x_col}")
        print(f"   Available: {', '.join(headers)}")
        return 1
    
    if y_col not in headers:
        print(f"❌ Column not found: {y_col}")
        print(f"   Available: {', '.join(headers)}")
        return 1
    
    plot = create_text_plot(data, x_col, y_col, args.type)
    print(plot)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
