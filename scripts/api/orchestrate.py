#!/usr/bin/env python3
"""
Title: API Module CLI
API Module Orchestrator

Thin orchestrator script providing CLI access to api module functionality.
Calls actual module functions from codomyrmex.api.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys
from pathlib import Path

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        ensure_output_directory,
        format_output,
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
        format_output,
        load_json_file,
        print_error,
        print_section,
        print_success,
        validate_file_path,
    )

# Import module functions
from codomyrmex.api.documentation import (
    extract_api_specs,
    generate_api_docs,
    generate_openapi_spec,
    validate_openapi_spec,
)

logger = get_logger(__name__)


def handle_generate_docs(args):
    """Handle generate API docs command."""
    try:
        # Validate source path exists
        source_path = validate_file_path(args.source, must_exist=True)
        # Ensure output directory exists
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Generating API documentation from {source_path} to {output_path}")

        result = generate_api_docs(
            source_path=str(source_path),
            output_path=str(output_path),
        )

        print_section("API Documentation Generation")
        if isinstance(result, dict):
            print(format_output(result, format_type="json"))
            success = result.get("success", False)
        else:
            print(format_output(result))
            success = bool(result)
        print_section("", separator="")

        if success:
            print_success("API documentation generated", context=str(output_path))
        else:
            print_error("API documentation generation failed")
        return success

    except CodomyrmexError as e:
        logger.error(f"API documentation error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("API documentation error", context=str(e), exception=e)
        return False
    except FileNotFoundError as e:
        logger.error(f"Source path not found: {args.source}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Source path not found", context=args.source, exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error generating API docs")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error generating API docs", exception=e)
        return False


def handle_extract_specs(args):
    """Handle extract API specs command."""
    try:
        # Validate source path exists
        source_path = validate_file_path(args.source, must_exist=True)

        if getattr(args, "verbose", False):
            logger.info(f"Extracting API specifications from {source_path}")

        result = extract_api_specs(source_path=str(source_path))

        print_section("API Specifications Extracted")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        print_success("API specifications extracted")
        return True

    except CodomyrmexError as e:
        logger.error(f"API documentation error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("API documentation error", context=str(e), exception=e)
        return False
    except FileNotFoundError as e:
        logger.error(f"Source path not found: {args.source}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Source path not found", context=args.source, exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error extracting API specs")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error extracting API specs", exception=e)
        return False


def handle_generate_openapi(args):
    """Handle generate OpenAPI spec command."""
    try:
        # Validate source path exists
        source_path = validate_file_path(args.source, must_exist=True)
        # Ensure output directory exists
        output_path = ensure_output_directory(args.output)

        if getattr(args, "verbose", False):
            logger.info(f"Generating OpenAPI spec from {source_path} to {output_path}")

        result = generate_openapi_spec(
            source_path=str(source_path),
            output_path=str(output_path),
        )

        print_section("OpenAPI Specification Generated")
        if isinstance(result, dict):
            print(format_output(result, format_type="json"))
            success = result.get("success", False)
        else:
            print(format_output(result))
            success = bool(result)
        print_section("", separator="")

        if success:
            print_success("OpenAPI spec generated", context=str(output_path))
        else:
            print_error("OpenAPI spec generation failed")
        return success

    except CodomyrmexError as e:
        logger.error(f"API documentation error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("API documentation error", context=str(e), exception=e)
        return False
    except FileNotFoundError as e:
        logger.error(f"Source path not found: {args.source}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Source path not found", context=args.source, exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error generating OpenAPI spec")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error generating OpenAPI spec", exception=e)
        return False


def handle_validate_openapi(args):
    """Handle validate OpenAPI spec command."""
    try:
        # Validate spec file exists
        spec_path = validate_file_path(args.spec, must_exist=True, must_be_file=True)

        if getattr(args, "verbose", False):
            logger.info(f"Validating OpenAPI spec: {spec_path}")

        spec = load_json_file(spec_path)
        result = validate_openapi_spec(spec)

        print_section("OpenAPI Specification Validation")
        if isinstance(result, dict):
            print(format_output(result, format_type="json"))
            valid = result.get("valid", False)
        else:
            print(format_output(result))
            valid = bool(result)
        print_section("", separator="")

        if valid:
            print_success("OpenAPI spec is valid")
        else:
            print_error("OpenAPI spec is invalid")
        return valid

    except FileNotFoundError as e:
        logger.error(f"Spec file not found: {args.spec}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Spec file not found", context=args.spec, exception=e)
        return False
    except CodomyrmexError as e:
        logger.error(f"API documentation error: {str(e)}")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("API documentation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error validating OpenAPI spec")
        if getattr(args, "verbose", False):
            logger.exception("Detailed error information:")
        print_error("Unexpected error validating OpenAPI spec", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="API Documentation operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate-docs --source src/ --output docs/api/
  %(prog)s extract-specs --source src/
  %(prog)s generate-openapi --source src/ --output openapi.json
  %(prog)s validate-openapi --spec openapi.json
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate docs command
    gen_parser = subparsers.add_parser("generate-docs", help="Generate API documentation")
    gen_parser.add_argument("--source", "-s", required=True, help="Source code path")
    gen_parser.add_argument("--output", "-o", required=True, help="Output directory")

    # Extract specs command
    extract_parser = subparsers.add_parser("extract-specs", help="Extract API specifications")
    extract_parser.add_argument("--source", "-s", required=True, help="Source code path")

    # Generate OpenAPI command
    openapi_parser = subparsers.add_parser("generate-openapi", help="Generate OpenAPI specification")
    openapi_parser.add_argument("--source", "-s", required=True, help="Source code path")
    openapi_parser.add_argument("--output", "-o", required=True, help="Output file path")

    # Validate OpenAPI command
    validate_parser = subparsers.add_parser("validate-openapi", help="Validate OpenAPI specification")
    validate_parser.add_argument("--spec", "-s", required=True, help="OpenAPI spec file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "generate-docs": handle_generate_docs,
        "extract-specs": handle_extract_specs,
        "generate-openapi": handle_generate_openapi,
        "validate-openapi": handle_validate_openapi,
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

