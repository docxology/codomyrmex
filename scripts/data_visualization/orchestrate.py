#!/usr/bin/env python3
"""
Data Visualization Orchestrator

Thin orchestrator script providing CLI access to data_visualization module functionality.
Calls actual module functions from codomyrmex.data_visualization.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import PlottingError, VisualizationError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        ensure_output_directory,
        load_json_file,
        print_error,
        print_section,
        print_success,
        validate_file_path,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        ensure_output_directory,
        load_json_file,
        print_error,
        print_section,
        print_success,
        validate_file_path,
    )

# Import module functions
from codomyrmex.data_visualization import (
    create_bar_chart,
    create_heatmap,
    create_histogram,
    create_line_plot,
    create_pie_chart,
    create_scatter_plot,
    create_git_tree_mermaid,
    create_git_tree_png,
    visualize_git_repository,
)

logger = get_logger(__name__)


def parse_data_file(file_path: Path):
    """Parse data from JSON file."""
    return load_json_file(file_path)


def handle_line_plot(args):
    """Handle line plot creation."""
    try:
        # Ensure output directory exists
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Creating line plot: {output_path}")

        # Parse data if provided
        if args.data_file:
            data = parse_data_file(Path(args.data_file))
            x = data.get("x", [])
            y = data.get("y", [])
        else:
            # Use provided values or default
            x = args.x if args.x else list(range(10))
            y = args.y if args.y else [i**2 for i in x]

        create_line_plot(
            x=x,
            y=y,
            title=args.title,
            output_path=str(output_path),
        )

        print_success(f"Line plot created", context=str(output_path))
        return True

    except (VisualizationError, PlottingError) as e:
        logger.error(f"Visualization error: {str(e)}")
        print_error("Visualization error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during line plot creation")
        print_error("Unexpected error during line plot creation", exception=e)
        return False


def handle_scatter_plot(args):
    """Handle scatter plot creation."""
    try:
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Creating scatter plot: {output_path}")

        if args.data_file:
            data = parse_data_file(Path(args.data_file))
            x = data.get("x", [])
            y = data.get("y", [])
        else:
            x = args.x if args.x else list(range(10))
            y = args.y if args.y else [i**2 for i in x]

        create_scatter_plot(
            x=x,
            y=y,
            title=args.title,
            output_path=str(output_path),
        )

        print_success(f"Scatter plot created", context=str(output_path))
        return True

    except (VisualizationError, PlottingError) as e:
        logger.error(f"Visualization error: {str(e)}")
        print_error("Visualization error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during scatter plot creation")
        print_error("Unexpected error during scatter plot creation", exception=e)
        return False


def handle_bar_chart(args):
    """Handle bar chart creation."""
    try:
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Creating bar chart: {output_path}")

        if args.data_file:
            data = parse_data_file(Path(args.data_file))
            x = data.get("x", [])
            y = data.get("y", [])
        else:
            x = args.x if args.x else list(range(10))
            y = args.y if args.y else [i**2 for i in x]

        create_bar_chart(
            x=x,
            y=y,
            title=args.title,
            output_path=str(output_path),
        )

        print_success(f"Bar chart created", context=str(output_path))
        return True

    except (VisualizationError, PlottingError) as e:
        logger.error(f"Visualization error: {str(e)}")
        print_error("Visualization error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during bar chart creation")
        print_error("Unexpected error during bar chart creation", exception=e)
        return False


def handle_histogram(args):
    """Handle histogram creation."""
    try:
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Creating histogram: {output_path}")

        if args.data_file:
            data = parse_data_file(Path(args.data_file))
            values = data.get("values", [])
        else:
            values = args.values if args.values else list(range(100))

        create_histogram(
            values=values,
            title=args.title,
            output_path=str(output_path),
        )

        print_success(f"Histogram created", context=str(output_path))
        return True

    except (VisualizationError, PlottingError) as e:
        logger.error(f"Visualization error: {str(e)}")
        print_error("Visualization error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during histogram creation")
        print_error("Unexpected error during histogram creation", exception=e)
        return False


def handle_pie_chart(args):
    """Handle pie chart creation."""
    try:
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Creating pie chart: {output_path}")

        if args.data_file:
            data = parse_data_file(Path(args.data_file))
            labels = data.get("labels", [])
            values = data.get("values", [])
        else:
            labels = args.labels if args.labels else ["A", "B", "C", "D"]
            values = args.values if args.values else [30, 25, 20, 25]

        create_pie_chart(
            labels=labels,
            values=values,
            title=args.title,
            output_path=str(output_path),
        )

        print_success(f"Pie chart created", context=str(output_path))
        return True

    except (VisualizationError, PlottingError) as e:
        logger.error(f"Visualization error: {str(e)}")
        print_error("Visualization error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during pie chart creation")
        print_error("Unexpected error during pie chart creation", exception=e)
        return False


def handle_heatmap(args):
    """Handle heatmap creation."""
    try:
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Creating heatmap: {output_path}")

        if args.data_file:
            data = parse_data_file(Path(args.data_file))
            matrix = data.get("matrix", [])
        else:
            # Create sample matrix
            import numpy as np

            matrix = np.random.rand(10, 10).tolist()

        create_heatmap(
            data=matrix,
            title=args.title,
            output_path=str(output_path),
        )

        print_success(f"Heatmap created", context=str(output_path))
        return True

    except (VisualizationError, PlottingError) as e:
        logger.error(f"Visualization error: {str(e)}")
        print_error("Visualization error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during heatmap creation")
        print_error("Unexpected error during heatmap creation", exception=e)
        return False


def handle_git_visualize(args):
    """Handle git repository visualization."""
    try:
        repo_path = args.repo if args.repo else "."
        output_dir = args.output if args.output else "./git_analysis"

        if getattr(args, "verbose", False):
            logger.info(f"Visualizing git repository: {repo_path}")
            logger.info(f"Output directory: {output_dir}")

        # Ensure output directory exists
        ensure_output_directory(Path(output_dir) / "dummy")

        result = visualize_git_repository(repo_path, output_dir=output_dir)

        if result:
            print_success(f"Git visualization complete", context=f"Check {output_dir}/ for results")
            return True
        else:
            print_error("Git visualization failed")
            return False

    except Exception as e:
        logger.exception("Unexpected error during git visualization")
        print_error("Unexpected error during git visualization", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Data Visualization operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s line-plot --output output/line.png --title "My Line Plot"
  %(prog)s scatter-plot --data-file data.json --output output/scatter.png
  %(prog)s bar-chart --output output/bar.png --title "Bar Chart"
  %(prog)s histogram --output output/hist.png --title "Distribution"
  %(prog)s pie-chart --output output/pie.png --title "Pie Chart"
  %(prog)s heatmap --output output/heat.png --title "Heatmap"
  %(prog)s git-visualize --repo . --output ./git_analysis
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Common arguments
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--output", "-o", default="output/plot.png", help="Output file path"
    )
    common_parser.add_argument("--title", "-t", help="Plot title")
    common_parser.add_argument(
        "--data-file", "-d", help="JSON file with data (x, y arrays)"
    )

    # Line plot
    line_parser = subparsers.add_parser(
        "line-plot", parents=[common_parser], help="Create line plot"
    )
    line_parser.add_argument("--x", nargs="+", type=float, help="X values")
    line_parser.add_argument("--y", nargs="+", type=float, help="Y values")

    # Scatter plot
    scatter_parser = subparsers.add_parser(
        "scatter-plot", parents=[common_parser], help="Create scatter plot"
    )
    scatter_parser.add_argument("--x", nargs="+", type=float, help="X values")
    scatter_parser.add_argument("--y", nargs="+", type=float, help="Y values")

    # Bar chart
    bar_parser = subparsers.add_parser(
        "bar-chart", parents=[common_parser], help="Create bar chart"
    )
    bar_parser.add_argument("--x", nargs="+", help="X labels")
    bar_parser.add_argument("--y", nargs="+", type=float, help="Y values")

    # Histogram
    hist_parser = subparsers.add_parser(
        "histogram", parents=[common_parser], help="Create histogram"
    )
    hist_parser.add_argument("--values", nargs="+", type=float, help="Values")

    # Pie chart
    pie_parser = subparsers.add_parser(
        "pie-chart", parents=[common_parser], help="Create pie chart"
    )
    pie_parser.add_argument("--labels", nargs="+", help="Labels")
    pie_parser.add_argument("--values", nargs="+", type=float, help="Values")

    # Heatmap
    heat_parser = subparsers.add_parser(
        "heatmap", parents=[common_parser], help="Create heatmap"
    )

    # Git visualize
    git_parser = subparsers.add_parser("git-visualize", help="Visualize git repository")
    git_parser.add_argument("--repo", default=".", help="Repository path")
    git_parser.add_argument(
        "--output", "-o", default="./git_analysis", help="Output directory"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "line-plot": handle_line_plot,
        "scatter-plot": handle_scatter_plot,
        "bar-chart": handle_bar_chart,
        "histogram": handle_histogram,
        "pie-chart": handle_pie_chart,
        "heatmap": handle_heatmap,
        "git-visualize": handle_git_visualize,
    }

    handler = handlers.get(args.command)
    if handler:
        success = handler(args)
        return 0 if success else 1
    else:
        print_error("Unknown command", context=args.command)
        return 1


if __name__ == "__main__":
    sys.exit(main())

