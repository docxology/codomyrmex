"""Generic representations and base classes for the email module."""

import abc
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class EmailAddress(BaseModel):
    """Represents a single email address (e.g. 'John Doe <john@example.com>')."""
    email: str
    name: Optional[str] = None


class EmailMessage(BaseModel):
    """A generic representation of an email message."""
    id: Optional[str] = None
    thread_id: Optional[str] = None
    subject: str
    sender: EmailAddress
    to: List[EmailAddress] = Field(default_factory=list)
    cc: List[EmailAddress] = Field(default_factory=list)
    bcc: List[EmailAddress] = Field(default_factory=list)
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    date: datetime
    labels: List[str] = Field(default_factory=list)


class EmailDraft(BaseModel):
    """A generic representation of an email draft."""
    subject: str
    to: List[str] = Field(default_factory=list)
    cc: List[str] = Field(default_factory=list)
    bcc: List[str] = Field(default_factory=list)
    body_text: str
    body_html: Optional[str] = None


class EmailProvider(abc.ABC):
    """Abstract base class for all email providers."""

    @abc.abstractmethod
    def list_messages(self, query: str = "", max_results: int = 100) -> List[EmailMessage]:
        """List messages matching the generic query."""
        pass

    @abc.abstractmethod
    def get_message(self, message_id: str) -> EmailMessage:
        """Fetch a specific message by its ID."""
        pass

    @abc.abstractmethod
    def send_message(self, draft: EmailDraft) -> EmailMessage:
        """Send a new email immediately."""
        pass

    @abc.abstractmethod
    def create_draft(self, draft: EmailDraft) -> str:
        """Create a new draft and return its ID."""
        pass

    @abc.abstractmethod
    def delete_message(self, message_id: str) -> None:
        """Delete an email message."""
        pass

    @abc.abstractmethod
    def modify_labels(self, message_id: str, add_labels: List[str], remove_labels: List[str]) -> None:
        """Add or remove labels from a message."""
        pass
