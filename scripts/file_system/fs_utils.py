#!/usr/bin/env python3
"""
File system utilities and operations - Orchestrator script.

This script demonstrates the use of the codomyrmex.file_system module.
Usage:
    python fs_utils.py <command> [options]
"""

import argparse
import sys
from pathlib import Path

# Add src to sys.path for local development
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.file_system import create_file_system_manager


def format_size(bytes: int) -> str:
    """Format bytes as human readable."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes < 1024:
            return f"{bytes:.1f} {unit}"
        bytes /= 1024
    return f"{bytes:.1f} TB"


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "file_system"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/file_system/config.yaml")

    parser = argparse.ArgumentParser(description="Codomyrmex File System Utilities")
    subparsers = parser.add_subparsers(dest="command")

    # Analyze command
    analyze = subparsers.add_parser("analyze", help="Analyze directory contents")
    analyze.add_argument("path", default=".", nargs="?")

    # Duplicates command
    dups = subparsers.add_parser("duplicates", help="Find duplicate files")
    dups.add_argument("path", default=".", nargs="?")

    # Tree command
    tree = subparsers.add_parser("tree", help="Show directory tree")
    tree.add_argument("path", default=".", nargs="?")
    tree.add_argument("--depth", "-d", type=int, default=3)

    # Disk command
    disk = subparsers.add_parser("disk", help="Show disk usage")
    disk.add_argument("path", default=".", nargs="?")

    args = parser.parse_args()

    fs = create_file_system_manager()

    if not args.command:
        print("📁 Codomyrmex File System Utilities\n")
        print("Commands:")
        print("  analyze    - Analyze directory contents")
        print("  duplicates - Find duplicate files")
        print("  tree       - Show directory tree")
        print("  disk       - Show disk usage")
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
        items = fs.list_dir(path, recursive=True)

        files = [i for i in items if i.is_file()]
        dirs = [i for i in items if i.is_dir()]
        total_size = sum(f.stat().st_size for f in files)

        print(f"   Files: {len(files)}")
        print(f"   Directories: {len(dirs)}")
        print(f"   Total size: {format_size(total_size)}")

        # Extension stats
        ext_stats = {}
        for f in files:
            ext = f.suffix.lower() or "no_ext"
            if ext not in ext_stats:
                ext_stats[ext] = {"count": 0, "size": 0}
            ext_stats[ext]["count"] += 1
            ext_stats[ext]["size"] += f.stat().st_size

        print("\n   By extension:")
        sorted_ext = sorted(ext_stats.items(), key=lambda x: -x[1]["size"])
        for ext, data in sorted_ext[:10]:
            print(f"     {ext}: {data['count']} files, {format_size(data['size'])}")

    elif args.command == "duplicates":
        path = Path(args.path)
        print(f"🔍 Finding duplicates in: {path}\n")

        duplicates = fs.find_duplicates(path)
        if duplicates:
            print(f"   Found {len(duplicates)} duplicate groups:\n")
            for h, paths in sorted(
                duplicates.items(), key=lambda x: -x[1][0].stat().st_size
            )[:10]:
                size = paths[0].stat().st_size
                print(f"   {format_size(size)} (Hash: {h[:12]}...):")
                for p in paths[:3]:
                    print(f"     - {p.relative_to(path)}")
        else:
            print("   No duplicates found")

    elif args.command == "tree":
        path = Path(args.path)
        print(f"📂 {path}\n")

        def print_tree(p, prefix="", depth=0, max_depth=3):
            if depth >= max_depth:
                return
            try:
                items = sorted(fs.list_dir(p), key=lambda x: (x.is_file(), x.name))
            except PermissionError:
                print(f"{prefix}└── [Permission Denied]")
                return

            for i, item in enumerate(items[:20]):
                is_last = i == len(items) - 1 or i == 19
                connector = "└── " if is_last else "├── "
                print(f"{prefix}{connector}{item.name}")
                if item.is_dir():
                    ext = "    " if is_last else "│   "
                    print_tree(item, prefix + ext, depth + 1, max_depth)

        print_tree(path, max_depth=args.depth)

    elif args.command == "disk":
        path = Path(args.path)
        usage = fs.get_disk_usage(path)
        print(f"💾 Disk Usage for: {path.resolve()}\n")
        print(f"   Total: {format_size(usage['total'])}")
        print(f"   Used:  {format_size(usage['used'])} ({usage['percent']:.1f}%)")
        print(f"   Free:  {format_size(usage['free'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
