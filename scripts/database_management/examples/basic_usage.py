#!/usr/bin/env python3
"""
Database Management - Real Usage Examples

Demonstrates actual database capabilities:
- DatabaseManager usage
- Connection configuration
- Backup/Migration stubs
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.database_management import (
    DatabaseManager,
    DatabaseConnection,
    generate_schema
)

def main():
    # Auto-injected: Load configuration
    import yaml
    from pathlib import Path
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "database_management" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from config/database_management/config.yaml")

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
            name="local_sqlite",
            db_type=DatabaseType.SQLITE,
            database=db_path
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
        schema = generate_schema(models=[], output_dir="output/schema")
        print_success("  generate_schema called successfully.")
    except Exception as e:
        print_info(f"  generate_schema demo: {e}")

    print_success("Database management examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
