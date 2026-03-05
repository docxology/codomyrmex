"""Jules CLI agent client for Codomyrmex.

Wraps the Jules coding agent CLI (``julius``) for subprocess-based AI code editing,
task dispatch, and swarm orchestration.
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import AgentError, AgentTimeoutError, JulesError
from codomyrmex.agents.generic import CLIAgentBase

if TYPE_CHECKING:
    from collections.abc import Iterator

# Auth-related strings Jules CLI may emit on failure
_AUTH_MARKERS = (
    "unauthorized",
    "unauthenticated",
    "401",
    "403",
    "forbidden",
    "login required",
    "please log in",
    "not authenticated",
)

# Jules subcommands that bypass the "new" default
_DIRECT_COMMANDS = frozenset(
    {"auth", "config", "login", "logout", "list", "cancel", "get", "status"}
)


class JulesClient(CLIAgentBase):
    """Client for interacting with Jules CLI tool."""

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize Jules client.

        Args:
            config: Optional configuration override. Recognised keys:
                ``jules_command`` (str, default ``"jules"``),
                ``jules_timeout`` (int, default 30),
                ``jules_working_dir`` (str | None).
        """
        super().__init__(
            name="jules",
            command="jules",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.TASK_DECOMPOSITION,
            ],
            config=config or {},
            timeout=30,
            working_dir=None,
        )

        # Only override base-class defaults when the config key is explicitly set
        jules_command = self.get_config_value("jules_command", config=config)
        timeout = self.get_config_value("jules_timeout", config=config)
        working_dir_str = self.get_config_value("jules_working_dir", config=config)

        if jules_command:
            self.command = jules_command
        if timeout is not None:
            self.timeout = timeout
        if working_dir_str:
            self.working_dir = Path(working_dir_str)

        # Verify jules is available against the resolved command
        if not self._check_command_available(check_args=["help"]):
            self.logger.warning(
                "Jules command not found, some operations may fail",
                extra={"command": self.command},
            )

    def _execute_impl(self, request: AgentRequest) -> AgentResponse:
        """Execute Jules command with exponential-backoff retry on timeouts."""
        prompt = request.prompt
        context = request.context or {}
        jules_args = self._build_jules_args(prompt, context)

        retries = 3

        for attempt in range(retries):
            try:
                result = self._execute_command(args=jules_args)

                # Check for auth errors in output
                stdout = result.get("stdout", "").lower()
                stderr = result.get("stderr", "").lower()
                if any(
                    marker in stdout or marker in stderr for marker in _AUTH_MARKERS
                ):
                    raise JulesError(
                        "Jules authentication failed. Please run 'jules auth login'.",
                        command=self.command,
                    )

                return self._build_response_from_result(
                    result,
                    request,
                    additional_metadata={
                        "jules_success": result.get("success", False),
                        "command_full": " ".join([self.command, *jules_args]),
                        "attempt": attempt + 1,
                    },
                )
            except AgentTimeoutError as e:
                if attempt < retries - 1:
                    time.sleep(min(2**attempt, 8))
                    continue
                raise JulesError(
                    f"Jules command timed out after {retries} attempts: {e}",
                    command=self.command,
                ) from e
            except AgentError as e:
                raise JulesError(
                    f"Jules command failed: {e}", command=self.command
                ) from e
            except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
                self.logger.error(f"Jules execution failed: {e}", exc_info=True)
                raise JulesError(
                    f"Jules command failed: {e}", command=self.command
                ) from e
        return None

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream Jules command output."""
        prompt = request.prompt
        context = request.context or {}
        jules_args = self._build_jules_args(prompt, context)
        yield from self._stream_command(args=jules_args)

    def _build_jules_args(self, prompt: str, context: dict[str, Any]) -> list[str]:
        """Build jules command arguments from prompt and context.

        Args:
            prompt: Task description passed to Jules.
            context: Optional keys — ``command`` (str), ``args`` (list[str]),
                ``repo`` (str), ``parallel`` (int).

        Returns:
            Argument list suitable for subprocess call.
        """
        # Direct subcommand passthrough
        if context.get("command"):
            cmd = context["command"]
            if cmd in _DIRECT_COMMANDS:
                args = [cmd]
                if context.get("args"):
                    args.extend(context["args"])
                return args

        args = ["new"]

        if "repo" in context:
            args.extend(["--repo", str(context["repo"])])

        if "parallel" in context:
            args.extend(["--parallel", str(context["parallel"])])

        args.append(prompt)
        return args

    def get_jules_help(self) -> dict[str, Any]:
        """Get jules help information.

        Returns:
            dict with keys: ``help_text``, ``exit_code``, ``available``.
        """
        try:
            result = self._execute_command(args=["help"], timeout=5)
            return {
                "help_text": result.get("stdout", ""),
                "exit_code": result.get("exit_code", 0),
                "available": result.get("success", False),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning(f"Failed to get Jules help: {e}")
            return {
                "help_text": "",
                "exit_code": -1,
                "available": False,
                "error": str(e),
            }

    def execute_jules_command(
        self,
        command: str,
        args: list[str] | None = None,
        config_path: Path | None = None,
    ) -> dict[str, Any]:
        """Execute a jules subcommand directly.

        Args:
            command: The jules subcommand (e.g., ``'auth'``, ``'config'``).
            args: Additional arguments appended after the subcommand.
            config_path: Path to a custom config file (passed as ``--config``).

        Returns:
            Raw subprocess result dict from ``_execute_command``.
        """
        jules_args = [command]

        if config_path:
            jules_args.extend(["--config", str(config_path)])

        if args:
            jules_args.extend(args)

        return self._execute_command(args=jules_args)

    def dispatch_swarm(
        self,
        tasks: list[str],
        repo: str,
        parallel: int = 100,
        batch_size: int = 10,
    ) -> list[AgentResponse]:
        """Dispatch a swarm of Jules agents to execute many tasks in parallel.

        Batches ``tasks`` into groups of ``batch_size`` and calls
        ``julius new --repo <repo> --parallel <parallel> "<compound_prompt>"``
        for each batch.

        Args:
            tasks: Ordered list of task descriptions to execute.
            repo: Repository path or GitHub slug (e.g. ``'owner/repo'``).
            parallel: Jules ``--parallel`` value — agents per batch (default 100).
            batch_size: Max tasks combined into one Jules invocation (default 10).

        Returns:
            List of :class:`AgentResponse`, one per batch.
        """
        if not tasks:
            return []

        responses: list[AgentResponse] = []

        for batch_start in range(0, len(tasks), batch_size):
            batch = tasks[batch_start : batch_start + batch_size]
            batch_num = batch_start // batch_size + 1
            total_batches = (len(tasks) + batch_size - 1) // batch_size

            compound_prompt = (
                f"[Swarm batch {batch_num}/{total_batches} — {len(batch)} tasks]\n\n"
                + "\n".join(f"{i + 1}. {t}" for i, t in enumerate(batch))
            )

            self.logger.info(
                "Dispatching Jules swarm batch",
                extra={
                    "batch": batch_num,
                    "total_batches": total_batches,
                    "task_count": len(batch),
                    "repo": repo,
                    "parallel": parallel,
                },
            )

            request = AgentRequest(
                prompt=compound_prompt,
                context={"repo": repo, "parallel": parallel},
            )
            responses.append(self.execute(request))

        return responses


class JulesSwarmDispatcher:
    """Orchestrates large Jules swarm runs from structured task lists.

    Example::

        client = JulesClient()
        dispatcher = JulesSwarmDispatcher.from_todo_md(
            client, repo="owner/repo", todo_path=Path("TODO.md")
        )
        responses = dispatcher.dispatch(parallel=100)
    """

    def __init__(self, client: JulesClient, repo: str, tasks: list[str] | None = None):
        """
        Args:
            client: Configured :class:`JulesClient` instance.
            repo: Target repository path or GitHub slug.
            tasks: Optional pre-parsed task list. Populated by :meth:`from_todo_md`.
        """
        self.client = client
        self.repo = repo
        self.tasks: list[str] = tasks or []

    @classmethod
    def from_todo_md(
        cls,
        client: JulesClient,
        repo: str,
        todo_path: Path,
        priority_filter: str | None = None,
    ) -> JulesSwarmDispatcher:
        """Parse open ``- [ ]`` TODO items from a Markdown file.

        Args:
            client: Configured :class:`JulesClient` instance.
            repo: Target repository path or GitHub slug.
            todo_path: Path to a ``TODO.md``-style file.
            priority_filter: If set (e.g. ``"CRITICAL"`` or ``"HIGH"``), only
                include items under sections whose heading contains that string.

        Returns:
            :class:`JulesSwarmDispatcher` with ``tasks`` populated.

        Raises:
            FileNotFoundError: If ``todo_path`` does not exist.
        """
        text = todo_path.read_text(encoding="utf-8")
        tasks: list[str] = []

        if priority_filter:
            # Find sections matching the filter, extract their checkbox items
            section_pattern = re.compile(
                rf"(?:^|\n)(#{{}}\s[^\n]*{re.escape(priority_filter)}[^\n]*)\n(.*?)(?=\n#{{}}|\Z)",
                re.IGNORECASE | re.DOTALL,
            )
            for match in section_pattern.finditer(text):
                section_body = match.group(2)
                for item in re.finditer(r"^- \[ \] (.+)$", section_body, re.MULTILINE):
                    tasks.append(item.group(1).strip())
        else:
            for item in re.finditer(r"^- \[ \] (.+)$", text, re.MULTILINE):
                tasks.append(item.group(1).strip())

        return cls(client=client, repo=repo, tasks=tasks)

    def dispatch(
        self,
        parallel: int = 100,
        batch_size: int = 10,
    ) -> list[AgentResponse]:
        """Fire the full swarm using the stored task list.

        Args:
            parallel: Jules ``--parallel`` value (default 100).
            batch_size: Tasks per Jules invocation (default 10).

        Returns:
            List of :class:`AgentResponse`, one per batch.
        """
        return self.client.dispatch_swarm(
            tasks=self.tasks,
            repo=self.repo,
            parallel=parallel,
            batch_size=batch_size,
        )
