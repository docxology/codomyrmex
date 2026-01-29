#!/usr/bin/env python3
"""
File system utilities and operations.

Usage:
    python fs_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import os
import shutil
from datetime import datetime


def format_size(bytes: int) -> str:
    """Format bytes as human readable."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"


def analyze_directory(path: Path) -> dict:
    """Analyze directory contents."""
    stats = {
        "files": 0, "dirs": 0, "total_size": 0,
        "by_ext": {}, "largest": []
    }
    
    for item in path.rglob("*"):
        if item.is_file():
            size = item.stat().st_size
            stats["files"] += 1
            stats["total_size"] += size
            
            ext = item.suffix.lower() or "no_ext"
            if ext not in stats["by_ext"]:
                stats["by_ext"][ext] = {"count": 0, "size": 0}
            stats["by_ext"][ext]["count"] += 1
            stats["by_ext"][ext]["size"] += size
            
            stats["largest"].append((size, str(item)))
        elif item.is_dir():
            stats["dirs"] += 1
    
    stats["largest"] = sorted(stats["largest"], reverse=True)[:10]
    return stats


def find_duplicates(path: Path) -> list:
    """Find potential duplicate files by size."""
    by_size = {}
    
    for f in path.rglob("*"):
        if f.is_file():
            size = f.stat().st_size
            if size not in by_size:
                by_size[size] = []
            by_size[size].append(str(f))
    
    return [(size, files) for size, files in by_size.items() if len(files) > 1 and size > 1024]


def main():
    parser = argparse.ArgumentParser(description="File system utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Analyze command
    analyze = subparsers.add_parser("analyze", help="Analyze directory")
    analyze.add_argument("path", default=".", nargs="?")
    
    # Duplicates command
    dups = subparsers.add_parser("duplicates", help="Find potential duplicates")
    dups.add_argument("path", default=".", nargs="?")
    
    # Tree command
    tree = subparsers.add_parser("tree", help="Show directory tree")
    tree.add_argument("path", default=".", nargs="?")
    tree.add_argument("--depth", "-d", type=int, default=3)
    
    args = parser.parse_args()
    
    if not args.command:
        print("📁 File System Utilities\n")
        print("Commands:")
        print("  analyze    - Analyze directory contents")
        print("  duplicates - Find potential duplicate files")
        print("  tree       - Show directory tree")
        print("\nExamples:")
        print("  python fs_utils.py analyze src/")
        print("  python fs_utils.py duplicates .")
        print("  python fs_utils.py tree --depth 2")
        return 0
    
    if args.command == "analyze":
        path = Path(args.path)
        if not path.exists():
            print(f"❌ Path not found: {args.path}")
            return 1
        
        print(f"📊 Analyzing: {path}\n")
        stats = analyze_directory(path)
        
        print(f"   Files: {stats['files']}")
        print(f"   Directories: {stats['dirs']}")
        print(f"   Total size: {format_size(stats['total_size'])}")
        
        print("\n   By extension:")
        sorted_ext = sorted(stats['by_ext'].items(), key=lambda x: -x[1]['size'])
        for ext, data in sorted_ext[:10]:
            print(f"     {ext}: {data['count']} files, {format_size(data['size'])}")
        
        if stats['largest']:
            print("\n   Largest files:")
            for size, name in stats['largest'][:5]:
                print(f"     {format_size(size)}: {Path(name).name}")
    
    elif args.command == "duplicates":
        path = Path(args.path)
        print(f"🔍 Finding duplicates in: {path}\n")
        
        dups = find_duplicates(path)
        if dups:
            print(f"   Found {len(dups)} potential duplicate groups:\n")
            for size, files in sorted(dups, reverse=True)[:10]:
                print(f"   {format_size(size)}:")
                for f in files[:3]:
                    print(f"     - {Path(f).name}")
        else:
            print("   No duplicates found")
    
    elif args.command == "tree":
        path = Path(args.path)
        print(f"📂 {path}\n")
        
        def print_tree(p, prefix="", depth=0, max_depth=3):
            if depth >= max_depth:
                return
            items = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name))
            for i, item in enumerate(items[:20]):
                is_last = i == len(items) - 1 or i == 19
                connector = "└── " if is_last else "├── "
                print(f"{prefix}{connector}{item.name}")
                if item.is_dir():
                    ext = "    " if is_last else "│   "
                    print_tree(item, prefix + ext, depth + 1, max_depth)
        
        print_tree(path, max_depth=args.depth)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
