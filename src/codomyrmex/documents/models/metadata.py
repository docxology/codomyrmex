"""Document metadata models."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class MetadataField:
    """A single metadata field."""
    
    name: str
    value: Any
    data_type: Optional[str] = None
    source: Optional[str] = None  # Where this metadata came from


@dataclass
class DocumentMetadata:
    """Document metadata container."""
    
    title: Optional[str] = None
    author: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    version: Optional[str] = None
    tags: list[str] = None
    custom_fields: dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.custom_fields is None:
            self.custom_fields = {}
    
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

