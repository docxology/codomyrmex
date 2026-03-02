#!/usr/bin/env python3
"""
Log viewer and analysis utilities.

Usage:
    python log_viewer.py [path] [--level LEVEL] [--tail N]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import re
from datetime import datetime


LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LOG_PATTERN = re.compile(r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})?.*?(DEBUG|INFO|WARNING|ERROR|CRITICAL)', re.IGNORECASE)


def parse_log_line(line: str) -> dict:
    """Parse a log line."""
    match = LOG_PATTERN.search(line)
    if match:
        return {
            "timestamp": match.group(1),
            "level": match.group(2).upper() if match.group(2) else None,
            "message": line.strip(),
        }
    return {"message": line.strip()}


def find_log_files(path: str) -> list:
    """Find log files."""
    p = Path(path)
    if p.is_file():
        return [p]
    
    patterns = ["*.log", "*.txt", "logs/*.log"]
    found = []
    for pattern in patterns:
        found.extend(p.glob(pattern))
    return sorted(found, key=lambda x: x.stat().st_mtime, reverse=True)[:10]


def analyze_logs(lines: list) -> dict:
    """Analyze log content."""
    stats = {level: 0 for level in LOG_LEVELS}
    errors = []
    
    for line in lines:
        parsed = parse_log_line(line)
        level = parsed.get("level")
        if level in stats:
            stats[level] += 1
        if level in ["ERROR", "CRITICAL"]:
            errors.append(parsed["message"][:100])
    
    return {"stats": stats, "errors": errors[:10]}


def main():
    parser = argparse.ArgumentParser(description="Log viewer and analysis")
    parser.add_argument("path", nargs="?", default=".", help="Log file or directory")
    parser.add_argument("--level", "-l", choices=LOG_LEVELS, default=None, help="Filter by level")
    parser.add_argument("--tail", "-t", type=int, default=None, help="Show last N lines")
    parser.add_argument("--analyze", "-a", action="store_true", help="Analyze log statistics")
    parser.add_argument("--errors", "-e", action="store_true", help="Show only errors")
    args = parser.parse_args()
    
    files = find_log_files(args.path)
    
    if not files:
        print("📋 No log files found")
        print("   Searched for: *.log, logs/*.log")
        return 0
    
    print(f"📋 Log Files ({len(files)}):\n")
    
    for log_file in files[:5]:
        size = log_file.stat().st_size / 1024
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        print(f"📄 {log_file.name} ({size:.1f} KB, {mtime.strftime('%Y-%m-%d %H:%M')})")
        
        with open(log_file) as f:
            lines = f.readlines()
        
        if args.analyze:
            analysis = analyze_logs(lines)
            print("   Level distribution:")
            for level, count in analysis["stats"].items():
                if count > 0:
                    print(f"     {level}: {count}")
            if analysis["errors"]:
                print(f"   Recent errors: {len(analysis['errors'])}")
            continue
        
        # Filter lines
        filtered = lines
        if args.level:
            filtered = [l for l in lines if args.level.upper() in l.upper()]
        if args.errors:
            filtered = [l for l in lines if any(e in l.upper() for e in ["ERROR", "CRITICAL"])]
        if args.tail:
            filtered = filtered[-args.tail:]
        
        print(f"   Lines: {len(filtered)}/{len(lines)}")
        for line in filtered[:10]:
            print(f"   {line.strip()[:80]}")
        if len(filtered) > 10:
            print(f"   ... ({len(filtered) - 10} more)")
        print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
