"""Pi Coding Agent — RPC client.

Communicates with `pi --mode rpc` over stdin/stdout using newline-delimited
JSON (JSONL).  All I/O uses the stdlib only — zero external dependencies.

Protocol reference: https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/rpc.md
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional, Self

if TYPE_CHECKING:
    from collections.abc import Generator

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class PiConfig:
    """Configuration for the Pi coding agent client."""

    provider: str = "google"
    model: str = ""
    api_key: str = ""
    thinking: str = ""  # off | minimal | low | medium | high | xhigh
    tools: str = "read,bash,edit,write"
    session_dir: str = ""
    no_session: bool = False
    extra_args: list[str] = field(default_factory=list)

    # Process control
    pi_bin: str = ""  # Override path to `pi` binary
    cwd: str = ""  # Working directory for the pi process
    env: dict[str, str] = field(default_factory=dict)
    startup_timeout: float = 10.0  # Seconds to wait for pi to start


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class PiError(Exception):
    """Base exception for Pi client errors."""


class PiStartupError(PiError):
    """Raised when the pi process cannot be started."""


class PiProtocolError(PiError):
    """Raised on framing / parsing errors in the JSONL protocol."""


class PiTimeoutError(PiError):
    """Raised when waiting for a response times out."""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class PiClient:
    """High-level client for the pi coding agent RPC protocol.

    Usage::

        from codomyrmex.agents.pi import PiClient, PiConfig

        client = PiClient(PiConfig(provider="anthropic"))
        client.start()

        for event in client.prompt("list *.py files in src/"):
            if event.get("type") == "message_update":
                ae = event.get("assistantMessageEvent", {})
                if ae.get("type") == "text_delta":
                    print(ae["delta"], end="", flush=True)

        client.stop()
    """

    def __init__(self, config: Optional[PiConfig | dict] = None):
        if config is None:
            config = PiConfig()
        elif isinstance(config, dict):
            config = PiConfig(
                **{
                    k: v
                    for k, v in config.items()
                    if k in PiConfig.__dataclass_fields__
                }
            )
        self._config: PiConfig = config
        self._proc: Optional[subprocess.Popen] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._events: list[dict] = []
        self._lock = threading.Lock()
        self._request_id = 0

    # -- Lifecycle -----------------------------------------------------------

    @property
    def is_running(self) -> bool:
        """Return True if the pi subprocess is alive."""
        return self._proc is not None and self._proc.poll() is None

    def start(self) -> PiClient:
        """Launch the pi RPC subprocess.

        Returns self for chaining.
        Raises PiStartupError if pi cannot be found or fails to start.
        """
        if self.is_running:
            return self

        pi_bin = self._config.pi_bin or shutil.which("pi") or "pi"

        cmd: list[str] = [pi_bin, "--mode", "rpc"]

        if self._config.provider:
            cmd += ["--provider", self._config.provider]
        if self._config.model:
            cmd += ["--model", self._config.model]
        if self._config.api_key:
            cmd += ["--api-key", self._config.api_key]
        if self._config.thinking:
            cmd += ["--thinking", self._config.thinking]
        if self._config.tools:
            cmd += ["--tools", self._config.tools]
        if self._config.no_session:
            cmd += ["--no-session"]
        if self._config.session_dir:
            cmd += ["--session-dir", self._config.session_dir]
        cmd += self._config.extra_args

        env = {**os.environ, **self._config.env}
        cwd = self._config.cwd or None

        try:
            self._proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd,
                env=env,
            )
        except FileNotFoundError:
            raise PiStartupError(
                f"pi binary not found at '{pi_bin}'. "
                "Install with: npm install -g @mariozechner/pi-coding-agent"
            )
        except OSError as exc:
            raise PiStartupError(f"Failed to start pi: {exc}")

        # Start event reader thread
        self._events = []
        self._reader_thread = threading.Thread(target=self._read_events, daemon=True)
        self._reader_thread.start()

        return self

    def stop(self) -> dict:
        """Terminate the pi subprocess gracefully.

        Returns a dict with ``status`` and ``pid``.
        """
        if not self.is_running:
            return {"status": "not_running", "pid": None}

        pid = self._proc.pid
        try:
            self._proc.terminate()
            self._proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._proc.kill()
            self._proc.wait(timeout=2)

        self._proc = None
        return {"status": "stopped", "pid": pid}

    # -- RPC commands --------------------------------------------------------

    def _next_id(self) -> str:
        self._request_id += 1
        return f"req-{self._request_id}"

    def _send(self, cmd: dict) -> None:
        """Send a JSONL command to pi's stdin."""
        if not self.is_running:
            raise PiError("Pi process is not running. Call start() first.")
        line = json.dumps(cmd) + "\n"
        try:
            self._proc.stdin.write(line)
            self._proc.stdin.flush()
        except (BrokenPipeError, OSError) as exc:
            raise PiError(f"Failed to send command: {exc}")

    def _read_events(self) -> None:
        """Background thread: Continuously read JSONL events from stdout."""
        assert self._proc is not None
        stdout = self._proc.stdout
        if stdout is None:
            return
        try:
            for raw_line in stdout:
                line = raw_line.rstrip("\n").rstrip("\r")
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    with self._lock:
                        self._events.append(event)
                except json.JSONDecodeError:
                    pass  # Ignore non-JSON lines (startup banners, etc.)
        except (ValueError, OSError):
            pass  # Process closed

    def _drain_events(self) -> list[dict]:
        """Drain and return buffered events (thread-safe)."""
        with self._lock:
            evts, self._events = self._events[:], []
        return evts

    def prompt(
        self,
        message: str,
        *,
        images: Optional[list[dict]] = None,
        streaming_behavior: Optional[str] = None,
        timeout: float = 120.0,
    ) -> Generator[dict, None, None]:
        """Send a prompt and yield events until agent_end.

        Args:
            message: The user prompt.
            images: Optional list of image attachments (ImageContent format).
            streaming_behavior: ``"steer"`` or ``"followUp"`` if agent is mid-run.
            timeout: Max seconds to wait for agent_end.

        Yields:
            Each RPC event dict (message_update, tool_execution_*, agent_end, etc).
        """
        cmd: dict[str, Any] = {
            "id": self._next_id(),
            "type": "prompt",
            "message": message,
        }
        if images:
            cmd["images"] = images
        if streaming_behavior:
            cmd["streamingBehavior"] = streaming_behavior

        self._send(cmd)
        yield from self._wait_for_agent_end(timeout)

    def steer(self, message: str, *, images: Optional[list[dict]] = None) -> None:
        """Send a steering message (interrupts current tool chain)."""
        cmd: dict[str, Any] = {"type": "steer", "message": message}
        if images:
            cmd["images"] = images
        self._send(cmd)

    def follow_up(self, message: str, *, images: Optional[list[dict]] = None) -> None:
        """Queue a follow-up message (runs after agent finishes)."""
        cmd: dict[str, Any] = {"type": "follow_up", "message": message}
        if images:
            cmd["images"] = images
        self._send(cmd)

    def abort(self) -> None:
        """Abort the current agent operation."""
        self._send({"type": "abort"})

    def new_session(self, parent_session: Optional[str] = None) -> None:
        """Start a fresh session."""
        cmd: dict[str, Any] = {"type": "new_session"}
        if parent_session:
            cmd["parentSession"] = parent_session
        self._send(cmd)

    def set_model(self, model: str) -> None:
        """Switch model mid-session."""
        self._send({"type": "set_model", "model": model})

    def set_thinking(self, level: str) -> None:
        """set thinking level (off|minimal|low|medium|high|xhigh)."""
        self._send({"type": "set_thinking", "level": level})

    def get_state(self) -> None:
        """Request current agent state."""
        self._send({"id": self._next_id(), "type": "get_state"})

    def compact(self) -> None:
        """Trigger manual compaction."""
        self._send({"type": "compact"})

    # -- Helpers -------------------------------------------------------------

    def _wait_for_agent_end(self, timeout: float) -> Generator[dict, None, None]:
        """Yield events until ``agent_end`` or timeout."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            events = self._drain_events()
            for evt in events:
                yield evt
                if evt.get("type") == "agent_end":
                    return
            if not events:
                time.sleep(0.05)
        raise PiTimeoutError(f"Timed out waiting for agent_end after {timeout}s")

    def prompt_sync(
        self,
        message: str,
        *,
        timeout: float = 120.0,
    ) -> str:
        """Send a prompt and return the full text response (blocking).

        Collects all ``text_delta`` events and concatenates them.
        """
        parts: list[str] = []
        for event in self.prompt(message, timeout=timeout):
            if event.get("type") == "message_update":
                ae = event.get("assistantMessageEvent", {})
                if ae.get("type") == "text_delta":
                    parts.append(ae.get("delta", ""))
        return "".join(parts)

    def run_print(
        self,
        message: str,
        *,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ) -> str:
        """Run ``pi -p <message>`` in non-interactive print mode.

        This is a standalone subprocess call — it does NOT require
        ``start()`` and does not use the RPC protocol.

        Returns the stdout output.
        """
        pi_bin = self._config.pi_bin or shutil.which("pi") or "pi"
        cmd = [pi_bin, "-p", message]
        if provider or self._config.provider:
            cmd += ["--provider", provider or self._config.provider]
        if model or self._config.model:
            cmd += ["--model", model or self._config.model]

        env = {**os.environ, **self._config.env}
        cwd = self._config.cwd or None

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env,
            )
            if result.returncode != 0:
                raise PiError(
                    f"pi exited with code {result.returncode}: {result.stderr}"
                )
            return result.stdout
        except FileNotFoundError:
            raise PiStartupError(
                f"pi binary not found at '{pi_bin}'. "
                "Install with: npm install -g @mariozechner/pi-coding-agent"
            )
        except subprocess.TimeoutExpired:
            raise PiTimeoutError(f"pi -p timed out after {timeout}s")

    # -- Context methods -----------------------------------------------------

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()

    def __repr__(self) -> str:
        state = "running" if self.is_running else "stopped"
        return (
            f"PiClient(provider={self._config.provider!r}, "
            f"model={self._config.model!r}, state={state!r})"
        )
