#!/usr/bin/env python3
"""
Ollama Integration Orchestrator

Main orchestrator for Ollama LLM integration workflows.
Provides CLI access to Ollama integration functionality.
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import CodomyrmexError

# Define Ollama-specific exceptions (previously from language_models module)
class OllamaError(CodomyrmexError):
    """Base exception for Ollama operations."""
    pass

class OllamaConnectionError(OllamaError):
    """Raised when connection to Ollama fails."""
    pass

class OllamaTimeoutError(OllamaError):
    """Raised when Ollama operation times out."""
    pass

class OllamaModelError(OllamaError):
    """Raised when there's an issue with the Ollama model."""
    pass

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        save_json_file,
    )
except ImportError:
    # Fallback if running from different directory
    sys.path.insert(0, str(Path(__file__).parent))
    from _orchestrator_utils import (
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
            logger.info("Retrieving Ollama integration information")

        info = {
            "module": "ollama_integration",
            "description": "Ollama LLM integration workflows and examples",
            "available_scripts": [
                {"name": "basic_usage.py", "description": "Simple usage examples"},
                {"name": "integration_demo.py", "description": "Comprehensive demo"},
                {"name": "model_management.py", "description": "Model management"},
            ],
            "location": "scripts/ollama_integration/",
        }

        print_section("Ollama Integration Orchestrator")
        print("Main orchestrator for Ollama LLM integration workflows.")
        print("")
        print("Available scripts:")
        for script in info["available_scripts"]:
            print(f"  • {script['name']} - {script['description']}")
        print("")
        print(f"Location: {info['location']}")
        print_section("", separator="")

        output = getattr(args, "output", None)
        if output:
            output_path = save_json_file(info, output)
            if verbose:
                logger.info(f"Information saved to {output_path}")
            print_success(f"Information saved to {output_path}")

        return True

    except OllamaError as e:
        logger.error(f"Ollama error: {str(e)}")
        print_error("Failed to retrieve integration information", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except CodomyrmexError as e:
        logger.error(f"Codomyrmex error: {str(e)}")
        print_error("Failed to retrieve integration information", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error retrieving integration information")
        print_error("Unexpected error retrieving integration information", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Ollama Integration operations",
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
    info_parser = subparsers.add_parser("info", help="Show integration information")
    info_parser.add_argument("--output", "-o", help="Output file path for JSON results")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

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
