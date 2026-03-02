#!/usr/bin/env python3
"""
Orchestrator for database_management.
Demonstrates the improved database management module with a working example.
"""

import sys
import tempfile
from pathlib import Path

# Ensure codomyrmex is in path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.database_management import (
    manage_databases,
    MigrationManager,
    DatabasePerformanceMonitor,
    BackupManager
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
            print(f"Loaded config from {config_path.name}")

    print("--- Codomyrmex Database Management Orchestrator ---")
    
    # 1. Setup workspace and database
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)
        db_file = workspace / "orchestrator_demo.db"
        db_url = f"sqlite:///{db_file}"
        
        print(f"[*] Initializing database: {db_url}")
        manager = manage_databases(db_url)
        
        # 2. Run Migrations
        print("[*] Setting up migrations...")
        mig_manager = MigrationManager(workspace_dir=str(workspace), database_url=db_url)
        
        create_table_sql = """
        CREATE TABLE sensors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT,
            last_value REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        mig_manager.create_migration(
            name="create_sensors_table",
            description="Initial schema for sensors",
            sql=create_table_sql,
            rollback_sql="DROP TABLE sensors;"
        )
        
        print("[*] Applying migrations...")
        results = mig_manager.apply_pending_migrations()
        for res in results:
            if res.success:
                print(f"  [+] Migration {res.migration_id} applied successfully.")
        
        # 3. Execute Queries
        print("[*] Seeding data...")
        with manager.transaction() as tx:
            tx.execute("INSERT INTO sensors (name, type, last_value) VALUES (?, ?, ?)", ("Temp01", "temperature", 22.5), commit=False)
            tx.execute("INSERT INTO sensors (name, type, last_value) VALUES (?, ?, ?)", ("Hum01", "humidity", 45.0), commit=False)
        
        print("[*] Querying data...")
        result = manager.execute("SELECT * FROM sensors")
        if result.success:
            for row in result.to_dict_list():
                print(f"  - Sensor: {row['name']} ({row['type']}) = {row['last_value']}")
        
        # 4. Performance Monitoring
        print("[*] Recording performance metrics...")
        monitor = DatabasePerformanceMonitor(workspace_dir=str(workspace))
        monitor.record_database_metrics("demo_db", {
            "connections_active": 1,
            "queries_per_second": 10.5,
            "average_query_time_ms": result.execution_time * 1000
        })
        
        report = monitor.analyze_database_performance("demo_db")
        print(f"  [+] Health status: {report.get('performance_issues', 'Healthy')}")
        
        # 5. Backup
        print("[*] Creating database backup...")
        backup_manager = BackupManager(workspace_dir=str(workspace), database_url=db_url)
        backup_res = backup_manager.create_backup("orchestrator_demo")
        if backup_res.success:
            print(f"  [+] Backup created: {backup_res.backup_id} ({backup_res.file_size_mb:.2f} MB)")
            
    print("\n--- Orchestration Complete ---")

if __name__ == "__main__":
    main()
