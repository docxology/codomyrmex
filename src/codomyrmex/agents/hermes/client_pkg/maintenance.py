"""Hermes client mixin: Doctor, skills, coverage loop."""

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
from codomyrmex.agents.hermes.client_pkg.errors import (
    AUTO_HEAL_ALLOWLIST,
    AutoRetryException,
    HermesError,
)
from codomyrmex.agents.hermes.session import HermesSession, SQLiteSessionStore
from codomyrmex.agents.hermes.skill_names import (
    SESSION_METADATA_HERMES_SKILLS_KEY,
    agent_context_for_hermes_skills,
    normalize_hermes_skill_names,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


class HermesMaintenanceMixin:
    def _build_hermes_args(self, prompt: str, context: dict[str, Any]) -> list[str]:
        """Build hermes CLI arguments from prompt and context.

        Args:
            prompt: Text prompt or task description.
            context: Context dictionary which may include keys:
                - ``command``: Subcommand (e.g. ``"skills"``, ``"setup"``)
                - ``args``: Additional arguments for the subcommand

        Returns:
            Argument list suitable for subprocess call.

        """
        if context.get("command"):
            cmd = context["command"]
            args = [cmd]
            if context.get("args"):
                args.extend(context["args"])
            return args
        # Non-interactive mode: -Q suppresses spinner/banner, --provider forces the
        # configured inference provider so hermes never enters the setup wizard.
        skill_names = normalize_hermes_skill_names(context=context)
        args: list[str] = ["chat"]
        if skill_names:
            args.extend(["-s", ",".join(skill_names)])
        args.extend(["-q", prompt, "-Q", "--provider", self._hermes_provider])
        if self._yolo:
            args.append("--yolo")
        if self._continue_session:
            args.extend(["--continue", self._continue_session])
        if self._pass_session_id:
            args.append("--pass-session-id")
        return args
    def _heal_environment(self, package_name: str) -> dict[str, Any]:
        """Attempt to automatically install a missing package using uv.

        Only packages in the ``AUTO_HEAL_ALLOWLIST`` set are eligible for
        automatic installation.  All other packages must be installed
        manually by the user.

        Args:
            package_name: The name of the package that triggered the ImportError.

        Returns:
            dict containing success boolean and the subprocess output.

        """
        try:
            # We enforce a strict mapping to hyphenated strings just in case
            safe_pkg = package_name.replace("_", "-").split(".")[0]

            # Check allowlist before attempting installation
            if safe_pkg not in AUTO_HEAL_ALLOWLIST:
                self.logger.warning(
                    f"Package '{safe_pkg}' not in auto-heal allowlist. "
                    f"Install manually with: uv add {safe_pkg}"
                )
                return {
                    "success": False,
                    "output": f"Package {safe_pkg} not in auto-heal allowlist. Install manually with: uv add {safe_pkg}",
                }

            # Subprocess to uv add the package into the current active environment/workspace
            result = subprocess.run(
                ["uv", "add", safe_pkg],
                capture_output=True,
                text=True,
                timeout=30,
                # cwd self.working_dir or root
            )

            if result.returncode == 0:
                self.logger.info(f"Successfully auto-healed dependency: {safe_pkg}")
                return {
                    "success": True,
                    "output": f"Successfully installed {safe_pkg} via uv add.",
                }
            self.logger.error(f"Auto-heal failed for {safe_pkg}: {result.stderr}")
            return {
                "success": False,
                "output": f"Failed to install {safe_pkg}. Stderr: {result.stderr}",
            }

        except Exception as e:
            self.logger.error(f"Auto-heal exception for {package_name}: {e}")
            return {"success": False, "output": f"Exception during uv add: {e!s}"}
    def _run_coverage_loop(
        self, target_path: str, max_turns: int = 5
    ) -> dict[str, Any]:
        """Autonomous testing loop (Red/Green/Refactor).

        Repeatedly executes pytest against the target_path. If failures occur,
        forwards the stack traces to a nested Hermes session for automated repair
        until the tests pass or max_turns is exhausted.
        """
        import os
        import subprocess

        # Check if target_path exists
        if not os.path.exists(target_path):
            return {
                "status": "error",
                "message": f"Target path does not exist: {target_path}",
                "trace": "",
            }

        turn = 0
        trace = ""
        while turn < max_turns:
            try:
                run = subprocess.run(
                    ["uv", "run", "pytest", target_path, "-v", "--tb=short"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
            except subprocess.TimeoutExpired as exc:
                self.logger.error("pytest timed out after %s seconds", 120)
                return {
                    "status": "error",
                    "message": f"pytest execution timed out: {exc}",
                    "trace": "",
                }

            if run.returncode == 0:
                self.logger.info(
                    f"Coverage loop complete: {target_path} is fully green."
                )
                return {"status": "success", "turns": turn, "output": run.stdout}

            turn += 1
            self.logger.warning(
                f"Coverage loop test failure ({turn}/{max_turns}). Initiating heal."
            )

            # Extract relevant traceback lines to fit within reasonable context lengths
            trace = (run.stdout + "\n" + run.stderr).strip()
            # Feed it right back into a nested chat_session to fix the code
            repair_prompt = (
                f"You are the autonomous Coverage Loop agent.\n"
                f"I just ran pytest on {target_path} and it failed with the following traceback:\n\n"
                f"```text\n{trace}\n```\n\n"
                f"Please analyze the failure, utilize any file-editing MCP tools you have to fix "
                f"EITHER the test file OR the source file to resolve this failure correctly. "
                f"Do not use mock objects; ensure the code functionally passes."
            )

            # Spawn a distinct auto-session to resolve it
            session_id = f"coverage_loop_{Path(target_path).stem}_{turn}"
            response = self.chat_session(prompt=repair_prompt, session_name=session_id)

            if not response.is_success():
                self.logger.error(
                    "Coverage loop repair agent failed to respond cleanly."
                )
                return {
                    "status": "error",
                    "message": "Repair agent failed.",
                    "trace": trace,
                }

        return {
            "status": "failed",
            "message": f"Did not achieve green tests after {max_turns} turns.",
            "trace": trace,
        }
    def get_version(self) -> str | None:
        """Get the installed Hermes CLI version string.

        Runs ``hermes version`` and parses the output.

        Returns:
            Version string (e.g. ``"0.2.0"``) or ``None`` if unavailable.

        """
        if not self._cli_available:
            return None
        try:
            import re as _re

            result = subprocess.run(
                [self.command, "version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Parse version from output like "Hermes Agent v0.2.0" or "0.2.0"
            output = (result.stdout + result.stderr).strip()
            match = _re.search(r"(\d+\.\d+\.\d+)", output)
            return match.group(1) if match else output or None
        except Exception as e:
            self.logger.debug("Could not get Hermes version: %s", e)
            return None
    def run_doctor(self) -> dict[str, Any]:
        """Run ``hermes doctor`` for comprehensive health diagnostics.

        Available in Hermes CLI v0.2.0+.  Returns structured results.

        Returns:
            dict with ``success`` boolean and ``output`` or ``error``.

        """
        if not self._cli_available:
            return {"success": False, "error": "Hermes CLI not available"}
        try:
            result = subprocess.run(
                [self.command, "doctor"],
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "NO_COLOR": "1"},
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "hermes doctor timed out after 30s"}
        except Exception as e:
            self.logger.warning("hermes doctor failed: %s", e)
            return {"success": False, "error": str(e)}
    def list_skills(self) -> dict[str, Any]:
        """list active skills available to Hermes.

        Returns:
            dict with ``success`` boolean and ``output`` or ``error``.

        """
        if self._active_backend != "cli":
            return {"success": False, "error": "Skills listing requires the Hermes CLI"}
        try:
            result = self._execute_command(args=["skills", "list"])
            return {
                "success": result.get("success", False),
                "output": result.get("stdout", ""),
            }
        except Exception as e:
            self.logger.warning("Failed to list Hermes skills: %s", e)
            return {"success": False, "error": str(e)}
    def get_hermes_status(self) -> dict[str, Any]:
        """Get the current Hermes configuration status.

        Returns:
            dict with diagnostic information including the active backend.

        """
        status: dict[str, Any] = {
            "active_backend": self._active_backend,
            "cli_available": self._cli_available,
            "ollama_available": self._ollama_available,
            "ollama_model": self._ollama_model,
            "fallback_model": self._fallback_model,
            "fallback_provider": self._fallback_provider,
        }
        if self._active_backend == "cli":
            try:
                result = self._execute_command(args=["status"], timeout=10)
                status.update(
                    {
                        "success": result.get("success", False),
                        "output": result.get("stdout", ""),
                        "exit_code": result.get("exit_code", 0),
                    }
                )
            except Exception as e:
                status.update({"success": False, "error": str(e), "exit_code": -1})
        else:
            status["success"] = self._ollama_available
        return status
