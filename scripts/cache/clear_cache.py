#!/usr/bin/env python3
"""
Clear cache entries selectively or completely.

Usage:
    python clear_cache.py [--all] [--older-than DAYS] [--type EXT]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
from datetime import datetime, timedelta


def get_cache_dirs() -> list:
    """Find common cache directories."""
    cache_locations = [
        Path.home() / ".cache" / "codomyrmex",
        Path.home() / ".codomyrmex" / "cache",
        Path(".codomyrmex") / "cache",
        Path("output") / "cache",
    ]
    return [p for p in cache_locations if p.exists()]


def clear_cache(cache_path: Path, older_than_days: int = None, file_types: list = None, dry_run: bool = True) -> dict:
    """Clear cache entries based on criteria."""
    stats = {"deleted": 0, "size_freed": 0, "skipped": 0}
    cutoff = datetime.now() - timedelta(days=older_than_days) if older_than_days else None
    
    for f in cache_path.rglob("*"):
        if f.is_file():
            should_delete = True
            
            if cutoff:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if mtime > cutoff:
                    should_delete = False
            
            if file_types:
                if f.suffix.lstrip(".") not in file_types:
                    should_delete = False
            
            if should_delete:
                size = f.stat().st_size
                if not dry_run:
                    f.unlink()
                stats["deleted"] += 1
                stats["size_freed"] += size
            else:
                stats["skipped"] += 1
    
    return stats


def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(description="Clear cache entries")
    parser.add_argument("--all", "-a", action="store_true", help="Clear all cache entries")
    parser.add_argument("--older-than", "-o", type=int, default=None, help="Clear entries older than N days")
    parser.add_argument("--type", "-t", action="append", help="Clear specific file types (e.g., json, pickle)")
    parser.add_argument("--path", "-p", default=None, help="Specific cache path")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Show what would be deleted")
    parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")
    args = parser.parse_args()
    
    if not args.all and not args.older_than and not args.type:
        print("🗑️  Cache Cleaner")
        print("\n   Specify what to clear:")
        print("   --all              Clear everything")
        print("   --older-than N     Clear entries older than N days")
        print("   --type EXT         Clear specific file types")
        print("\n   Add --dry-run to preview without deleting")
        return 0
    
    if args.path:
        cache_dirs = [Path(args.path)]
    else:
        cache_dirs = get_cache_dirs()
    
    if not cache_dirs:
        print("📦 No cache directories found")
        return 0
    
    dry_run = args.dry_run or not args.force
    
    if dry_run and not args.dry_run:
        print("⚠️  Running in dry-run mode (use --force to actually delete)\n")
    
    total_deleted = 0
    total_freed = 0
    
    for cache_dir in cache_dirs:
        older_than = args.older_than if not args.all else None
        file_types = args.type
        
        stats = clear_cache(cache_dir, older_than, file_types, dry_run)
        total_deleted += stats["deleted"]
        total_freed += stats["size_freed"]
        
        action = "Would delete" if dry_run else "Deleted"
        print(f"📦 {cache_dir}")
        print(f"   {action}: {stats['deleted']} files ({format_size(stats['size_freed'])})")
        if stats["skipped"]:
            print(f"   Skipped: {stats['skipped']} files")
    
    print(f"\n{'🔍 Preview' if dry_run else '✅ Complete'}: {total_deleted} files, {format_size(total_freed)}")
    
    if dry_run and total_deleted > 0:
        print("\n   To delete, run with --force")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
