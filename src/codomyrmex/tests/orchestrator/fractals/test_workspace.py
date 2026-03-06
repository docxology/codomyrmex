"""Tests for workspace git management."""

from pathlib import Path

from codomyrmex.orchestrator.fractals.workspace import WorkspaceManager


def test_workspace_manager_lifecycle(tmp_path: Path) -> None:
    """Test initializing a workspace and managing worktrees completely naturally."""
    wm = WorkspaceManager(tmp_path)

    # 1. Initialize
    wm.init_workspace()
    assert (tmp_path / ".git").exists()
    assert (tmp_path / ".gitkeep").exists()

    # 2. Add worktree
    task_id = "test-123"
    wt_path = wm.create_worktree(task_id)
    assert wt_path.exists()
    assert wt_path.is_dir()

    # 3. Worktree points to our workspace logically
    assert (wt_path / ".git").exists()  # git worktrees put a .git FILE (not dir) inside child worktrees

    # 4. Remove worktree
    wm.remove_worktree(task_id)
    # The directory should be gone or git tracked differently
    assert not wt_path.exists()
