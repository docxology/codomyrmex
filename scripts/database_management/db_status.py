#!/usr/bin/env python3
"""
Check database connectivity and display status.

Usage:
    python db_status.py [--url URL] [--type TYPE]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import os
import json


def check_sqlite(path: str) -> dict:
    """Check SQLite database status."""
    import sqlite3
    
    if not Path(path).exists():
        return {"status": "error", "message": f"File not found: {path}"}
    
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get counts
        table_stats = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM '{table}'")
                table_stats[table] = cursor.fetchone()[0]
            except:
                table_stats[table] = "error"
        
        conn.close()
        
        return {
            "status": "connected",
            "type": "sqlite",
            "path": path,
            "tables": len(tables),
            "table_stats": table_stats,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def check_postgres(url: str) -> dict:
    """Check PostgreSQL connection."""
    try:
        import psycopg2
        conn = psycopg2.connect(url)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "status": "connected",
            "type": "postgresql",
            "version": version.split(",")[0],
            "tables": len(tables),
        }
    except ImportError:
        return {"status": "error", "message": "psycopg2 not installed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def find_local_databases() -> list:
    """Find local SQLite databases."""
    patterns = ["*.db", "*.sqlite", "*.sqlite3"]
    found = []
    
    for pattern in patterns:
        found.extend(Path(".").glob(pattern))
        found.extend(Path(".").glob(f"**/{pattern}"))
    
    return list(set(found))[:10]


def main():
    parser = argparse.ArgumentParser(description="Check database status")
    parser.add_argument("--url", "-u", default=None, help="Database URL")
    parser.add_argument("--type", "-t", choices=["sqlite", "postgres", "auto"], default="auto")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    print("🗄️  Database Status Checker\n")
    
    results = []
    
    if args.url:
        if args.type == "postgres" or args.url.startswith("postgres"):
            results.append(check_postgres(args.url))
        else:
            results.append(check_sqlite(args.url))
    else:
        # Check environment variables
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            print(f"📌 Found DATABASE_URL environment variable")
            if "postgres" in db_url:
                results.append(check_postgres(db_url))
            else:
                results.append(check_sqlite(db_url))
        
        # Find local SQLite databases
        local_dbs = find_local_databases()
        if local_dbs:
            print(f"📁 Found {len(local_dbs)} local database(s)\n")
            for db in local_dbs[:5]:
                results.append(check_sqlite(str(db)))
    
    if args.json:
        print(json.dumps(results, indent=2))
        return 0
    
    if not results:
        print("ℹ️  No databases found")
        print("   Set DATABASE_URL or use --url to specify")
        return 0
    
    for result in results:
        if result["status"] == "connected":
            print(f"✅ {result.get('type', 'database').upper()}")
            if "path" in result:
                print(f"   Path: {result['path']}")
            if "version" in result:
                print(f"   Version: {result['version']}")
            print(f"   Tables: {result['tables']}")
            
            if "table_stats" in result:
                print("   Table details:")
                for table, count in list(result["table_stats"].items())[:10]:
                    print(f"     - {table}: {count} rows")
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")
        print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
