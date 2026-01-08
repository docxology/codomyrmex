#!/usr/bin/env python3
"""
Website Module Orchestrator

Thin orchestrator script providing CLI access to website module functionality.
Wraps existing website generation and serving scripts.
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
import subprocess
from pathlib import Path

# Import shared utilities
from codomyrmex.utils.cli_helpers import (
    format_output,
    print_error,
    print_section,
    print_success,
)

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

logger = get_logger(__name__)


def handle_generate(args):
    """Handle generate website command."""
    try:
        script_path = Path(__file__).parent / "generate.py"
        cmd = [sys.executable, str(script_path)]
        
        if args.output_dir:
            cmd.extend(["--output-dir", args.output_dir])
            
        if getattr(args, "verbose", False):
            logger.info(f"Running generate script: {' '.join(cmd)}")
            
        # Delegate to the existing script
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0

    except Exception as e:
        logger.exception("Unexpected error generating website")
        print_error("Unexpected error generating website", exception=e)
        return False


def handle_serve(args):
    """Handle serve website command."""
    try:
        script_path = Path(__file__).parent / "serve.py"
        cmd = [sys.executable, str(script_path)]
        
        if args.port:
            cmd.extend(["--port", str(args.port)])
        
        if args.directory:
            cmd.extend(["--directory", args.directory])
            
        if getattr(args, "verbose", False):
            logger.info(f"Running serve script: {' '.join(cmd)}")
            
        # Delegate to the existing script
        result = subprocess.run(cmd, capture_output=False)
        return result.returncode == 0

    except Exception as e:
        logger.exception("Unexpected error serving website")
        print_error("Unexpected error serving website", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Website operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate
  %(prog)s serve
  %(prog)s generate --output-dir ./site
  %(prog)s serve --port 9000
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate website")
    gen_parser.add_argument("--output-dir", help="Output directory")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Serve website")
    serve_parser.add_argument("--port", "-p", type=int, help="Port to serve on")
    serve_parser.add_argument("--directory", "-d", help="Directory to serve")
    
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "generate": handle_generate,
        "serve": handle_serve,
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