"""Core aider runner -- subprocess wrapper around the aider CLI."""

from __future__ import annotations

import shutil
import subprocess

from codomyrmex.aider.exceptions import AiderNotInstalledError, AiderTimeoutError

# Safe defaults applied to every subprocess call
_SAFE_FLAGS = ["--yes", "--no-pretty", "--no-auto-commits"]


class AiderRunner:
    """Wraps the aider CLI tool via subprocess for programmatic use."""

    def __init__(self, model: str = "", timeout: int = 300) -> None:
        from codomyrmex.aider.config import get_config

        cfg = get_config()
        self.model = model or cfg.model
        self.timeout = timeout

    # --- internal helpers ---

    def _find_aider(self) -> str:
        """Return path to aider binary or raise AiderNotInstalledError."""
        path = shutil.which("aider")
        if not path:
            raise AiderNotInstalledError(
                "aider binary not found in PATH. "
                "Install with: uv tool install aider-chat"
            )
        return path

    def _build_cmd(
        self,
        message: str,
        files: list[str],
        *,
        chat_mode: str = "code",
        editor_model: str = "",
    ) -> list[str]:
        """Build the subprocess command list."""
        aider = self._find_aider()
        cmd = [aider, "--model", self.model, "--message", message]
        cmd.extend(_SAFE_FLAGS)
        if chat_mode != "code":
            cmd.extend(["--chat-mode", chat_mode])
        if editor_model:
            cmd.extend(["--editor-model", editor_model])
        cmd.extend(files)
        return cmd

    def _run_subprocess(self, cmd: list[str]) -> subprocess.CompletedProcess:
        """Execute subprocess with timeout and capture output."""
        try:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise AiderTimeoutError(
                f"aider subprocess timed out after {self.timeout}s"
            ) from exc

    # --- public API ---

    def run_message(self, files: list[str], instruction: str) -> dict[str, str]:
        """Run aider in code mode with a single instruction."""
        cmd = self._build_cmd(instruction, files, chat_mode="code")
        proc = self._run_subprocess(cmd)
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": str(proc.returncode),
        }

    def run_ask(self, files: list[str], question: str) -> dict[str, str]:
        """Run aider in ask mode (no file changes)."""
        cmd = self._build_cmd(question, files, chat_mode="ask")
        proc = self._run_subprocess(cmd)
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": str(proc.returncode),
        }

    def run_architect(
        self, files: list[str], task: str, editor_model: str = ""
    ) -> dict[str, str]:
        """Run aider in architect mode for complex multi-step tasks."""
        aider = self._find_aider()
        cmd = [aider, "--model", self.model, "--architect", "--message", task]
        cmd.extend(_SAFE_FLAGS)
        if editor_model:
            cmd.extend(["--editor-model", editor_model])
        cmd.extend(files)
        proc = self._run_subprocess(cmd)
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": str(proc.returncode),
        }


def get_aider_version() -> str:
    """Return the installed aider version string, or empty string if not installed."""
    aider_path = shutil.which("aider")
    if not aider_path:
        return ""
    try:
        proc = subprocess.run(
            [aider_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.stdout.strip() or proc.stderr.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""
