"""Hermes client mixin: Interactive chat sessions."""

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


class HermesChatMixin:
    def chat_session(
        self,
        prompt: str,
        session_id: str | None = None,
        session_name: str | None = None,
        max_tokens: int | None = None,
        hermes_skill: str | None = None,
        hermes_skills: list[str] | str | None = None,
    ) -> AgentResponse:
        """Execute a stateful multi-turn chat.

        Args:
            prompt: User prompt.
            session_id: Session ID (optional). If omitted, a new one is created.
            session_name: Human-friendly session name (v0.2.0). If provided and
                no session_id is given, attempts to resume by name.
            hermes_skill: Optional single Hermes CLI skill name to preload (``-s``).
            hermes_skills: Optional skill names (list or comma-separated string).
                Stored on the session and applied on each CLI turn (Ollama ignores).

        Returns:
            Response containing the assistant's reply and the session ID in metadata.

        """
        with SQLiteSessionStore(self._session_db_path) as store:
            # Try to resolve session by name first (v0.2.0 feature)
            if not session_id and session_name:
                existing = store.find_by_name(session_name)
                if existing:
                    session = existing
                    session_id = session.session_id
                else:
                    session = HermesSession(name=session_name)
                    session_id = session.session_id
            elif session_id:
                session = store.load(session_id)
                if not session:
                    session = HermesSession(session_id=session_id, name=session_name)
            else:
                session = HermesSession(name=session_name)
                session_id = session.session_id

            # Update name if provided on an existing session
            if session_name and session.name != session_name:
                session.name = session_name

            skill_fragment = agent_context_for_hermes_skills(
                hermes_skill, hermes_skills
            )
            if skill_fragment.get("hermes_skills"):
                session.metadata[SESSION_METADATA_HERMES_SKILLS_KEY] = skill_fragment[
                    "hermes_skills"
                ]

            store.save(session)

            current_prompt = prompt
            role = "user"
            autonomous_turns = 0
            max_turns = 10
            final_response = None

            while autonomous_turns < max_turns:
                session.add_message(role, current_prompt)

                max_session_msgs = self.config.get("max_session_messages", 20)
                if len(session.messages) > max_session_msgs:
                    self._summarize_context(session)
                    store.save(session)

                # Auto-compress history if it exceeds token limits
                history_messages = session.messages[:-1]  # exclude the current prompt
                if self._compressor.needs_compression(history_messages):
                    history_messages = self._compressor.compress(history_messages)
                    self.logger.info(
                        "Session %s: compressed %d → %d history messages",
                        session.session_id,
                        len(session.messages) - 1,
                        len(history_messages),
                    )

                # Build full prompt containing history
                history_text = ""
                for msg in history_messages:
                    history_text += f"[{msg['role'].upper()}]\n{msg['content']}\n\n"

                system_directives = (
                    f"You are the Hermes agent. Your current session ID is '{session.session_id}'.\n"
                    "For complex, multi-step requests, you MUST break them down into an internal checklist "
                    "using the `hermes_create_task` and `hermes_update_task_status` MCP tools. "
                    "Create tasks first, then execute them iteratively. Update their status to 'completed' or 'failed' as you go."
                )

                if history_text:
                    extra_facts = ""
                    extracted_facts = session.metadata.get("extracted_facts", "")
                    if extracted_facts:
                        extra_facts = f"\n\nRetained Long-Term Facts / Preferences:\n{extracted_facts}\n"

                    full_prompt = (
                        f"{system_directives}{extra_facts}\n\n"
                        f"Previous Conversation:\n{history_text}"
                        f"[{session.messages[-1]['role'].upper()}]\n{current_prompt}\n\n"
                        f"Please respond."
                    )
                else:
                    full_prompt = f"{system_directives}\n\nUser: {current_prompt}"

                raw_stored = session.metadata.get(SESSION_METADATA_HERMES_SKILLS_KEY)
                if isinstance(raw_stored, list):
                    sess_skills = [str(x) for x in raw_stored if str(x).strip()]
                else:
                    sess_skills = None
                self._session_skills_for_next_execute = sess_skills
                try:
                    request = AgentRequest(prompt=full_prompt, context={})
                    response = self.execute(request, max_tokens=max_tokens)
                finally:
                    self._session_skills_for_next_execute = None
                final_response = response

                if response.is_success():
                    # Reload session FIRST to get latest metadata changes from MCP tools
                    latest_session = store.load(session_id)
                    if latest_session:
                        session.metadata = latest_session.metadata

                    session.add_message("assistant", response.content)
                    store.save(session)

                    tasks: dict[str, Any] = session.metadata.get("workflow_tasks", {})

                    has_pending = any(
                        t.get("status") in ("pending", "running")
                        for t in tasks.values()
                    )
                    if has_pending:
                        autonomous_turns += 1
                        current_prompt = "System: You have pending tasks in your workflow checklist. Please execute the next logical task, use necessary tools, and update its status when done."
                        role = "user"
                    else:
                        break  # All tasks completed, or no tasks created
                else:
                    exit_code = response.metadata.get("exit_code", 0)
                    if exit_code != 0 and autonomous_turns < max_turns:
                        autonomous_turns += 1
                        error_trace = response.error or response.metadata.get(
                            "stderr", "Unknown error"
                        )

                        # 1.5.13 Dependency Healing Interception
                        import re

                        missing_pkg_match = re.search(
                            r"(?:ModuleNotFoundError|ImportError): No module named '([^']+)'",
                            error_trace,
                        )
                        if missing_pkg_match:
                            missing_pkg = missing_pkg_match.group(1)
                            self.logger.warning(
                                f"Detected missing dependency '{missing_pkg}'. Initiating autonomous healing."
                            )
                            heal_result = self._heal_environment(missing_pkg)

                            attempts = session.metadata.get("heal_attempts", 0) + 1
                            session.metadata["heal_attempts"] = attempts
                            successes = session.metadata.get("heal_success_rate", 0)
                            if heal_result["success"]:
                                session.metadata["heal_success_rate"] = successes + 1

                            error_trace += f"\n\n[SYSTEM AUTO-HEAL]: Attempted to install missing package '{missing_pkg}'. Result: {heal_result['output']}"

                        self.logger.warning(
                            "Subprocess execution failed (exit_code=%s). Initiating recovery loop via AutoRetryException logic.",
                            exit_code,
                        )

                        template_path = (
                            Path(__file__).parent / "templates" / "recovery_prompt.txt"
                        )
                        if template_path.exists():
                            recovery_text = template_path.read_text(
                                encoding="utf-8"
                            ).format(failed_trace=error_trace)
                        else:
                            recovery_text = f"System: Tool failed with trace:\n<FAILED_TRACE>\n{error_trace}\n</FAILED_TRACE>\nFix the error and proceed."

                        if response.content:
                            session.add_message(
                                "assistant",
                                f"{response.content}\n[Execution Interrupted]",
                            )

                        current_prompt = recovery_text
                        role = "system"
                        # Reload session to ensure we don't drop state
                        store.save(session)
                        continue
                    break  # Error executing, and we are out of retry turns

            # Sync securely to Obsidian Vault if configured (D1 implementation)
            if self._obsidian_vault and final_response and final_response.is_success():
                try:
                    from codomyrmex.agents.hermes.gateway.memory import (
                        sync_session_to_vault,
                    )

                    sync_session_to_vault(session, self._obsidian_vault)
                except Exception as e:
                    self.logger.error("Error executing vault sync hook: %s", e)

            if final_response:
                if final_response.metadata is None:
                    final_response.metadata = {}
                final_response.metadata["session_id"] = session.session_id
                if session.name:
                    final_response.metadata["session_name"] = session.name
                final_response.metadata["workflow_tasks"] = session.metadata.get(
                    "workflow_tasks", {}
                )
                final_response.metadata["autonomous_turns"] = autonomous_turns
                return final_response

            from codomyrmex.agents.core import AgentResponse

            return AgentResponse(content="", error="Execution loop failed", metadata={})
