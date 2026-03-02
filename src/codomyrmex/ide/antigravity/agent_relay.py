"""Agent Relay — File-based inter-agent message bus.

Provides a JSONL-backed message relay for asynchronous communication
between agent processes (e.g. Antigravity ↔ Claude Code). Each channel
is a directory under ``~/.codomyrmex/agent_relay/<channel_id>/`` containing
a ``messages.jsonl`` file that both agents append to and poll from.

Example::

    >>> from codomyrmex.ide.antigravity.agent_relay import AgentRelay
    >>> relay = AgentRelay("my-channel")
    >>> relay.post_message("antigravity", "Analyze config.yaml")
    >>> messages = relay.poll_messages(since_cursor=0)
    >>> print(messages[0].content)
    'Analyze config.yaml'

Architecture::

    Antigravity ──post──▶ messages.jsonl ◀──poll── Claude Code
                          (append-only)
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone, UTC
from pathlib import Path
from typing import Any

try:
    from codomyrmex.logging_monitoring import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


# =====================================================================
# Message Types
# =====================================================================

MSG_CHAT = "chat"
MSG_TOOL_REQUEST = "tool_request"
MSG_TOOL_RESULT = "tool_result"
MSG_SYSTEM = "system"
MSG_HEARTBEAT = "heartbeat"

ALL_MSG_TYPES = frozenset({MSG_CHAT, MSG_TOOL_REQUEST, MSG_TOOL_RESULT, MSG_SYSTEM, MSG_HEARTBEAT})


# =====================================================================
# Data Structures
# =====================================================================

@dataclass
class RelayMessage:
    """A single message in the relay channel.

    Attributes:
        id: Unique message identifier.
        timestamp: ISO-8601 UTC timestamp.
        sender: Identity of the sender (e.g. ``"antigravity"``, ``"claude_code"``).
        msg_type: One of ``chat``, ``tool_request``, ``tool_result``, ``system``, ``heartbeat``.
        content: Text content for chat/system messages.
        tool_name: Tool name for tool_request messages.
        tool_args: Tool arguments for tool_request messages.
        request_id: Links tool_result back to tool_request.
        metadata: Arbitrary metadata dict.
        cursor: Line number in the JSONL file (set on read).
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    sender: str = ""
    msg_type: str = MSG_CHAT
    content: str = ""
    tool_name: str | None = None
    tool_args: dict[str, Any] | None = None
    request_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    cursor: int = 0

    def to_json(self) -> str:
        """Serialize to a single JSON line.

        Returns:
            JSON string (no trailing newline).
        """
        d = asdict(self)
        d.pop("cursor", None)  # cursor is a read-side concept
        return json.dumps(d, default=str)

    @classmethod
    def from_json(cls, line: str, cursor: int = 0) -> RelayMessage:
        """Deserialize from a JSON line.

        Args:
            line: JSON string.
            cursor: Line number in the JSONL file.

        Returns:
            Parsed ``RelayMessage``.
        """
        data = json.loads(line)
        data["cursor"] = cursor
        return cls(**data)

    @property
    def is_chat(self) -> bool:
        return self.msg_type == MSG_CHAT

    @property
    def is_tool_request(self) -> bool:
        return self.msg_type == MSG_TOOL_REQUEST

    @property
    def is_tool_result(self) -> bool:
        return self.msg_type == MSG_TOOL_RESULT


# =====================================================================
# Relay Engine
# =====================================================================

DEFAULT_RELAY_DIR = Path.home() / ".codomyrmex" / "agent_relay"


class AgentRelay:
    """File-based relay for inter-agent communication.

    Each channel is a directory containing ``messages.jsonl`` (append-only).
    Multiple agents poll the same file with independent cursors.

    Attributes:
        channel_id: Unique channel identifier.
        channel_dir: Path to the channel directory.
        messages_path: Path to the JSONL file.
    """

    def __init__(
        self,
        channel_id: str,
        *,
        relay_dir: Path | str | None = None,
    ) -> None:
        """Initialize the relay.

        Args:
            channel_id: Channel identifier (used as directory name).
            relay_dir: Root directory for all channels.
                Defaults to ``~/.codomyrmex/agent_relay/``.
        """
        root = Path(relay_dir) if relay_dir else DEFAULT_RELAY_DIR
        self.channel_id = channel_id
        self.channel_dir = root / channel_id
        self.messages_path = self.channel_dir / "messages.jsonl"

        # Ensure channel directory exists
        self.channel_dir.mkdir(parents=True, exist_ok=True)

        # Create messages file if it doesn't exist
        if not self.messages_path.exists():
            self.messages_path.touch()
            logger.info(f"Created relay channel: {self.channel_id}")

        logger.info(f"AgentRelay initialized: {self.channel_dir}")

    # ── Writing ───────────────────────────────────────────────────

    def _append(self, msg: RelayMessage) -> int:
        """Append a message to the JSONL file.

        Args:
            msg: Message to append.

        Returns:
            The cursor (line number) of the appended message.
        """
        line = msg.to_json()
        with open(self.messages_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            # Flush to ensure other processes see the write
            f.flush()
            os.fsync(f.fileno())

        cursor = self._count_lines()
        logger.debug(f"Appended message {msg.id} at cursor {cursor}")
        return cursor

    def post_message(
        self,
        sender: str,
        content: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> RelayMessage:
        """Post a chat message to the relay.

        Args:
            sender: Sender identity.
            content: Message text.
            metadata: Optional metadata.

        Returns:
            The posted ``RelayMessage``.
        """
        msg = RelayMessage(
            sender=sender,
            msg_type=MSG_CHAT,
            content=content,
            metadata=metadata or {},
        )
        self._append(msg)
        logger.info(f"[{sender}] posted chat: {content[:80]}...")
        return msg

    def post_tool_request(
        self,
        sender: str,
        tool_name: str,
        tool_args: dict[str, Any] | None = None,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> RelayMessage:
        """Post a tool execution request.

        Args:
            sender: Sender identity.
            tool_name: Name of the tool to execute.
            tool_args: Tool arguments.
            metadata: Optional metadata.

        Returns:
            The posted ``RelayMessage`` (use its ``id`` to match the result).
        """
        msg = RelayMessage(
            sender=sender,
            msg_type=MSG_TOOL_REQUEST,
            content=f"Execute tool: {tool_name}",
            tool_name=tool_name,
            tool_args=tool_args or {},
            metadata=metadata or {},
        )
        self._append(msg)
        logger.info(f"[{sender}] requested tool: {tool_name}")
        return msg

    def post_tool_result(
        self,
        sender: str,
        request_id: str,
        result: Any,
        *,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> RelayMessage:
        """Post a tool execution result.

        Args:
            sender: Sender identity.
            request_id: The ``id`` of the original tool_request.
            result: Tool execution result.
            error: Error message if tool failed.
            metadata: Optional metadata.

        Returns:
            The posted ``RelayMessage``.
        """
        content = json.dumps(result, default=str) if not isinstance(result, str) else result
        meta = metadata or {}
        if error:
            meta["error"] = error

        msg = RelayMessage(
            sender=sender,
            msg_type=MSG_TOOL_RESULT,
            content=content,
            request_id=request_id,
            metadata=meta,
        )
        self._append(msg)
        logger.info(f"[{sender}] posted tool result for request {request_id}")
        return msg

    def post_heartbeat(self, sender: str) -> RelayMessage:
        """Post a heartbeat to indicate liveness.

        Args:
            sender: Sender identity.

        Returns:
            The posted ``RelayMessage``.
        """
        msg = RelayMessage(
            sender=sender,
            msg_type=MSG_HEARTBEAT,
            content="heartbeat",
        )
        self._append(msg)
        return msg

    def post_system(self, content: str) -> RelayMessage:
        """Post a system message (e.g. channel opened/closed).

        Args:
            content: System message text.

        Returns:
            The posted ``RelayMessage``.
        """
        msg = RelayMessage(
            sender="system",
            msg_type=MSG_SYSTEM,
            content=content,
        )
        self._append(msg)
        return msg

    # ── Reading ───────────────────────────────────────────────────

    def poll_messages(
        self,
        *,
        since_cursor: int = 0,
        sender_filter: str | None = None,
        type_filter: str | None = None,
        exclude_heartbeats: bool = True,
    ) -> list[RelayMessage]:
        """Poll for new messages since a cursor position.

        Args:
            since_cursor: Line number to start reading from (0-indexed).
            sender_filter: Only return messages from this sender.
            type_filter: Only return messages of this type.
            exclude_heartbeats: Skip heartbeat messages (default True).

        Returns:
            List of new ``RelayMessage`` objects.
        """
        messages: list[RelayMessage] = []

        if not self.messages_path.exists():
            return messages

        with open(self.messages_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f):
                if line_num < since_cursor:
                    continue

                line = line.strip()
                if not line:
                    continue

                try:
                    msg = RelayMessage.from_json(line, cursor=line_num + 1)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Skipping malformed line {line_num}: {e}")
                    continue

                # Filters
                if exclude_heartbeats and msg.msg_type == MSG_HEARTBEAT:
                    continue
                if sender_filter and msg.sender != sender_filter:
                    continue
                if type_filter and msg.msg_type != type_filter:
                    continue

                messages.append(msg)

        return messages

    def get_latest_cursor(self) -> int:
        """Get the current end-of-file cursor.

        Returns:
            Line count (next poll should use this as ``since_cursor``).
        """
        return self._count_lines()

    def get_history(
        self,
        *,
        limit: int | None = None,
        exclude_heartbeats: bool = True,
    ) -> list[RelayMessage]:
        """Get full message history.

        Args:
            limit: Maximum messages to return (from end).
            exclude_heartbeats: Skip heartbeat messages.

        Returns:
            List of ``RelayMessage`` objects.
        """
        all_msgs = self.poll_messages(
            since_cursor=0,
            exclude_heartbeats=exclude_heartbeats,
        )
        if limit:
            return all_msgs[-limit:]
        return all_msgs

    def await_response(
        self,
        request_id: str,
        *,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
        since_cursor: int = 0,
    ) -> RelayMessage | None:
        """Block until a tool_result for a given request_id appears.

        Args:
            request_id: The request ID to wait for.
            timeout: Maximum seconds to wait.
            poll_interval: Seconds between polls.
            since_cursor: Cursor to start polling from.

        Returns:
            The matching ``RelayMessage`` or None if timed out.
        """
        deadline = time.monotonic() + timeout
        cursor = since_cursor

        while time.monotonic() < deadline:
            messages = self.poll_messages(
                since_cursor=cursor,
                type_filter=MSG_TOOL_RESULT,
            )
            for msg in messages:
                if msg.request_id == request_id:
                    return msg
                cursor = max(cursor, msg.cursor)

            time.sleep(poll_interval)

        logger.warning(f"Timeout waiting for response to {request_id}")
        return None

    # ── Channel Management ────────────────────────────────────────

    def clear(self) -> None:
        """Clear all messages in the channel."""
        with open(self.messages_path, "w", encoding="utf-8") as f:
            f.truncate(0)
        logger.info(f"Cleared channel: {self.channel_id}")

    def get_stats(self) -> dict[str, Any]:
        """Get channel statistics.

        Returns:
            Dictionary with message counts by type and sender.
        """
        messages = self.poll_messages(since_cursor=0, exclude_heartbeats=False)
        by_type: dict[str, int] = {}
        by_sender: dict[str, int] = {}
        for msg in messages:
            by_type[msg.msg_type] = by_type.get(msg.msg_type, 0) + 1
            by_sender[msg.sender] = by_sender.get(msg.sender, 0) + 1

        return {
            "channel_id": self.channel_id,
            "total_messages": len(messages),
            "by_type": by_type,
            "by_sender": by_sender,
            "path": str(self.messages_path),
        }

    @staticmethod
    def list_channels(relay_dir: Path | str | None = None) -> list[str]:
        """List all available relay channels.

        Args:
            relay_dir: Root relay directory.

        Returns:
            List of channel IDs.
        """
        root = Path(relay_dir) if relay_dir else DEFAULT_RELAY_DIR
        if not root.exists():
            return []
        return sorted(
            d.name for d in root.iterdir()
            if d.is_dir() and (d / "messages.jsonl").exists()
        )

    # ── Internals ─────────────────────────────────────────────────

    def _count_lines(self) -> int:
        """Count lines in the messages file."""
        if not self.messages_path.exists():
            return 0
        with open(self.messages_path, encoding="utf-8") as f:
            return sum(1 for _ in f)


__all__ = [
    "AgentRelay",
    "RelayMessage",
    "MSG_CHAT",
    "MSG_TOOL_REQUEST",
    "MSG_TOOL_RESULT",
    "MSG_SYSTEM",
    "MSG_HEARTBEAT",
    "DEFAULT_RELAY_DIR",
]
