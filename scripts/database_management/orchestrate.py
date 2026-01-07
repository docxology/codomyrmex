#!/usr/bin/env python3
"""
Database Management Orchestrator

Thin orchestrator script providing CLI access to database_management module functionality.
Calls actual module functions from codomyrmex.database_management.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import sys

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import module-specific exceptions
from codomyrmex.exceptions import DatabaseError, CodomyrmexError

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        validate_file_path,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        validate_file_path,
    )

# Import module functions
from codomyrmex.database_management import (
    backup_database,
    manage_databases,
    run_migrations,
)

logger = get_logger(__name__)


def handle_backup(args):
    """Handle backup database command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would backup database {args.database} to {args.output}")
            return True

        output_path = validate_file_path(args.output, must_exist=False)
        
        if getattr(args, "verbose", False):
            logger.info(f"Backing up database {args.database} to {output_path}")

        result = backup_database(database_name=args.database, output_path=str(output_path))

        print_section("Database Backup")
        if isinstance(result, dict):
            success = result.get("success", False)
            print(format_output(result, format_type="json"))
        else:
            success = bool(result)
            print(format_output(result, format_type="json"))
        print_section("", separator="")

        if success:
            print_success(f"Database backup created: {output_path}")
        else:
            print_error("Database backup failed")
        return success

    except ValueError as e:
        logger.error(f"Invalid output path: {args.output}")
        print_error("Invalid output path", context=args.output, exception=e)
        return False
    except DatabaseError as e:
        logger.error(f"Database error: {str(e)}")
        print_error("Database error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error backing up database")
        print_error("Unexpected error backing up database", exception=e)
        return False


def handle_migrate(args):
    """Handle run migrations command."""
    try:
        if getattr(args, "dry_run", False):
            print_info(f"Dry run: Would run migrations on database {args.database}")
            return True

        if getattr(args, "verbose", False):
            logger.info(f"Running migrations on database {args.database}")

        result = run_migrations(database_name=args.database)

        print_section("Database Migration")
        if isinstance(result, dict):
            success = result.get("success", False)
            print(format_output(result, format_type="json"))
        else:
            success = bool(result)
            print(format_output(result, format_type="json"))
        print_section("", separator="")

        if success:
            print_success("Migrations completed successfully")
        else:
            print_error("Migrations failed")
        return success

    except DatabaseError as e:
        logger.error(f"Database error: {str(e)}")
        print_error("Database error", context=str(e), exception=e)
        return False
    except Exception as e:
        logger.exception("Unexpected error running migrations")
        print_error("Unexpected error running migrations", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Database Management operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s backup --database mydb --output backup.sql
  %(prog)s migrate --database mydb
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

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup database")
    backup_parser.add_argument("--database", "-d", required=True, help="Database name")
    backup_parser.add_argument("--output", "-o", required=True, help="Output file path")

    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Run migrations")
    migrate_parser.add_argument("--database", "-d", required=True, help="Database name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate handler
    handlers = {
        "backup": handle_backup,
        "migrate": handle_migrate,
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

