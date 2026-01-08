#!/usr/bin/env python3
"""
AI Code Editing Orchestrator

Thin orchestrator script providing CLI access to ai_code_editing module functionality.
Calls actual module functions from codomyrmex.agents.ai_code_editing.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to Python path for codomyrmex imports
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent
_SRC_DIR = _REPO_ROOT / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

# Import logging setup
try:
    from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger
except ImportError:
    # Fallback if module not available
    def setup_logging(): pass
    def get_logger(name):
        import logging
        return logging.getLogger(name)

# Import module-specific exceptions
from codomyrmex.exceptions import (
    AIProviderError,
    CodeEditingError,
    CodeGenerationError,
    CodomyrmexError,
)

# Import shared utilities
try:
    from _orchestrator_utils import (
        determine_language_from_file,
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        validate_file_path,
    )
except ImportError:
    # Fallback if running from different directory
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        determine_language_from_file,
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        validate_file_path,
    )

# Import module functions
from codomyrmex.agents.ai_code_editing import (
    analyze_code_quality,
    generate_code_snippet,
    get_available_models,
    get_supported_languages,
    get_supported_providers,
    refactor_code_snippet,
    validate_api_keys,
)

logger = get_logger(__name__)


def handle_generate(args):
    """Handle code generation command."""
    try:
        if getattr(args, "verbose", False):
            logger.info(f"Generating code with prompt: {args.prompt[:50]}...")
            logger.info(f"Language: {args.language}, Provider: {args.provider}")

        result = generate_code_snippet(
            prompt=args.prompt,
            language=args.language,
            provider=args.provider,
        )

        if result.get("status") == "success":
            print_section("Generated code")
            print(result.get("generated_code", ""))
            print_section("", separator="")
            print_success(f"Code generated successfully")
            return True
        else:
            error_msg = result.get("error_message", "Unknown error")
            logger.error(f"Code generation failed: {error_msg}")
            print_error("Code generation failed", context=error_msg)
            return False

    except (CodeGenerationError, AIProviderError) as e:
        logger.error(f"Code generation error: {str(e)}")
        print_error("Code generation error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during code generation")
        print_error("Unexpected error during code generation", exception=e)
        return False


def handle_refactor(args):
    """Handle code refactoring command."""
    try:
        # Validate and read the file
        file_path = validate_file_path(args.file, must_exist=True, must_be_file=True)

        if getattr(args, "verbose", False):
            logger.info(f"Refactoring file: {file_path}")
            logger.info(f"Instruction: {args.instruction}")

        with open(file_path, encoding="utf-8") as f:
            code = f.read()

        # Determine language from file extension
        language = determine_language_from_file(file_path)

        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would refactor {file_path} with language {language}")
            return True

        result = refactor_code_snippet(
            code_snippet=code,
            refactoring_instruction=args.instruction,
            language=language,
        )

        if result.get("status") in ["success", "no_change_needed"]:
            print_section("Refactored code")
            print(result.get("refactored_code", ""))
            print_section("", separator="")
            if result.get("explanation"):
                print(f"Explanation: {result['explanation']}")
            print_success(f"Code refactored successfully")
            return True
        else:
            error_msg = result.get("error_message", "Unknown error")
            logger.error(f"Refactoring failed: {error_msg}")
            print_error("Refactoring failed", context=error_msg)
            return False

    except FileNotFoundError as e:
        logger.error(f"File not found: {args.file}")
        print_error("File not found", context=str(args.file))
        return False
    except (CodeEditingError, AIProviderError) as e:
        logger.error(f"Refactoring error: {str(e)}")
        print_error("Refactoring error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error during refactoring")
        print_error("Unexpected error during refactoring", exception=e)
        return False


def handle_analyze(args):
    """Handle code analysis command."""
    try:
        file_path = validate_file_path(args.file, must_exist=True, must_be_file=True)

        if getattr(args, "verbose", False):
            logger.info(f"Analyzing file: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            code = f.read()

        result = analyze_code_quality(code)

        print_section("Code Analysis Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        # Save output if requested
        if hasattr(args, "output") and args.output:
            from _orchestrator_utils import save_json_file
            output_path = save_json_file(result, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except FileNotFoundError as e:
        logger.error(f"File not found: {args.file}")
        print_error("File not found", context=str(args.file))
        return False
    except Exception as e:
        logger.exception("Unexpected error during analysis")
        print_error("Unexpected error during analysis", exception=e)
        return False


def handle_validate_api_keys(args):
    """Handle API key validation command."""
    try:
        result = validate_api_keys()

        print_section("API Key Validation Results")
        all_valid = True
        for provider, status in result.items():
            is_valid = status.get("valid", False)
            message = status.get("message", "Unknown")
            if is_valid:
                print_success(f"{provider}: {message}")
            else:
                print_error(f"{provider}: {message}")
                all_valid = False
        print_section("", separator="")

        if all_valid:
            print_success("All API keys are valid")
        else:
            print_error("Some API keys are invalid or missing")
        return all_valid

    except Exception as e:
        logger.exception("Unexpected error during API key validation")
        print_error("Unexpected error during API key validation", exception=e)
        return False


def handle_list_providers(args):
    """Handle list providers command."""
    try:
        providers = get_supported_providers()
        print_section("Supported LLM Providers")
        for provider in providers:
            print(f"  • {provider}")
        print_section("", separator="")
        return True

    except Exception as e:
        logger.exception("Unexpected error listing providers")
        print_error("Unexpected error listing providers", exception=e)
        return False


def handle_list_languages(args):
    """Handle list languages command."""
    try:
        languages = get_supported_languages()
        print_section("Supported Programming Languages")
        for language in languages:
            print(f"  • {language}")
        print_section("", separator="")
        return True

    except Exception as e:
        logger.exception("Unexpected error listing languages")
        print_error("Unexpected error listing languages", exception=e)
        return False


def handle_list_models(args):
    """Handle list models command."""
    try:
        models = get_available_models(provider=args.provider)
        print_section(f"Available Models for {args.provider}")
        for model in models:
            print(f"  • {model}")
        print_section("", separator="")
        return True

    except Exception as e:
        logger.exception("Unexpected error listing models")
        print_error("Unexpected error listing models", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="AI Code Editing operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate "create a fibonacci function" --language python
  %(prog)s refactor file.py "optimize for performance"
  %(prog)s analyze file.py
  %(prog)s validate-api-keys
  %(prog)s list-providers
  %(prog)s list-languages
  %(prog)s list-models --provider openai
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Dry run mode (no changes)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate code snippet")
    gen_parser.add_argument("prompt", help="Code generation prompt")
    gen_parser.add_argument(
        "--language", "-l", default="python", help="Programming language"
    )
    gen_parser.add_argument(
        "--provider", "-p", default="openai", help="LLM provider"
    )

    # Refactor command
    ref_parser = subparsers.add_parser("refactor", help="Refactor code")
    ref_parser.add_argument("file", help="File to refactor")
    ref_parser.add_argument("instruction", help="Refactoring instruction")
    ref_parser.add_argument("--output", "-o", help="Output file path (optional)")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze code quality")
    analyze_parser.add_argument("file", help="File to analyze")
    analyze_parser.add_argument("--output", "-o", help="Output file path for results (JSON)")

    # Validate API keys command
    subparsers.add_parser("validate-api-keys", help="Validate API keys")

    # List providers command
    subparsers.add_parser("list-providers", help="List supported providers")

    # List languages command
    subparsers.add_parser("list-languages", help="List supported languages")

    # List models command
    models_parser = subparsers.add_parser("list-models", help="List available models")
    models_parser.add_argument(
        "--provider", "-p", default="openai", help="LLM provider"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "generate": handle_generate,
        "refactor": handle_refactor,
        "analyze": handle_analyze,
        "validate-api-keys": handle_validate_api_keys,
        "list-providers": handle_list_providers,
        "list-languages": handle_list_languages,
        "list-models": handle_list_models,
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

