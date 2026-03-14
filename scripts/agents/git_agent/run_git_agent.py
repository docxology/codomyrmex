#!/usr/bin/env python3
"""Git Agent — Thin Script Orchestrator.

Uses GitAgent to report current repo status and branch info.

Usage:
    python scripts/agents/git_agent/run_git_agent.py [repo_path]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    sys.path.insert(
        0, str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    )

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    repo_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else str(Path(__file__).resolve().parent.parent.parent.parent)
    )
    print_info(f"Git Agent — analyzing {repo_path}...")

    try:
        from codomyrmex.agents.git_agent import GitAgent
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    agent = GitAgent(repo_path=repo_path)
    print_success(f"GitAgent instantiated for: {repo_path}")

    if hasattr(agent, "get_status"):
        status = agent.get_status()
        print_info(f"  Status: {status}")
    if hasattr(agent, "get_branch"):
        branch = agent.get_branch()
        print_info(f"  Branch: {branch}")

    print_success("Git agent probe complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
