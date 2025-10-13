"""
Comprehensive unit tests for ResourceManager.

This module contains extensive unit tests for the ResourceManager class,
covering all public methods, error conditions, and edge cases.
"""

import pytest
import threading
import time
from unittest.mock import Mock, patch, MagicMock

from codomyrmex.project_orchestration.resource_manager import (
    ResourceManager,
    Resource,
)
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)
from codomyrmex.project_orchestration.resource_manager import (
    ResourceType,
    ResourceStatus,
    ResourceAllocation,
    ResourceUsage,
)


class TestResource:
    """Test cases for Resource dataclass."""

    def test_resource_creation(self):
        """Test basic Resource creation."""
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
            unit="cores",
            status=ResourceStatus.AVAILABLE,
            metadata={"cores": 1, "frequency": "2.4GHz"},
        )

        assert resource.id == "cpu_1"
        assert resource.name == "CPU Core 1"
        assert resource.resource_type == ResourceType.CPU
        assert resource.capacity == 100.0
        assert resource.unit == "cores"
        assert resource.status == ResourceStatus.AVAILABLE
        assert resource.metadata == {"cores": 1, "frequency": "2.4GHz"}

    def test_resource_defaults(self):
        """Test Resource with default values."""
        resource = Resource(
            id="mem_1",
            name="Memory 1",
            resource_type=ResourceType.MEMORY,
            capacity=1024.0,
        )

        assert resource.id == "mem_1"
        assert resource.name == "Memory 1"
        assert resource.resource_type == ResourceType.MEMORY
        assert resource.capacity == 1024.0
        assert resource.unit == "units"
        assert resource.status == ResourceStatus.AVAILABLE
        assert resource.metadata == {}

    def test_resource_serialization(self):
        """Test Resource serialization to/from dictionary."""
        resource = Resource(
            id="disk_1",
            name="Disk Storage 1",
            resource_type=ResourceType.DISK,
            capacity=1000.0,
            unit="GB",
            status=ResourceStatus.IN_USE,
            metadata={"type": "SSD", "interface": "SATA"},
        )

        # Test to_dict
        resource_dict = resource.to_dict()
        assert resource_dict["id"] == "disk_1"
        assert resource_dict["name"] == "Disk Storage 1"
        assert resource_dict["resource_type"] == ResourceType.DISK.value
        assert resource_dict["capacity"] == 1000.0
        assert resource_dict["unit"] == "GB"
        assert resource_dict["status"] == ResourceStatus.IN_USE.value
        assert resource_dict["metadata"] == {"type": "SSD", "interface": "SATA"}

        # Test from_dict
        restored_resource = Resource.from_dict(resource_dict)
        assert restored_resource.id == "disk_1"
        assert restored_resource.name == "Disk Storage 1"
        assert restored_resource.resource_type == ResourceType.DISK
        assert restored_resource.capacity == 1000.0
        assert restored_resource.unit == "GB"
        assert restored_resource.status == ResourceStatus.IN_USE
        assert restored_resource.metadata == {"type": "SSD", "interface": "SATA"}


class TestResourceAllocation:
    """Test cases for ResourceAllocation dataclass."""

    def test_resource_allocation_creation(self):
        """Test basic ResourceAllocation creation."""
        allocation = ResourceAllocation(
            resource_id="cpu_1",
            task_id="task_1",
            allocated_amount=50.0,
            allocation_time=time.time(),
            timeout=300,
        )

        assert allocation.resource_id == "cpu_1"
        assert allocation.task_id == "task_1"
        assert allocation.allocated_amount == 50.0
        assert allocation.allocation_time is not None
        assert allocation.timeout == 300
        assert allocation.status == ResourceStatus.IN_USE

    def test_resource_allocation_defaults(self):
        """Test ResourceAllocation with default values."""
        allocation = ResourceAllocation(
            resource_id="mem_1", task_id="task_1", allocated_amount=100.0
        )

        assert allocation.resource_id == "mem_1"
        assert allocation.task_id == "task_1"
        assert allocation.allocated_amount == 100.0
        assert allocation.allocation_time is not None
        assert allocation.timeout is None
        assert allocation.status == ResourceStatus.IN_USE


class TestResourceUsage:
    """Test cases for ResourceUsage dataclass."""

    def test_resource_usage_creation(self):
        """Test basic ResourceUsage creation."""
        usage = ResourceUsage(
            resource_id="cpu_1",
            current_usage=75.0,
            peak_usage=90.0,
            average_usage=60.0,
            last_updated=time.time(),
        )

        assert usage.resource_id == "cpu_1"
        assert usage.current_usage == 75.0
        assert usage.peak_usage == 90.0
        assert usage.average_usage == 60.0
        assert usage.last_updated is not None

    def test_resource_usage_defaults(self):
        """Test ResourceUsage with default values."""
        usage = ResourceUsage(resource_id="mem_1")

        assert usage.resource_id == "mem_1"
        assert usage.current_usage == 0.0
        assert usage.peak_usage == 0.0
        assert usage.average_usage == 0.0
        assert usage.last_updated is not None


class TestResourceManager:
    """Test cases for ResourceManager class."""

    @pytest.fixture
    def resource_manager(self):
        """Create a ResourceManager instance for testing."""
        return ResourceManager()

    def test_resource_manager_initialization(self):
        """Test ResourceManager initialization."""
        manager = ResourceManager()

        assert manager.resources == {}
        assert manager.allocations == {}
        assert manager.usage_stats == {}
        assert manager.lock is not None
        assert manager.logger is not None

    def test_add_resource(self, resource_manager):
        """Test adding resource to manager."""
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )

        result = resource_manager.add_resource(resource)

        assert result is True
        assert "cpu_1" in resource_manager.resources
        assert resource_manager.resources["cpu_1"] == resource

    def test_add_resource_duplicate(self, resource_manager):
        """Test adding duplicate resource."""
        resource1 = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )

        resource2 = Resource(
            id="cpu_1",
            name="CPU Core 2",
            resource_type=ResourceType.CPU,
            capacity=200.0,
        )

        # Add first resource
        result1 = resource_manager.add_resource(resource1)
        assert result1 is True

        # Try to add duplicate
        result2 = resource_manager.add_resource(resource2)
        assert result2 is False
        assert (
            resource_manager.resources["cpu_1"] == resource1
        )  # Original should remain

    def test_get_resource(self, resource_manager):
        """Test getting resource by ID."""
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )

        resource_manager.add_resource(resource)

        retrieved_resource = resource_manager.get_resource("cpu_1")
        assert retrieved_resource == resource

        # Test non-existent resource
        non_existent = resource_manager.get_resource("nonexistent")
        assert non_existent is None

    def test_list_resources(self, resource_manager):
        """Test listing resources."""
        # Add multiple resources
        cpu_resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )

        mem_resource = Resource(
            id="mem_1",
            name="Memory 1",
            resource_type=ResourceType.MEMORY,
            capacity=1024.0,
        )

        resource_manager.add_resource(cpu_resource)
        resource_manager.add_resource(mem_resource)

        resources = resource_manager.list_resources()

        assert len(resources) == 2
        assert "cpu_1" in resources
        assert "mem_1" in resources

    def test_list_resources_by_type(self, resource_manager):
        """Test listing resources by type."""
        # Add resources of different types
        cpu_resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )

        mem_resource = Resource(
            id="mem_1",
            name="Memory 1",
            resource_type=ResourceType.MEMORY,
            capacity=1024.0,
        )

        resource_manager.add_resource(cpu_resource)
        resource_manager.add_resource(mem_resource)

        # List CPU resources
        cpu_resources = resource_manager.list_resources(resource_type=ResourceType.CPU)
        assert len(cpu_resources) == 1
        assert cpu_resources[0].id == "cpu_1"

        # List memory resources
        mem_resources = resource_manager.list_resources(
            resource_type=ResourceType.MEMORY
        )
        assert len(mem_resources) == 1
        assert mem_resources[0].id == "mem_1"

    def test_allocate_resource_success(self, resource_manager):
        """Test successful resource allocation."""
        # Add resource
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )
        resource_manager.add_resource(resource)

        # Allocate resource
        allocation = resource_manager.allocate_resource(
            resource_id="cpu_1", task_id="task_1", amount=50.0
        )

        assert allocation is not None
        assert allocation.resource_id == "cpu_1"
        assert allocation.task_id == "task_1"
        assert allocation.allocated_amount == 50.0
        assert allocation.status == ResourceStatus.IN_USE

        # Check allocation is tracked
        assert "task_1" in resource_manager.allocations
        assert resource_manager.allocations["task_1"]["cpu_1"] == allocation

    def test_allocate_resource_insufficient_capacity(self, resource_manager):
        """Test resource allocation with insufficient capacity."""
        # Add resource with limited capacity
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )
        resource_manager.add_resource(resource)

        # Try to allocate more than available
        allocation = resource_manager.allocate_resource(
            resource_id="cpu_1", task_id="task_1", amount=150.0
        )

        assert allocation is None

    def test_allocate_resource_nonexistent(self, resource_manager):
        """Test allocating non-existent resource."""
        allocation = resource_manager.allocate_resource(
            resource_id="nonexistent", task_id="task_1", amount=50.0
        )

        assert allocation is None

    def test_release_resource(self, resource_manager):
        """Test releasing resource allocation."""
        # Add and allocate resource
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )
        resource_manager.add_resource(resource)

        allocation = resource_manager.allocate_resource(
            resource_id="cpu_1", task_id="task_1", amount=50.0
        )

        assert allocation is not None

        # Release resource
        result = resource_manager.release_resource("task_1", "cpu_1")

        assert result is True
        assert "task_1" not in resource_manager.allocations

    def test_release_resource_nonexistent(self, resource_manager):
        """Test releasing non-existent allocation."""
        result = resource_manager.release_resource("task_1", "cpu_1")

        assert result is False

    def test_get_available_capacity(self, resource_manager):
        """Test getting available resource capacity."""
        # Add resource
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )
        resource_manager.add_resource(resource)

        # Initially all capacity is available
        available = resource_manager.get_available_capacity("cpu_1")
        assert available == 100.0

        # Allocate some capacity
        resource_manager.allocate_resource("cpu_1", "task_1", 30.0)

        # Check available capacity
        available = resource_manager.get_available_capacity("cpu_1")
        assert available == 70.0

    def test_get_available_capacity_nonexistent(self, resource_manager):
        """Test getting available capacity for non-existent resource."""
        available = resource_manager.get_available_capacity("nonexistent")

        assert available == 0.0

    def test_get_resource_usage(self, resource_manager):
        """Test getting resource usage statistics."""
        # Add resource
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )
        resource_manager.add_resource(resource)

        # Allocate some capacity
        resource_manager.allocate_resource("cpu_1", "task_1", 50.0)

        # Get usage statistics
        usage = resource_manager.get_resource_usage("cpu_1")

        assert usage is not None
        assert usage.resource_id == "cpu_1"
        assert usage.current_usage == 50.0
        assert usage.peak_usage == 50.0
        assert usage.average_usage == 50.0

    def test_get_resource_usage_nonexistent(self, resource_manager):
        """Test getting usage for non-existent resource."""
        usage = resource_manager.get_resource_usage("nonexistent")

        assert usage is None

    def test_get_all_usage_stats(self, resource_manager):
        """Test getting all resource usage statistics."""
        # Add multiple resources
        cpu_resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )

        mem_resource = Resource(
            id="mem_1",
            name="Memory 1",
            resource_type=ResourceType.MEMORY,
            capacity=1024.0,
        )

        resource_manager.add_resource(cpu_resource)
        resource_manager.add_resource(mem_resource)

        # Allocate some capacity
        resource_manager.allocate_resource("cpu_1", "task_1", 50.0)
        resource_manager.allocate_resource("mem_1", "task_2", 256.0)

        # Get all usage stats
        all_usage = resource_manager.get_all_usage_stats()

        assert len(all_usage) == 2
        assert "cpu_1" in all_usage
        assert "mem_1" in all_usage
        assert all_usage["cpu_1"].current_usage == 50.0
        assert all_usage["mem_1"].current_usage == 256.0

    def test_cleanup_expired_allocations(self, resource_manager):
        """Test cleaning up expired allocations."""
        # Add resource
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )
        resource_manager.add_resource(resource)

        # Create allocation with short timeout
        allocation = ResourceAllocation(
            resource_id="cpu_1",
            task_id="task_1",
            allocated_amount=50.0,
            allocation_time=time.time() - 10,  # 10 seconds ago
            timeout=5,  # 5 second timeout
        )

        resource_manager.allocations["task_1"] = {"cpu_1": allocation}

        # Cleanup expired allocations
        cleaned = resource_manager.cleanup_expired_allocations()

        assert cleaned == 1
        assert "task_1" not in resource_manager.allocations

    def test_cleanup_expired_allocations_none_expired(self, resource_manager):
        """Test cleanup when no allocations are expired."""
        # Add resource
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )
        resource_manager.add_resource(resource)

        # Create allocation with long timeout
        allocation = ResourceAllocation(
            resource_id="cpu_1",
            task_id="task_1",
            allocated_amount=50.0,
            allocation_time=time.time(),
            timeout=300,  # 5 minute timeout
        )

        resource_manager.allocations["task_1"] = {"cpu_1": allocation}

        # Cleanup expired allocations
        cleaned = resource_manager.cleanup_expired_allocations()

        assert cleaned == 0
        assert "task_1" in resource_manager.allocations

    def test_get_resource_summary(self, resource_manager):
        """Test getting resource summary."""
        # Add multiple resources
        cpu_resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )

        mem_resource = Resource(
            id="mem_1",
            name="Memory 1",
            resource_type=ResourceType.MEMORY,
            capacity=1024.0,
        )

        resource_manager.add_resource(cpu_resource)
        resource_manager.add_resource(mem_resource)

        # Allocate some capacity
        resource_manager.allocate_resource("cpu_1", "task_1", 50.0)
        resource_manager.allocate_resource("mem_1", "task_2", 256.0)

        # Get summary
        summary = resource_manager.get_resource_summary()

        assert "total_resources" in summary
        assert "total_capacity" in summary
        assert "total_allocated" in summary
        assert "total_available" in summary
        assert "resource_types" in summary
        assert "active_allocations" in summary

        assert summary["total_resources"] == 2
        assert summary["total_capacity"] == 1124.0
        assert summary["total_allocated"] == 306.0
        assert summary["total_available"] == 818.0
        assert summary["active_allocations"] == 2


class TestResourceManagerConcurrency:
    """Test cases for ResourceManager concurrency."""

    def test_concurrent_allocations(self):
        """Test concurrent resource allocations."""
        manager = ResourceManager()

        # Add resource
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )
        manager.add_resource(resource)

        # Function to allocate resource
        def allocate_resource(task_id, amount):
            return manager.allocate_resource("cpu_1", task_id, amount)

        # Create multiple threads
        threads = []
        results = {}

        def worker(task_id, amount):
            results[task_id] = allocate_resource(task_id, amount)

        # Start multiple threads
        for i in range(5):
            thread = threading.Thread(target=worker, args=(f"task_{i}", 20.0))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Check results
        successful_allocations = sum(
            1 for result in results.values() if result is not None
        )
        assert successful_allocations == 5  # All should succeed with 20.0 each

        # Check total allocated capacity
        available = manager.get_available_capacity("cpu_1")
        assert available == 0.0  # All capacity should be allocated

    def test_concurrent_releases(self):
        """Test concurrent resource releases."""
        manager = ResourceManager()

        # Add resource
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )
        manager.add_resource(resource)

        # Allocate resources first
        for i in range(5):
            manager.allocate_resource("cpu_1", f"task_{i}", 20.0)

        # Function to release resource
        def release_resource(task_id):
            return manager.release_resource(task_id, "cpu_1")

        # Create multiple threads
        threads = []
        results = {}

        def worker(task_id):
            results[task_id] = release_resource(task_id)

        # Start multiple threads
        for i in range(5):
            thread = threading.Thread(target=worker, args=(f"task_{i}",))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Check results
        successful_releases = sum(1 for result in results.values() if result is True)
        assert successful_releases == 5  # All should succeed

        # Check total available capacity
        available = manager.get_available_capacity("cpu_1")
        assert available == 100.0  # All capacity should be available


class TestResourceManagerIntegration:
    """Integration tests for ResourceManager."""

    def test_complex_resource_scenario(self):
        """Test complex resource allocation scenario."""
        manager = ResourceManager()

        # Add multiple resources
        cpu_resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )

        mem_resource = Resource(
            id="mem_1",
            name="Memory 1",
            resource_type=ResourceType.MEMORY,
            capacity=1024.0,
        )

        disk_resource = Resource(
            id="disk_1",
            name="Disk Storage 1",
            resource_type=ResourceType.DISK,
            capacity=1000.0,
        )

        manager.add_resource(cpu_resource)
        manager.add_resource(mem_resource)
        manager.add_resource(disk_resource)

        # Allocate resources for multiple tasks
        task1_cpu = manager.allocate_resource("cpu_1", "task_1", 30.0)
        task1_mem = manager.allocate_resource("mem_1", "task_1", 256.0)

        task2_cpu = manager.allocate_resource("cpu_1", "task_2", 40.0)
        task2_disk = manager.allocate_resource("disk_1", "task_2", 500.0)

        task3_mem = manager.allocate_resource("mem_1", "task_3", 512.0)
        task3_disk = manager.allocate_resource("disk_1", "task_3", 300.0)

        # All allocations should succeed
        assert task1_cpu is not None
        assert task1_mem is not None
        assert task2_cpu is not None
        assert task2_disk is not None
        assert task3_mem is not None
        assert task3_disk is not None

        # Check available capacities
        assert manager.get_available_capacity("cpu_1") == 30.0
        assert manager.get_available_capacity("mem_1") == 256.0
        assert manager.get_available_capacity("disk_1") == 200.0

        # Release some resources
        manager.release_resource("task_1", "cpu_1")
        manager.release_resource("task_2", "disk_1")

        # Check updated capacities
        assert manager.get_available_capacity("cpu_1") == 60.0
        assert manager.get_available_capacity("disk_1") == 700.0

        # Get summary
        summary = manager.get_resource_summary()
        assert summary["total_resources"] == 3
        assert summary["active_allocations"] == 4  # 2 CPU + 2 memory + 1 disk

    def test_resource_cleanup_workflow(self):
        """Test resource cleanup workflow."""
        manager = ResourceManager()

        # Add resource
        resource = Resource(
            id="cpu_1",
            name="CPU Core 1",
            resource_type=ResourceType.CPU,
            capacity=100.0,
        )
        manager.add_resource(resource)

        # Create allocation with short timeout
        allocation = ResourceAllocation(
            resource_id="cpu_1",
            task_id="task_1",
            allocated_amount=50.0,
            allocation_time=time.time() - 10,  # 10 seconds ago
            timeout=5,  # 5 second timeout
        )

        manager.allocations["task_1"] = {"cpu_1": allocation}

        # Verify allocation exists
        assert "task_1" in manager.allocations
        assert manager.get_available_capacity("cpu_1") == 50.0

        # Cleanup expired allocations
        cleaned = manager.cleanup_expired_allocations()

        # Verify cleanup
        assert cleaned == 1
        assert "task_1" not in manager.allocations
        assert manager.get_available_capacity("cpu_1") == 100.0


if __name__ == "__main__":
    pytest.main([__file__])
