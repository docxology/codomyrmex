#!/usr/bin/env python3
"""
Interactive commit message builder with conventional commit format.

Usage:
    python commit_helper.py [--type TYPE] [--scope SCOPE] [--message MESSAGE]
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import subprocess


# Conventional commit types
COMMIT_TYPES = {
    "feat": "A new feature",
    "fix": "A bug fix",
    "docs": "Documentation only changes",
    "style": "Changes that do not affect the meaning of the code",
    "refactor": "A code change that neither fixes a bug nor adds a feature",
    "perf": "A code change that improves performance",
    "test": "Adding missing tests or correcting existing tests",
    "build": "Changes that affect the build system or external dependencies",
    "ci": "Changes to CI configuration files and scripts",
    "chore": "Other changes that don't modify src or test files",
    "revert": "Reverts a previous commit",
}


def run_git(args: list) -> tuple:
    """Run a git command and return (success, output)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def get_staged_files() -> list:
    """Get list of staged files."""
    success, output = run_git(["diff", "--cached", "--name-only"])
    if success and output:
        return output.split("\n")
    return []


def infer_scope(files: list) -> str:
    """Infer scope from staged files."""
    if not files:
        return ""
    
    # Find common directory
    parts_list = [Path(f).parts for f in files]
    if not parts_list or not parts_list[0]:
        return ""
    
    # Check if all files share a common parent
    common = []
    for i in range(len(parts_list[0])):
        part = parts_list[0][i]
        if all(len(p) > i and p[i] == part for p in parts_list):
            common.append(part)
        else:
            break
    
    if common:
        # Return the most specific directory
        scope = common[-1] if common else ""
        # Skip generic names
        if scope in ("src", "scripts", "tests", "docs"):
            return common[-2] if len(common) > 1 else ""
        return scope
    
    return ""


def infer_type(files: list) -> str:
    """Infer commit type from staged files."""
    if not files:
        return "chore"
    
    extensions = [Path(f).suffix for f in files]
    paths = [str(f).lower() for f in files]
    
    # Check for common patterns
    if any("test" in p for p in paths):
        return "test"
    if any("readme" in p or "docs/" in p or ".md" in e for p, e in zip(paths, extensions)):
        return "docs"
    if any("ci" in p or ".github" in p or "workflow" in p for p in paths):
        return "ci"
    if any("package.json" in p or "requirements" in p or "pyproject" in p for p in paths):
        return "build"
    
    return "feat"  # Default


def build_commit_message(commit_type: str, scope: str, message: str, breaking: bool = False) -> str:
    """Build conventional commit message."""
    type_part = commit_type
    if breaking:
        type_part += "!"
    
    if scope:
        return f"{type_part}({scope}): {message}"
    return f"{type_part}: {message}"


def main():
    parser = argparse.ArgumentParser(description="Build conventional commit messages")
    parser.add_argument("--type", "-t", choices=list(COMMIT_TYPES.keys()), default=None,
                        help="Commit type (auto-detected if not specified)")
    parser.add_argument("--scope", "-s", default=None,
                        help="Commit scope (auto-detected if not specified)")
    parser.add_argument("--message", "-m", default=None,
                        help="Commit message (required)")
    parser.add_argument("--breaking", "-b", action="store_true",
                        help="Mark as breaking change")
    parser.add_argument("--commit", "-c", action="store_true",
                        help="Actually perform the commit")
    parser.add_argument("--list-types", "-l", action="store_true",
                        help="List available commit types")
    args = parser.parse_args()
    
    if args.list_types:
        print("📋 Conventional commit types:\n")
        for t, desc in COMMIT_TYPES.items():
            print(f"   {t:10} - {desc}")
        return 0
    
    # Get staged files
    staged = get_staged_files()
    
    if not staged:
        print("⚠️  No files staged for commit")
        print("   Stage files with: git add <files>")
        return 1
    
    print(f"📁 Staged files ({len(staged)}):")
    for f in staged[:10]:
        print(f"   + {f}")
    if len(staged) > 10:
        print(f"   ... and {len(staged) - 10} more")
    print()
    
    # Determine type
    commit_type = args.type or infer_type(staged)
    if not args.type:
        print(f"🔍 Auto-detected type: {commit_type}")
    
    # Determine scope
    scope = args.scope if args.scope is not None else infer_scope(staged)
    if scope and not args.scope:
        print(f"🔍 Auto-detected scope: {scope}")
    
    # Get message
    if not args.message:
        print("\n❌ Message required. Use --message or -m flag")
        print(f"\n   Example: python commit_helper.py -t {commit_type} -m \"your message here\"")
        return 1
    
    # Build commit message
    full_message = build_commit_message(commit_type, scope, args.message, args.breaking)
    
    print(f"\n📝 Commit message:")
    print(f"   {full_message}")
    
    if args.commit:
        success, output = run_git(["commit", "-m", full_message])
        if success:
            print("\n✅ Committed successfully!")
            print(f"   {output.split(chr(10))[0]}")
        else:
            print(f"\n❌ Commit failed: {output}")
            return 1
    else:
        print("\n💡 To commit, add --commit or run:")
        print(f'   git commit -m "{full_message}"')
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
