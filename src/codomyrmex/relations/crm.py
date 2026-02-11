from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, Set
from uuid import uuid4, UUID

class InteractionType(Enum):
    EMAIL = auto()
    CALL = auto()
    MEETING = auto()
    SOCIAL_MEDIA = auto()

@dataclass
class Interaction:
    """Record of a communication event."""
    type: InteractionType
    summary: str
    timestamp: datetime = field(default_factory=datetime.now)
    id: UUID = field(default_factory=uuid4)

@dataclass
class Contact:
    """External entity (person or organization)."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    tags: Set[str] = field(default_factory=set)
    history: List[Interaction] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def log_interaction(self, interaction: Interaction) -> None:
        self.history.append(interaction)

    def add_tag(self, tag: str) -> None:
        self.tags.add(tag)

class CRM:
    """Customer Relationship Management engine."""
    
    def __init__(self):
        self._contacts: List[Contact] = []

    def add_contact(self, contact: Contact) -> None:
        self._contacts.append(contact)

    def search(self, query: str) -> List[Contact]:
        """Simple search by name or email."""
        query = query.lower()
        results = []
        for c in self._contacts:
            if query in c.name.lower() or (c.email and query in c.email.lower()):
                results.append(c)
        return results

    def get_contact(self, contact_id: UUID) -> Optional[Contact]:
        for c in self._contacts:
            if c.id == contact_id:
                return c
        return None
