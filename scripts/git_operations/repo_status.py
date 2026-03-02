#!/usr/bin/env python3
"""
Display comprehensive Git repository status.

Usage:
    python repo_status.py [--path PATH] [--verbose]
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import subprocess
import os


def run_git(args: list, cwd: str = ".") -> tuple:
    """Run a git command and return (success, output)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def get_branch_info(path: str) -> dict:
    """Get current branch information."""
    info = {}
    
    success, branch = run_git(["branch", "--show-current"], path)
    info["current_branch"] = branch if success else "unknown"
    
    success, output = run_git(["branch", "-a"], path)
    if success:
        branches = [b.strip().lstrip("* ") for b in output.split("\n") if b.strip()]
        info["local_branches"] = [b for b in branches if not b.startswith("remotes/")]
        info["remote_branches"] = [b for b in branches if b.startswith("remotes/")]
    
    success, ahead_behind = run_git(["rev-list", "--left-right", "--count", "HEAD...@{upstream}"], path)
    if success:
        parts = ahead_behind.split()
        if len(parts) == 2:
            info["ahead"] = int(parts[0])
            info["behind"] = int(parts[1])
    
    return info


def get_status_info(path: str) -> dict:
    """Get repository status."""
    info = {"staged": [], "modified": [], "untracked": [], "deleted": []}
    
    success, output = run_git(["status", "--porcelain"], path)
    if success:
        for line in output.split("\n"):
            if len(line) < 3:
                continue
            status = line[:2]
            filename = line[3:]
            
            if status[0] in "MADRCU":
                info["staged"].append(filename)
            if status[1] == "M":
                info["modified"].append(filename)
            elif status[1] == "D":
                info["deleted"].append(filename)
            elif status == "??":
                info["untracked"].append(filename)
    
    return info


def get_recent_commits(path: str, count: int = 5) -> list:
    """Get recent commit history."""
    success, output = run_git(
        ["log", f"-{count}", "--oneline", "--pretty=format:%h|%s|%ar"],
        path
    )
    if not success:
        return []
    
    commits = []
    for line in output.split("\n"):
        parts = line.split("|")
        if len(parts) >= 3:
            commits.append({
                "hash": parts[0],
                "message": parts[1][:50],
                "time": parts[2]
            })
    return commits


def get_stash_info(path: str) -> list:
    """Get stash list."""
    success, output = run_git(["stash", "list"], path)
    if success and output:
        return output.split("\n")
    return []


def main():
    parser = argparse.ArgumentParser(description="Display Git repository status")
    parser.add_argument("--path", "-p", default=".", help="Repository path (default: current directory)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed information")
    args = parser.parse_args()
    
    path = os.path.abspath(args.path)
    
    # Verify it's a git repository
    if not os.path.exists(os.path.join(path, ".git")):
        print(f"❌ Not a git repository: {path}")
        return 1
    
    print(f"📁 Repository: {path}\n")
    
    # Branch info
    branch_info = get_branch_info(path)
    print(f"🌿 Branch: {branch_info.get('current_branch', 'unknown')}")
    
    ahead = branch_info.get("ahead", 0)
    behind = branch_info.get("behind", 0)
    if ahead or behind:
        if ahead:
            print(f"   ↑ {ahead} commits ahead of upstream")
        if behind:
            print(f"   ↓ {behind} commits behind upstream")
    
    if args.verbose:
        local = branch_info.get("local_branches", [])
        print(f"\n   Local branches: {len(local)}")
        for b in local[:5]:
            marker = "→ " if b == branch_info.get("current_branch") else "  "
            print(f"   {marker}{b}")
    
    print()
    
    # Status
    status = get_status_info(path)
    total_changes = len(status["staged"]) + len(status["modified"]) + len(status["untracked"]) + len(status["deleted"])
    
    if total_changes == 0:
        print("✅ Working tree clean")
    else:
        print(f"📝 Changes ({total_changes} files):")
        
        if status["staged"]:
            print(f"   ✓ Staged: {len(status['staged'])}")
            if args.verbose:
                for f in status["staged"][:5]:
                    print(f"      + {f}")
        
        if status["modified"]:
            print(f"   ● Modified: {len(status['modified'])}")
            if args.verbose:
                for f in status["modified"][:5]:
                    print(f"      ~ {f}")
        
        if status["untracked"]:
            print(f"   ? Untracked: {len(status['untracked'])}")
            if args.verbose:
                for f in status["untracked"][:5]:
                    print(f"      ? {f}")
        
        if status["deleted"]:
            print(f"   ✗ Deleted: {len(status['deleted'])}")
    
    print()
    
    # Recent commits
    commits = get_recent_commits(path, 5 if args.verbose else 3)
    if commits:
        print("📜 Recent commits:")
        for c in commits:
            print(f"   {c['hash']} {c['message']} ({c['time']})")
    
    # Stashes
    stashes = get_stash_info(path)
    if stashes:
        print(f"\n📦 Stashes: {len(stashes)}")
        if args.verbose:
            for s in stashes[:3]:
                print(f"   {s}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
