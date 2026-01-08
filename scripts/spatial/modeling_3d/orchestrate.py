#!/usr/bin/env python3
"""
3D Modeling Orchestrator

Thin orchestrator script providing CLI access to spatial module functionality.
Calls actual module functions from codomyrmex.spatial.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import Modeling3DError, CodomyrmexError

# Import shared utilities
from codomyrmex.utils.cli_helpers import (
    format_output,
    print_error,
    print_info,
    print_section,
    print_success,
    save_json_file,
)

logger = get_logger(__name__)


def handle_info(args):
    """Handle info command."""
    try:
        verbose = getattr(args, "verbose", False)
        if verbose:
            logger.info("Retrieving 3D Modeling module information")

        info = {
            "module": "spatial",
            "description": "3D modeling, rendering, and AR/VR/XR capabilities",
            "components": [
                {"name": "Scene3D", "description": "3D scene management"},
                {"name": "Object3D", "description": "3D object handling"},
                {"name": "Camera3D", "description": "Camera controls"},
                {"name": "ARSession", "description": "AR session management"},
                {"name": "VRRenderer", "description": "VR rendering"},
                {"name": "RenderPipeline", "description": "Rendering pipeline"},
            ],
            "api_location": "src/codomyrmex/spatial/",
        }

        print_section("3D Modeling Module Information")
        print("This module provides 3D modeling, rendering, and AR/VR/XR capabilities.")
        print("")
        print("Available Components:")
        for component in info["components"]:
            print(f"  - {component['name']}: {component['description']}")
        print("")
        print(f"See: {info['api_location']} for complete API")
        print_section("", separator="")

        output = getattr(args, "output", None)
        if output:
            output_path = save_json_file(info, output)
            if verbose:
                logger.info(f"Information saved to {output_path}")
            print_success(f"Information saved to {output_path}")

        return True

    except Modeling3DError as e:
        logger.error(f"Modeling error: {str(e)}")
        print_error("Failed to retrieve module information", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except CodomyrmexError as e:
        logger.error(f"Codomyrmex error: {str(e)}")
        print_error("Failed to retrieve module information", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error retrieving module information")
        print_error("Unexpected error retrieving module information", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="3D Modeling operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s info
  %(prog)s info --output info.json --verbose
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--output", "-o", help="Output file path for JSON results"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show module information")
    info_parser.add_argument("--output", "-o", help="Output file path for JSON results")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "info": handle_info,
    }

    handler = handlers.get(args.command)
    if handler:
        success = handler(args)
        return 0 if success else 1
    else:
        print_error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
