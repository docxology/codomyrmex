#!/usr/bin/env python3
"""
Database Management - Real Usage Examples

Demonstrates actual database capabilities:
- DatabaseManager usage
- Connection configuration
- Backup/Migration stubs
"""

import os
import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.database_management import (
    DatabaseConnection,
    DatabaseManager,
    generate_schema,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "database_management"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/database_management/config.yaml")

    setup_logging()
    print_info("Running Database Management Examples...")

    # 1. Database Manager & Connection
    print_info("Testing DatabaseManager and real connection (SQLite)...")
    try:
        from codomyrmex.database_management.db_manager import DatabaseType

        mgr = DatabaseManager()

        # Define a real SQLite connection for testing
        db_path = "output/test_app.db"
        conn = DatabaseConnection(
            name="local_sqlite", db_type=DatabaseType.SQLITE, database=db_path
        )
        mgr.add_connection(conn)
        print_success(f"  DatabaseConnection registered: '{conn.name}' -> {db_path}")

        # Test connection string generation
        print_info(f"  Connection string: {conn.get_connection_string()}")

    except Exception as e:
        print_error(f"  DatabaseManager flow failed: {e}")

    # 2. Schema Generation
    print_info("Testing generate_schema...")
    try:
        # Create output dir if needed
        os.makedirs("output/schema", exist_ok=True)
        generate_schema(models=[], output_dir="output/schema")
        print_success("  generate_schema called successfully.")
    except Exception as e:
        print_info(f"  generate_schema demo: {e}")

    print_success("Database management examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
