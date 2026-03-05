"""Core runner for the gws (Google Workspace CLI) subprocess wrapper."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any

from codomyrmex.agents.google_workspace.exceptions import (
    GWSNotInstalledError,
    GWSTimeoutError,
)


class GoogleWorkspaceRunner:
    """Wraps the gws CLI tool via subprocess for programmatic use."""

    def __init__(self, account: str = "", timeout: int = 60) -> None:
        from codomyrmex.agents.google_workspace.config import get_config

        cfg = get_config()
        self.account = account or cfg.account
        self.timeout = timeout

    def _find_gws(self) -> str:
        """Return path to gws binary or raise GWSNotInstalledError."""
        path = shutil.which("gws")
        if not path:
            raise GWSNotInstalledError(
                "gws binary not found in PATH. "
                "Install with: npm install -g @googleworkspace/cli"
            )
        return path

    def _build_env(self) -> dict[str, str]:
        """Build subprocess environment with auth credentials injected."""
        from codomyrmex.agents.google_workspace.config import get_config

        cfg = get_config()
        env = os.environ.copy()
        if cfg.token:
            env["GOOGLE_WORKSPACE_CLI_TOKEN"] = cfg.token
        if cfg.credentials_file:
            env["GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE"] = cfg.credentials_file
        if self.account or cfg.account:
            env["GOOGLE_WORKSPACE_CLI_ACCOUNT"] = self.account or cfg.account
        return env

    def _build_cmd(
        self,
        service: str,
        resource: str,
        method: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        page_all: bool = False,
        dry_run: bool = False,
    ) -> list[str]:
        """Build the subprocess command list."""
        gws = self._find_gws()
        cmd: list[str] = [gws, service, resource, method]
        if params:
            cmd.extend(["--params", json.dumps(params)])
        if body:
            cmd.extend(["--json", json.dumps(body)])
        if page_all:
            cmd.append("--page-all")
        if dry_run:
            cmd.append("--dry-run")
        return cmd

    def _run_subprocess(self, cmd: list[str]) -> subprocess.CompletedProcess:
        """Execute subprocess with timeout and capture output."""
        try:
            return subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=self._build_env(),
            )
        except subprocess.TimeoutExpired as exc:
            raise GWSTimeoutError(
                f"gws subprocess timed out after {self.timeout}s"
            ) from exc

    def _parse_output(self, stdout: str) -> Any:
        """Parse stdout as JSON, NDJSON, or raw string."""
        text = stdout.strip()
        if not text:
            return text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # Try NDJSON (newline-delimited JSON)
        lines = [line for line in text.splitlines() if line.strip()]
        if len(lines) > 1:
            parsed = []
            for line in lines:
                try:
                    parsed.append(json.loads(line))
                except json.JSONDecodeError:
                    parsed.append(line)
            return parsed
        return text

    def run(
        self,
        service: str,
        resource: str,
        method: str,
        *,
        params: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        page_all: bool = False,
        dry_run: bool = False,
    ) -> dict[str, str]:
        """Run a gws command and return raw output dict."""
        cmd = self._build_cmd(
            service, resource, method,
            params=params, body=body, page_all=page_all, dry_run=dry_run,
        )
        proc = self._run_subprocess(cmd)
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": str(proc.returncode),
        }

    def schema(self, tool_path: str) -> dict[str, str]:
        """Fetch the JSON schema for a gws tool path (e.g., 'drive.files.list')."""
        gws = self._find_gws()
        cmd = [gws, "schema", tool_path]
        proc = self._run_subprocess(cmd)
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": str(proc.returncode),
        }

    def check(self) -> str:
        """Return the gws version string, or empty string if not installed."""
        gws_path = shutil.which("gws")
        if not gws_path:
            return ""
        try:
            proc = subprocess.run(
                [gws_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return proc.stdout.strip() or proc.stderr.strip()
        except (subprocess.TimeoutExpired, OSError):
            return ""


def get_gws_version() -> str:
    """Return the installed gws version string, or empty string if not installed."""
    gws_path = shutil.which("gws")
    if not gws_path:
        return ""
    try:
        proc = subprocess.run(
            [gws_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.stdout.strip() or proc.stderr.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""
