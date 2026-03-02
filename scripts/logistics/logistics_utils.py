#!/usr/bin/env python3
"""
Logistics and workflow management utilities.

Usage:
    python logistics_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
from datetime import datetime, timedelta


def estimate_time(tasks: list) -> dict:
    """Estimate total time for tasks."""
    total_hours = 0
    breakdown = []
    
    for task in tasks:
        hours = task.get("hours", 1)
        total_hours += hours
        breakdown.append({"name": task.get("name", "Task"), "hours": hours})
    
    return {
        "total_hours": total_hours,
        "total_days": round(total_hours / 8, 1),
        "breakdown": breakdown
    }


def create_schedule(tasks: list, start_date: datetime = None) -> list:
    """Create a schedule from tasks."""
    start = start_date or datetime.now()
    schedule = []
    current = start
    
    for task in tasks:
        hours = task.get("hours", 1)
        end = current + timedelta(hours=hours)
        schedule.append({
            "name": task.get("name", "Task"),
            "start": current.isoformat(),
            "end": end.isoformat(),
            "hours": hours
        })
        current = end
    
    return schedule


def main():
    parser = argparse.ArgumentParser(description="Logistics utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Estimate command
    estimate = subparsers.add_parser("estimate", help="Estimate time")
    estimate.add_argument("file", nargs="?", help="Tasks JSON file")
    
    # Schedule command
    schedule = subparsers.add_parser("schedule", help="Create schedule")
    schedule.add_argument("file", nargs="?", help="Tasks JSON file")
    
    # Demo command
    subparsers.add_parser("demo", help="Demo with sample tasks")
    
    args = parser.parse_args()
    
    if not args.command:
        print("📦 Logistics Utilities\n")
        print("Commands:")
        print("  estimate - Estimate total time")
        print("  schedule - Create schedule")
        print("  demo     - Demo with sample tasks")
        return 0
    
    sample_tasks = [
        {"name": "Planning", "hours": 4},
        {"name": "Development", "hours": 16},
        {"name": "Testing", "hours": 8},
        {"name": "Documentation", "hours": 4},
        {"name": "Deployment", "hours": 2},
    ]
    
    if args.command == "estimate":
        if args.file:
            tasks = json.loads(Path(args.file).read_text())
        else:
            tasks = sample_tasks
            print("📊 Using sample tasks (provide JSON file for custom)\n")
        
        result = estimate_time(tasks)
        print(f"⏱️  Time Estimate:\n")
        for item in result["breakdown"]:
            print(f"   {item['name']}: {item['hours']}h")
        print(f"\n   Total: {result['total_hours']}h ({result['total_days']} days)")
    
    elif args.command == "schedule":
        if args.file:
            tasks = json.loads(Path(args.file).read_text())
        else:
            tasks = sample_tasks
        
        schedule = create_schedule(tasks)
        print("📅 Schedule:\n")
        for item in schedule:
            start = datetime.fromisoformat(item["start"])
            print(f"   {start.strftime('%Y-%m-%d %H:%M')} - {item['name']} ({item['hours']}h)")
    
    elif args.command == "demo":
        print("📦 Sample Tasks:\n")
        for t in sample_tasks:
            print(f"   • {t['name']}: {t['hours']}h")
        
        result = estimate_time(sample_tasks)
        print(f"\n   Total: {result['total_hours']}h")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
