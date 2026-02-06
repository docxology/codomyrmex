"""Document metadata models."""

import copy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class MetadataField:
    """A single metadata field."""

    name: str
    value: Any
    data_type: str | None = None
    source: str | None = None


@dataclass
class DocumentMetadata:
    """Document metadata container."""

    title: str | None = None
    author: str | None = None
    created_at: datetime | None = None
    modified_at: datetime | None = None
    version: str | None = None
    tags: list[str] = field(default_factory=list)
    custom_fields: dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "DocumentMetadata":
        """Return a deep copy of this metadata."""
        return copy.deepcopy(self)

    def to_dict(self) -> dict:
        """Convert metadata to dictionary."""
        return {
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "version": self.version,
            "tags": self.tags,
            "custom_fields": self.custom_fields,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentMetadata":
        """Create metadata from dictionary."""
        created_at = None
        modified_at = None

        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
        if data.get("modified_at"):
            modified_at = datetime.fromisoformat(data["modified_at"])

        return cls(
            title=data.get("title"),
            author=data.get("author"),
            created_at=created_at,
            modified_at=modified_at,
            version=data.get("version"),
            tags=data.get("tags", []),
            custom_fields=data.get("custom_fields", {}),
        )
