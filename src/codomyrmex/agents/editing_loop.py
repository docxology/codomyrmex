"""Autonomous Code Editing Loop — Ollama → Antigravity → Claude review.

Orchestrates a plan→edit→review cycle across three LLM providers:

1. **Ollama** (local) generates an editing plan from the task description.
2. **Antigravity** (IDE agent) executes the file edits via its native tools.
3. **Claude Code** (or Ollama fallback) reviews the result and approves or
   requests another iteration.

Example::

    >>> from codomyrmex.agents.editing_loop import EditingOrchestrator, EditTask
    >>> task = EditTask(description="Add docstrings to helpers.py",
    ...                 file_path="src/helpers.py")
    >>> orch = EditingOrchestrator()
    >>> result = orch.run_task(task)
    >>> result.approved
    True
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from codomyrmex.agents.llm_client import OllamaClient, AgentRequest, get_llm_client
from codomyrmex.ide.antigravity.agent_relay import AgentRelay
from codomyrmex.ide.antigravity.message_scheduler import (
    MessageScheduler,
    SchedulerConfig,
)


# =====================================================================
# Data Structures
# =====================================================================

@dataclass
class EditTask:
    """A single code-editing task to be processed by the loop.

    Attributes:
        description: Human-readable description of the edit.
        file_path: Primary file to edit.
        edit_type: Hint for the planner (e.g. ``"refactor"``, ``"add"``, ``"fix"``).
        context_files: Additional files the planner should read.
        approved: Set to ``True`` when the reviewer accepts the edit.
        result: Final edit summary after approval.
        review_notes: Accumulated reviewer feedback across iterations.
        iterations_used: How many plan→edit→review cycles were executed.
    """

    description: str
    file_path: str = ""
    edit_type: str = "edit"
    context_files: list[str] = field(default_factory=list)
    approved: bool = False
    result: str = ""
    review_notes: list[str] = field(default_factory=list)
    iterations_used: int = 0


@dataclass
class EditingConfig:
    """Configuration for the editing orchestrator.

    Attributes:
        ollama_model: Model name for the Ollama planner.
        review_provider: Provider for the review step (``"claude"`` or ``"ollama"``).
        review_model: Model for the review step (if Ollama).
        max_iterations: Maximum plan→edit→review cycles per task.
        approval_threshold: Minimum review score (0-10) to auto-approve.
        auto_apply_edits: Whether to apply edits without confirmation.
        context_files: Global context files injected into every task.
        scheduler_config: Rate-limiting config for relay messages.
        channel: Relay channel ID (auto-generated if empty).
    """

    ollama_model: str = ""
    review_provider: str = "ollama"
    review_model: str = ""
    max_iterations: int = 5
    approval_threshold: float = 7.0
    auto_apply_edits: bool = True
    context_files: list[str] = field(default_factory=list)
    scheduler_config: SchedulerConfig | None = None
    channel: str = ""

    def __post_init__(self) -> None:
        """Execute   Post Init   operations natively."""
        import os
        if not self.ollama_model:
            self.ollama_model = os.environ.get("OLLAMA_MODEL", "codellama:latest")
        if not self.review_model:
            self.review_model = os.environ.get(
                "OLLAMA_REVIEW_MODEL", self.ollama_model
            )


# =====================================================================
# Editing Orchestrator
# =====================================================================

class EditingOrchestrator:
    """Autonomous plan→edit→review loop across Ollama, Antigravity, and Claude.

    For each :class:`EditTask`:

    1. **Plan** — Ollama generates a concrete editing plan.
    2. **Edit** — Antigravity executes file edits via ``replace_file_content``.
    3. **Review** — Claude Code (or Ollama fallback) reviews the diff.
    4. Repeat until approved or ``max_iterations`` reached.

    Args:
        config: Orchestrator configuration.
    """

    def __init__(self, config: EditingConfig | None = None) -> None:
        """Execute   Init   operations natively."""
        self.config = config or EditingConfig()

        # Planner: always Ollama (fast, local).
        import os
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self._planner = OllamaClient(
            model=self.config.ollama_model, base_url=base_url,
        )

        # Reviewer: Claude if available, else Ollama.
        if self.config.review_provider == "claude":
            try:
                self._reviewer = get_llm_client(identity="reviewer")
            except RuntimeError:
                logger.warning(
                    "Claude unavailable for review — falling back to Ollama"
                )
                self._reviewer = OllamaClient(
                    model=self.config.review_model, base_url=base_url,
                )
        else:
            self._reviewer = OllamaClient(
                model=self.config.review_model, base_url=base_url,
            )

        # Antigravity client (lazy — only needed during _edit).
        self._ag_client: Any = None

        # Relay + scheduler for inter-agent messages.
        channel = self.config.channel or f"editing-{int(time.time())}"
        self._relay = AgentRelay(channel)
        self._scheduler: MessageScheduler | None = None
        if self.config.scheduler_config:
            self._scheduler = MessageScheduler(
                self._relay, self.config.scheduler_config, identity="editor",
            )

        logger.info(
            f"EditingOrchestrator initialized: planner={self.config.ollama_model}, "
            f"reviewer={self.config.review_provider}/{self.config.review_model}, "
            f"channel={channel}"
        )

    # ── Public API ───────────────────────────────────────────────────

    def run_task(self, task: EditTask) -> EditTask:
        """Run a single task through the full plan→edit→review cycle.

        Args:
            task: The editing task.

        Returns:
            The same ``EditTask`` with ``approved``, ``result``, and
            ``review_notes`` populated.
        """
        feedback = ""
        iteration = 0

        while iteration < self.config.max_iterations and not task.approved:
            iteration += 1
            task.iterations_used = iteration
            logger.info(
                f"[EditLoop] Task '{task.description[:50]}' — "
                f"iteration {iteration}/{self.config.max_iterations}"
            )

            # 1. Plan
            plan = self._plan(task, feedback)
            logger.info(f"[EditLoop] Plan generated ({len(plan)} chars)")

            # 2. Edit
            edit_summary = self._edit(task, plan)
            logger.info(f"[EditLoop] Edit applied: {edit_summary[:80]}")

            # 3. Review
            approved, notes, score = self._review(task, plan, edit_summary)
            task.review_notes.append(
                f"[iter {iteration}] score={score:.1f} — {notes}"
            )

            if approved:
                task.approved = True
                task.result = edit_summary
                logger.info(
                    f"[EditLoop] APPROVED at iteration {iteration} "
                    f"(score={score:.1f})"
                )
            else:
                feedback = notes
                logger.info(
                    f"[EditLoop] Revision requested (score={score:.1f}): "
                    f"{notes[:80]}"
                )

        if not task.approved:
            task.result = f"Not approved after {iteration} iterations"
            logger.warning(f"[EditLoop] Task exhausted {iteration} iterations")

        return task

    def run_tasks(self, tasks: list[EditTask]) -> list[EditTask]:
        """Run multiple tasks sequentially.

        Args:
            tasks: List of editing tasks.

        Returns:
            The same list with results populated.
        """
        for task in tasks:
            self.run_task(task)
        return tasks

    @classmethod
    def from_todo(
        cls,
        todo_path: str | Path,
        *,
        config: EditingConfig | None = None,
    ) -> tuple[EditingOrchestrator, list[EditTask]]:
        """Create an orchestrator and task list from a TO-DO markdown file.

        Parses unchecked items (``- [ ]``) as editing tasks.

        Args:
            todo_path: Path to the TO-DO file.
            config: Optional configuration override.

        Returns:
            Tuple of (orchestrator, tasks).
        """
        from codomyrmex.agents.orchestrator import extract_todo_items

        path = Path(todo_path)
        if not path.is_file():
            raise FileNotFoundError(f"TO-DO file not found: {path}")

        text = path.read_text(errors="replace")
        items = extract_todo_items(text)

        tasks = [
            EditTask(description=item, edit_type="todo")
            for item in items
        ]

        orch = cls(config=config)
        logger.info(
            f"[EditLoop] from_todo: {len(tasks)} tasks from {path.name}"
        )
        return orch, tasks

    # ── Private: Plan ────────────────────────────────────────────────

    def _plan(self, task: EditTask, feedback: str = "") -> str:
        """Generate an editing plan using Ollama.

        Args:
            task: The current task.
            feedback: Reviewer feedback from the previous iteration.

        Returns:
            A text plan describing what edits to make.
        """
        # Read file content for context.
        file_content = ""
        if task.file_path:
            try:
                file_content = Path(task.file_path).read_text(errors="replace")
                if len(file_content) > 8000:
                    file_content = file_content[:8000] + "\n... (truncated)"
            except (FileNotFoundError, OSError):
                file_content = "(file not found)"

        # Read additional context files.
        context_parts: list[str] = []
        all_context = list(task.context_files) + list(self.config.context_files)
        for cf in all_context:
            try:
                content = Path(cf).read_text(errors="replace")
                if len(content) > 4000:
                    content = content[:4000] + "\n... (truncated)"
                context_parts.append(f"=== {Path(cf).name} ===\n{content}")
            except (FileNotFoundError, OSError):
                pass

        context_section = ""
        if context_parts:
            context_section = (
                "\n\nAdditional context files:\n" + "\n\n".join(context_parts)
            )

        feedback_section = ""
        if feedback:
            feedback_section = (
                f"\n\nPrevious reviewer feedback (address these issues):\n"
                f"{feedback}"
            )

        prompt = (
            f"System: You are a code editing planner. Generate a precise, "
            f"actionable plan for the following edit.\n\n"
            f"Task: {task.description}\n"
            f"Edit type: {task.edit_type}\n"
            f"Target file: {task.file_path or '(not specified)'}\n"
            f"\nCurrent file content:\n{file_content}"
            f"{context_section}"
            f"{feedback_section}"
            f"\n\nGenerate a step-by-step plan. For each step, specify the "
            f"exact content to find and replace. Use this format:\n"
            f"STEP N: [description]\n"
            f"FIND: [exact text to find]\n"
            f"REPLACE: [replacement text]\n"
        )

        req = AgentRequest(prompt=prompt)
        resp = self._planner.execute_with_session(req)
        return resp.content.strip() if hasattr(resp, "content") else str(resp)

    # ── Private: Edit ────────────────────────────────────────────────

    def _edit(self, task: EditTask, plan: str) -> str:
        """Execute file edits via Antigravity's replace_file_content tool.

        Args:
            task: The current task.
            plan: The editing plan from :meth:`_plan`.

        Returns:
            A summary of what was changed.
        """
        if not task.file_path:
            return "No file_path specified — plan generated but not applied"

        client = self._get_ag_client()
        if client is None:
            return f"Antigravity unavailable — plan:\n{plan[:500]}"

        # Parse FIND/REPLACE blocks from the plan.
        edits = self._parse_plan_edits(plan)
        if not edits:
            return f"No FIND/REPLACE blocks parsed from plan — raw plan:\n{plan[:500]}"

        applied = 0
        errors: list[str] = []

        for i, (find_text, replace_text) in enumerate(edits, 1):
            try:
                result = client.invoke_tool("replace_file_content", {
                    "TargetFile": str(Path(task.file_path).resolve()),
                    "TargetContent": find_text,
                    "ReplacementContent": replace_text,
                    "StartLine": 0,
                    "EndLine": 0,
                })
                if hasattr(result, "success") and result.success:
                    applied += 1
                else:
                    error_msg = getattr(result, "error", "unknown error")
                    errors.append(f"Step {i}: {error_msg}")
            except Exception as e:
                errors.append(f"Step {i}: {e}")

        summary = f"Applied {applied}/{len(edits)} edits to {task.file_path}"
        if errors:
            summary += f"\nErrors: {'; '.join(errors)}"

        # Log to relay.
        self._relay.post_message("editor", summary)

        return summary

    def _parse_plan_edits(self, plan: str) -> list[tuple[str, str]]:
        """Extract FIND/REPLACE pairs from a plan text.

        Returns:
            List of (find_text, replace_text) tuples.
        """
        import re

        edits: list[tuple[str, str]] = []
        # Match FIND: ... REPLACE: ... blocks (greedy within step boundaries).
        pattern = re.compile(
            r"FIND:\s*(.+?)REPLACE:\s*(.+?)(?=(?:STEP\s+\d|FIND:|$))",
            re.DOTALL,
        )
        for match in pattern.finditer(plan):
            find_text = match.group(1).strip()
            replace_text = match.group(2).strip()
            if find_text and replace_text:
                edits.append((find_text, replace_text))

        return edits

    def _get_ag_client(self) -> Any:
        """Lazy-initialize the Antigravity client."""
        if self._ag_client is None:
            try:
                from codomyrmex.ide.antigravity import AntigravityClient
                client = AntigravityClient()
                if client.connect():
                    self._ag_client = client
                else:
                    logger.warning("Antigravity session not found")
                    return None
            except ImportError:
                logger.warning("Antigravity module not available")
                return None
        return self._ag_client

    # ── Private: Review ──────────────────────────────────────────────

    def _review(
        self,
        task: EditTask,
        plan: str,
        edit_summary: str,
    ) -> tuple[bool, str, float]:
        """Review the applied edits and decide whether to approve.

        Args:
            task: The current task.
            plan: The plan that was executed.
            edit_summary: Summary of what was changed.

        Returns:
            Tuple of (approved, review_notes, score).
        """
        # Read the file after edits (if it exists).
        post_edit_content = ""
        if task.file_path:
            try:
                post_edit_content = Path(task.file_path).read_text(
                    errors="replace"
                )
                if len(post_edit_content) > 8000:
                    post_edit_content = (
                        post_edit_content[:8000] + "\n... (truncated)"
                    )
            except (FileNotFoundError, OSError):
                post_edit_content = "(file not found after edit)"

        prompt = (
            f"System: You are a code reviewer. Evaluate the following edit.\n\n"
            f"Original task: {task.description}\n"
            f"Edit type: {task.edit_type}\n"
            f"Plan executed:\n{plan[:2000]}\n"
            f"Edit result: {edit_summary}\n"
            f"\nFile after edit:\n{post_edit_content}\n"
            f"\nRate this edit from 0 to 10 and explain your assessment.\n"
            f"Format your response as:\n"
            f"SCORE: [number 0-10]\n"
            f"APPROVED: [yes/no]\n"
            f"NOTES: [your feedback]\n"
        )

        req = AgentRequest(prompt=prompt)
        resp = self._reviewer.execute_with_session(req)
        review_text = resp.content.strip() if hasattr(resp, "content") else str(resp)

        # Parse score and approval.
        score = self._parse_score(review_text)
        approved = (
            "APPROVED: yes" in review_text.lower()
            or score >= self.config.approval_threshold
        )
        notes = self._parse_notes(review_text)

        return approved, notes, score

    @staticmethod
    def _parse_score(review_text: str) -> float:
        """Extract a numeric score from review text."""
        import re
        match = re.search(r"SCORE:\s*([\d.]+)", review_text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        return 0.0

    @staticmethod
    def _parse_notes(review_text: str) -> str:
        """Extract notes from review text."""
        import re
        match = re.search(r"NOTES:\s*(.+)", review_text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return review_text


__all__ = [
    "EditTask",
    "EditingConfig",
    "EditingOrchestrator",
]
