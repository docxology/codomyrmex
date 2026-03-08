"""Server lifecycle manager for the PAI Project Manager Bun server."""

from __future__ import annotations

import contextlib
import logging
import os
import shutil
import signal
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from codomyrmex.pai_pm.exceptions import (
    PaiPmNotInstalledError,
    PaiPmServerError,
)

logger = logging.getLogger(__name__)

# Allowlist of env var prefixes passed to the Bun subprocess.
# API keys for Python-side LLMs are explicitly excluded.
_ENV_ALLOWLIST_PREFIXES = ("PAI_", "GOOGLE_", "AGENTMAIL_", "GITHUB_")
_ENV_ALLOWLIST_EXACT = ("PATH", "HOME", "USER", "LOGNAME", "TMPDIR", "LANG", "NO_COLOR")
_ENV_BLOCKLIST_EXACT = frozenset({"ANTHROPIC_API_KEY", "OPENAI_API_KEY"})

_PID_FILE = Path.home() / ".codomyrmex" / "pai_pm.pid"


def get_bun_version() -> str:
    """Return the installed bun version string, or empty string if not installed."""
    bun_path = shutil.which("bun")
    if not bun_path:
        return ""
    try:
        proc = subprocess.run(
            [bun_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return proc.stdout.strip() or proc.stderr.strip()
    except (subprocess.TimeoutExpired, OSError):
        return ""


class PaiPmServerManager:
    """Manages the lifecycle of the PAI PM Bun server subprocess."""

    def __init__(self) -> None:
        from codomyrmex.pai_pm.config import get_config

        self._cfg = get_config()

    # ── Internal helpers ──────────────────────────────────────────────────

    def _find_bun(self) -> str:
        """Return path to bun binary or raise PaiPmNotInstalledError."""
        path = shutil.which("bun")
        if not path:
            raise PaiPmNotInstalledError(
                "bun runtime not found in PATH. Install from https://bun.sh"
            )
        return path

    def _base_url(self) -> str:
        return f"http://{self._cfg.host}:{self._cfg.port}"

    def _build_safe_env(self) -> dict[str, str]:
        """Build a subprocess env allowlist, excluding sensitive API keys."""
        safe: dict[str, str] = {}
        for key, val in os.environ.items():
            if key in _ENV_BLOCKLIST_EXACT:
                continue
            if key in _ENV_ALLOWLIST_EXACT:
                safe[key] = val
                continue
            if any(key.startswith(pfx) for pfx in _ENV_ALLOWLIST_PREFIXES):
                safe[key] = val
        safe["NO_COLOR"] = "1"
        return safe

    def _write_pid(self, pid: int) -> None:
        """Write PID to file with restricted permissions."""
        _PID_FILE.parent.mkdir(parents=True, exist_ok=True)
        _PID_FILE.write_text(str(pid))
        _PID_FILE.chmod(0o600)

    def _read_pid(self) -> int | None:
        """Read PID from file; return None if file missing or invalid."""
        try:
            return int(_PID_FILE.read_text().strip())
        except (OSError, ValueError):
            return None

    # ── Public API ────────────────────────────────────────────────────────

    def is_running(self) -> bool:
        """Return True if the server is responding to health checks."""
        try:
            url = f"{self._base_url()}/api/health"
            with urllib.request.urlopen(url, timeout=2) as resp:
                return resp.status == 200
        except Exception as _exc:
            return False

    def start(self) -> dict[str, object]:
        """Start the PAI PM server as a background subprocess.

        Returns:
            dict with keys: status, pid, port, host

        Raises:
            PaiPmServerError: if server does not become healthy within startup_timeout.
        """
        if self.is_running():
            return {
                "status": "already_running",
                "pid": self._read_pid(),
                "port": self._cfg.port,
                "host": self._cfg.host,
            }

        bun = self._find_bun()
        script = self._cfg.server_script

        proc = subprocess.Popen(
            [bun, script],
            env=self._build_safe_env(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        self._write_pid(proc.pid)
        logger.info("PAI PM server started (pid=%d port=%d)", proc.pid, self._cfg.port)

        deadline = time.monotonic() + self._cfg.startup_timeout
        while time.monotonic() < deadline:
            if self.is_running():
                return {
                    "status": "started",
                    "pid": proc.pid,
                    "port": self._cfg.port,
                    "host": self._cfg.host,
                }
            time.sleep(0.5)

        proc.terminate()
        raise PaiPmServerError(
            f"PAI PM server did not become healthy within {self._cfg.startup_timeout}s"
        )

    def stop(self) -> dict[str, object]:
        """Stop the PAI PM server by PID.

        Returns:
            dict with keys: status, pid
        """
        pid = self._read_pid()
        if pid is None:
            return {"status": "not_running", "pid": None}

        try:
            os.kill(pid, signal.SIGTERM)
            for _ in range(10):
                time.sleep(0.5)
                try:
                    os.kill(pid, 0)  # probe: still alive?
                except ProcessLookupError:
                    break
            else:
                os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass  # already dead

        with contextlib.suppress(OSError):
            _PID_FILE.unlink(missing_ok=True)

        logger.info("PAI PM server stopped (pid=%d)", pid)
        return {"status": "stopped", "pid": pid}
