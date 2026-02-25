"""
Terminal shell management utilities.

Provides utilities for managing terminal shells and sessions.
"""

import os
import queue
import shlex
import signal
import subprocess
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ShellType(Enum):
    """Types of shells."""
    BASH = "bash"
    ZSH = "zsh"
    SH = "sh"
    FISH = "fish"
    POWERSHELL = "powershell"
    CMD = "cmd"


@dataclass
class ShellConfig:
    """Configuration for a shell."""
    shell_type: ShellType
    executable: str
    args: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    cwd: str | None = None
    timeout: float | None = None

    @classmethod
    def detect(cls) -> 'ShellConfig':
        """Detect the default shell."""
        shell_path = os.environ.get('SHELL', '/bin/sh')
        shell_name = os.path.basename(shell_path)

        shell_map = {
            'bash': ShellType.BASH,
            'zsh': ShellType.ZSH,
            'sh': ShellType.SH,
            'fish': ShellType.FISH,
        }

        shell_type = shell_map.get(shell_name, ShellType.SH)

        return cls(
            shell_type=shell_type,
            executable=shell_path,
        )


@dataclass
class CommandResult:
    """Result of a command execution."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float

    @property
    def success(self) -> bool:
        """Execute Success operations natively."""
        return self.exit_code == 0

    def to_dict(self) -> dict[str, Any]:
        """Execute To Dict operations natively."""
        return {
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "success": self.success,
        }


class Shell:
    """A shell for executing commands."""

    def __init__(self, config: ShellConfig | None = None):
        """Execute   Init   operations natively."""
        self.config = config or ShellConfig.detect()
        self._process: subprocess.Popen | None = None
        self._history: list[CommandResult] = []

    def run(
        self,
        command: str,
        timeout: float | None = None,
        env: dict[str, str] | None = None,
        cwd: str | None = None,
    ) -> CommandResult:
        """Run a command and wait for completion."""
        start_time = time.time()

        # Build environment
        full_env = os.environ.copy()
        full_env.update(self.config.env)
        if env:
            full_env.update(env)

        # Build command
        shell_args = [self.config.executable, '-c', command]

        try:
            result = subprocess.run(
                shell_args,
                capture_output=True,
                text=True,
                env=full_env,
                cwd=cwd or self.config.cwd,
                timeout=timeout or self.config.timeout,
            )

            cmd_result = CommandResult(
                command=command,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_ms=(time.time() - start_time) * 1000,
            )

        except subprocess.TimeoutExpired as e:
            cmd_result = CommandResult(
                command=command,
                exit_code=-1,
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=f"Command timed out after {timeout}s",
                duration_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            cmd_result = CommandResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

        self._history.append(cmd_result)
        return cmd_result

    def run_background(
        self,
        command: str,
        env: dict[str, str] | None = None,
        cwd: str | None = None,
    ) -> subprocess.Popen:
        """Run a command in the background."""
        full_env = os.environ.copy()
        full_env.update(self.config.env)
        if env:
            full_env.update(env)

        shell_args = [self.config.executable, '-c', command]

        process = subprocess.Popen(
            shell_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
            cwd=cwd or self.config.cwd,
        )

        return process

    def get_history(self) -> list[CommandResult]:
        """Get command history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear command history."""
        self._history.clear()


class InteractiveShell:
    """An interactive shell session."""

    def __init__(self, config: ShellConfig | None = None):
        """Execute   Init   operations natively."""
        self.config = config or ShellConfig.detect()
        self._process: subprocess.Popen | None = None
        self._output_queue: queue.Queue = queue.Queue()
        self._reader_thread: threading.Thread | None = None
        self._running = False

    def start(self) -> None:
        """Start the interactive shell."""
        if self._running:
            return

        full_env = os.environ.copy()
        full_env.update(self.config.env)

        self._process = subprocess.Popen(
            [self.config.executable, '-i'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=full_env,
            cwd=self.config.cwd,
            bufsize=0,
        )

        self._running = True

        # Start output reader thread
        self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
        self._reader_thread.start()

    def _read_output(self) -> None:
        """Read output from the shell."""
        while self._running and self._process:
            try:
                line = self._process.stdout.readline()
                if line:
                    self._output_queue.put(line.decode())
                elif self._process.poll() is not None:
                    break
            except Exception:
                break

    def send(self, command: str) -> None:
        """Send a command to the shell."""
        if not self._running or not self._process:
            raise RuntimeError("Shell not running")

        self._process.stdin.write(f"{command}\n".encode())
        self._process.stdin.flush()

    def read_output(self, timeout: float = 1.0) -> str:
        """Read available output."""
        output_lines = []
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                line = self._output_queue.get(timeout=0.1)
                output_lines.append(line)
            except queue.Empty:
                if output_lines:
                    break

        return "".join(output_lines)

    def execute(self, command: str, timeout: float = 5.0) -> str:
        """Execute a command and return output."""
        # Clear any pending output
        while not self._output_queue.empty():
            try:
                self._output_queue.get_nowait()
            except queue.Empty:
                break

        self.send(command)
        return self.read_output(timeout)

    def stop(self) -> None:
        """Stop the shell."""
        self._running = False

        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None

        if self._reader_thread:
            self._reader_thread.join(timeout=1)
            self._reader_thread = None

    @property
    def is_running(self) -> bool:
        """Execute Is Running operations natively."""
        return self._running and self._process is not None


class CommandBuilder:
    """Builder for constructing shell commands."""

    def __init__(self, base_command: str = ""):
        """Execute   Init   operations natively."""
        self._parts: list[str] = []
        if base_command:
            self._parts.append(base_command)
        self._env: dict[str, str] = {}
        self._redirects: list[str] = []

    def add(self, *args: str) -> 'CommandBuilder':
        """Add arguments to the command."""
        self._parts.extend(args)
        return self

    def flag(self, name: str, value: str | None = None) -> 'CommandBuilder':
        """Add a flag to the command."""
        if value is not None:
            self._parts.extend([name, value])
        else:
            self._parts.append(name)
        return self

    def env(self, key: str, value: str) -> 'CommandBuilder':
        """Add an environment variable."""
        self._env[key] = value
        return self

    def pipe(self, command: str) -> 'CommandBuilder':
        """Pipe output to another command."""
        self._parts.extend(['|', command])
        return self

    def redirect_stdout(self, path: str, append: bool = False) -> 'CommandBuilder':
        """Redirect stdout to a file."""
        op = ">>" if append else ">"
        self._redirects.append(f"{op} {shlex.quote(path)}")
        return self

    def redirect_stderr(self, path: str) -> 'CommandBuilder':
        """Redirect stderr to a file."""
        self._redirects.append(f"2> {shlex.quote(path)}")
        return self

    def background(self) -> 'CommandBuilder':
        """Run command in background."""
        self._parts.append('&')
        return self

    def build(self) -> str:
        """Build the final command string."""
        parts = []

        # Add environment variables
        for key, value in self._env.items():
            parts.append(f"{key}={shlex.quote(value)}")

        # Add command parts
        parts.extend(self._parts)

        # Add redirects
        parts.extend(self._redirects)

        return " ".join(parts)


def create_shell(shell_type: ShellType | None = None) -> Shell:
    """Create a shell instance."""
    if shell_type:
        executables = {
            ShellType.BASH: "/bin/bash",
            ShellType.ZSH: "/bin/zsh",
            ShellType.SH: "/bin/sh",
            ShellType.FISH: "/usr/bin/fish",
        }
        config = ShellConfig(
            shell_type=shell_type,
            executable=executables.get(shell_type, "/bin/sh"),
        )
    else:
        config = ShellConfig.detect()

    return Shell(config)


__all__ = [
    "ShellType",
    "ShellConfig",
    "CommandResult",
    "Shell",
    "InteractiveShell",
    "CommandBuilder",
    "create_shell",
]
