import hashlib
from datetime import datetime

from .models import Conversation, MessageRole
from .stores import InMemoryHistoryStore


class ConversationManager:
    """
    High-level manager for conversation history.

    Usage:
        manager = ConversationManager()

        # Start a new conversation
        conv = manager.create_conversation("Code Review Session")

        # Add messages
        conv.add_user_message("Review this code...")
        conv.add_assistant_message("Here's my review...")

        # Save
        manager.save(conv)

        # Later, retrieve
        conv = manager.get_conversation(conv_id)
    """

    def __init__(
        self,
        store: InMemoryHistoryStore | None = None,
        max_messages_per_conversation: int = 100,
    ):
        """Initialize this instance."""
        self.store = store or InMemoryHistoryStore()
        self.max_messages = max_messages_per_conversation
        self._active_conversation: Conversation | None = None

    def create_conversation(
        self,
        title: str = "",
        system_prompt: str | None = None,
        **metadata
    ) -> Conversation:
        """Create a new conversation."""
        conv_id = hashlib.sha256(
            f"{datetime.now().isoformat()}{title}".encode()
        ).hexdigest()[:16]

        conv = Conversation(
            conversation_id=conv_id,
            title=title or f"Conversation {conv_id[:8]}",
            metadata=metadata,
        )

        if system_prompt:
            conv.add_message(MessageRole.SYSTEM, system_prompt)

        self._active_conversation = conv
        return conv

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        """Get a conversation by ID."""
        return self.store.load(conversation_id)

    def save(self, conversation: Conversation | None = None) -> None:
        """Save a conversation."""
        conv = conversation or self._active_conversation
        if conv:
            # Truncate if needed
            if len(conv.messages) > self.max_messages:
                conv.truncate(self.max_messages)
            self.store.save(conv)

    def delete(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        return self.store.delete(conversation_id)

    def list_recent(self, limit: int = 20) -> list[Conversation]:
        """List recent conversations."""
        return self.store.list_conversations(limit=limit)

    def search(self, query: str) -> list[Conversation]:
        """Search conversations."""
        return self.store.search(query)

    @property
    def active(self) -> Conversation | None:
        """Get the active conversation."""
        return self._active_conversation

    def set_active(self, conversation_id: str) -> Conversation | None:
        """Set the active conversation."""
        conv = self.store.load(conversation_id)
        if conv:
            self._active_conversation = conv
        return conv


