#!/usr/bin/env python3
"""
Model Context Protocol Orchestrator

Thin orchestrator script providing CLI access to model_context_protocol module functionality.
Calls actual module functions from codomyrmex.model_context_protocol.

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
from codomyrmex.exceptions import ModelContextError, CodomyrmexError

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
            logger.info("Retrieving Model Context Protocol module information")

        info = {
            "module": "model_context_protocol",
            "description": "Standardized protocol for LLM tool interactions",
            "features": [
                "Schema definitions for MCP tools",
                "Tool specifications and validation",
                "Protocol enforcement",
                "Integration with all AI-enhanced modules",
            ],
            "api_location": "src/codomyrmex/model_context_protocol/",
            "note": "The MCP framework serves as the foundation for all AI-enhanced modules.",
        }

        print_section("Model Context Protocol Module Information")
        print("This module provides standardized protocol for LLM tool interactions.")
        print("")
        print("Key Features:")
        for feature in info["features"]:
            print(f"  - {feature}")
        print("")
        print(info["note"])
        print(f"See: {info['api_location']} for complete API")
        print_section("", separator="")

        output = getattr(args, "output", None)
        if output:
            output_path = save_json_file(info, output)
            if verbose:
                logger.info(f"Information saved to {output_path}")
            print_success(f"Information saved to {output_path}")

        return True

    except ModelContextError as e:
        logger.error(f"MCP error: {str(e)}")
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


def handle_list_tools(args):
    """Handle list tools command."""
    try:
        verbose = getattr(args, "verbose", False)
        if verbose:
            logger.info("Listing available MCP tools")

        # Try to import MCP tools if available
        try:
            from codomyrmex.model_context_protocol import get_mcp_tools
            tools = get_mcp_tools()

            print_section("Available MCP Tools")
            result = {"tools": [], "count": 0, "success": True}

            if isinstance(tools, dict):
                for tool_name, tool_info in tools.items():
                    print(f"  • {tool_name}")
                    tool_entry = {"name": tool_name}
                    if isinstance(tool_info, dict):
                        if "description" in tool_info:
                            desc = tool_info["description"]
                            print(f"    Description: {desc}")
                            tool_entry["description"] = desc
                        tool_entry.update(tool_info)
                    result["tools"].append(tool_entry)
                result["count"] = len(result["tools"])
            elif isinstance(tools, list):
                for tool in tools:
                    print(f"  • {tool}")
                    result["tools"].append(tool if isinstance(tool, dict) else {"name": str(tool)})
                result["count"] = len(result["tools"])
            else:
                print(format_output(tools, format_type="json"))
                result["tools"] = tools
                result["count"] = len(tools) if isinstance(tools, (list, dict)) else 1

            print_section("", separator="")

            if verbose:
                logger.info(f"Found {result['count']} MCP tools")

            output = getattr(args, "output", None)
            if output:
                output_path = save_json_file(result, output)
                if verbose:
                    logger.info(f"Results saved to {output_path}")
                print_success(f"Results saved to {output_path}")

            return True
        except ImportError:
            print_info("MCP tools not available in this module")
            print_section("", separator="")
            result = {"tools": [], "count": 0, "success": True, "note": "MCP tools not available"}
            output = getattr(args, "output", None)
            if output:
                output_path = save_json_file(result, output)
                if verbose:
                    logger.info(f"Results saved to {output_path}")
                print_success(f"Results saved to {output_path}")
            return True

    except ModelContextError as e:
        logger.error(f"MCP error: {str(e)}")
        print_error("Failed to list MCP tools", context=str(e), exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False
    except Exception as e:
        logger.exception("Unexpected error listing MCP tools")
        print_error("Unexpected error listing MCP tools", exception=e)
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Model Context Protocol operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s info
  %(prog)s list-tools --output tools.json --verbose
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

    # List tools command
    list_parser = subparsers.add_parser("list-tools", help="List available MCP tools")
    list_parser.add_argument("--output", "-o", help="Output file path for JSON results")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "info": handle_info,
        "list-tools": handle_list_tools,
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
