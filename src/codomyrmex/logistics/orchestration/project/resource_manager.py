from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional
import json
import logging
import os
import time

from dataclasses import asdict, dataclass, field
from enum import Enum
import psutil
import threading

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.performance import monitor_performance






"""
Resource Management System for Codomyrmex

This module provides resource allocation, dependency management, and coordination
for tasks and workflows across the Codomyrmex ecosystem.
"""


# Import Codomyrmex modules
try:

    logger = get_logger(__name__)
except ImportError:

    logger = logging.getLogger(__name__)

try:

    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

    def monitor_performance(*args, **kwargs):
        """Decorator for performance monitoring (fallback)."""
        def decorator(func):
            return func

        return decorator


class ResourceType(Enum):
    """Types of resources in the system."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    FILE = "file"
    DATABASE = "database"
    EXTERNAL_API = "external_api"
    GPU = "gpu"
    QUEUE = "queue"
    LOCK = "lock"
    SEMAPHORE = "semaphore"


class ResourceStatus(Enum):
    """Resource availability status."""

    AVAILABLE = "available"
    IN_USE = "in_use"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


@dataclass
class ResourceLimits:
    """Resource usage limits and quotas."""

    max_cpu_cores: Optional[int] = None
    max_memory_gb: Optional[float] = None
    max_disk_gb: Optional[float] = None
    max_network_mbps: Optional[float] = None
    max_concurrent_users: Optional[int] = None
    max_requests_per_minute: Optional[int] = None
    timeout_seconds: Optional[int] = None


@dataclass
class ResourceUsage:
    """Represents usage statistics for a resource (compatibility type expected by tests)."""

    resource_id: str
    current_usage: float = 0.0
    peak_usage: float = 0.0
    average_usage: float = 0.0
    last_updated: float = field(default_factory=lambda: time.time())


@dataclass
class Resource:
    """Represents a system resource that can be allocated to tasks.

    This class provides a backward-compatible constructor that accepts
    both `resource_type` (tests) and `type` (internal code) and supports
    simple numeric `capacity` or dict-based capacity mappings.
    """

    id: str
    name: str
    type: ResourceType
    description: str = ""
    status: ResourceStatus = ResourceStatus.AVAILABLE
    capacity: dict[str, Any] = field(default_factory=dict)
    allocated: dict[str, Any] = field(default_factory=dict)
    limits: ResourceLimits = field(default_factory=ResourceLimits)
    total_allocations: int = 0
    total_usage_time: float = 0.0
    current_users: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __init__(
        self,
        id: str,
        name: str,
        resource_type: Optional[ResourceType] = None,
        type: Optional[ResourceType] = None,
        capacity: Optional[Any] = None,
        unit: Optional[str] = None,
        description: str = "",
        status: ResourceStatus = ResourceStatus.AVAILABLE,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs,
    ):
        # Accept resource_type (test usage) or type (internal usage)
        rt = resource_type or type
        if rt is None:
            raise ValueError("Resource requires a resource_type/type")

        # Normalize capacity: allow numeric -> {'units': value} or dict
        if capacity is None:
            cap = {}
        elif isinstance(capacity, dict):
            cap = capacity
        else:
            key = unit or "units"
            cap = {key: float(capacity)}

        # Assign fields
        self.id = id
        self.name = name
        self.type = rt
        self.description = description
        self.status = status
        self.capacity = cap
        self.allocated = {}
        self.limits = kwargs.get("limits", ResourceLimits())
        self.total_allocations = 0
        self.total_usage_time = 0.0
        self.current_users = set()
        self.metadata = metadata or {}
        self.tags = kwargs.get("tags", [])
        self.created_at = kwargs.get("created_at", datetime.now(timezone.utc))
        self.updated_at = kwargs.get("updated_at", datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        data = {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "status": self.status.value,
            "capacity": self.capacity,
            "allocated": self.allocated,
            "limits": (
                asdict(self.limits)
                if isinstance(self.limits, ResourceLimits)
                else self.limits
            ),
            "total_allocations": self.total_allocations,
            "total_usage_time": self.total_usage_time,
            "current_users": list(self.current_users),
            "metadata": self.metadata,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Resource":
        """
        Create a Resource instance from a dictionary.

        Args:
            data: Dictionary containing resource data.

        Returns:
            New Resource instance.
        """
        rt = (
            ResourceType(data.get("type"))
            if "type" in data
            else ResourceType(data.get("resource_type"))
        )
        inst = cls(
            id=data.get("id"),
            name=data.get("name"),
            resource_type=rt,
            capacity=data.get("capacity") or {},
            description=data.get("description", ""),
            status=(
                ResourceStatus(data.get("status"))
                if data.get("status")
                else ResourceStatus.AVAILABLE
            ),
            metadata=data.get("metadata", {}),
        )
        # Restore timestamps if present
        try:
            if "created_at" in data:
                inst.created_at = datetime.fromisoformat(data["created_at"])
            if "updated_at" in data:
                inst.updated_at = datetime.fromisoformat(data["updated_at"])
        except Exception:
            pass
        return inst

    def is_available(self) -> bool:
        return self.status == ResourceStatus.AVAILABLE

    def can_allocate(self, requested: dict[str, Any], user_id: str) -> bool:
        """
        Check if requested resources can be allocated.

        Args:
            requested: Dictionary of requested resources.
            user_id: ID of the user requesting resources.

        Returns:
            True if allocation is possible, False otherwise.
        """
        if not self.is_available():
            return False

        # concurrent users
        if (
            self.limits.max_concurrent_users
            and len(self.current_users) >= self.limits.max_concurrent_users
            and user_id not in self.current_users
        ):
            return False

        for key, amount in requested.items():
            if key in self.capacity:
                available = self.capacity[key] - self.allocated.get(key, 0)
                if amount > available:
                    return False
        return True

    def allocate(self, requested: dict[str, Any], user_id: str) -> bool:
        """
        Allocate resources to a user.

        Args:
            requested: Dictionary of requested resources.
            user_id: ID of the user requesting resources.

        Returns:
            True if allocation successful, False otherwise.
        """
        if not self.can_allocate(requested, user_id):
            return False
        for key, amount in requested.items():
            self.allocated[key] = self.allocated.get(key, 0) + amount
        self.current_users.add(user_id)
        self.total_allocations += 1
        self.updated_at = datetime.now(timezone.utc)
        return True

    def deallocate(self, released: dict[str, Any], user_id: str):
        """Deallocate resources and update user tracking.

        Args:
            released: Parameter for the operation.
            user_id: Unique identifier.
        """
        for key, amount in released.items():
            if key in self.allocated:
                self.allocated[key] = max(0, self.allocated[key] - amount)
        self.current_users.discard(user_id)
        self.updated_at = datetime.now(timezone.utc)

    def get_utilization(self) -> dict[str, float]:
        """
        Get current resource utilization percentage.

        Returns:
            Dictionary mapping resource keys to utilization percentage (0-100).
        """
        utilization = {}
        for key, capacity in self.capacity.items():
            try:
                if capacity and capacity > 0:
                    used = self.allocated.get(key, 0)
                    utilization[key] = (used / capacity) * 100.0
            except Exception:
                utilization[key] = 0.0
        return utilization


@dataclass
class ResourceAllocation:
    """Represents an active resource allocation."""

    id: str
    resource_id: str
    user_id: str  # Task ID or user ID
    allocated: dict[str, Any]
    allocated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if allocation has expired."""
        if self.expires_at:
            return datetime.now(timezone.utc) > self.expires_at
        return False


class ResourceManager:
    """Manages system resources and their allocation."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize the resource manager."""
        self.config_file = config_file or "resources.json"

        # Resource storage
        self.resources: dict[str, Resource] = {}
        self.allocations: dict[str, ResourceAllocation] = {}

        # Thread safety
        self.lock = threading.RLock()

        # Resource pools by type
        self.resource_pools: dict[ResourceType, list[str]] = defaultdict(list)

        # Load configuration and initialize default resources
        self.load_resources()
        if not self.resources:
            self._create_default_resources()

        # Start cleanup thread
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_expired_allocations, daemon=True
        )
        self.cleanup_thread.start()

        logger.info(f"ResourceManager initialized with {len(self.resources)} resources")

    def _create_default_resources(self):
        """Create default system resources."""
        # CPU resource
        cpu_resource = Resource(
            id="system_cpu",
            name="System CPU",
            type=ResourceType.CPU,
            description="System CPU cores",
            capacity={"cores": os.cpu_count() or 4},
            limits=ResourceLimits(max_cpu_cores=os.cpu_count() or 4),
        )
        self.add_resource(cpu_resource)

        # Memory resource
        try:

            memory_gb = psutil.virtual_memory().total / (1024**3)
        except ImportError:
            memory_gb = 8.0  # Default to 8GB

        memory_resource = Resource(
            id="system_memory",
            name="System Memory",
            type=ResourceType.MEMORY,
            description="System RAM",
            capacity={"gb": memory_gb},
            limits=ResourceLimits(max_memory_gb=memory_gb * 0.8),  # Reserve 20%
        )
        self.add_resource(memory_resource)

        # Disk resource
        try:
            disk_usage = os.statvfs("/")
            disk_gb = (disk_usage.f_bavail * disk_usage.f_frsize) / (1024**3)
        except (AttributeError, OSError):
            disk_gb = 100.0  # Default to 100GB

        disk_resource = Resource(
            id="system_disk",
            name="System Disk",
            type=ResourceType.DISK,
            description="System disk space",
            capacity={"gb": disk_gb},
            limits=ResourceLimits(max_disk_gb=disk_gb * 0.9),  # Reserve 10%
        )
        self.add_resource(disk_resource)

        # Network resource
        network_resource = Resource(
            id="system_network",
            name="System Network",
            type=ResourceType.NETWORK,
            description="Network bandwidth",
            capacity={"mbps": 1000},  # Default to 1Gbps
            limits=ResourceLimits(max_network_mbps=1000),
        )
        self.add_resource(network_resource)

        # External API quota (example)
        api_resource = Resource(
            id="openai_api",
            name="OpenAI API",
            type=ResourceType.EXTERNAL_API,
            description="OpenAI API quota",
            capacity={"requests_per_minute": 60, "tokens_per_minute": 10000},
            limits=ResourceLimits(max_requests_per_minute=60, timeout_seconds=30),
        )
        self.add_resource(api_resource)

    def add_resource(self, resource: Resource) -> bool:
        """Add a resource to the manager."""
        with self.lock:
            if resource.id in self.resources:
                logger.warning(f"Resource {resource.id} already exists")
                return False

            self.resources[resource.id] = resource
            self.resource_pools[resource.type].append(resource.id)

            logger.info(f"Added resource: {resource.name} ({resource.id})")
            return True

    def remove_resource(self, resource_id: str) -> bool:
        """Remove a resource from the manager."""
        with self.lock:
            resource = self.resources.get(resource_id)
            if not resource:
                return False

            # Check if resource is in use
            if resource.current_users:
                logger.error(
                    f"Cannot remove resource {resource_id} - currently in use by {resource.current_users}"
                )
                return False

            # Remove from pools and storage
            self.resource_pools[resource.type].remove(resource_id)
            del self.resources[resource_id]

            # Remove related allocations
            to_remove = [
                aid
                for aid, alloc in self.allocations.items()
                if alloc.resource_id == resource_id
            ]
            for aid in to_remove:
                del self.allocations[aid]

            logger.info(f"Removed resource: {resource_id}")
            return True

    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get a resource by ID."""
        with self.lock:
            return self.resources.get(resource_id)

    def list_resources(
        self,
        resource_type: Optional[ResourceType] = None,
        status: Optional[ResourceStatus] = None,
    ) -> list[Resource]:
        """List resources, optionally filtered by type and status."""
        with self.lock:
            resources = list(self.resources.values())

            if resource_type:
                resources = [r for r in resources if r.type == resource_type]

            if status:
                resources = [r for r in resources if r.status == status]

            return resources

    @monitor_performance(function_name="allocate_resources")
    def allocate_resources(
        self,
        user_id: str,
        requirements: dict[str, dict[str, Any]],
        timeout: Optional[int] = None,
    ) -> Optional[dict[str, str]]:
        """
        Allocate resources to a user based on requirements.

        Args:
            user_id: Identifier for the user/task requesting resources
            requirements: Dict mapping resource types to required amounts
                         e.g., {'cpu': {'cores': 2}, 'memory': {'gb': 4}}
            timeout: Optional timeout for allocation in seconds

        Returns:
            Dict mapping requirement keys to allocated resource IDs, or None if failed
        """
        allocations = {}
        allocated_resources = []

        try:
            with self.lock:
                # Find suitable resources for each requirement
                for req_key, req_spec in requirements.items():
                    resource_type = (
                        ResourceType(req_key) if isinstance(req_key, str) else req_key
                    )

                    # Find best resource for this requirement
                    suitable_resources = [
                        r
                        for r in self.resources.values()
                        if r.type == resource_type and r.can_allocate(req_spec, user_id)
                    ]

                    if not suitable_resources:
                        # No suitable resource found
                        logger.warning(
                            f"No suitable {resource_type.value} resource found for user {user_id}"
                        )
                        self._rollback_allocations(allocated_resources, user_id)
                        return None

                    # Choose resource with best fit (lowest utilization)
                    best_resource = min(
                        suitable_resources,
                        key=lambda r: sum(r.get_utilization().values()),
                    )

                    # Allocate resource
                    if best_resource.allocate(req_spec, user_id):
                        allocations[req_key] = best_resource.id
                        allocated_resources.append((best_resource, req_spec))

                        # Create allocation record
                        alloc_id = (
                            f"{user_id}_{best_resource.id}_{len(self.allocations)}"
                        )
                        allocation = ResourceAllocation(
                            id=alloc_id,
                            resource_id=best_resource.id,
                            user_id=user_id,
                            allocated=req_spec,
                            expires_at=(
                                datetime.now(timezone.utc)
                                + timezone.utc.utcoffset(None)
                                if timeout
                                else None
                            ),
                        )
                        self.allocations[alloc_id] = allocation

                        logger.debug(
                            f"Allocated {resource_type.value} resource {best_resource.id} to {user_id}"
                        )
                    else:
                        # Allocation failed
                        self._rollback_allocations(allocated_resources, user_id)
                        return None

                logger.info(
                    f"Successfully allocated {len(allocations)} resources to {user_id}"
                )
                return allocations

        except Exception as e:
            logger.error(f"Error allocating resources for {user_id}: {e}")
            self._rollback_allocations(allocated_resources, user_id)
            return None

    def _rollback_allocations(self, allocated_resources: list[tuple], user_id: str):
        """Rollback partial allocations on failure."""
        for resource, allocation in allocated_resources:
            resource.deallocate(allocation, user_id)

    def deallocate_resources(
        self, user_id: str, allocation_ids: Optional[list[str]] = None
    ) -> bool:
        """
        Deallocate resources for a user.

        Args:
            user_id: User identifier
            allocation_ids: Specific allocation IDs to release, or None for all

        Returns:
            True if successful
        """
        with self.lock:
            # Find allocations to release
            if allocation_ids:
                to_release = [aid for aid in allocation_ids if aid in self.allocations]
            else:
                to_release = [
                    aid
                    for aid, alloc in self.allocations.items()
                    if alloc.user_id == user_id
                ]

            released_count = 0
            for alloc_id in to_release:
                allocation = self.allocations[alloc_id]
                resource = self.resources.get(allocation.resource_id)

                if resource:
                    resource.deallocate(allocation.allocated, user_id)
                    released_count += 1

                del self.allocations[alloc_id]

            logger.info(f"Deallocated {released_count} resources for {user_id}")
            return released_count > 0

    def get_resource_usage(self, resource_id: Optional[str] = None) -> dict[str, Any]:
        """Get resource usage statistics."""
        with self.lock:
            if resource_id:
                resource = self.resources.get(resource_id)
                if not resource:
                    return {}

                return {
                    "resource_id": resource_id,
                    "name": resource.name,
                    "type": resource.type.value,
                    "status": resource.status.value,
                    "capacity": resource.capacity,
                    "allocated": resource.allocated,
                    "utilization": resource.get_utilization(),
                    "current_users": len(resource.current_users),
                    "total_allocations": resource.total_allocations,
                }
            else:
                # System-wide usage
                usage = {
                    "total_resources": len(self.resources),
                    "total_allocations": len(self.allocations),
                    "resources_by_type": {},
                    "utilization_summary": {},
                }

                for resource_type in ResourceType:
                    type_resources = [
                        r for r in self.resources.values() if r.type == resource_type
                    ]
                    usage["resources_by_type"][resource_type.value] = len(
                        type_resources
                    )

                    if type_resources:
                        avg_utilization = sum(
                            sum(r.get_utilization().values())
                            / max(1, len(r.get_utilization()))
                            for r in type_resources
                        ) / len(type_resources)
                        usage["utilization_summary"][resource_type.value] = round(
                            avg_utilization, 2
                        )

                return usage

    def get_user_allocations(self, user_id: str) -> list[dict[str, Any]]:
        """Get all allocations for a specific user."""
        with self.lock:
            user_allocations = []
            for allocation in self.allocations.values():
                if allocation.user_id == user_id:
                    resource = self.resources.get(allocation.resource_id)
                    user_allocations.append(
                        {
                            "allocation_id": allocation.id,
                            "resource_id": allocation.resource_id,
                            "resource_name": resource.name if resource else "Unknown",
                            "resource_type": (
                                resource.type.value if resource else "Unknown"
                            ),
                            "allocated": allocation.allocated,
                            "allocated_at": allocation.allocated_at.isoformat(),
                            "expires_at": (
                                allocation.expires_at.isoformat()
                                if allocation.expires_at
                                else None
                            ),
                        }
                    )
            return user_allocations

    def _cleanup_expired_allocations(self):
        """Background thread to cleanup expired allocations."""
        while True:
            try:
                with self.lock:
                    expired_allocations = [
                        aid
                        for aid, alloc in self.allocations.items()
                        if alloc.is_expired()
                    ]

                    for alloc_id in expired_allocations:
                        allocation = self.allocations[alloc_id]
                        resource = self.resources.get(allocation.resource_id)

                        if resource:
                            resource.deallocate(
                                allocation.allocated, allocation.user_id
                            )

                        del self.allocations[alloc_id]
                        logger.debug(f"Cleaned up expired allocation: {alloc_id}")

                # Sleep for cleanup interval
                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in resource cleanup: {e}")
                time.sleep(60)

    def save_resources(self):
        """Save resource configuration to file."""
        try:
            config = {
                "resources": {
                    rid: resource.to_dict() for rid, resource in self.resources.items()
                },
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save resources: {e}")

    def load_resources(self):
        """Load resource configuration from file."""
        if not os.path.exists(self.config_file):
            return

        try:
            with open(self.config_file) as f:
                config = json.load(f)

            for resource_data in config.get("resources", {}).values():
                resource = Resource.from_dict(resource_data)
                self.resources[resource.id] = resource
                self.resource_pools[resource.type].append(resource.id)

        except Exception as e:
            logger.error(f"Failed to load resources: {e}")

    def health_check(self) -> dict[str, Any]:
        """Perform health check on all resources."""
        with self.lock:
            health = {
                "overall_status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "resources": {},
                "issues": [],
            }

            for resource in self.resources.values():
                resource_health = {
                    "status": resource.status.value,
                    "utilization": resource.get_utilization(),
                    "users": len(resource.current_users),
                    "healthy": True,
                }

                # Check for issues
                utilization = resource.get_utilization()
                if any(util > 90 for util in utilization.values()):
                    resource_health["healthy"] = False
                    health["issues"].append(
                        f"Resource {resource.name} is over 90% utilized"
                    )

                if resource.status != ResourceStatus.AVAILABLE:
                    resource_health["healthy"] = False
                    health["issues"].append(
                        f"Resource {resource.name} is not available"
                    )

                health["resources"][resource.id] = resource_health

            if health["issues"]:
                health["overall_status"] = (
                    "degraded" if len(health["issues"]) < 5 else "unhealthy"
                )

            return health


# Global resource manager instance
_resource_manager = None


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager
