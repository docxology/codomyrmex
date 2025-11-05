#!/usr/bin/env python3
"""
Language Models Orchestrator

Thin orchestrator script providing CLI access to language_models module functionality.
Calls actual module functions from codomyrmex.language_models.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.language_models.ollama_client import OllamaError

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

# Import module functions
from codomyrmex.language_models import (
    check_ollama_availability,
    get_available_models,
    get_config,
)

logger = get_logger(__name__)


def handle_check_availability(args):
    """Handle check availability command."""
    try:
        verbose = getattr(args, "verbose", False)
        if verbose:
            logger.info("Checking Ollama availability")

        available = check_ollama_availability()

        print_section("Ollama Availability Check")
        if available:
            print_success("Ollama is available")
        else:
            print_error("Ollama is not available")
        print_section("", separator="")

        result = {"available": available, "success": True}
        output = getattr(args, "output", None)
        if output:
            output_path = save_json_file(result, output)
            if verbose:
                logger.info(f"Results saved to {output_path}")
            print_success(f"Results saved to {output_path}")

        return available

    except OllamaError as e:
        logger.error(f"Ollama error: {str(e)}")
        print_error("Ollama availability check failed", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error checking Ollama availability")
        print_error("Unexpected error checking Ollama availability", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def handle_list_models(args):
    """Handle list models command."""
    try:
        verbose = getattr(args, "verbose", False)
        if verbose:
            logger.info("Listing available models")

        models = get_available_models()

        print_section("Available Models")
        if models:
            for model in models:
                print(f"  • {model}")
            if verbose:
                logger.info(f"Found {len(models)} models")
        else:
            print_info("No models available")
            if verbose:
                logger.info("No models found")
        print_section("", separator="")

        result = {"models": models, "count": len(models) if models else 0, "success": True}
        output = getattr(args, "output", None)
        if output:
            output_path = save_json_file(result, output)
            if verbose:
                logger.info(f"Results saved to {output_path}")
            print_success(f"Results saved to {output_path}")

        return True

    except OllamaError as e:
        logger.error(f"Ollama error: {str(e)}")
        print_error("Failed to list models", context=str(e), exception=e)
        if verbose:
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error listing models")
        print_error("Unexpected error listing models", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def handle_config(args):
    """Handle show config command."""
    try:
        verbose = getattr(args, "verbose", False)
        if verbose:
            logger.info("Retrieving language models configuration")

        config = get_config()

        print_section("Language Models Configuration")
        print(format_output(config, format_type="json"))
        print_section("", separator="")

        output = getattr(args, "output", None)
        if output:
            output_path = save_json_file(config, output)
            if verbose:
                logger.info(f"Configuration saved to {output_path}")
            print_success(f"Configuration saved to {output_path}")

        return True

    except CodomyrmexError as e:
        logger.error(f"Configuration error: {str(e)}")
        print_error("Failed to get configuration", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error getting config")
        print_error("Unexpected error getting config", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Language Models operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s check-availability
  %(prog)s list-models
  %(prog)s config --output config.json
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

    # Check availability command
    check_parser = subparsers.add_parser("check-availability", help="Check Ollama availability")
    check_parser.add_argument("--output", "-o", help="Output file path for JSON results")

    # List models command
    list_parser = subparsers.add_parser("list-models", help="List available models")
    list_parser.add_argument("--output", "-o", help="Output file path for JSON results")

    # Config command
    config_parser = subparsers.add_parser("config", help="Show configuration")
    config_parser.add_argument("--output", "-o", help="Output file path for JSON results")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "check-availability": handle_check_availability,
        "list-models": handle_list_models,
        "config": handle_config,
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

