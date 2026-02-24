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
        """Execute Mcp Tool operations natively."""
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


@mcp_tool(
    category="git_operations",
    description="Delete a local branch. Use force=True to delete unmerged branches.",
)
def git_delete_branch(path: str, branch_name: str, force: bool = False) -> dict[str, Any]:
    """Delete a local git branch."""
    try:
        result = _git().delete_branch(branch_name, repository_path=path, force=force)
        return {"status": "ok", "branch": branch_name, "deleted": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Merge a source branch into a target branch.",
)
def git_merge(path: str, source_branch: str, target_branch: str = None) -> dict[str, Any]:
    """Merge source_branch into target_branch (or current branch)."""
    try:
        result = _git().merge_branch(source_branch, target_branch=target_branch, repository_path=path)
        return {"status": "ok", "merged": result, "source": source_branch, "target": target_branch}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Rebase current branch onto a target branch.",
)
def git_rebase(path: str, target_branch: str) -> dict[str, Any]:
    """Rebase current branch onto target_branch."""
    try:
        result = _git().rebase_branch(target_branch, repository_path=path)
        return {"status": "ok", "rebased": result, "target": target_branch}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Cherry-pick a specific commit onto the current branch.",
)
def git_cherry_pick(path: str, commit_sha: str) -> dict[str, Any]:
    """Cherry-pick a commit."""
    try:
        result = _git().cherry_pick(commit_sha, repository_path=path)
        return {"status": "ok", "cherry_picked": result, "commit": commit_sha}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Revert a specific commit by creating a new inverse commit.",
)
def git_revert(path: str, commit_sha: str) -> dict[str, Any]:
    """Revert a commit."""
    try:
        result = _git().revert_commit(commit_sha, repository_path=path)
        return {"status": "ok", "reverted": result, "commit": commit_sha}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Reset the repository to a commit using soft, mixed, or hard mode.",
)
def git_reset(path: str, mode: str = "mixed", target: str = "HEAD") -> dict[str, Any]:
    """Reset repository to a commit."""
    try:
        result = _git().reset_changes(mode=mode, target=target, repository_path=path)
        return {"status": "ok", "reset": result, "mode": mode, "target": target}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Amend the most recent commit message or content.",
)
def git_amend(path: str, message: str = None) -> dict[str, Any]:
    """Amend the last commit."""
    try:
        result = _git().amend_commit(message=message, repository_path=path)
        return {"status": "ok", "amended_sha": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Stash uncommitted changes with an optional description message.",
)
def git_stash(path: str = ".", message: str = None) -> dict[str, Any]:
    """Stash uncommitted changes."""
    try:
        result = _git().stash_changes(message=message, repository_path=path)
        return {"status": "ok", "stashed": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Apply a stash entry to the working directory.",
)
def git_stash_apply(path: str = ".", stash_ref: str = None) -> dict[str, Any]:
    """Apply a stash."""
    try:
        result = _git().apply_stash(stash_ref=stash_ref, repository_path=path)
        return {"status": "ok", "applied": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="List all stash entries in the repository.",
)
def git_stash_list(path: str = ".") -> dict[str, Any]:
    """List all stashes."""
    try:
        result = _git().list_stashes(repository_path=path)
        return {"status": "ok", "stashes": result, "count": len(result)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Create a lightweight or annotated tag at the current commit.",
)
def git_create_tag(path: str, tag_name: str, message: str = None) -> dict[str, Any]:
    """Create a git tag."""
    try:
        result = _git().create_tag(tag_name, message=message, repository_path=path)
        return {"status": "ok", "tag": tag_name, "created": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="List all tags in the repository.",
)
def git_list_tags(path: str = ".") -> dict[str, Any]:
    """List all tags."""
    try:
        result = _git().list_tags(repository_path=path)
        return {"status": "ok", "tags": result, "count": len(result)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Fetch changes from a remote repository without merging.",
)
def git_fetch(path: str = ".", remote: str = "origin") -> dict[str, Any]:
    """Fetch from remote."""
    try:
        result = _git().fetch_changes(remote=remote, repository_path=path)
        return {"status": "ok", "fetched": result, "remote": remote}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Add a named remote URL to the repository.",
)
def git_add_remote(path: str, name: str, url: str) -> dict[str, Any]:
    """Add a remote."""
    try:
        result = _git().add_remote(name, url, repository_path=path)
        return {"status": "ok", "added": result, "name": name, "url": url}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Remove a named remote from the repository.",
)
def git_remove_remote(path: str, name: str) -> dict[str, Any]:
    """Remove a remote."""
    try:
        result = _git().remove_remote(name, repository_path=path)
        return {"status": "ok", "removed": result, "name": name}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="List all configured remotes for the repository.",
)
def git_list_remotes(path: str = ".") -> dict[str, Any]:
    """List all remotes."""
    try:
        result = _git().list_remotes(repository_path=path)
        return {"status": "ok", "remotes": result, "count": len(result)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Show git blame output for a file (line-by-line commit attribution).",
)
def git_blame(path: str, file_path: str) -> dict[str, Any]:
    """Get git blame for a file."""
    try:
        result = _git().get_blame(file_path, repository_path=path)
        return {"status": "ok", "blame": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Get detailed metadata for a specific commit by SHA.",
)
def git_commit_details(path: str, commit_sha: str) -> dict[str, Any]:
    """Get detailed information about a specific commit."""
    try:
        result = _git().get_commit_details(commit_sha, repository_path=path)
        return {"status": "ok", "commit": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Read a git configuration value by key.",
)
def git_get_config(path: str, key: str, global_config: bool = False) -> dict[str, Any]:
    """Get a git config value."""
    try:
        result = _git().get_config(key, repository_path=path, global_config=global_config)
        return {"status": "ok", "key": key, "value": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="Set a git configuration value (local or global scope).",
)
def git_set_config(path: str, key: str, value: str, global_config: bool = False) -> dict[str, Any]:
    """Set a git config value."""
    try:
        result = _git().set_config(key, value, repository_path=path, global_config=global_config)
        return {"status": "ok", "key": key, "value": value, "set": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@mcp_tool(
    category="git_operations",
    description="WARNING: Irreversible. Deletes untracked files from the working tree.",
)
def git_clean(path: str, force: bool = False, directories: bool = False) -> dict[str, Any]:
    """Clean untracked files from the repository."""
    try:
        result = _git().clean_repository(force=force, directories=directories, repository_path=path)
        return {"status": "ok", "cleaned": result}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
