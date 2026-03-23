"""System health status CLI definitions for /codomyrmexStatus."""

import os
from datetime import datetime
from pathlib import Path


# Provide modular defaults for the info
def get_system_vitals() -> dict:
    """Scan simple system vitals including memory buffer utilization."""
    vitals = {
        "timestamp": datetime.now().isoformat(),
        "active_worktrees": 0,
        "database_size_mb": 0.0,
        "logs_size_mb": 0.0,
    }

    # Count worktrees
    wt_dir = Path(".git/worktrees")
    if wt_dir.exists():
        vitals["active_worktrees"] = len(list(wt_dir.iterdir()))

    # Check some basic db size
    db_path = Path("agentic_memory_primary.db")
    if db_path.exists():
        vitals["database_size_mb"] = round(db_path.stat().st_size / (1024 * 1024), 2)

    # Check logs size in /tmp/ or local
    log_dir = Path("logs")
    if log_dir.exists():
        total_size = sum(
            f.stat().st_size for f in log_dir.glob("**/*.log") if f.is_file()
        )
        vitals["logs_size_mb"] = round(total_size / (1024 * 1024), 2)

    return vitals


def print_status_report():
    """Print the formatted /codomyrmexStatus report."""
    vitals = get_system_vitals()

    print("==================================================")
    print("          CODOMYRMEX SYSTEM HEALTH STATUS")
    print("==================================================")
    print(f"Timestamp:          {vitals['timestamp']}")
    print(f"Active Worktrees:   {vitals['active_worktrees']}")
    print(f"Agentic DB Size:    {vitals['database_size_mb']} MB")
    print(f"Log Volume:         {vitals['logs_size_mb']} MB")

    # Add some environment vitals
    print("\nEnvironment Constraints:")
    print(f"UV_PROJECT_ENV:     {os.environ.get('UV_PROJECT_ENV', 'Not set')}")
    print(
        f"ANTHROPIC_API_KEY:  {'set' if 'ANTHROPIC_API_KEY' in os.environ else 'Not set'}"
    )

    print("==================================================")
