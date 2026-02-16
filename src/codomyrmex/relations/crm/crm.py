"""Contact Relationship Manager.

Provides Contact, Interaction, and ContactManager classes for
managing contacts, tagging, searching, and tracking interaction
history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4


@dataclass
class Interaction:
    """A recorded interaction with a contact.

    Attributes:
        id: Unique identifier.
        type: Interaction category (email, call, meeting, note, etc.).
        notes: Free-text description of the interaction.
        timestamp: When the interaction occurred.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    type: str = "note"
    notes: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class Contact:
    """A person or organization in the CRM.

    Attributes:
        id: Unique identifier.
        name: Display name.
        email: Primary email address.
        tags: List of categorical tags.
        metadata: Arbitrary key-value metadata.
        created_at: ISO-format creation timestamp.
        interactions: History of interactions with this contact.
    """

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    email: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    interactions: list[Interaction] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the contact to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "interaction_count": len(self.interactions),
        }


class ContactManager:
    """Manages a collection of contacts with search and tagging.

    Provides CRUD operations, tag-based filtering, interaction
    logging, and basic search capabilities.
    """

    def __init__(self) -> None:
        """Initialize an empty contact manager."""
        self._contacts: dict[str, Contact] = {}

    def add_contact(self, name: str, email: str, **kwargs: Any) -> Contact:
        """Create and store a new contact.

        Args:
            name: Contact display name.
            email: Contact email address.
            **kwargs: Additional fields passed to Contact (tags, metadata, etc.).

        Returns:
            The newly created Contact instance.
        """
        tags = kwargs.pop("tags", [])
        metadata = kwargs.pop("metadata", {})
        contact = Contact(name=name, email=email, tags=tags, metadata=metadata)
        self._contacts[contact.id] = contact
        return contact

    def get_contact(self, contact_id: str) -> Contact | None:
        """Retrieve a contact by ID.

        Args:
            contact_id: The contact's unique identifier.

        Returns:
            The Contact if found, otherwise None.
        """
        return self._contacts.get(contact_id)

    def remove_contact(self, contact_id: str) -> bool:
        """Remove a contact by ID. Returns True if removed."""
        if contact_id in self._contacts:
            del self._contacts[contact_id]
            return True
        return False

    def search_contacts(self, query: str) -> list[Contact]:
        """Search contacts by name, email, or tags.

        The query is matched case-insensitively against the contact's
        name, email, and each tag.

        Args:
            query: Search string.

        Returns:
            List of matching Contact instances.
        """
        q = query.lower()
        results: list[Contact] = []
        for contact in self._contacts.values():
            if q in contact.name.lower():
                results.append(contact)
            elif q in contact.email.lower():
                results.append(contact)
            elif any(q in tag.lower() for tag in contact.tags):
                results.append(contact)
        return results

    def tag_contact(self, contact_id: str, tags: list[str]) -> bool:
        """Add tags to a contact.

        Args:
            contact_id: The contact's ID.
            tags: Tags to add (duplicates are ignored).

        Returns:
            True if the contact was found and updated.
        """
        contact = self._contacts.get(contact_id)
        if contact is None:
            return False
        existing = set(contact.tags)
        for tag in tags:
            if tag not in existing:
                contact.tags.append(tag)
                existing.add(tag)
        return True

    def get_interaction_history(self, contact_id: str) -> list[dict[str, Any]]:
        """Retrieve the interaction history for a contact.

        Args:
            contact_id: The contact's ID.

        Returns:
            List of interaction dicts sorted by timestamp (newest first),
            or an empty list if the contact is not found.
        """
        contact = self._contacts.get(contact_id)
        if contact is None:
            return []
        interactions = sorted(
            contact.interactions,
            key=lambda i: i.timestamp,
            reverse=True,
        )
        return [
            {"id": i.id, "type": i.type, "notes": i.notes, "timestamp": i.timestamp}
            for i in interactions
        ]

    def add_interaction(self, contact_id: str, type: str, notes: str) -> Interaction | None:
        """Log a new interaction with a contact.

        Args:
            contact_id: The contact's ID.
            type: Interaction type (e.g., 'email', 'call', 'meeting').
            notes: Description of the interaction.

        Returns:
            The created Interaction, or None if the contact was not found.
        """
        contact = self._contacts.get(contact_id)
        if contact is None:
            return None
        interaction = Interaction(type=type, notes=notes)
        contact.interactions.append(interaction)
        return interaction

    def get_contacts_by_tag(self, tag: str) -> list[Contact]:
        """Return all contacts that have a specific tag."""
        return [c for c in self._contacts.values() if tag in c.tags]

    @property
    def all_contacts(self) -> list[Contact]:
        """Read-only list of all contacts."""
        return list(self._contacts.values())

    def __len__(self) -> int:
        return len(self._contacts)
