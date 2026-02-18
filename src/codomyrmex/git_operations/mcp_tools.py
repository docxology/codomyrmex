"""MCP tool definitions for the git_operations module.

Exposes core git operations (status, commit, branch, diff, log) as
MCP tools discoverable by Claude Code and other MCP-compatible agents.
"""

from __future__ import annotations

from typing import Any

try:
    from codomyrmex.model_context_protocol.decorators import mcp_tool
except ImportError:
    def mcp_tool(**kwargs: Any):  # type: ignore[misc]
        def decorator(func: Any) -> Any:
            func._mcp_tool_meta = kwargs
            return func
        return decorator


def _git():
    """Lazy import to avoid circular import with git_operations.__init__."""
    from .core import git
    return git


@mcp_tool(
    category="git_operations",
    description="Check if git is available on this system.",
)
def git_check_availability() -> dict[str, Any]:
    """Check if git is available."""
    available = _git().check_git_availability()
    return {"status": "ok", "git_available": available}


@mcp_tool(
    category="git_operations",
    description="Check if a directory is a git repository.",
)
def git_is_repo(path: str) -> dict[str, Any]:
    """Check if path is a git repository."""
    try:
        result = _git().is_git_repository(path)
        return {"status": "ok", "is_git_repository": result, "path": path}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Get the status of a git repository (modified, staged, untracked files).",
)
def git_repo_status(path: str = ".") -> dict[str, Any]:
    """Get git status for a repository."""
    try:
        result = _git().get_status(path)
        return {"status": "ok", "git_status": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Get the current branch name of a git repository.",
)
def git_current_branch(path: str = ".") -> dict[str, Any]:
    """Get the current branch name."""
    try:
        branch = _git().get_current_branch(path)
        return {"status": "ok", "branch": branch}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Get the diff of uncommitted changes in a git repository.",
)
def git_diff(path: str = ".", staged: bool = False) -> dict[str, Any]:
    """Get diff of changes."""
    try:
        diff = _git().get_diff(path, staged=staged)
        return {"status": "ok", "diff": diff}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Get recent commit history for a git repository.",
)
def git_log(path: str = ".", max_count: int = 10) -> dict[str, Any]:
    """Get commit history."""
    try:
        history = _git().get_commit_history(path, max_count=max_count)
        return {"status": "ok", "commits": history}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Initialize a new git repository at the given path.",
)
def git_init(path: str) -> dict[str, Any]:
    """Initialize a git repository."""
    try:
        result = _git().initialize_git_repository(path)
        return {"status": "ok", "initialized": True, "path": path, "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Clone a git repository from a URL to a local path.",
)
def git_clone(url: str, path: str, branch: str | None = None) -> dict[str, Any]:
    """Clone a repository."""
    try:
        result = _git().clone_repository(url, path, branch=branch)
        return {"status": "ok", "cloned": True, "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Stage files and create a commit with a message.",
)
def git_commit(
    path: str, message: str, files: list[str] | None = None
) -> dict[str, Any]:
    """Stage files and commit."""
    try:
        g = _git()
        if files:
            g.add_files(path, files)
        result = g.commit_changes(path, message)
        return {"status": "ok", "committed": True, "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Create a new branch in a git repository.",
)
def git_create_branch(path: str, branch_name: str) -> dict[str, Any]:
    """Create a new branch."""
    try:
        result = _git().create_branch(path, branch_name)
        return {"status": "ok", "branch": branch_name, "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Switch to a different branch in a git repository.",
)
def git_switch_branch(path: str, branch_name: str) -> dict[str, Any]:
    """Switch to a branch."""
    try:
        result = _git().switch_branch(path, branch_name)
        return {"status": "ok", "branch": branch_name, "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Pull latest changes from a remote git repository.",
)
def git_pull(path: str = ".", remote: str = "origin") -> dict[str, Any]:
    """Pull changes from remote."""
    try:
        result = _git().pull_changes(path, remote=remote)
        return {"status": "ok", "pulled": True, "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Push local commits to a remote git repository.",
)
def git_push(path: str = ".", remote: str = "origin") -> dict[str, Any]:
    """Push changes to remote."""
    try:
        result = _git().push_changes(path, remote=remote)
        return {"status": "ok", "pushed": True, "result": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
