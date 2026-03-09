"""Resource Management System for Codomyrmex.

This module provides resource allocation, dependency management, and coordination
for tasks and workflows across the Codomyrmex ecosystem.
"""

import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from codomyrmex.logging_monitoring import get_logger

# Import performance monitoring with fallback
try:
    from codomyrmex.performance import monitor_performance
except ImportError:
    # Fallback if performance module is not available or has circular imports
    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""

        def decorator(func):
            """Decorator."""
            return func

        return decorator


logger = get_logger(__name__)


class ResourceType(Enum):
    """Types of resources."""

    COMPUTE = "compute"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    API_QUOTA = "api_quota"
    DATABASE = "database"
    CUSTOM = "custom"
    FILE_HANDLE = "file_handle"
    THREAD = "thread"
    PROCESS = "process"
    LOCK = "lock"


class ResourceStatus(Enum):
    """Status of resources."""

    AVAILABLE = "available"
    ALLOCATED = "allocated"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    DEPLETED = "depleted"
    UNKNOWN = "unknown"


@dataclass
class ResourceLimits:
    """Resource limits definition."""

    min_value: float = 0
    max_value: float = float("inf")
    default_allocation: float = 1.0
    burst_limit: float | None = None
    unit: str = "unit"


@dataclass
class ResourceAllocation:
    """Record of a resource allocation."""

    allocation_id: str
    resource_id: str
    requester_id: str
    amount: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceUsage:
    """Current usage statistics for a resource."""

    resource_id: str
    total_capacity: float
    allocated_amount: float
    available_amount: float
    allocation_count: int
    utilization_percentage: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Resource:
    """Resource definition."""

    id: str
    name: str
    type: ResourceType
    capacity: float = 1.0
    description: str = ""
    limits: ResourceLimits = field(default_factory=ResourceLimits)
    status: ResourceStatus = ResourceStatus.AVAILABLE
    metadata: dict[str, Any] = field(default_factory=dict)

    # Runtime state (not serialized)
    allocated: float = 0.0
    allocations: dict[str, ResourceAllocation] = field(default_factory=dict)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        """Convert resource to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "capacity": self.capacity,
            "allocated": self.allocated,
            "status": self.status.value,
            "limits": asdict(self.limits),
            "metadata": self.metadata,
            "allocations": {k: asdict(v) for k, v in self.allocations.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Resource":
        """Create resource from dictionary."""
        limits_data = data.get("limits", {})
        limits = ResourceLimits(**limits_data)

        resource = cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", "unknown"),
            type=ResourceType(data.get("type", "custom")),
            capacity=data.get("capacity", 1.0),
            description=data.get("description", ""),
            limits=limits,
            status=ResourceStatus(data.get("status", "available")),
            metadata=data.get("metadata", {}),
        )

        # Restore allocations if present (carefully)
        if "allocations" in data:
            resource.allocated = data.get("allocated", 0.0)
            # Rehydrating allocations is complex due to datetime
            # Skipping detailed allocation rehydration for simplicity in this factory method

        return resource


class ResourceManager:
    """Manages system resources and allocations."""

    def __init__(self):
        """Initialize the resource manager."""
        self.resources: dict[str, Resource] = {}
        self.total_allocations = 0
        self._lock = threading.RLock()

        # Initialize default resources
        self._init_default_resources()

    def _init_default_resources(self):
        """Initialize standard system resources."""
        # Generic Compute Resource
        self.add_resource(
            Resource(
                id="sys-compute",
                name="System Compute",
                type=ResourceType.COMPUTE,
                capacity=100.0,
                description="Virtual CPU units",
                limits=ResourceLimits(unit="vCPU"),
            )
        )

        # Generic Memory Resource
        self.add_resource(
            Resource(
                id="sys-memory",
                name="System Memory",
                type=ResourceType.MEMORY,
                capacity=1024.0,
                description="System RAM in MB/GB units",
                limits=ResourceLimits(unit="MB"),
            )
        )

        # API Quota
        self.add_resource(
            Resource(
                id="api-global",
                name="Global API Quota",
                type=ResourceType.API_QUOTA,
                capacity=1000.0,
                description="Global API calls per minute",
                limits=ResourceLimits(unit="RPM"),
            )
        )

    @monitor_performance("add_resource")
    def add_resource(self, resource: Resource) -> bool:
        """Add a resource to management."""
        with self._lock:
            if resource.id in self.resources:
                logger.warning("Resource %s already exists, overwriting", resource.id)

            self.resources[resource.id] = resource
            logger.info("Added resource: %s (%s)", resource.name, resource.type.value)
            return True

    @monitor_performance("get_resource")
    def get_resource(self, resource_id: str) -> Resource | None:
        """Get a resource by ID."""
        return self.resources.get(resource_id)

    def get_resource_by_name(self, name: str) -> Resource | None:
        """Get a resource by name."""
        for resource in self.resources.values():
            if resource.name == name:
                return resource
        return None

    @monitor_performance("allocate_resource")
    def allocate(
        self,
        resource_id: str,
        requester_id: str,
        amount: float = 1.0,
        timeout: float | None = None,
    ) -> ResourceAllocation | None:
        """Allocate a resource."""
        with self._lock:
            resource = self.resources.get(resource_id)
            if not resource:
                logger.error("Cannot allocate: Resource %s not found", resource_id)
                return None

            if resource.status not in (
                ResourceStatus.AVAILABLE,
                ResourceStatus.ALLOCATED,
            ):
                logger.warning(
                    "Resource %s is %s", resource.name, resource.status.value
                )
                return None

            # Check capacity
            available = resource.capacity - resource.allocated
            if available < amount:
                logger.warning(
                    "Insufficient capacity for %s: requested %s, available %s",
                    resource.name,
                    amount,
                    available,
                )
                resource.status = (
                    ResourceStatus.BUSY if available <= 0 else ResourceStatus.ALLOCATED
                )
                return None

            # Create allocation
            allocation_id = str(uuid.uuid4())
            allocation = ResourceAllocation(
                allocation_id=allocation_id,
                resource_id=resource_id,
                requester_id=requester_id,
                amount=amount,
            )

            resource.allocations[allocation_id] = allocation
            resource.allocated += amount
            self.total_allocations += 1

            # Update status
            resource.status = (
                ResourceStatus.ALLOCATED
                if resource.allocated < resource.capacity
                else ResourceStatus.BUSY
            )

            logger.info(
                "Allocated %s %s of %s to %s",
                amount,
                resource.limits.unit,
                resource.name,
                requester_id,
            )
            return allocation

    @monitor_performance("release_resource")
    def release(self, allocation_id: str) -> bool:
        """Release an allocated resource."""
        with self._lock:
            # Search for the allocation across all resources
            target_resource = None
            target_allocation = None

            for resource in self.resources.values():
                if allocation_id in resource.allocations:
                    target_resource = resource
                    target_allocation = resource.allocations[allocation_id]
                    break

            if not target_resource or not target_allocation:
                logger.warning("Allocation %s not found", allocation_id)
                return False

            # Remove allocation
            amount = target_allocation.amount
            del target_resource.allocations[allocation_id]
            target_resource.allocated = max(0.0, target_resource.allocated - amount)

            # Update status
            if target_resource.allocated < target_resource.capacity:
                target_resource.status = (
                    ResourceStatus.AVAILABLE
                    if target_resource.allocated == 0
                    else ResourceStatus.ALLOCATED
                )

            logger.info(
                "Released %s %s of %s",
                amount,
                target_resource.limits.unit,
                target_resource.name,
            )
            return True

    @monitor_performance("get_usage")
    def get_usage(self, resource_id: str) -> ResourceUsage | None:
        """Get usage statistics for a resource."""
        resource = self.resources.get(resource_id)
        if not resource:
            return None

        return ResourceUsage(
            resource_id=resource.id,
            total_capacity=resource.capacity,
            allocated_amount=resource.allocated,
            available_amount=resource.capacity - resource.allocated,
            allocation_count=len(resource.allocations),
            utilization_percentage=(resource.allocated / resource.capacity * 100)
            if resource.capacity > 0
            else 0,
        )

    def list_resources(self, type_filter: ResourceType | None = None) -> list[Resource]:
        """List all resources, optionally filtered by type."""
        if type_filter:
            return [r for r in self.resources.values() if r.type == type_filter]
        return list(self.resources.values())

    def cleanup_expired_allocations(self) -> int:
        """Release all expired allocations."""
        now = datetime.now(UTC)
        cleaned_count = 0

        with self._lock:
            for resource in self.resources.values():
                expired_ids = []
                for alloc_id, alloc in resource.allocations.items():
                    if alloc.expires_at and alloc.expires_at < now:
                        expired_ids.append(alloc_id)

                for alloc_id in expired_ids:
                    if self.release(alloc_id):
                        cleaned_count += 1

        if cleaned_count > 0:
            logger.info("Cleaned up %s expired allocations", cleaned_count)

        return cleaned_count

    def allocate_resources(
        self,
        requester_id: str,
        requirements: dict[str, Any],
        timeout: float | None = None,
    ) -> list[ResourceAllocation] | None:
        """Legacy wrapper: allocate multiple resources from requirements dictionary."""
        allocations = []
        with self._lock:
            # First map requirements to known resources
            # requirements format: {"cpu": {"cores": 1}, "memory": {"gb": 1}}
            # We map "cpu" -> "sys-compute", "memory" -> "sys-memory"

            mapping = {"cpu": "sys-compute", "memory": "sys-memory"}
            for req_key, req_vals in requirements.items():
                resource_id = mapping.get(req_key, req_key)
                amount = float(
                    req_vals.get(
                        "cores", req_vals.get("gb", req_vals.get("amount", 1.0))
                    )
                )

                allocated = self.allocate(resource_id, requester_id, amount, timeout)
                if not allocated:
                    # Rollback all allocations if one fails
                    for alloc in allocations:
                        self.release(alloc.allocation_id)
                    return None

                allocations.append(allocated)

            return allocations

    def deallocate_resources(self, requester_id: str) -> bool:
        """Legacy wrapper: release all resources allocated to a requester."""
        with self._lock:
            released_any = False
            for resource in self.resources.values():
                allocs_to_release = []
                for alloc_id, alloc in resource.allocations.items():
                    if alloc.requester_id == requester_id:
                        allocs_to_release.append(alloc_id)

                for alloc_id in allocs_to_release:
                    self.release(alloc_id)
                    released_any = True

            return released_any


# Global resource manager instance
_resource_manager = None


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager
