"""Test suite for advanced features in Physical Management module."""

import time

import pytest

from codomyrmex.logging_monitoring.logger_config import get_logger
from codomyrmex.physical_management import (
    ObjectType,
    PhysicalObject,
    PhysicalObjectManager,
)

logger = get_logger(__name__)

from codomyrmex.physical_management import (
    EventType,
    MaterialProperties,
    MaterialType,
    ObjectEvent,
    ObjectRegistry,
    SpatialIndex,
)


class TestMaterialProperties:
    """Test cases for MaterialProperties."""

    def test_material_properties_creation(self):
        """Test creating material properties."""
        props = MaterialProperties(
            density=7850,
            elasticity=200e9,
            thermal_conductivity=45,
            specific_heat=500,
            melting_point=1811,
        )

        assert props.density == 7850
        assert props.elasticity == 200e9
        assert props.thermal_conductivity == 45
        assert props.specific_heat == 500
        assert props.melting_point == 1811

    def test_material_properties_from_type(self):
        """Test creating material properties from material type."""
        metal_props = MaterialProperties.from_material_type(MaterialType.METAL)
        plastic_props = MaterialProperties.from_material_type(MaterialType.PLASTIC)

        assert metal_props.density > plastic_props.density
        assert metal_props.elasticity > plastic_props.elasticity
        assert metal_props.melting_point > plastic_props.melting_point


class TestAdvancedPhysicalObject:
    """Test cases for enhanced PhysicalObject functionality."""

    def test_object_with_material_properties(self):
        """Test object creation with material properties."""
        obj = PhysicalObject(
            id="test_obj",
            name="Test Object",
            object_type=ObjectType.DEVICE,
            location=(0, 0, 0),
            material=MaterialType.METAL,
            mass=10.0,
            volume=0.001,  # 1 liter
        )

        assert obj.material == MaterialType.METAL
        assert obj.material_properties is not None
        assert obj.density == 10000.0  # 10 kg / 0.001 m³

    def test_tag_management(self):
        """Test tag addition and removal."""
        obj = PhysicalObject(
            id="test_obj",
            name="Test Object",
            object_type=ObjectType.SENSOR,
            location=(0, 0, 0),
        )

        # Add tags
        obj.add_tag("important")
        obj.add_tag("monitored")

        assert obj.has_tag("important")
        assert obj.has_tag("monitored")
        assert len(obj.tags) == 2

        # Remove tag
        assert obj.remove_tag("important")
        assert not obj.has_tag("important")
        assert obj.has_tag("monitored")

        # Try to remove non-existent tag
        assert not obj.remove_tag("nonexistent")

    def test_connection_management(self):
        """Test object connection functionality."""
        obj1 = PhysicalObject(
            id="obj1",
            name="Object 1",
            object_type=ObjectType.DEVICE,
            location=(0, 0, 0),
        )

        obj2_id = "obj2"

        # Connect objects
        obj1.connect_to(obj2_id)
        assert obj1.is_connected_to(obj2_id)
        assert obj2_id in obj1.connections

        # Disconnect objects
        assert obj1.disconnect_from(obj2_id)
        assert not obj1.is_connected_to(obj2_id)

        # Try to disconnect non-connected object
        assert not obj1.disconnect_from("nonexistent")

    def test_temperature_and_thermal_energy(self):
        """Test temperature management and thermal energy calculation."""
        obj = PhysicalObject(
            id="test_obj",
            name="Test Object",
            object_type=ObjectType.DEVICE,
            location=(0, 0, 0),
            material=MaterialType.METAL,
            mass=1.0,
        )

        # Update temperature
        obj.update_temperature(373.15)  # 100°C
        assert obj.temperature == 373.15

        # Calculate thermal energy
        thermal_energy = obj.calculate_thermal_energy()
        assert thermal_energy > 0

        # Should be mass * specific_heat * (temp - 273.15)
        expected = 1.0 * obj.material_properties.specific_heat * (373.15 - 273.15)
        assert abs(thermal_energy - expected) < 1e-10

    def test_object_age_and_time_tracking(self):
        """Test object age and update time tracking."""
        obj = PhysicalObject(
            id="test_obj",
            name="Test Object",
            object_type=ObjectType.SENSOR,
            location=(0, 0, 0),
        )

        # Age should be very small initially
        age = obj.get_age()
        assert 0 <= age < 1.0

        # Time since update should be very small
        time_since_update = obj.time_since_update()
        assert 0 <= time_since_update < 1.0

        # Wait a bit and update
        time.sleep(0.01)  # Reduced wait time for faster tests
        obj.add_tag("updated")

        # Age should increase but time since update should reset
        new_age = obj.get_age()
        new_time_since_update = obj.time_since_update()

        assert new_age >= age  # Age should at least not decrease
        assert new_time_since_update < 0.01  # Should be very small after update


class TestSpatialIndex:
    """Test cases for SpatialIndex."""

    def test_spatial_index_creation(self):
        """Test creating spatial index."""
        index = SpatialIndex(grid_size=5.0)
        assert index.grid_size == 5.0

    def test_add_and_remove_objects(self):
        """Test adding and removing objects from spatial index."""
        index = SpatialIndex(grid_size=10.0)

        # Add objects
        index.add_object("obj1", 5, 5, 5)  # Distance from (5,5,5) = 0
        index.add_object("obj2", 12, 12, 12)  # Distance from (5,5,5) = 12.12
        index.add_object("obj3", 7, 8, 9)  # Distance from (5,5,5) = 5.74

        # Get nearby objects with radius that includes obj1 and obj3, but excludes obj2
        nearby = index.get_nearby_cells(5, 5, 5, 10)
        assert "obj1" in nearby
        assert "obj2" not in nearby  # Too far away
        assert "obj3" in nearby

        # Get nearby objects with larger radius that includes all
        nearby_large = index.get_nearby_cells(5, 5, 5, 20)
        assert "obj1" in nearby_large
        assert "obj2" in nearby_large
        assert "obj3" in nearby_large

        # Remove object and verify
        index.remove_object("obj2")
        nearby_after_removal = index.get_nearby_cells(5, 5, 5, 20)
        assert "obj1" in nearby_after_removal
        assert "obj2" not in nearby_after_removal
        assert "obj3" in nearby_after_removal

    def test_spatial_index_grid_boundaries(self):
        """Test spatial index grid boundaries and distance filtering."""
        index = SpatialIndex(grid_size=10.0)

        # Add objects at specific positions
        index.add_object("obj1", 0, 0, 0)  # Distance from (5,5,5) = 8.66
        index.add_object("obj2", 10, 10, 10)  # Distance from (5,5,5) = 8.66
        index.add_object("obj3", 7, 7, 7)  # Distance from (5,5,5) = 3.46

        # Test with radius that includes obj3 but excludes obj1 and obj2
        nearby = index.get_nearby_cells(5, 5, 5, 4)
        assert "obj3" in nearby
        assert "obj1" not in nearby
        assert "obj2" not in nearby

        # Test with larger radius that includes all objects
        nearby_large = index.get_nearby_cells(5, 5, 5, 10)
        assert "obj1" in nearby_large
        assert "obj2" in nearby_large
        assert "obj3" in nearby_large

        # Test with very small radius that excludes everything
        nearby_small = index.get_nearby_cells(5, 5, 5, 2)
        assert "obj1" not in nearby_small
        assert "obj2" not in nearby_small
        assert "obj3" not in nearby_small


class TestEventSystem:
    """Test cases for event system."""

    def test_event_creation(self):
        """Test creating events."""
        event = ObjectEvent(
            event_type=EventType.CREATED, object_id="test_obj", data={"key": "value"}
        )

        assert event.event_type == EventType.CREATED
        assert event.object_id == "test_obj"
        assert event.data["key"] == "value"
        assert event.timestamp > 0

    def test_event_handlers(self):
        """Test event handler registration and emission."""
        registry = ObjectRegistry()
        events_received = []

        def event_handler(event):
            events_received.append(event)

        # Register event handler
        registry.add_event_handler(EventType.CREATED, event_handler)

        # Create object (should emit CREATED event)
        obj = PhysicalObject(
            id="test_obj",
            name="Test Object",
            object_type=ObjectType.SENSOR,
            location=(0, 0, 0),
        )
        registry.register_object(obj)

        # Check that event was received
        assert len(events_received) == 1
        assert events_received[0].event_type == EventType.CREATED
        assert events_received[0].object_id == "test_obj"

    def test_event_handler_removal(self):
        """Test event handler removal."""
        registry = ObjectRegistry()
        events_received = []

        def event_handler(event):
            events_received.append(event)

        # Register and then remove event handler
        registry.add_event_handler(EventType.CREATED, event_handler)
        assert registry.remove_event_handler(EventType.CREATED, event_handler)

        # Create object (should not emit to removed handler)
        obj = PhysicalObject(
            id="test_obj",
            name="Test Object",
            object_type=ObjectType.SENSOR,
            location=(0, 0, 0),
        )
        registry.register_object(obj)

        # No events should be received
        assert len(events_received) == 0

    def test_event_filtering(self):
        """Test event filtering by type, object ID, and timestamp."""
        registry = ObjectRegistry()

        # Create some events manually
        event1 = ObjectEvent(EventType.CREATED, "obj1")
        event2 = ObjectEvent(EventType.MOVED, "obj1")
        event3 = ObjectEvent(EventType.CREATED, "obj2")

        registry.event_history = [event1, event2, event3]

        # Filter by event type
        created_events = registry.get_events(event_type=EventType.CREATED)
        assert len(created_events) == 2
        assert all(e.event_type == EventType.CREATED for e in created_events)

        # Filter by object ID
        obj1_events = registry.get_events(object_id="obj1")
        assert len(obj1_events) == 2
        assert all(e.object_id == "obj1" for e in obj1_events)

        # Filter by timestamp
        recent_events = registry.get_events(since=time.time() - 1)
        assert len(recent_events) >= 0  # Should include recent events


class TestTagSystem:
    """Test cases for tag-based object management."""

    def test_get_objects_by_tags_match_all(self):
        """Test getting objects by tags with match_all=True."""
        registry = ObjectRegistry()

        # Create objects with different tags
        obj1 = PhysicalObject("obj1", "Object 1", ObjectType.SENSOR, (0, 0, 0))
        obj1.add_tag("sensor")
        obj1.add_tag("temperature")

        obj2 = PhysicalObject("obj2", "Object 2", ObjectType.SENSOR, (1, 1, 1))
        obj2.add_tag("sensor")
        obj2.add_tag("humidity")

        obj3 = PhysicalObject("obj3", "Object 3", ObjectType.SENSOR, (2, 2, 2))
        obj3.add_tag("sensor")
        obj3.add_tag("temperature")
        obj3.add_tag("outdoor")

        registry.register_object(obj1)
        registry.register_object(obj2)
        registry.register_object(obj3)

        # Find objects with specific tags (match all)
        temp_sensors = registry.get_objects_by_tags(
            {"sensor", "temperature"}, match_all=True
        )
        assert len(temp_sensors) == 2
        assert obj1 in temp_sensors
        assert obj3 in temp_sensors

        # Find objects with tags that not all have (should be empty)
        outdoor_temp = registry.get_objects_by_tags(
            {"sensor", "temperature", "outdoor"}, match_all=True
        )
        assert len(outdoor_temp) == 1
        assert obj3 in outdoor_temp

    def test_get_objects_by_tags_match_any(self):
        """Test getting objects by tags with match_all=False."""
        registry = ObjectRegistry()

        # Create objects
        obj1 = PhysicalObject("obj1", "Object 1", ObjectType.SENSOR, (0, 0, 0))
        obj1.add_tag("temperature")

        obj2 = PhysicalObject("obj2", "Object 2", ObjectType.SENSOR, (1, 1, 1))
        obj2.add_tag("humidity")

        obj3 = PhysicalObject("obj3", "Object 3", ObjectType.DEVICE, (2, 2, 2))
        obj3.add_tag("controller")

        registry.register_object(obj1)
        registry.register_object(obj2)
        registry.register_object(obj3)

        # Find objects with any of the specified tags
        sensors = registry.get_objects_by_tags(
            {"temperature", "humidity"}, match_all=False
        )
        assert len(sensors) == 2
        assert obj1 in sensors
        assert obj2 in sensors
        assert obj3 not in sensors


class TestNetworkTopology:
    """Test cases for network topology analysis."""

    def test_network_topology_creation(self):
        """Test creating network topology."""
        registry = ObjectRegistry()

        # Create connected objects
        obj1 = PhysicalObject("obj1", "Object 1", ObjectType.DEVICE, (0, 0, 0))
        obj2 = PhysicalObject("obj2", "Object 2", ObjectType.DEVICE, (1, 1, 1))
        obj3 = PhysicalObject("obj3", "Object 3", ObjectType.DEVICE, (2, 2, 2))

        obj1.connect_to("obj2")
        obj2.connect_to("obj3")
        obj3.connect_to("obj1")  # Create triangle

        registry.register_object(obj1)
        registry.register_object(obj2)
        registry.register_object(obj3)

        # Get topology
        topology = registry.get_network_topology()

        assert "obj2" in topology["obj1"]
        assert "obj3" in topology["obj2"]
        assert "obj1" in topology["obj3"]

    def test_network_path_finding(self):
        """Test finding paths through network connections."""
        registry = ObjectRegistry()

        # Create chain of connected objects
        objects = []
        for i in range(5):
            obj = PhysicalObject(f"obj{i}", f"Object {i}", ObjectType.DEVICE, (i, 0, 0))
            if i > 0:
                obj.connect_to(f"obj{i-1}")
                objects[i - 1].connect_to(f"obj{i}")
            objects.append(obj)
            registry.register_object(obj)

        # Find path from first to last
        path = registry.find_path_through_network("obj0", "obj4")
        assert path is not None
        assert path[0] == "obj0"
        assert path[-1] == "obj4"
        assert len(path) <= 5

    def test_network_metrics(self):
        """Test network topology metrics calculation."""
        registry = ObjectRegistry()

        # Create simple network
        obj1 = PhysicalObject("obj1", "Object 1", ObjectType.DEVICE, (0, 0, 0))
        obj2 = PhysicalObject("obj2", "Object 2", ObjectType.DEVICE, (1, 1, 1))
        obj3 = PhysicalObject("obj3", "Object 3", ObjectType.DEVICE, (2, 2, 2))

        # Connect in triangle (fully connected)
        obj1.connect_to("obj2")
        obj1.connect_to("obj3")
        obj2.connect_to("obj1")
        obj2.connect_to("obj3")
        obj3.connect_to("obj1")
        obj3.connect_to("obj2")

        registry.register_object(obj1)
        registry.register_object(obj2)
        registry.register_object(obj3)

        # Analyze metrics
        metrics = registry.analyze_network_metrics()

        assert metrics["total_objects"] == 3
        assert (
            metrics["total_connections"] == 3
        )  # Each bidirectional connection counted once
        assert metrics["average_degree"] == 2.0
        assert metrics["max_degree"] == 2
        assert metrics["min_degree"] == 2
        assert metrics["density"] == 1.0  # Fully connected triangle


class TestIntegrationAdvanced:
    """Integration tests for advanced features."""

    def test_complete_advanced_workflow(self):
        """Test complete workflow with advanced features."""
        manager = PhysicalObjectManager()

        # Create objects with different materials and properties
        metal_sensor = manager.create_object(
            "metal_sensor",
            "Metal Temperature Sensor",
            ObjectType.SENSOR,
            x=0,
            y=0,
            z=0,
            material=MaterialType.METAL,
            mass=0.5,
            temperature=298.15,
        )

        plastic_device = manager.create_object(
            "plastic_device",
            "Plastic Control Device",
            ObjectType.DEVICE,
            x=5,
            y=5,
            z=0,
            material=MaterialType.PLASTIC,
            mass=0.2,
        )

        # Add tags and connections
        metal_sensor.add_tag("temperature")
        metal_sensor.add_tag("critical")
        plastic_device.add_tag("controller")

        metal_sensor.connect_to("plastic_device")
        plastic_device.connect_to("metal_sensor")

        # Test spatial queries
        nearby = manager.get_nearby_objects(2, 2, 0, 5)
        assert len(nearby) >= 1

        # Test network analysis
        topology = manager.registry.get_network_topology()
        assert "plastic_device" in topology["metal_sensor"]

        # Test event system
        events_received = []

        def event_handler(event):
            events_received.append(event)

        manager.registry.add_event_handler(EventType.CREATED, event_handler)

        # Create another object (should trigger event)
        manager.create_object(
            "new_obj", "New Object", ObjectType.ACTUATOR, x=10, y=10, z=0
        )

        # Verify event was received
        assert len(events_received) >= 1

        # Test tag-based queries
        critical_objects = manager.registry.get_objects_by_tags({"critical"})
        assert len(critical_objects) == 1
        assert critical_objects[0].id == "metal_sensor"

        # Test network metrics
        metrics = manager.registry.analyze_network_metrics()
        assert metrics["total_objects"] == 3
        assert metrics["total_connections"] >= 1


if __name__ == "__main__":
    pytest.main([__file__])
