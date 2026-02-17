"""
Data Lineage Models

Data classes and enums for lineage tracking.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NodeType(Enum):
    """Types of lineage nodes."""
    DATASET = "dataset"
    TRANSFORMATION = "transformation"
    MODEL = "model"
    ARTIFACT = "artifact"
    EXTERNAL = "external"


class EdgeType(Enum):
    """Types of lineage edges."""
    DERIVED_FROM = "derived_from"
    PRODUCED_BY = "produced_by"
    USED_BY = "used_by"
    INPUT_TO = "input_to"


@dataclass
class LineageNode:
    """A node in the lineage graph."""
    id: str
    name: str
    node_type: NodeType
    version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def key(self) -> str:
        """Get unique key."""
        return f"{self.node_type.value}:{self.id}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type.value,
            "version": self.version,
            "metadata": self.metadata,
        }


@dataclass
class LineageEdge:
    """An edge connecting two nodes."""
    source_id: str
    target_id: str
    edge_type: EdgeType
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def key(self) -> str:
        """Get unique key."""
        return f"{self.source_id}->{self.target_id}:{self.edge_type.value}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.edge_type.value,
        }


@dataclass
class DataAsset:
    """A data asset with lineage information."""
    id: str
    name: str
    location: str
    schema: dict[str, str] | None = None
    row_count: int | None = None
    size_bytes: int | None = None
    checksum: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def compute_checksum(self, data: bytes) -> str:
        """Compute checksum of data."""
        self.checksum = hashlib.sha256(data).hexdigest()
        return self.checksum
