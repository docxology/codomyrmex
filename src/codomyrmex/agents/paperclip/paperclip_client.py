"""Paperclip CLI client for Codomyrmex agents.

Wraps the ``paperclipai`` CLI (v0.2.7+) — a Node.js tool for
orchestrating zero-human companies with org charts, budgets,
governance, and agent coordination.

See: https://github.com/paperclipai/paperclip
"""

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from codomyrmex.agents.core import (
    AgentCapabilities,
    AgentRequest,
    AgentResponse,
)
from codomyrmex.agents.core.exceptions import (
    AgentError,
    AgentTimeoutError,
    PaperclipError,
)
from codomyrmex.agents.generic import CLIAgentBase


class PaperclipClient(CLIAgentBase):
    """Client for interacting with the Paperclip CLI tool.

    Paperclip orchestrates teams of AI agents into company structures
    with org charts, budgets, heartbeats, governance, and goal alignment.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize Paperclip client.

        Args:
            config: Optional configuration override. Recognized keys:

                - ``paperclip_command``: CLI binary name (default ``paperclipai``)
                - ``paperclip_timeout``: Default timeout in seconds (default 120)
                - ``paperclip_working_dir``: Working directory for CLI
                - ``paperclip_agent_id``: Default agent ID for heartbeat runs
                - ``paperclip_api_base``: API base URL (default ``http://localhost:3100``)
                - ``paperclip_config_path``: Path to Paperclip config file
        """
        super().__init__(
            name="paperclip",
            command="paperclipai",
            capabilities=[
                AgentCapabilities.CODE_GENERATION,
                AgentCapabilities.CODE_EDITING,
                AgentCapabilities.CODE_ANALYSIS,
                AgentCapabilities.TEXT_COMPLETION,
                AgentCapabilities.STREAMING,
                AgentCapabilities.MULTI_TURN,
                AgentCapabilities.TOOL_USE,
            ],
            config=config or {},
            timeout=120,
            working_dir=None,
        )

        paperclip_command = (
            self.get_config_value("paperclip_command", config=config) or "paperclipai"
        )
        timeout = self.get_config_value("paperclip_timeout", config=config)
        working_dir_str = self.get_config_value("paperclip_working_dir", config=config)
        working_dir = Path(working_dir_str) if working_dir_str else None

        self.command = paperclip_command
        self.timeout = timeout
        self.working_dir = working_dir
        self.agent_id: str | None = self.get_config_value(
            "paperclip_agent_id", config=config
        )
        self.api_base: str = (
            self.get_config_value("paperclip_api_base", config=config)
            or "http://localhost:3100"
        )
        self.config_path: str | None = self.get_config_value(
            "paperclip_config_path", config=config
        )

        # Verify paperclipai is available
        if not self._check_command_available(check_args=["--version"]):
            self.logger.warning(
                "Paperclip CLI not found, some operations may fail",
                extra={"command": self.command},
            )

    # ------------------------------------------------------------------ #
    # CLIAgentBase overrides
    # ------------------------------------------------------------------ #

    def _execute_impl(
        self, request: AgentRequest, max_tokens: int | None = None
    ) -> AgentResponse:
        """Execute a Paperclip heartbeat run for an agent.

        The default execution mode triggers a single heartbeat run
        via ``paperclipai heartbeat run --agent-id <id>``.
        """
        prompt = request.prompt
        context = request.context or {}
        args = self._build_paperclip_args(prompt, context)

        try:
            result = self._execute_command(args=args)
            return self._build_response_from_result(
                result,
                request,
                additional_metadata={
                    "paperclip_success": result.get("success", False),
                    "command_full": " ".join([self.command, *args]),
                },
            )
        except AgentTimeoutError as e:
            raise PaperclipError(
                f"Paperclip command timed out: {e!s}", command=self.command
            ) from e
        except AgentError as e:
            raise PaperclipError(
                f"Paperclip command failed: {e!s}", command=self.command
            ) from e
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Paperclip execution failed: %s", e, exc_info=True)
            raise PaperclipError(
                f"Paperclip command failed: {e!s}", command=self.command
            ) from e

    def _stream_impl(self, request: AgentRequest) -> Iterator[str]:
        """Stream Paperclip heartbeat output."""
        prompt = request.prompt
        context = request.context or {}
        args = self._build_paperclip_args(prompt, context)
        yield from self._stream_command(args=args)

    # ------------------------------------------------------------------ #
    # Argument builder
    # ------------------------------------------------------------------ #

    def _build_paperclip_args(self, prompt: str, context: dict[str, Any]) -> list[str]:
        """Build paperclipai command arguments from prompt and context.

        Supports subcommands:

        - ``heartbeat run --agent-id <id>`` for agent invocation
        - ``doctor`` for health diagnostics
        - ``onboard --yes`` for auto-setup
        - ``configure --section <section>`` for configuration
        - ``company list`` for listing companies
        - ``issue create`` for ticket creation
        """
        args: list[str] = []

        # Inject global config path if set
        if self.config_path:
            args.extend(["--config", self.config_path])

        # Doctor shortcut
        if context.get("doctor", False):
            args.append("doctor")
            if context.get("repair", False):
                args.append("--repair")
            return args

        # Onboard shortcut
        if context.get("onboard", False):
            args.extend(["onboard", "--yes"])
            return args

        # Configure shortcut
        if "configure_section" in context:
            args.extend(["configure", "--section", context["configure_section"]])
            return args

        # Explicit command dispatch
        if "command" in context:
            command = context["command"]
            if command == "doctor":
                args.append("doctor")
                if context.get("repair", False):
                    args.append("--repair")
                return args
            if command == "onboard":
                args.extend(["onboard", "--yes"])
                return args
            if command == "company_list":
                args.extend(["company", "list"])
                if context.get("json", False):
                    args.append("--json")
                return args
            if command == "issue_create":
                company_id = context.get("company_id", "")
                title = context.get("title", prompt)
                args.extend(
                    [
                        "issue",
                        "create",
                        "--company-id",
                        str(company_id),
                        "--title",
                        title,
                    ]
                )
                if context.get("description"):
                    args.extend(["--description", context["description"]])
                return args
            if command == "agent_list":
                company_id = context.get("company_id", "")
                args.extend(["agent", "list", "--company-id", str(company_id)])
                return args
            if command == "dashboard":
                company_id = context.get("company_id", "")
                args.extend(["dashboard", "--company-id", str(company_id)])
                return args

        # Default: heartbeat run
        agent_id = context.get("agent_id") or self.agent_id
        if not agent_id:
            # Fall back to generic run
            args.append("run")
            return args

        args.extend(["heartbeat", "run", "--agent-id", agent_id])

        source = context.get("source", "on_demand")
        args.extend(["--source", source])

        trigger = context.get("trigger", "manual")
        args.extend(["--trigger", trigger])

        if context.get("json", False):
            args.append("--json")
        if context.get("debug", False):
            args.append("--debug")

        timeout_ms = context.get("timeout_ms")
        if timeout_ms:
            args.extend(["--timeout-ms", str(timeout_ms)])

        return args

    # ------------------------------------------------------------------ #
    # High-level convenience methods
    # ------------------------------------------------------------------ #

    def get_version(self) -> dict[str, Any]:
        """Get Paperclip CLI version information."""
        try:
            result = self._execute_command(args=["--version"], timeout=5)
            return {
                "version": result.get("stdout", "").strip(),
                "exit_code": result.get("exit_code", 0),
                "available": result.get("success", False),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning("Failed to get Paperclip version: %s", e)
            return {"version": "", "exit_code": -1, "available": False, "error": str(e)}

    def run_doctor(self, repair: bool = False) -> dict[str, Any]:
        """Run Paperclip doctor for health diagnostics.

        Args:
            repair: If True, attempt automatic repair of issues.
        """
        try:
            args = ["doctor"]
            if repair:
                args.append("--repair")
            result = self._execute_command(args=args, timeout=30)
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Paperclip doctor failed: %s", e, exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def onboard(self) -> dict[str, Any]:
        """Run interactive Paperclip onboard setup (auto-accept defaults).

        Equivalent to ``paperclipai onboard --yes``.
        """
        try:
            result = self._execute_command(args=["onboard", "--yes"], timeout=120)
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Paperclip onboard failed: %s", e, exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def configure(self, section: str) -> dict[str, Any]:
        """Update a Paperclip configuration section.

        Args:
            section: Section to configure (llm, database, logging,
                     server, storage, secrets).
        """
        try:
            result = self._execute_command(
                args=["configure", "--section", section], timeout=30
            )
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Paperclip configure failed: %s", e, exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def trigger_heartbeat(
        self,
        agent_id: str,
        *,
        source: str = "on_demand",
        trigger: str = "manual",
    ) -> dict[str, Any]:
        """Trigger a single heartbeat run for an agent.

        Args:
            agent_id: Agent ID to invoke.
            source: Invocation source (timer | assignment | on_demand | automation).
            trigger: Trigger detail (manual | ping | callback | system).
        """
        try:
            result = self._execute_command(
                args=[
                    "heartbeat",
                    "run",
                    "--agent-id",
                    agent_id,
                    "--source",
                    source,
                    "--trigger",
                    trigger,
                    "--json",
                ],
                timeout=self.timeout,
            )
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Paperclip heartbeat failed: %s", e, exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def list_companies(self) -> dict[str, Any]:
        """list all companies in the Paperclip instance."""
        try:
            result = self._execute_command(
                args=["company", "list", "--json"], timeout=15
            )
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning("Paperclip company list failed: %s", e)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def list_agents(self, company_id: str) -> dict[str, Any]:
        """list agents in a company.

        Args:
            company_id: Company identifier.
        """
        try:
            result = self._execute_command(
                args=["agent", "list", "--company-id", company_id, "--json"],
                timeout=15,
            )
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning("Paperclip agent list failed: %s", e)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def create_issue(
        self, company_id: str, title: str, description: str | None = None
    ) -> dict[str, Any]:
        """Create a ticket/issue in a company.

        Args:
            company_id: Company identifier.
            title: Issue title.
            description: Optional detailed description.
        """
        try:
            args = [
                "issue",
                "create",
                "--company-id",
                company_id,
                "--title",
                title,
            ]
            if description:
                args.extend(["--description", description])
            args.append("--json")
            result = self._execute_command(args=args, timeout=15)
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Paperclip issue create failed: %s", e, exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def get_env(self) -> dict[str, Any]:
        """Print environment variables for deployment."""
        try:
            result = self._execute_command(args=["env"], timeout=10)
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.warning("Paperclip env failed: %s", e)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def db_backup(self, output_dir: str | None = None) -> dict[str, Any]:
        """Create a one-off database backup.

        Args:
            output_dir: Optional backup output directory.
        """
        try:
            args = ["db:backup", "--json"]
            if output_dir:
                args.extend(["--dir", output_dir])
            result = self._execute_command(args=args, timeout=60)
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Paperclip db:backup failed: %s", e, exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def import_company(self, source: str) -> dict[str, Any]:
        """Import a company from a source (path, URL, GitHub).

        Args:
            source: Source path or URL for import.
        """
        try:
            result = self._execute_command(
                args=["company", "import", source, "--json"], timeout=120
            )
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Paperclip company import failed: %s", e, exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def export_company(self, company_id: str, output_dir: str) -> dict[str, Any]:
        """Export a company to a directory.

        Args:
            company_id: Company identifier.
            output_dir: Output directory path.
        """
        try:
            result = self._execute_command(
                args=["company", "export", company_id, "--path", output_dir, "--json"],
                timeout=60,
            )
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Paperclip company export failed: %s", e, exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def approve_request(self, approval_id: str) -> dict[str, Any]:
        """Approve an agent hire or action request.

        Args:
            approval_id: ID of the approval request.
        """
        try:
            result = self._execute_command(
                args=["approval", "approve", approval_id, "--json"], timeout=30
            )
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
                "error": result.get("stderr") if not result.get("success") else None,
                "exit_code": result.get("exit_code", 0),
            }
        except (ValueError, RuntimeError, AttributeError, OSError, TypeError) as e:
            self.logger.error("Paperclip approval failed: %s", e, exc_info=True)
            return {"success": False, "output": "", "error": str(e), "exit_code": -1}

    def bootstrap_mission(
        self, company_id: str, title: str, description: str, trigger_agent_id: str
    ) -> dict[str, Any]:
        """Bootstrap a mission by creating an issue and instantly triggering the orchestrating agent.

        Args:
            company_id: Company identifier.
            title: Title of the mission/epic issue.
            description: Detailed description of the mission.
            trigger_agent_id: ID of the agent (e.g. CEO) to immediately trigger for mission execution.
        """
        issue_result = self.create_issue(company_id, title, description)
        if not issue_result.get("success"):
            return {
                "success": False,
                "output": issue_result.get("output", ""),
                "error": issue_result.get("error", "Failed to create mission issue."),
                "exit_code": issue_result.get("exit_code", -1),
            }

        heartbeat_result = self.trigger_heartbeat(
            agent_id=trigger_agent_id, source="automation", trigger="system"
        )
        return {
            "success": heartbeat_result.get("success", False),
            "output": f"Issue Created: {issue_result.get('output', '')}\nHeartbeat Triggered: {heartbeat_result.get('output', '')}",
            "error": heartbeat_result.get("error")
            if not heartbeat_result.get("success")
            else None,
            "exit_code": heartbeat_result.get("exit_code", 0),
        }
