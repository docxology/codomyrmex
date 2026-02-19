"""Antigravity ConversationHistory Bridge.

Bridges Antigravity's artifact filesystem (``task.md``, ``implementation_plan.md``,
``walkthrough.md``) with the ``agents.history.ConversationHistory`` module for
cross-conversation agent memory persistence.

Example::

    >>> from codomyrmex.ide.antigravity.history_bridge import ArtifactHistoryBridge
    >>> bridge = ArtifactHistoryBridge("/path/to/brain/conv-id")
    >>> bridge.save_agent_memory("key", {"data": "value"})
    >>> bridge.load_agent_memory("key")
    {'data': 'value'}
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


# Standard Antigravity artifact names
ARTIFACT_NAMES: frozenset[str] = frozenset({
    "task.md",
    "implementation_plan.md",
    "walkthrough.md",
})


class ArtifactHistoryBridge:
    """Bridges Antigravity artifacts with agent memory.

    Reads and writes to the Antigravity brain directory to provide
    agents with persistent context across conversations.

    Attributes:
        brain_dir: Path to the conversation's brain directory.
    """

    def __init__(self, brain_dir: str | Path) -> None:
        """Initialize the bridge.

        Args:
            brain_dir: Absolute path to the conversation's brain directory.
        """
        self.brain_dir = Path(brain_dir)
        self._memory_dir = self.brain_dir / ".agent_memory"
        logger.info(f"ArtifactHistoryBridge initialized: {self.brain_dir}")

    def list_artifacts(self) -> list[str]:
        """List existing artifacts in the brain directory.

        Returns:
            List of artifact filenames.
        """
        if not self.brain_dir.exists():
            return []
        return [
            f.name for f in self.brain_dir.iterdir()
            if f.is_file() and f.suffix == ".md"
        ]

    def read_artifact(self, name: str) -> str | None:
        """Read an artifact's content.

        Args:
            name: Artifact filename (e.g. ``"task.md"``).

        Returns:
            File content or None if not found.
        """
        path = self.brain_dir / name
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def read_task_status(self) -> dict[str, Any]:
        """Parse task.md into structured status.

        Returns:
            Dictionary with ``total``, ``completed``, ``in_progress``,
            and ``items`` list.
        """
        content = self.read_artifact("task.md")
        if content is None:
            return {"total": 0, "completed": 0, "in_progress": 0, "items": []}

        items: list[dict[str, str]] = []
        total = completed = in_progress = 0

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("- [x]"):
                items.append({"status": "done", "text": stripped[5:].strip()})
                total += 1
                completed += 1
            elif stripped.startswith("- [/]"):
                items.append({"status": "in_progress", "text": stripped[5:].strip()})
                total += 1
                in_progress += 1
            elif stripped.startswith("- [ ]"):
                items.append({"status": "todo", "text": stripped[5:].strip()})
                total += 1

        return {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "items": items,
        }

    def save_agent_memory(self, key: str, data: Any) -> None:
        """Persist structured data to the agent memory store.

        Args:
            key: Memory key (used as filename).
            data: JSON-serializable data to store.
        """
        self._memory_dir.mkdir(parents=True, exist_ok=True)
        path = self._memory_dir / f"{key}.json"
        path.write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8",
        )
        logger.info(f"Saved agent memory: {key}")

    def load_agent_memory(self, key: str) -> Any | None:
        """Load structured data from the agent memory store.

        Args:
            key: Memory key.

        Returns:
            Deserialized data or None if not found.
        """
        path = self._memory_dir / f"{key}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list_memories(self) -> list[str]:
        """List all agent memory keys.

        Returns:
            List of memory keys.
        """
        if not self._memory_dir.exists():
            return []
        return [
            f.stem for f in self._memory_dir.iterdir()
            if f.is_file() and f.suffix == ".json"
        ]

    def get_conversation_context(self) -> dict[str, Any]:
        """Build a comprehensive context from all artifacts and memories.

        Returns:
            Dictionary with artifacts, task_status, and memories.
        """
        return {
            "artifacts": self.list_artifacts(),
            "task_status": self.read_task_status(),
            "memories": {
                key: self.load_agent_memory(key) for key in self.list_memories()
            },
        }


__all__ = [
    "ArtifactHistoryBridge",
    "ARTIFACT_NAMES",
]
