"""Performance and benchmarking tests for Physical Management module."""

import pytest
import time
import statistics
from typing import List, Dict, Any
from codomyrmex.physical_management import (
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

    PhysicalObjectManager,
    ObjectType,
    ObjectStatus,
    PhysicalObject,
    MaterialType,
    SpatialIndex,
    ObjectRegistry,
    EventType,
)


class PerformanceMetrics:
    """Helper class for collecting performance metrics."""

    def __init__(self):
        self.execution_times: List[float] = []
        self.memory_usage: List[int] = []

    def add_timing(self, execution_time: float):
        """Add execution time measurement."""
        self.execution_times.append(execution_time)

    def get_statistics(self) -> Dict[str, float]:
        """Get timing statistics."""
        if not self.execution_times:
            return {}

        return {
            "min": min(self.execution_times),
            "max": max(self.execution_times),
            "mean": statistics.mean(self.execution_times),
            "median": statistics.median(self.execution_times),
            "stdev": (
                statistics.stdev(self.execution_times)
                if len(self.execution_times) > 1
                else 0.0
            ),
        }


class TestObjectCreationPerformance:
    """Test performance of object creation and management."""

    def test_bulk_object_creation_performance(self):
        """Test performance of creating many objects."""
        manager = PhysicalObjectManager()
        metrics = PerformanceMetrics()

        # Test creating 1000 objects
        num_objects = 1000

        start_time = time.time()
        for i in range(num_objects):
            manager.create_object(
                f"obj_{i}",
                f"Object {i}",
                ObjectType.SENSOR,
                x=i % 100,
                y=(i // 100) % 100,
                z=i // 10000,
                material=MaterialType.METAL,
            )
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_object = total_time / num_objects

        # Assert reasonable performance (less than 1ms per object)
        assert (
            avg_time_per_object < 0.001
        ), f"Object creation too slow: {avg_time_per_object:.4f}s per object"

        # Verify all objects were created
        assert len(manager.registry.objects) == num_objects

        print(
            f"Created {num_objects} objects in {total_time:.3f}s ({avg_time_per_object*1000:.2f}ms per object)"
        )

    def test_object_lookup_performance(self):
        """Test performance of object lookups."""
        manager = PhysicalObjectManager()

        # Create test objects
        num_objects = 10000
        for i in range(num_objects):
            manager.create_object(
                f"obj_{i}",
                f"Object {i}",
                ObjectType.SENSOR,
                x=i % 100,
                y=(i // 100) % 100,
                z=0,
            )

        # Test lookup performance
        lookup_ids = [
            f"obj_{i}" for i in range(0, num_objects, 100)
        ]  # Every 100th object

        start_time = time.time()
        for obj_id in lookup_ids:
            obj = manager.registry.get_object(obj_id)
            assert obj is not None
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_lookup = total_time / len(lookup_ids)

        # Assert reasonable performance (less than 0.1ms per lookup)
        assert (
            avg_time_per_lookup < 0.0001
        ), f"Object lookup too slow: {avg_time_per_lookup:.6f}s per lookup"

        print(
            f"Performed {len(lookup_ids)} lookups in {total_time:.4f}s ({avg_time_per_lookup*1000000:.1f}μs per lookup)"
        )


class TestSpatialIndexPerformance:
    """Test performance of spatial indexing operations."""

    def test_spatial_index_insertion_performance(self):
        """Test performance of spatial index insertions."""
        index = SpatialIndex(grid_size=10.0)
        metrics = PerformanceMetrics()

        num_objects = 50000

        # Measure insertion time
        start_time = time.time()
        for i in range(num_objects):
            x = (i * 17) % 1000  # Distribute objects across space
            y = (i * 23) % 1000
            z = (i * 31) % 100
            index.add_object(f"obj_{i}", x, y, z)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_insertion = total_time / num_objects

        # Assert reasonable performance
        assert (
            avg_time_per_insertion < 0.0001
        ), f"Spatial index insertion too slow: {avg_time_per_insertion:.6f}s per insertion"

        print(
            f"Inserted {num_objects} objects into spatial index in {total_time:.3f}s ({avg_time_per_insertion*1000000:.1f}μs per insertion)"
        )

    def test_spatial_query_performance(self):
        """Test performance of spatial queries."""
        index = SpatialIndex(grid_size=10.0)

        # Insert test objects
        num_objects = 10000
        for i in range(num_objects):
            x = (i * 17) % 500
            y = (i * 23) % 500
            z = (i * 31) % 50
            index.add_object(f"obj_{i}", x, y, z)

        # Perform spatial queries
        num_queries = 1000
        query_radius = 50.0

        start_time = time.time()
        for i in range(num_queries):
            x = (i * 37) % 500
            y = (i * 41) % 500
            z = (i * 43) % 50
            nearby = index.get_nearby_cells(x, y, z, query_radius)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_query = total_time / num_queries

        # Assert reasonable performance
        assert (
            avg_time_per_query < 0.01
        ), f"Spatial query too slow: {avg_time_per_query:.4f}s per query"

        print(
            f"Performed {num_queries} spatial queries in {total_time:.3f}s ({avg_time_per_query*1000:.2f}ms per query)"
        )


class TestDistanceCalculationPerformance:
    """Test performance of distance calculations."""

    def test_distance_calculation_performance(self):
        """Test performance of distance calculations between objects."""
        manager = PhysicalObjectManager()

        # Create test objects
        num_objects = 1000
        objects = []
        for i in range(num_objects):
            obj = manager.create_object(
                f"obj_{i}",
                f"Object {i}",
                ObjectType.SENSOR,
                x=i % 100,
                y=(i // 100) % 100,
                z=0,
            )
            objects.append(obj)

        # Test distance calculations
        num_calculations = 10000

        start_time = time.time()
        for i in range(num_calculations):
            obj1 = objects[i % len(objects)]
            obj2 = objects[(i + 1) % len(objects)]
            distance = obj1.distance_to(obj2)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_calculation = total_time / num_calculations

        # Assert reasonable performance
        assert (
            avg_time_per_calculation < 0.00001
        ), f"Distance calculation too slow: {avg_time_per_calculation:.8f}s per calculation"

        print(
            f"Performed {num_calculations} distance calculations in {total_time:.4f}s ({avg_time_per_calculation*1000000:.1f}μs per calculation)"
        )


class TestCollisionDetectionPerformance:
    """Test performance of collision detection."""

    def test_collision_detection_performance(self):
        """Test performance of collision detection with many objects."""
        manager = PhysicalObjectManager()

        # Create objects in a small area (some will collide)
        num_objects = 500  # Smaller number due to O(n²) complexity
        for i in range(num_objects):
            manager.create_object(
                f"obj_{i}",
                f"Object {i}",
                ObjectType.DEVICE,
                x=(i % 50) * 0.5,  # Pack objects close together
                y=((i // 50) % 50) * 0.5,
                z=0,
            )

        # Test collision detection
        start_time = time.time()
        collisions = manager.registry.check_collisions(collision_distance=1.0)
        end_time = time.time()

        total_time = end_time - start_time

        # Assert reasonable performance (should complete in reasonable time)
        assert (
            total_time < 5.0
        ), f"Collision detection too slow: {total_time:.3f}s for {num_objects} objects"

        print(
            f"Collision detection for {num_objects} objects completed in {total_time:.3f}s, found {len(collisions)} collisions"
        )


class TestNetworkAnalysisPerformance:
    """Test performance of network analysis operations."""

    def test_network_topology_performance(self):
        """Test performance of network topology analysis."""
        registry = ObjectRegistry()

        # Create network of connected objects
        num_objects = 1000
        objects = []

        for i in range(num_objects):
            obj = PhysicalObject(
                f"obj_{i}",
                f"Object {i}",
                ObjectType.DEVICE,
                location=(i % 100, (i // 100) % 100, 0),
            )

            # Connect to a few other objects (create sparse network)
            for j in range(min(5, i)):  # Connect to up to 5 previous objects
                if (i + j) % 7 == 0:  # Sparse connections
                    obj.connect_to(f"obj_{j}")
                    if j < len(objects):
                        objects[j].connect_to(f"obj_{i}")

            objects.append(obj)
            registry.register_object(obj)

        # Test network topology generation
        start_time = time.time()
        topology = registry.get_network_topology()
        end_time = time.time()

        topology_time = end_time - start_time

        # Test network metrics calculation
        start_time = time.time()
        metrics = registry.analyze_network_metrics()
        end_time = time.time()

        metrics_time = end_time - start_time

        # Assert reasonable performance
        assert (
            topology_time < 1.0
        ), f"Network topology generation too slow: {topology_time:.3f}s"
        assert (
            metrics_time < 2.0
        ), f"Network metrics calculation too slow: {metrics_time:.3f}s"

        print(f"Network topology for {num_objects} objects: {topology_time:.3f}s")
        print(f"Network metrics calculation: {metrics_time:.3f}s")
        print(
            f"Network has {metrics['total_connections']} connections, density: {metrics['density']:.4f}"
        )


class TestEventSystemPerformance:
    """Test performance of event system."""

    def test_event_emission_performance(self):
        """Test performance of event emission and handling."""
        registry = ObjectRegistry()
        events_received = []

        def fast_handler(event):
            events_received.append(event.event_type)

        def slow_handler(event):
            time.sleep(0.001)  # Simulate slow handler
            events_received.append(event.event_type)

        # Register multiple handlers
        registry.add_event_handler(EventType.CREATED, fast_handler)
        registry.add_event_handler(EventType.CREATED, slow_handler)

        # Test event emission performance
        num_objects = 100  # Limited due to slow handler

        start_time = time.time()
        for i in range(num_objects):
            obj = PhysicalObject(
                f"obj_{i}", f"Object {i}", ObjectType.SENSOR, location=(i, 0, 0)
            )
            registry.register_object(obj)
        end_time = time.time()

        total_time = end_time - start_time
        avg_time_per_event = total_time / num_objects

        # Verify events were handled
        assert len(events_received) == num_objects * 2  # Two handlers per event

        print(
            f"Event emission for {num_objects} objects: {total_time:.3f}s ({avg_time_per_event*1000:.1f}ms per event)"
        )


class TestMemoryUsage:
    """Test memory usage patterns."""

    def test_object_memory_footprint(self):
        """Test memory footprint of objects."""
        import sys

        # Measure memory usage of different object configurations
        basic_obj = PhysicalObject(
            "basic", "Basic Object", ObjectType.SENSOR, location=(0, 0, 0)
        )

        advanced_obj = PhysicalObject(
            "advanced",
            "Advanced Object",
            ObjectType.DEVICE,
            location=(0, 0, 0),
            material=MaterialType.METAL,
            mass=10.0,
            volume=1.0,
            temperature=300.0,
        )

        # Add some connections and tags to advanced object
        for i in range(10):
            advanced_obj.connect_to(f"connection_{i}")
            advanced_obj.add_tag(f"tag_{i}")

        basic_size = sys.getsizeof(basic_obj)
        advanced_size = sys.getsizeof(advanced_obj)

        print(f"Basic object size: {basic_size} bytes")
        print(f"Advanced object size: {advanced_size} bytes")

        # Assert objects don't use excessive memory
        assert basic_size < 1000, f"Basic object too large: {basic_size} bytes"
        assert advanced_size < 2000, f"Advanced object too large: {advanced_size} bytes"

    def test_registry_scaling(self):
        """Test how registry memory usage scales with object count."""
        import sys

        registry = ObjectRegistry()

        # Measure memory at different scales
        scales = [100, 1000, 5000]
        memory_usage = []

        for scale in scales:
            # Clear registry
            registry = ObjectRegistry()

            # Add objects
            for i in range(scale):
                obj = PhysicalObject(
                    f"obj_{i}",
                    f"Object {i}",
                    ObjectType.SENSOR,
                    location=(i % 100, (i // 100) % 100, 0),
                )
                registry.register_object(obj)

            # Measure memory (approximate)
            registry_size = sys.getsizeof(registry)
            objects_size = sum(sys.getsizeof(obj) for obj in registry.objects.values())
            total_size = registry_size + objects_size

            memory_usage.append((scale, total_size))

            print(
                f"Registry with {scale} objects: {total_size} bytes ({total_size/scale:.1f} bytes per object)"
            )

        # Check that memory scaling is reasonable (should be roughly linear)
        if len(memory_usage) >= 2:
            ratio = memory_usage[-1][1] / memory_usage[0][1]
            scale_ratio = memory_usage[-1][0] / memory_usage[0][0]

            # Memory usage should scale roughly linearly with object count
            assert (
                ratio / scale_ratio < 2.0
            ), f"Memory usage scaling poorly: {ratio/scale_ratio:.2f}x"


class TestStressTests:
    """Stress tests for extreme conditions."""

    def test_large_scale_operations(self):
        """Test operations at large scale."""
        manager = PhysicalObjectManager()

        # Create large number of objects
        num_objects = 20000
        print(f"Creating {num_objects} objects...")

        start_time = time.time()
        for i in range(num_objects):
            manager.create_object(
                f"stress_obj_{i}",
                f"Stress Object {i}",
                ObjectType.SENSOR,
                x=(i * 17) % 1000,
                y=(i * 23) % 1000,
                z=(i * 31) % 100,
                material=MaterialType.METAL if i % 2 == 0 else MaterialType.PLASTIC,
            )
        creation_time = time.time() - start_time

        print(f"Created {num_objects} objects in {creation_time:.2f}s")

        # Test bulk operations
        print("Testing bulk operations...")

        # Nearby object queries
        start_time = time.time()
        for i in range(100):
            nearby = manager.get_nearby_objects(x=i * 10, y=i * 10, z=0, radius=50)
        query_time = time.time() - start_time

        print(f"100 spatial queries completed in {query_time:.3f}s")

        # Statistics gathering
        start_time = time.time()
        stats = manager.get_statistics()
        stats_time = time.time() - start_time

        print(f"Statistics calculation completed in {stats_time:.3f}s")

        # Verify system still works correctly
        assert stats["total_objects"] == num_objects
        assert len(manager.registry.objects) == num_objects

        print("Large scale stress test completed successfully")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-s"])  # -s to show print outputs
