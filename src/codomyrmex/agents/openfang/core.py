"""OpenFangRunner — subprocess wrapper for the openfang binary."""
from __future__ import annotations

import shutil
import subprocess
from typing import TYPE_CHECKING

from .config import OpenFangConfig, get_config
from .exceptions import OpenFangNotInstalledError, OpenFangTimeoutError

if TYPE_CHECKING:
    from collections.abc import Iterator


class OpenFangRunner:
    """Subprocess-based integration for the openfang Agent OS.

    All public methods return dicts with {"stdout": str, "stderr": str, "returncode": str}.
    This keeps the MCP tool layer consistent and agnostic to upstream CLI churn.
    """

    def __init__(self, timeout: int | None = None, config: OpenFangConfig | None = None) -> None:
        self._config = config or get_config()
        self._timeout = timeout if timeout is not None else self._config.timeout
        self._cmd_path = self._find_openfang()

    def _find_openfang(self) -> str:
        """Return path to openfang binary or raise OpenFangNotInstalledError."""
        path = shutil.which(self._config.command)
        if path is None:
            raise OpenFangNotInstalledError(
                f"openfang binary not found on PATH (command={self._config.command!r}). "
                "Install: curl -fsSL https://openfang.sh/install.sh | sh"
            )
        return path

    def _run(self, args: list[str]) -> dict[str, str]:
        """Run openfang with the given args and return stdout/stderr/returncode."""
        cmd = [self._cmd_path, *args]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self._timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise OpenFangTimeoutError(
                f"openfang timed out after {self._timeout}s: {' '.join(cmd)}"
            ) from exc
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": str(result.returncode),
        }

    def execute(self, prompt: str) -> dict[str, str]:
        """Run openfang agent with a user prompt."""
        return self._run(["agent", "--message", prompt])

    def stream(self, prompt: str) -> Iterator[str]:
        """Stream openfang agent output line by line."""
        cmd = [self._cmd_path, "agent", "--message", prompt, "--stream"]
        try:
            with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            ) as proc:
                if proc.stdout:
                    yield from proc.stdout
        except OSError as exc:
            raise OpenFangNotInstalledError(str(exc)) from exc

    def hands_list(self) -> dict[str, str]:
        """List available autonomous Hands."""
        return self._run(["hands", "list"])

    def hands_run(self, hand_name: str, config_path: str = "") -> dict[str, str]:
        """Run a named Hand (autonomous agent package)."""
        args = ["hands", "run", hand_name]
        if config_path:
            args += ["--config", config_path]
        return self._run(args)

    def send_message(self, channel: str, target: str, message: str) -> dict[str, str]:
        """Send a message via a channel adapter (e.g. telegram, slack)."""
        return self._run(
            ["message", "send", "--channel", channel, "--to", target, "--message", message]
        )

    def gateway_action(self, action: str) -> dict[str, str]:
        """Control the openfang WebSocket gateway: start | stop | status."""
        if action not in {"start", "stop", "status"}:
            return {"stdout": "", "stderr": f"Unknown action: {action}", "returncode": "1"}
        return self._run(["gateway", action])

    def doctor(self) -> dict[str, str]:
        """Run openfang doctor health checks."""
        return self._run(["doctor"])

    def version(self) -> dict[str, str]:
        """Return openfang version info."""
        return self._run(["--version"])


def get_openfang_version() -> str:
    """Return openfang version string, or '' if not installed."""
    try:
        runner = OpenFangRunner()
        result = runner.version()
        return result["stdout"].strip()
    except Exception as _exc:
        return ""
