"""Git workspace and worktree management for isolated task execution."""

import subprocess
from pathlib import Path


class WorkspaceManager:
    """Manages git workspaces and worktrees for fractal tasks."""

    def __init__(self, workspace_path: str | Path):
        self.workspace_path = Path(workspace_path).expanduser().resolve()
        self.worktrees_dir = self.workspace_path / ".worktrees"

    def _run(self, cmd: list[str], cwd: Path) -> str:
        """Run a CLI command and return its output."""
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Command failed with exit code {result.returncode}: {result.stderr.strip()}"
            )
        return result.stdout.strip()

    def init_workspace(self) -> None:
        """Initialize the workspace directory with a git repository."""
        self.workspace_path.mkdir(parents=True, exist_ok=True)

        if not (self.workspace_path / ".git").exists():
            self._run(["git", "init"], self.workspace_path)

            # create initial commit
            gitkeep = self.workspace_path / ".gitkeep"
            gitkeep.touch()
            self._run(["git", "add", "."], self.workspace_path)
            self._run(["git", "commit", "-m", "initial commit"], self.workspace_path)

    def create_worktree(self, task_id: str) -> Path:
        """Create a git worktree for a specific task. Returns the worktree path."""
        branch_name = f"task/{task_id}"
        worktree_path = self.worktrees_dir / task_id

        if worktree_path.exists():
            return worktree_path

        self.worktrees_dir.mkdir(parents=True, exist_ok=True)
        self._run(
            ["git", "worktree", "add", "-b", branch_name, str(worktree_path)],
            self.workspace_path,
        )
        return worktree_path

    def remove_worktree(self, task_id: str) -> None:
        """Remove a git worktree after task completion."""
        worktree_path = self.worktrees_dir / task_id
        if not worktree_path.exists():
            return

        self._run(
            ["git", "worktree", "remove", str(worktree_path), "--force"],
            self.workspace_path,
        )
