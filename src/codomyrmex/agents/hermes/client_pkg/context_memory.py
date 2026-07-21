"""Hermes client mixin: Context summarization and Obsidian export."""

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


class HermesContextMixin:
    def _summarize_context(self, session: Any) -> None:
        """Summarize and archive the oldest half of the session's messages."""
        messages = session.messages
        half = len(messages) // 2
        if half < 2:
            return

        oldest = messages[:half]
        latest = messages[half:]

        hist_text = ""
        for m in oldest:
            hist_text += f"[{m['role'].upper()}]\n{m['content']}\n\n"

        # 1. Pipeline Summary
        summary_prompt = (
            "Summarize the core facts, exact constraints, and key context from the following "
            "conversation excerpt securely. Format your output strictly as a dense timeline or list.\n\n"
            f"<EXCERPT>\n{hist_text}\n</EXCERPT>"
        )

        self.logger.info(
            "Triggering context summarization for session %s (compressing %d messages)",
            session.session_id,
            len(oldest),
        )
        summary_resp = self.execute(AgentRequest(prompt=summary_prompt))
        summary = (
            summary_resp.content
            if summary_resp.is_success()
            else "(Summarization failed)"
        )

        # 2. Fact Extraction
        fact_prompt = (
            "Extract any permanent user preferences, structural facts, or environmental constraints "
            "from this excerpt. Return ONLY a bulleted list of facts, nothing else. If none, return exactly 'NONE'.\n\n"
            f"<EXCERPT>\n{hist_text}\n</EXCERPT>"
        )
        fact_resp = self.execute(AgentRequest(prompt=fact_prompt))
        if fact_resp.is_success() and "NONE" not in fact_resp.content.strip().upper():
            existing_facts = session.metadata.get("extracted_facts", "")
            session.metadata["extracted_facts"] = (
                existing_facts + "\n" + fact_resp.content.strip()
            ).strip()

        # Fold existing summary if present into the new one (if the first message is already a summary)
        if (
            oldest
            and oldest[0].get("role") == "system"
            and "<SESSION_SUMMARY>" in oldest[0].get("content", "")
        ):
            prior_summary = (
                oldest[0]["content"]
                .replace("<SESSION_SUMMARY>", "")
                .replace("</SESSION_SUMMARY>", "")
                .strip()
            )
            summary = f"{prior_summary}\n\n[Continuance]:\n{summary}"

        # 3. Automated Graph Link Inference
        graph_prompt = (
            "You are an Obsidian notes semantic linker. Take the following summary text and strictly "
            "wrap any core architectural concepts, languages, frameworks, or significant domain entities "
            "with Obsidian-style double brackets (e.g., [[Concept]]). Do not change the text other than adding brackets. "
            f"Here is the text:\n\n{summary}"
        )
        graph_resp = self.execute(AgentRequest(prompt=graph_prompt))
        if graph_resp.is_success():
            summary = graph_resp.content.strip()

        summary_msg = {
            "role": "system",
            "content": f"<SESSION_SUMMARY>\n{summary}\n</SESSION_SUMMARY>",
        }
        session.messages = [summary_msg, *latest]

        # 4. Export to Obsidian natively
        self._export_to_obsidian(
            session_id=session.session_id, name=session.name, content=summary
        )
    def _export_to_obsidian(
        self, session_id: str, name: str | None, content: str
    ) -> None:
        """Export a semantic session summary to the Obsidian Vault if configured."""
        try:
            from codomyrmex.agentic_memory.obsidian.crud import create_note
            from codomyrmex.agentic_memory.obsidian.vault import ObsidianVault

            # Use configured vault path if set, otherwise discover in workspace
            if self._obsidian_vault:
                vault_path = Path(os.path.expanduser(self._obsidian_vault)).resolve()
            else:
                workspace_root = Path(os.path.abspath(".")).resolve()
                vault_path = workspace_root / "docs" / "brain"

            # If the vault exists, write natively
            if vault_path.exists() and vault_path.is_dir():
                vault = ObsidianVault(vault_path)
                safe_title = (
                    (name or f"session-{session_id}")[:50]
                    .replace("/", "-")
                    .replace("\\", "-")
                )
                note_path = f"Sessions/{safe_title}.md"
                fm = {
                    "agentic_id": session_id,
                    "importance": "high",
                    "memory_type": "semantic",
                    "source": "hermes_context_compression",
                }
                create_note(vault, note_path, content=content, frontmatter=fm)
                self.logger.info(
                    "Exported session %s context to Obsidian Vault: %s",
                    session_id,
                    note_path,
                )
        except Exception as e:
            self.logger.warning("Failed to export summary to Obsidian: %s", e)
