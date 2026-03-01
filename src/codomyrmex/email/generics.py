"""Generic representations and base classes for the email module."""

import abc
from datetime import datetime

from pydantic import BaseModel, Field


class EmailAddress(BaseModel):
    """Represents a single email address (e.g. 'John Doe <john@example.com>')."""
    email: str
    name: str | None = None


class EmailMessage(BaseModel):
    """A generic representation of an email message."""
    id: str | None = None
    thread_id: str | None = None
    subject: str
    sender: EmailAddress
    to: list[EmailAddress] = Field(default_factory=list)
    cc: list[EmailAddress] = Field(default_factory=list)
    bcc: list[EmailAddress] = Field(default_factory=list)
    body_text: str | None = None
    body_html: str | None = None
    date: datetime
    labels: list[str] = Field(default_factory=list)


class EmailDraft(BaseModel):
    """A generic representation of an email draft."""
    subject: str
    to: list[str] = Field(default_factory=list)
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)
    body_text: str
    body_html: str | None = None


class EmailProvider(abc.ABC):
    """Abstract base class for all email providers."""

    @abc.abstractmethod
    def list_messages(self, query: str = "", max_results: int = 100) -> list[EmailMessage]:
        """List messages matching the generic query."""
        ...

    @abc.abstractmethod
    def get_message(self, message_id: str) -> EmailMessage:
        """Fetch a specific message by its ID."""
        ...

    @abc.abstractmethod
    def send_message(self, draft: EmailDraft) -> EmailMessage:
        """Send a new email immediately."""
        ...

    @abc.abstractmethod
    def create_draft(self, draft: EmailDraft) -> str:
        """Create a new draft and return its ID."""
        ...

    @abc.abstractmethod
    def delete_message(self, message_id: str) -> None:
        """Delete an email message."""
        ...

    @abc.abstractmethod
    def modify_labels(self, message_id: str, add_labels: list[str], remove_labels: list[str]) -> None:
        """Add or remove labels from a message."""
        ...
