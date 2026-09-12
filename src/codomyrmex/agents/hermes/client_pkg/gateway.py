"""Hermes client mixin: Gateway status and FastMCP scaffold."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from codomyrmex.agents.core import AgentRequest, AgentResponse
from codomyrmex.agents.core.exceptions import AgentError, AgentTimeoutError
from codomyrmex.agents.hermes.client_pkg.errors import AutoRetryException, HermesError
from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore
from codomyrmex.agents.hermes.skill_names import (
    SESSION_METADATA_HERMES_SKILLS_KEY,
    agent_context_for_hermes_skills,
    normalize_hermes_skill_names,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


class HermesGatewayMixin:
    def get_gateway_status(self) -> dict:
        """Return status information for all running Hermes gateway instances.

        Runs ``hermes gateway status`` and parses the output into a dict.

        Returns:
            dict with keys: ``success``, ``instances`` (list), ``output``, ``error``.

        """
        if not self._cli_available:
            return {
                "success": False,
                "instances": [],
                "error": "Hermes CLI not available",
            }
        try:
            subprocess_env = dict(os.environ)
            subprocess_env["NO_COLOR"] = "1"
            result = subprocess.run(
                [self.command, "gateway", "status"],
                capture_output=True,
                text=True,
                timeout=10,
                env=subprocess_env,
            )
            output = result.stdout.strip()
            instances: list[dict] = []
            for line in output.splitlines():
                # Parse table rows: instance name, PID, model shown per line
                if "│" in line:
                    parts = [p.strip() for p in line.split("│") if p.strip()]
                    if len(parts) >= 2 and parts[0] not in ("Instance", "Name", ""):
                        instances.append(
                            {
                                "name": parts[0],
                                "status": parts[1] if len(parts) > 1 else "",
                                "model": parts[2] if len(parts) > 2 else "",
                            }
                        )
            return {
                "success": result.returncode == 0,
                "instances": instances,
                "output": output,
                "error": result.stderr.strip() if result.returncode != 0 else "",
            }
        except Exception as exc:
            self.logger.error("get_gateway_status failed: %s", exc)
            return {"success": False, "instances": [], "error": str(exc)}
    def get_model_info(self, model_id: str) -> dict:
        """Look up model context length and tool-use support.

        Queries the Hermes model catalog (``hermes_cli/models.py``) for
        metadata about *model_id*.  Falls back to the ``/model`` CLI command
        when the Python catalog doesn't have an entry.

        Args:
            model_id: OpenRouter model identifier, e.g.
                ``"nvidia/nemotron-3-super-120b-a12b:free"``.

        Returns:
            dict with keys: ``model_id``, ``context_length``, ``supports_tools``,
            ``provider``, ``source``.

        """
        try:
            # Try importing the upstream model catalog directly
            hermes_agent_path = Path(self.command).resolve().parent.parent
            models_path = hermes_agent_path / "hermes_cli" / "models.py"
            result: dict = {
                "model_id": model_id,
                "context_length": 0,
                "supports_tools": None,
                "provider": model_id.split("/", maxsplit=1)[0]
                if "/" in model_id
                else "unknown",
                "source": "unknown",
            }

            if models_path.exists():
                import importlib.util

                spec = importlib.util.spec_from_file_location(
                    "hermes_models", models_path
                )
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    # Look for model in catalog dictionaries
                    for attr_name in dir(mod):
                        attr = getattr(mod, attr_name)
                        if isinstance(attr, dict) and model_id in attr:
                            entry = attr[model_id]
                            if isinstance(entry, dict):
                                result["context_length"] = entry.get(
                                    "context_length", 0
                                )
                                result["supports_tools"] = entry.get("supports_tools")
                                result["source"] = "hermes_cli/models.py"
                                break
                            if isinstance(entry, int):
                                result["context_length"] = entry
                                result["source"] = "hermes_cli/models.py"
                                break

            # Fallback: run `hermes model --info <id>` if CLI available
            if result["context_length"] == 0 and self._cli_available:
                subprocess_env = dict(os.environ)
                subprocess_env["NO_COLOR"] = "1"
                cli_result = subprocess.run(
                    [self.command, "model", "--info", model_id],
                    capture_output=True,
                    text=True,
                    timeout=15,
                    env=subprocess_env,
                )
                if cli_result.returncode == 0:
                    result["output"] = cli_result.stdout.strip()
                    result["source"] = "hermes model --info"

            return result
        except Exception as exc:
            self.logger.error("get_model_info(%s) failed: %s", model_id, exc)
            return {"model_id": model_id, "context_length": 0, "error": str(exc)}
    def send_gateway_command(
        self,
        command: str,
        session_id: str | None = None,
    ) -> dict:
        """Dispatch a slash command to the running gateway.

        Primarily used for ``/approve`` and ``/deny`` to confirm or cancel
        dangerous command approvals (v0.4.0 gateway feature).

        Args:
            command: Slash command to send, e.g. ``"/approve"``,
                ``"/approve session"``, ``"/deny"``.
            session_id: Target session ID if the gateway maintains multiple.

        Returns:
            dict with keys: ``success``, ``output``, ``error``.

        """
        if not self._cli_available:
            return {"success": False, "output": "", "error": "Hermes CLI not available"}
        try:
            args = [self.command, "gateway", "cmd", command]
            if session_id:
                args += ["--session", session_id]
            subprocess_env = dict(os.environ)
            subprocess_env["NO_COLOR"] = "1"
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=15,
                env=subprocess_env,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.returncode != 0 else "",
            }
        except Exception as exc:
            self.logger.error("send_gateway_command(%s) failed: %s", command, exc)
            return {"success": False, "output": "", "error": str(exc)}
    def install_skill(self, repo_url: str) -> dict:
        """Install a Hermes skill from a git repository URL.

        Runs ``hermes skills install <repo_url>``.

        Args:
            repo_url: HTTPS or SSH URL of the skill repository.

        Returns:
            dict with keys: ``success``, ``output``, ``error``.

        """
        if not self._cli_available:
            return {"success": False, "output": "", "error": "Hermes CLI not available"}
        try:
            subprocess_env = dict(os.environ)
            subprocess_env["NO_COLOR"] = "1"
            result = subprocess.run(
                [self.command, "skills", "install", repo_url],
                capture_output=True,
                text=True,
                timeout=120,
                env=subprocess_env,
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.returncode != 0 else "",
            }
        except Exception as exc:
            self.logger.error("install_skill(%s) failed: %s", repo_url, exc)
            return {"success": False, "output": "", "error": str(exc)}
    def scaffold_fastmcp(
        self,
        output_dir: str,
        server_name: str,
        force: bool = False,
    ) -> dict[str, Any]:
        """Run the FastMCP scaffold script for Hermes-compatible MCP servers.

        Args:
            output_dir: Destination directory for generated package scaffold.
            server_name: Human-friendly FastMCP server name.
            force: Overwrite generated files when they already exist.

        Returns:
            dict with keys: ``success``, ``output``, ``error``, ``script_path``.
        """
        bundled = (
            Path(__file__).resolve().parent.parent
            / "optional-skills"
            / "mcp"
            / "fastmcp"
            / "scaffold_fastmcp.py"
        )
        cli_relative = (
            Path(self.command).resolve().parent.parent
            / "optional-skills"
            / "mcp"
            / "fastmcp"
            / "scaffold_fastmcp.py"
        )
        script_candidates = [bundled, cli_relative]
        script_path = next((path for path in script_candidates if path.exists()), None)
        if script_path is None:
            return {
                "success": False,
                "output": "",
                "error": (
                    "FastMCP scaffold script not found. Checked: "
                    + ", ".join(str(path) for path in script_candidates)
                ),
                "script_path": "",
            }
        try:
            args = [
                sys.executable,
                str(script_path),
                "--output-dir",
                output_dir,
                "--name",
                server_name,
            ]
            if force:
                args.append("--force")
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=60,
                env=dict(os.environ),
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip() if result.returncode != 0 else "",
                "script_path": str(script_path),
            }
        except Exception as exc:
            self.logger.error("scaffold_fastmcp(%s) failed: %s", output_dir, exc)
            return {
                "success": False,
                "output": "",
                "error": str(exc),
                "script_path": str(script_path),
            }
