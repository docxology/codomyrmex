#!/usr/bin/env python3
"""
Code Execution Sandbox Orchestrator

Thin orchestrator script providing CLI access to code_execution_sandbox module functionality.
Calls actual module functions from codomyrmex.code_execution_sandbox.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import (
    CodeExecutionError,
    SandboxError,
    ContainerError,
    CodomyrmexError,
)

# Import shared utilities
try:
    from _orchestrator_utils import (
        determine_language_from_file,
        ensure_output_directory,
        print_error,
        print_section,
        print_success,
        save_json_file,
        validate_file_path,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from _orchestrator_utils import (
        determine_language_from_file,
        ensure_output_directory,
        print_error,
        print_section,
        print_success,
        save_json_file,
        validate_file_path,
    )

# Import module functions
from codomyrmex.code_execution_sandbox import execute_code

logger = get_logger(__name__)


def handle_execute(args):
    """Handle code execution command."""
    try:
        # Read code from file or use provided code
        if args.file:
            file_path = validate_file_path(args.file, must_exist=True, must_be_file=True)
            with open(file_path, encoding="utf-8") as f:
                code = f.read()
        elif args.code:
            code = args.code
        else:
            print_error("Either --file or --code must be provided")
            return False

        # Determine language from file extension or argument
        language = args.language
        if not language and args.file:
            language = determine_language_from_file(file_path)

        if not language:
            language = "python"  # Default

        if getattr(args, "verbose", False):
            logger.info(f"Executing {language} code (timeout: {args.timeout}s)")

        result = execute_code(
            code=code,
            language=language,
            timeout=args.timeout,
        )

        print_section("Execution Results")
        if result.get("success"):
            print_success("Execution succeeded")
            if result.get("output"):
                print("\nOutput:")
                print(result["output"])
            if result.get("exit_code") is not None:
                print(f"\nExit Code: {result['exit_code']}")
        else:
            print_error("Execution failed")
            if result.get("error"):
                print(f"\nError: {result['error']}")
            if result.get("stderr"):
                print(f"\nStderr: {result['stderr']}")
            if result.get("exit_code") is not None:
                print(f"\nExit Code: {result['exit_code']}")
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(result, args.output)
            print_success(f"Results saved to {output_path}")

        return result.get("success", False)

    except FileNotFoundError as e:
        logger.error(f"File not found: {args.file}")
        print_error("File not found", context=str(args.file))
        return False
    except (CodeExecutionError, SandboxError, ContainerError) as e:
        logger.error(f"Execution error: {str(e)}")
        print_error("Execution error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during code execution")
        print_error("Unexpected error during code execution", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Code Execution Sandbox operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s execute --file script.py
  %(prog)s execute --code "print('Hello, World!')" --language python
  %(prog)s execute --file script.js --language javascript --timeout 30
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Execute command
    exec_parser = subparsers.add_parser("execute", help="Execute code in sandbox")
    exec_parser.add_argument(
        "--file", "-f", help="File containing code to execute"
    )
    exec_parser.add_argument(
        "--code", "-c", help="Code to execute (inline)"
    )
    exec_parser.add_argument(
        "--language", "-l", help="Programming language (python, javascript, etc.)"
    )
    exec_parser.add_argument(
        "--timeout", "-t", type=int, default=30, help="Execution timeout in seconds"
    )
    exec_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "execute": handle_execute,
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

