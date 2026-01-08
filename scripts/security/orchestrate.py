#!/usr/bin/env python3
"""
Security Module Orchestrator

Thin orchestrator script providing CLI access to security module functionality.
Calls actual module functions from codomyrmex.security.

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
        format_output,
        print_error,
        print_section,
        print_success,
        save_json_file,
        validate_file_path,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
        save_json_file,
        validate_file_path,
    )

# Import module functions
from codomyrmex.security import (
    audit_code_security,
    check_compliance,
    generate_security_report,
    scan_vulnerabilities,
)

logger = get_logger(__name__)


def handle_scan_vulnerabilities(args):
    """Handle scan vulnerabilities command."""
    try:
        target_path = validate_file_path(
            args.path if args.path else ".",
            must_exist=True,
            must_be_dir=True,
        )

        if getattr(args, "verbose", False):
            logger.info(f"Scanning vulnerabilities in: {target_path}")

        result = scan_vulnerabilities(target_path=str(target_path))

        print_section("Vulnerability Scan Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(result, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except FileNotFoundError as e:
        logger.error(f"Path not found: {args.path}")
        print_error("Path not found", context=str(args.path))
        return False
    except CodomyrmexError as e:
        logger.error(f"Security audit error: {str(e)}")
        print_error("Security audit error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error scanning vulnerabilities")
        print_error("Unexpected error scanning vulnerabilities", exception=e)
        return False


def handle_audit_code(args):
    """Handle audit code security command."""
    try:
        target_path = validate_file_path(
            args.path if args.path else ".",
            must_exist=True,
            must_be_dir=True,
        )

        if getattr(args, "verbose", False):
            logger.info(f"Auditing code security in: {target_path}")

        result = audit_code_security(target_path=str(target_path))

        print_section("Code Security Audit Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(result, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except FileNotFoundError as e:
        logger.error(f"Path not found: {args.path}")
        print_error("Path not found", context=str(args.path))
        return False
    except CodomyrmexError as e:
        logger.error(f"Security audit error: {str(e)}")
        print_error("Security audit error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error auditing code security")
        print_error("Unexpected error auditing code security", exception=e)
        return False


def handle_check_compliance(args):
    """Handle check compliance command."""
    try:
        target_path = validate_file_path(
            args.path if args.path else ".",
            must_exist=True,
            must_be_dir=True,
        )

        if getattr(args, "verbose", False):
            logger.info(f"Checking compliance in: {target_path} (standard: {args.standard})")

        result = check_compliance(target_path=str(target_path), standard=args.standard)

        print_section("Compliance Check Results")
        print(format_output(result, format_type="json"))
        print_section("", separator="")

        if args.output:
            output_path = save_json_file(result, args.output)
            print_success(f"Results saved to {output_path}")

        return True

    except FileNotFoundError as e:
        logger.error(f"Path not found: {args.path}")
        print_error("Path not found", context=str(args.path))
        return False
    except CodomyrmexError as e:
        logger.error(f"Security audit error: {str(e)}")
        print_error("Security audit error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error checking compliance")
        print_error("Unexpected error checking compliance", exception=e)
        return False


def handle_generate_report(args):
    """Handle generate security report command."""
    try:
        target_path = validate_file_path(
            args.path if args.path else ".",
            must_exist=True,
            must_be_dir=True,
        )
        output_path = validate_file_path(
            args.output,
            must_exist=False,
        )

        if getattr(args, "verbose", False):
            logger.info(f"Generating security report for: {target_path} -> {output_path}")

        result = generate_security_report(
            target_path=str(target_path),
            output_path=str(output_path),
        )

        print_section("Security Report Generation")
        if isinstance(result, dict):
            print(format_output(result, format_type="json"))
            success = result.get("success", False)
        else:
            print(format_output(result, format_type="text"))
            success = bool(result)
        print_section("", separator="")

        if success:
            print_success(f"Security report generated", context=str(output_path))
        else:
            print_error("Security report generation failed")
        return success

    except FileNotFoundError as e:
        logger.error(f"Path not found: {args.path}")
        print_error("Path not found", context=str(args.path))
        return False
    except CodomyrmexError as e:
        logger.error(f"Security audit error: {str(e)}")
        print_error("Security audit error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error generating security report")
        print_error("Unexpected error generating security report", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Security operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan-vulnerabilities --path src/
  %(prog)s audit-code --path src/
  %(prog)s check-compliance --path src/ --standard OWASP
  %(prog)s generate-report --path src/ --output security_report.json
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scan vulnerabilities command
    scan_parser = subparsers.add_parser("scan-vulnerabilities", help="Scan for vulnerabilities")
    scan_parser.add_argument("--path", "-p", default=".", help="Target path")
    scan_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    # Audit code command
    audit_parser = subparsers.add_parser("audit-code", help="Audit code security")
    audit_parser.add_argument("--path", "-p", default=".", help="Target path")
    audit_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    # Check compliance command
    compliance_parser = subparsers.add_parser("check-compliance", help="Check compliance")
    compliance_parser.add_argument("--path", "-p", default=".", help="Target path")
    compliance_parser.add_argument("--standard", "-s", help="Compliance standard")
    compliance_parser.add_argument(
        "--output", "-o", help="Output file path for results (JSON)"
    )

    # Generate report command
    report_parser = subparsers.add_parser("generate-report", help="Generate security report")
    report_parser.add_argument("--path", "-p", default=".", help="Target path")
    report_parser.add_argument("--output", "-o", required=True, help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    handlers = {
        "scan-vulnerabilities": handle_scan_vulnerabilities,
        "audit-code": handle_audit_code,
        "check-compliance": handle_check_compliance,
        "generate-report": handle_generate_report,
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

