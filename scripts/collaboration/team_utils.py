#!/usr/bin/env python3
"""
Collaboration and team utilities.

Usage:
    python team_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import subprocess
from collections import defaultdict


def get_git_contributors() -> list:
    """Get list of contributors from git log."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%aN <%aE>"],
            capture_output=True, text=True
        )
        contributors = defaultdict(int)
        for line in result.stdout.strip().split("\n"):
            if line:
                contributors[line] += 1
        return sorted(contributors.items(), key=lambda x: -x[1])
    except:
        return []


def analyze_file_ownership(path: str = ".") -> dict:
    """Analyze file ownership by contributor."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%aN", "--", path],
            capture_output=True, text=True
        )
        authors = defaultdict(int)
        for line in result.stdout.strip().split("\n"):
            if line:
                authors[line] += 1
        return dict(sorted(authors.items(), key=lambda x: -x[1]))
    except:
        return {}


def find_code_owners() -> list:
    """Find CODEOWNERS file entries."""
    codeowners_paths = [".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS"]
    
    for path in codeowners_paths:
        p = Path(path)
        if p.exists():
            entries = []
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split()
                        if len(parts) >= 2:
                            entries.append({
                                "pattern": parts[0],
                                "owners": parts[1:]
                            })
            return entries
    return []


def main():
    parser = argparse.ArgumentParser(description="Team collaboration utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Contributors command
    subparsers.add_parser("contributors", help="List contributors")
    
    # Ownership command
    ownership = subparsers.add_parser("ownership", help="Analyze file ownership")
    ownership.add_argument("path", nargs="?", default=".", help="Path to analyze")
    
    # CODEOWNERS command
    subparsers.add_parser("codeowners", help="Show CODEOWNERS entries")
    
    args = parser.parse_args()
    
    if not args.command:
        print("👥 Team Collaboration Utilities\n")
        print("Commands:")
        print("  contributors - List git contributors")
        print("  ownership    - Analyze file ownership")
        print("  codeowners   - Show CODEOWNERS entries")
        return 0
    
    if args.command == "contributors":
        contributors = get_git_contributors()
        print(f"👥 Contributors ({len(contributors)}):\n")
        for author, commits in contributors[:20]:
            print(f"   {commits:4d} commits - {author}")
        if len(contributors) > 20:
            print(f"\n   ... and {len(contributors) - 20} more")
    
    elif args.command == "ownership":
        ownership = analyze_file_ownership(args.path)
        print(f"📂 Ownership for: {args.path}\n")
        for author, changes in list(ownership.items())[:10]:
            print(f"   {changes:4d} changes - {author}")
    
    elif args.command == "codeowners":
        entries = find_code_owners()
        if entries:
            print(f"📋 CODEOWNERS ({len(entries)} rules):\n")
            for entry in entries[:15]:
                print(f"   {entry['pattern']:<30} → {' '.join(entry['owners'])}")
        else:
            print("📋 No CODEOWNERS file found")
            print("   Consider creating .github/CODEOWNERS")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
