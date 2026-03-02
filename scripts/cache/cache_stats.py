#!/usr/bin/env python3
"""
Display cache statistics and health metrics.

Usage:
    python cache_stats.py [--path PATH] [--verbose]
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
from datetime import datetime


def get_cache_dirs() -> list:
    """Find common cache directories."""
    cache_locations = [
        Path.home() / ".cache" / "codomyrmex",
        Path.home() / ".codomyrmex" / "cache",
        Path(".codomyrmex") / "cache",
        Path("output") / "cache",
    ]
    return [p for p in cache_locations if p.exists()]


def analyze_cache_dir(cache_path: Path) -> dict:
    """Analyze a cache directory."""
    stats = {
        "path": str(cache_path),
        "total_size": 0,
        "file_count": 0,
        "oldest": None,
        "newest": None,
        "by_type": {},
    }
    
    for f in cache_path.rglob("*"):
        if f.is_file():
            size = f.stat().st_size
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            
            stats["total_size"] += size
            stats["file_count"] += 1
            
            if stats["oldest"] is None or mtime < stats["oldest"]:
                stats["oldest"] = mtime
            if stats["newest"] is None or mtime > stats["newest"]:
                stats["newest"] = mtime
            
            ext = f.suffix or "no_ext"
            if ext not in stats["by_type"]:
                stats["by_type"][ext] = {"count": 0, "size": 0}
            stats["by_type"][ext]["count"] += 1
            stats["by_type"][ext]["size"] += size
    
    return stats


def format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(description="Display cache statistics")
    parser.add_argument("--path", "-p", default=None, help="Cache directory path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed breakdown")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    if args.path:
        cache_dirs = [Path(args.path)]
    else:
        cache_dirs = get_cache_dirs()
    
    if not cache_dirs:
        print("📦 No cache directories found")
        print("   Searched: ~/.cache/codomyrmex, ~/.codomyrmex/cache, .codomyrmex/cache")
        return 0
    
    all_stats = []
    
    for cache_dir in cache_dirs:
        stats = analyze_cache_dir(cache_dir)
        all_stats.append(stats)
        
        if args.json:
            continue
        
        print(f"📦 Cache: {stats['path']}")
        print(f"   Files: {stats['file_count']}")
        print(f"   Size: {format_size(stats['total_size'])}")
        
        if stats["oldest"]:
            print(f"   Oldest: {stats['oldest'].strftime('%Y-%m-%d %H:%M')}")
        if stats["newest"]:
            print(f"   Newest: {stats['newest'].strftime('%Y-%m-%d %H:%M')}")
        
        if args.verbose and stats["by_type"]:
            print("   By type:")
            for ext, data in sorted(stats["by_type"].items(), key=lambda x: -x[1]["size"]):
                print(f"     {ext}: {data['count']} files, {format_size(data['size'])}")
        print()
    
    if args.json:
        output = []
        for s in all_stats:
            s["oldest"] = s["oldest"].isoformat() if s["oldest"] else None
            s["newest"] = s["newest"].isoformat() if s["newest"] else None
            output.append(s)
        print(json.dumps(output, indent=2))
    
    total_size = sum(s["total_size"] for s in all_stats)
    total_files = sum(s["file_count"] for s in all_stats)
    
    if not args.json:
        print(f"📊 Total: {total_files} files, {format_size(total_size)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
