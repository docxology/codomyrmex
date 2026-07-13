"""Hermes client mixin: Worktrees, fork, merge, batch."""

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


class HermesSessionOpsMixin:
    def create_worktree(self, session_id: str) -> Path | None:
        """Create an isolated git worktree for a session.

        Args:
            session_id: Session identifier used to name the worktree branch.

        Returns:
            Path to the worktree directory, or None if creation fails.

        """
        worktree_path = self._worktree_base / f"hermes-{session_id}"
        branch_name = f"hermes/{session_id}"

        try:
            self._worktree_base.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["git", "worktree", "add", "-b", branch_name, str(worktree_path)],
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
            )
            self.logger.info(
                "Created worktree at %s (branch: %s)", worktree_path, branch_name
            )
            return worktree_path
        except subprocess.CalledProcessError as e:
            self.logger.warning("Failed to create worktree: %s", e.stderr)
            return None
        except Exception as e:
            self.logger.warning("Worktree creation error: %s", e)
            return None

    def cleanup_worktree(self, session_id: str) -> bool:
        """Remove an isolated git worktree after session completes.

        Args:
            session_id: Session identifier matching the worktree to clean up.

        Returns:
            True if cleanup succeeded.

        """
        worktree_path = self._worktree_base / f"hermes-{session_id}"
        branch_name = f"hermes/{session_id}"

        try:
            subprocess.run(
                ["git", "worktree", "remove", str(worktree_path), "--force"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            subprocess.run(
                ["git", "branch", "-D", branch_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.logger.info("Cleaned up worktree: %s", worktree_path)
            return True
        except Exception as e:
            self.logger.warning("Worktree cleanup failed: %s", e)
            return False

    def get_session_stats(self) -> dict[str, Any]:
        """Return summary statistics for the session database.

        Returns:
            dict with keys: ``session_count``, ``db_size_bytes``,
            ``oldest_session_at``, ``newest_session_at``.

        """
        with SQLiteSessionStore(self._session_db_path) as store:
            return store.get_stats()

    def fork_session(
        self, session_id: str, new_name: str | None = None
    ) -> HermesSession | None:
        """Fork an existing session into an independent child session.

        Args:
            session_id: Source session to fork from.
            new_name: Human-friendly name for the child session.

        Returns:
            The new :class:`~codomyrmex.agents.hermes.session.HermesSession`
            with all parent messages copied, or ``None`` if the source is missing.

        """
        with SQLiteSessionStore(self._session_db_path) as store:
            parent = store.load(session_id)
            if parent is None:
                self.logger.warning("Cannot fork unknown session: %s", session_id)
                return None
            child = parent.fork(new_name=new_name)
            store.save(child)
            self.logger.info(
                "Forked session %s → %s (name=%s)",
                session_id,
                child.session_id,
                child.name,
            )
            return child

    def export_session_markdown(self, session_id: str) -> str | None:
        """Export a session as formatted Markdown.

        Args:
            session_id: Session identifier.

        Returns:
            Markdown string, or ``None`` if session not found.

        """
        with SQLiteSessionStore(self._session_db_path) as store:
            return store.export_markdown(session_id)

    def batch_execute(
        self,
        prompts: list[str],
        parallel: bool = False,
        backend: str | None = None,
        timeout: int | None = None,
        hermes_skill: str | None = None,
        hermes_skills: list[str] | str | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a list of prompts, returning a list of result dicts.

        Args:
            prompts: list of prompt strings.
            parallel: If ``True``, use a :class:`~concurrent.futures.ThreadPoolExecutor`
                to submit all prompts concurrently.  Defaults to ``False`` (sequential).
            backend: Override the active backend (``\"cli\"`` | ``\"ollama\"``).
                If ``None``, uses the currently configured backend.
            timeout: Per-request timeout in seconds.  If ``None``, uses the client default.
            hermes_skill: Optional Hermes CLI skill for every prompt (see :meth:`chat_session`).
            hermes_skills: Optional skill list or comma-separated string for every prompt.

        Returns:
            list of dicts with keys ``prompt``, ``status``, ``content``, ``error``.

        """
        from codomyrmex.agents.core import AgentRequest

        if backend:
            orig_backend = self._active_backend
            self._active_backend = backend
        if timeout:
            orig_timeout = self.timeout
            self.timeout = timeout

        req_ctx = agent_context_for_hermes_skills(hermes_skill, hermes_skills)

        def _execute_one(prompt: str) -> dict[str, Any]:
            """Execute a single prompt and return a normalized result dict."""
            try:
                resp = self.execute(AgentRequest(prompt=prompt, context=dict(req_ctx)))
                return {
                    "prompt": prompt,
                    "status": "success" if resp.is_success() else "error",
                    "content": resp.content,
                    "error": resp.error,
                }
            except Exception as exc:
                return {
                    "prompt": prompt,
                    "status": "error",
                    "content": "",
                    "error": str(exc),
                }

        orig_backend: str | None = None
        orig_timeout: int | None = None
        try:
            if parallel:
                from concurrent.futures import ThreadPoolExecutor

                with ThreadPoolExecutor(max_workers=min(len(prompts), 8)) as ex:
                    results = list(ex.map(_execute_one, prompts))
            else:
                results = [_execute_one(p) for p in prompts]
        finally:
            if backend and orig_backend is not None:
                self._active_backend = orig_backend
            if timeout and orig_timeout is not None:
                self.timeout = orig_timeout

        return results

    def set_system_prompt(self, session_id: str, prompt: str) -> bool:
        """Prepend (or replace) a persistent system message in a session.

        Args:
            session_id: Session identifier.  If the session does not exist it
                will be created.
            prompt: System instruction text.

        Returns:
            ``True`` on success.

        """
        with SQLiteSessionStore(self._session_db_path) as store:
            # Create session if it doesn't exist
            if not store.load(session_id):
                store.save(HermesSession(session_id=session_id))
            return store.update_system_prompt(session_id, prompt)

    def get_session_detail(self, session_id: str) -> dict[str, Any] | None:
        """Return a rich detail dictionary for a session.

        Args:
            session_id: Session identifier.

        Returns:
            dict with all session fields plus ``message_count``, ``last_message``,
            ``has_system_prompt``, or ``None`` if not found.

        """
        with SQLiteSessionStore(self._session_db_path) as store:
            return store.get_detail(session_id)

    def session_merge(
        self, target_id: str, source_ids: list[str], deduplicate: bool = True
    ) -> bool:
        """Merge multiple source sessions into a target session.

        Args:
            target_id: Destination session identifier. Created if missing.
            source_ids: list of session identifiers to pull messages from.
            deduplicate: If True, exact duplicate consecutive messages are skipped.

        Returns:
            ``True`` if at least one session was merged successfully.

        """
        with SQLiteSessionStore(self._session_db_path) as store:
            target = store.load(target_id)
            if not target:
                target = HermesSession(session_id=target_id)
                store.save(target)

            merged_any = False
            for src_id in source_ids:
                src = store.load(src_id)
                if not src:
                    self.logger.warning("Merge source session '%s' not found.", src_id)
                    continue

                for msg in src.messages:
                    # Skip system prompts from sources if target already has messages
                    if msg.get("role") == "system" and target.messages:
                        continue

                    if deduplicate and target.messages:
                        last = target.messages[-1]
                        if msg.get("role") == last.get("role") and msg.get(
                            "content"
                        ) == last.get("content"):
                            continue

                    target.add_message(msg["role"], msg["content"])
                    merged_any = True

            if merged_any:
                store.save(target)
            return merged_any
