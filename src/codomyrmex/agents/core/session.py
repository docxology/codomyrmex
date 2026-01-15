"""
Agent Session Management.

Provides session handling for multi-turn conversations with agents,
including history tracking, persistence, and context windowing.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
import json
import uuid

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class Message:
    """A single message in a conversation."""
    
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Message":
        """Create from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            metadata=data.get("metadata", {}),
        )


@dataclass
class AgentSession:
    """
    Manages a conversation session with an agent.
    
    Provides:
    - Message history tracking
    - Session persistence (save/load)
    - Context windowing for token limits
    - Session metadata
    """
    
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ""
    messages: list[Message] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    max_history: int = 50
    
    def add_user_message(self, content: str, metadata: Optional[dict] = None) -> Message:
        """Add a user message to the session."""
        msg = Message(role="user", content=content, metadata=metadata or {})
        self.messages.append(msg)
        self._trim_history()
        return msg
    
    def add_assistant_message(self, content: str, metadata: Optional[dict] = None) -> Message:
        """Add an assistant message to the session."""
        msg = Message(role="assistant", content=content, metadata=metadata or {})
        self.messages.append(msg)
        self._trim_history()
        return msg
    
    def add_system_message(self, content: str, metadata: Optional[dict] = None) -> Message:
        """Add a system message to the session."""
        msg = Message(role="system", content=content, metadata=metadata or {})
        self.messages.append(msg)
        return msg
    
    def get_context(self, max_messages: Optional[int] = None) -> list[dict[str, str]]:
        """
        Get conversation context for sending to agent.
        
        Args:
            max_messages: Maximum messages to include (default: all)
            
        Returns:
            List of message dicts with role and content
        """
        messages = self.messages[-max_messages:] if max_messages else self.messages
        return [{"role": m.role, "content": m.content} for m in messages]
    
    def get_last_response(self) -> Optional[str]:
        """Get the last assistant response."""
        for msg in reversed(self.messages):
            if msg.role == "assistant":
                return msg.content
        return None
    
    def clear(self) -> None:
        """Clear all messages from the session."""
        self.messages.clear()
        logger.info(f"Session {self.session_id} cleared")
    
    def _trim_history(self) -> None:
        """Trim history to max_history limit, preserving system messages."""
        if len(self.messages) <= self.max_history:
            return
        
        system_msgs = [m for m in self.messages if m.role == "system"]
        other_msgs = [m for m in self.messages if m.role != "system"]
        
        keep_count = self.max_history - len(system_msgs)
        if keep_count > 0:
            self.messages = system_msgs + other_msgs[-keep_count:]
        else:
            self.messages = system_msgs[-self.max_history:]
    
    def save(self, path: Path) -> None:
        """
        Save session to file.
        
        Args:
            path: File path to save to
        """
        data = {
            "session_id": self.session_id,
            "agent_name": self.agent_name,
            "messages": [m.to_dict() for m in self.messages],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "max_history": self.max_history,
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Session saved to {path}")
    
    @classmethod
    def load(cls, path: Path) -> "AgentSession":
        """
        Load session from file.
        
        Args:
            path: File path to load from
            
        Returns:
            Loaded session
        """
        with open(path) as f:
            data = json.load(f)
        
        session = cls(
            session_id=data["session_id"],
            agent_name=data["agent_name"],
            messages=[Message.from_dict(m) for m in data["messages"]],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            max_history=data.get("max_history", 50),
        )
        
        logger.info(f"Session loaded from {path}")
        return session
    
    def __len__(self) -> int:
        """Return number of messages."""
        return len(self.messages)
    
    def __repr__(self) -> str:
        return f"AgentSession(id={self.session_id[:8]}..., messages={len(self.messages)})"


class SessionManager:
    """Manages multiple agent sessions."""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize session manager.
        
        Args:
            storage_dir: Directory for session persistence
        """
        self.sessions: dict[str, AgentSession] = {}
        self.storage_dir = storage_dir
        
        if storage_dir:
            storage_dir.mkdir(parents=True, exist_ok=True)
    
    def create_session(self, agent_name: str, session_id: Optional[str] = None) -> AgentSession:
        """Create a new session."""
        session = AgentSession(
            session_id=session_id or str(uuid.uuid4()),
            agent_name=agent_name,
        )
        self.sessions[session.session_id] = session
        logger.info(f"Created session {session.session_id} for {agent_name}")
        return session
    
    def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def get_or_create(self, agent_name: str, session_id: Optional[str] = None) -> AgentSession:
        """Get existing session or create new one."""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        return self.create_session(agent_name, session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.storage_dir:
                path = self.storage_dir / f"{session_id}.json"
                if path.exists():
                    path.unlink()
            logger.info(f"Deleted session {session_id}")
            return True
        return False
    
    def save_all(self) -> None:
        """Save all sessions to storage."""
        if not self.storage_dir:
            logger.warning("No storage directory configured")
            return
        
        for session_id, session in self.sessions.items():
            path = self.storage_dir / f"{session_id}.json"
            session.save(path)
    
    def load_all(self) -> int:
        """Load all sessions from storage. Returns count loaded."""
        if not self.storage_dir:
            return 0
        
        count = 0
        for path in self.storage_dir.glob("*.json"):
            try:
                session = AgentSession.load(path)
                self.sessions[session.session_id] = session
                count += 1
            except Exception as e:
                logger.warning(f"Failed to load session from {path}: {e}")
        
        return count
    
    def list_sessions(self, agent_name: Optional[str] = None) -> list[AgentSession]:
        """List all sessions, optionally filtered by agent name."""
        sessions = list(self.sessions.values())
        if agent_name:
            sessions = [s for s in sessions if s.agent_name == agent_name]
        return sessions
