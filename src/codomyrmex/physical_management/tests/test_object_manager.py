"""Test suite for Physical Management module."""

import pytest
import tempfile
import json
import time
from pathlib import Path
from codomyrmex.physical_management import (
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

    PhysicalObjectManager,
    ObjectType,
    ObjectStatus,
    PhysicalObject,
    PhysicsSimulator,
    Vector3D,
    ForceField,
    SensorManager,
    SensorType,
    SensorReading,
    DeviceInterface,
    DeviceStatus,
)


class TestPhysicalObjectManager:
    """Test cases for PhysicalObjectManager."""

    def test_manager_creation(self):
        """Test creating an object manager."""
        manager = PhysicalObjectManager()
        assert manager is not None
        assert len(manager.registry.objects) == 0

    def test_create_object(self):
        """Test creating physical objects."""
        manager = PhysicalObjectManager()

        obj = manager.create_object(
            "test_001", "Test Object", ObjectType.SENSOR, 1.0, 2.0, 3.0
        )

        assert obj.id == "test_001"
        assert obj.name == "Test Object"
        assert obj.object_type == ObjectType.SENSOR
        assert obj.location == (1.0, 2.0, 3.0)

    def test_update_location(self):
        """Test updating object location."""
        manager = PhysicalObjectManager()

        obj = manager.create_object(
            "test_001", "Test Object", ObjectType.SENSOR, 0, 0, 0
        )

        success = manager.update_object_location("test_001", 5.0, 5.0, 5.0)
        assert success

        updated_obj = manager.registry.get_object("test_001")
        assert updated_obj.location == (5.0, 5.0, 5.0)

    def test_nearby_objects(self):
        """Test finding nearby objects."""
        manager = PhysicalObjectManager()

        # Create objects at different locations
        manager.create_object("obj1", "Object 1", ObjectType.SENSOR, 0, 0, 0)
        manager.create_object("obj2", "Object 2", ObjectType.SENSOR, 1, 1, 1)
        manager.create_object("obj3", "Object 3", ObjectType.SENSOR, 10, 10, 10)

        # Test nearby search
        nearby = manager.get_nearby_objects(0, 0, 0, 2.0)
        assert len(nearby) == 2  # obj1 and obj2

        far_away = manager.get_nearby_objects(0, 0, 0, 0.5)
        assert len(far_away) == 1  # only obj1

    def test_distance_calculations(self):
        """Test distance calculation methods."""
        manager = PhysicalObjectManager()

        obj1 = manager.create_object("obj1", "Object 1", ObjectType.SENSOR, 0, 0, 0)
        obj2 = manager.create_object("obj2", "Object 2", ObjectType.SENSOR, 3, 4, 0)

        # Test distance between objects
        distance = obj1.distance_to(obj2)
        assert abs(distance - 5.0) < 1e-10  # 3-4-5 triangle

        # Test distance to point
        distance_to_point = obj1.distance_to_point(6, 8, 0)
        assert abs(distance_to_point - 10.0) < 1e-10

        # Test within range
        assert obj1.is_within_range(0, 0, 0, 1.0)
        assert not obj1.is_within_range(10, 10, 10, 1.0)

    def test_object_properties(self):
        """Test object property management."""
        manager = PhysicalObjectManager()
        obj = manager.create_object("test", "Test", ObjectType.SENSOR, 0, 0, 0)

        # Add properties
        obj.add_property("temperature", 25.0)
        obj.add_property("status", "active")

        assert obj.properties["temperature"] == 25.0
        assert obj.properties["status"] == "active"

        # Remove property
        removed_value = obj.remove_property("temperature")
        assert removed_value == 25.0
        assert "temperature" not in obj.properties

    def test_batch_operations(self):
        """Test batch operations on multiple objects."""
        manager = PhysicalObjectManager()

        # Create multiple objects
        for i in range(5):
            manager.create_object(f"obj_{i}", f"Object {i}", ObjectType.SENSOR, i, i, i)

        # Test batch status update
        object_ids = [f"obj_{i}" for i in range(3)]
        updated_count = manager.batch_update_status(
            object_ids, ObjectStatus.MAINTENANCE
        )
        assert updated_count == 3

        # Verify status changes
        for obj_id in object_ids:
            obj = manager.registry.get_object(obj_id)
            assert obj.status == ObjectStatus.MAINTENANCE

        # Test batch move
        moves = {
            "obj_0": (10, 10, 10),
            "obj_1": (20, 20, 20),
            "obj_nonexistent": (5, 5, 5),
        }
        moved_count = manager.batch_move_objects(moves)
        assert moved_count == 2  # obj_nonexistent doesn't exist

    def test_pathfinding(self):
        """Test pathfinding between objects."""
        manager = PhysicalObjectManager()

        # Create a line of objects for pathfinding
        manager.create_object("start", "Start", ObjectType.SENSOR, 0, 0, 0)
        manager.create_object("mid1", "Mid1", ObjectType.SENSOR, 2, 0, 0)
        manager.create_object("mid2", "Mid2", ObjectType.SENSOR, 4, 0, 0)
        manager.create_object("end", "End", ObjectType.SENSOR, 6, 0, 0)

        path = manager.find_path_between_objects("start", "end")
        assert path is not None
        assert len(path) >= 2  # Should include at least start and end

    def test_collision_detection(self):
        """Test collision detection."""
        manager = PhysicalObjectManager()

        # Create objects that should collide
        manager.create_object("obj1", "Object 1", ObjectType.SENSOR, 0, 0, 0)
        manager.create_object(
            "obj2", "Object 2", ObjectType.SENSOR, 0.5, 0, 0
        )  # Very close
        manager.create_object(
            "obj3", "Object 3", ObjectType.SENSOR, 10, 10, 10
        )  # Far away

        collisions = manager.registry.check_collisions(collision_distance=1.0)
        assert len(collisions) == 1
        assert ("obj1", "obj2") in [(c[0].id, c[1].id) for c in collisions] or (
            "obj2",
            "obj1",
        ) in [(c[0].id, c[1].id) for c in collisions]

    def test_clustering(self):
        """Test object clustering."""
        manager = PhysicalObjectManager()

        # Create two clusters
        # Cluster 1: around origin
        manager.create_object("c1_1", "Cluster 1 Obj 1", ObjectType.SENSOR, 0, 0, 0)
        manager.create_object("c1_2", "Cluster 1 Obj 2", ObjectType.SENSOR, 1, 1, 0)
        manager.create_object("c1_3", "Cluster 1 Obj 3", ObjectType.SENSOR, 2, 0, 0)

        # Cluster 2: far away
        manager.create_object("c2_1", "Cluster 2 Obj 1", ObjectType.SENSOR, 20, 20, 0)
        manager.create_object("c2_2", "Cluster 2 Obj 2", ObjectType.SENSOR, 21, 21, 0)

        clusters = manager.detect_object_clusters(
            cluster_radius=5.0, min_cluster_size=2
        )
        assert len(clusters) == 2

        # Check cluster sizes
        cluster_sizes = [len(cluster) for cluster in clusters]
        assert 3 in cluster_sizes  # First cluster
        assert 2 in cluster_sizes  # Second cluster

    def test_center_of_mass(self):
        """Test center of mass calculation."""
        manager = PhysicalObjectManager()

        # Create objects at known positions
        manager.create_object("obj1", "Object 1", ObjectType.SENSOR, 0, 0, 0)
        manager.create_object("obj2", "Object 2", ObjectType.SENSOR, 4, 0, 0)
        manager.create_object("obj3", "Object 3", ObjectType.SENSOR, 2, 3, 0)

        center = manager.calculate_center_of_mass()
        assert abs(center[0] - 2.0) < 1e-10  # (0+4+2)/3 = 2
        assert abs(center[1] - 1.0) < 1e-10  # (0+0+3)/3 = 1
        assert abs(center[2] - 0.0) < 1e-10  # (0+0+0)/3 = 0

    def test_boundary_box(self):
        """Test boundary box calculation."""
        manager = PhysicalObjectManager()

        manager.create_object("obj1", "Object 1", ObjectType.SENSOR, -1, -2, -3)
        manager.create_object("obj2", "Object 2", ObjectType.SENSOR, 5, 4, 3)
        manager.create_object("obj3", "Object 3", ObjectType.SENSOR, 2, 1, 0)

        bbox = manager.get_boundary_box()

        assert bbox["x"] == (-1, 5)
        assert bbox["y"] == (-2, 4)
        assert bbox["z"] == (-3, 3)


class TestPhysicsSimulator:
    """Test cases for PhysicsSimulator."""

    def test_simulator_creation(self):
        """Test creating a physics simulator."""
        sim = PhysicsSimulator()
        assert sim is not None
        assert len(sim.objects) == 0
        assert len(sim.force_fields) == 0

    def test_register_object(self):
        """Test registering objects for simulation."""
        sim = PhysicsSimulator()

        position = Vector3D(0, 5, 0)
        sim.register_object("ball", mass=1.0, position=position)

        assert "ball" in sim.objects
        assert sim.objects["ball"]["position"] == position

    def test_force_field_calculation(self):
        """Test force field calculations."""
        sim = PhysicsSimulator()

        force_field = ForceField(position=Vector3D(0, 0, 0), strength=10.0)

        object_pos = Vector3D(1, 0, 0)
        force = force_field.calculate_force(object_pos)

        # Force should point away from field center
        assert force.x > 0
        assert force.y == 0
        assert force.z == 0

    def test_energy_calculations(self):
        """Test energy calculation methods."""
        sim = PhysicsSimulator()

        # Register object with known mass and velocity
        position = Vector3D(0, 5, 0)
        velocity = Vector3D(3, 0, 0)
        sim.register_object("ball", mass=2.0, position=position, velocity=velocity)

        # Test kinetic energy: KE = 0.5 * m * v^2 = 0.5 * 2 * 9 = 9
        ke = sim.calculate_kinetic_energy("ball")
        assert abs(ke - 9.0) < 1e-10

        # Test potential energy: PE = m * g * h = 2 * 9.81 * 5 = 98.1
        pe = sim.calculate_potential_energy("ball")
        expected_pe = 2.0 * 9.81 * 5.0
        assert abs(pe - expected_pe) < 1e-10

    def test_impulse_application(self):
        """Test applying impulse to objects."""
        sim = PhysicsSimulator()

        position = Vector3D(0, 0, 0)
        velocity = Vector3D(0, 0, 0)
        sim.register_object("ball", mass=1.0, position=position, velocity=velocity)

        # Apply impulse
        impulse = Vector3D(5, 0, 0)
        success = sim.apply_impulse("ball", impulse)
        assert success

        # Check velocity change
        ball = sim.get_object_state("ball")
        assert abs(ball["velocity"].x - 5.0) < 1e-10
        assert abs(ball["velocity"].y - 0.0) < 1e-10

    def test_spring_constraints(self):
        """Test spring constraints between objects."""
        sim = PhysicsSimulator()

        pos1 = Vector3D(0, 0, 0)
        pos2 = Vector3D(3, 0, 0)  # 3 units apart
        sim.register_object("obj1", mass=1.0, position=pos1)
        sim.register_object("obj2", mass=1.0, position=pos2)

        # Add spring with rest length of 2 units
        success = sim.add_spring_constraint(
            "obj1", "obj2", rest_length=2.0, spring_constant=1.0
        )
        assert success

        # Run simulation step
        sim.update_physics(0.1)

        # Objects should be pulled closer together
        obj1_state = sim.get_object_state("obj1")
        obj2_state = sim.get_object_state("obj2")

        # Check that spring force was applied (objects should move towards each other)
        assert obj1_state["velocity"].x > 0  # obj1 moves towards obj2
        assert obj2_state["velocity"].x < 0  # obj2 moves towards obj1

    def test_collision_detection_physics(self):
        """Test collision detection in physics simulator."""
        sim = PhysicsSimulator()

        pos1 = Vector3D(0, 0, 0)
        pos2 = Vector3D(0.3, 0, 0)  # Very close
        pos3 = Vector3D(10, 0, 0)  # Far away

        sim.register_object("obj1", mass=1.0, position=pos1)
        sim.register_object("obj2", mass=1.0, position=pos2)
        sim.register_object("obj3", mass=1.0, position=pos3)

        collisions = sim.detect_collisions(collision_radius=0.5)
        assert len(collisions) == 1
        assert ("obj1", "obj2") in collisions or ("obj2", "obj1") in collisions

    def test_elastic_collision(self):
        """Test elastic collision handling."""
        sim = PhysicsSimulator()

        # Two objects moving towards each other
        pos1 = Vector3D(0, 0, 0)
        pos2 = Vector3D(1, 0, 0)
        vel1 = Vector3D(2, 0, 0)
        vel2 = Vector3D(-1, 0, 0)

        sim.register_object("obj1", mass=1.0, position=pos1, velocity=vel1)
        sim.register_object("obj2", mass=2.0, position=pos2, velocity=vel2)

        success = sim.handle_elastic_collision("obj1", "obj2")
        assert success

        # Check that velocities changed
        obj1_state = sim.get_object_state("obj1")
        obj2_state = sim.get_object_state("obj2")

        # Velocities should have changed from the collision
        assert obj1_state["velocity"].x != 2.0
        assert obj2_state["velocity"].x != -1.0


class TestVector3D:
    """Test cases for Vector3D class."""

    def test_vector_creation(self):
        """Test creating 3D vectors."""
        vec = Vector3D(1.0, 2.0, 3.0)
        assert vec.x == 1.0
        assert vec.y == 2.0
        assert vec.z == 3.0

    def test_vector_operations(self):
        """Test vector arithmetic."""
        vec1 = Vector3D(1, 2, 3)
        vec2 = Vector3D(4, 5, 6)

        # Addition
        result = vec1 + vec2
        assert result.x == 5
        assert result.y == 7
        assert result.z == 9

        # Scaling
        scaled = vec1 * 2
        assert scaled.x == 2
        assert scaled.y == 4
        assert scaled.z == 6

    def test_vector_magnitude(self):
        """Test vector magnitude calculation."""
        vec = Vector3D(3, 4, 0)
        assert abs(vec.magnitude() - 5.0) < 1e-10  # 3-4-5 triangle

        zero_vec = Vector3D(0, 0, 0)
        assert zero_vec.magnitude() == 0


class TestSensorManager:
    """Test cases for SensorManager."""

    def test_manager_creation(self):
        """Test creating a sensor manager."""
        manager = SensorManager()
        assert manager is not None
        assert len(manager.readings) == 0

    def test_add_reading(self):
        """Test adding sensor readings."""
        manager = SensorManager()

        reading = SensorReading("temp_001", SensorType.TEMPERATURE, 23.5, "°C")
        manager.add_reading(reading)

        assert len(manager.readings) == 1
        assert manager.readings[0] == reading

    def test_get_latest_reading(self):
        """Test getting latest reading by type."""
        manager = SensorManager()

        # Add readings
        temp1 = SensorReading("temp_001", SensorType.TEMPERATURE, 20.0, "°C")
        temp2 = SensorReading("temp_001", SensorType.TEMPERATURE, 25.0, "°C")
        humid = SensorReading("humid_001", SensorType.HUMIDITY, 60.0, "%")

        manager.add_reading(temp1)
        manager.add_reading(humid)
        manager.add_reading(temp2)

        latest_temp = manager.get_latest_reading(SensorType.TEMPERATURE)
        assert latest_temp == temp2
        assert latest_temp.value == 25.0

    def test_sensor_calibration(self):
        """Test sensor calibration functionality."""
        manager = SensorManager()

        # Create calibration data: (sensor_reading, actual_value)
        reference_values = [(20.0, 22.0), (30.0, 32.5), (40.0, 43.0)]

        calibration = manager.calibrate_sensor(
            "temp_001", reference_values, SensorType.TEMPERATURE
        )

        # Check that calibration coefficients are reasonable
        assert "slope" in calibration
        assert "offset" in calibration
        assert calibration["slope"] > 0  # Should be positive slope

        # Test applying calibration
        raw_reading = SensorReading("temp_001", SensorType.TEMPERATURE, 25.0, "°C")
        calibrated_reading = manager.apply_calibration(raw_reading)

        # Should have calibrated metadata
        assert calibrated_reading.metadata.get("calibrated") is True
        assert "raw_value" in calibrated_reading.metadata
        assert calibrated_reading.value != raw_reading.value  # Should be different

    def test_sensor_health_monitoring(self):
        """Test sensor health analysis."""
        manager = SensorManager()

        # Add normal readings
        for i in range(10):
            reading = SensorReading(
                "temp_001",
                SensorType.TEMPERATURE,
                20.0 + i * 0.1,  # Gradual increase
                "°C",
            )
            manager.add_reading(reading)

        health = manager.get_sensor_health("temp_001")
        assert health["status"] == "healthy"
        assert health["readings_count"] == 10
        assert health["anomalies_count"] == 0

    def test_sensor_drift_detection(self):
        """Test sensor drift detection."""
        manager = SensorManager()

        # Add baseline readings (old values around 20)
        base_time = time.time() - 90000  # 25 hours ago
        for i in range(20):
            reading = SensorReading(
                "temp_001",
                SensorType.TEMPERATURE,
                20.0 + (i % 5) * 0.1,  # Values around 20
                "°C",
                timestamp=base_time + i * 100,
            )
            manager.add_reading(reading)

        # Add recent readings (new values around 25 - showing drift)
        recent_time = time.time() - 1800  # 30 minutes ago
        for i in range(20):
            reading = SensorReading(
                "temp_001",
                SensorType.TEMPERATURE,
                25.0 + (i % 5) * 0.1,  # Values around 25
                "°C",
                timestamp=recent_time + i * 60,
            )
            manager.add_reading(reading)

        drift_analysis = manager.detect_sensor_drift("temp_001")
        assert drift_analysis["status"] in ["moderate_drift", "significant_drift"]
        assert drift_analysis["drift_amount"] > 0  # Positive drift

    def test_device_management(self):
        """Test device interface management."""
        manager = SensorManager()

        # Create device
        device = DeviceInterface(
            device_id="device_001",
            device_type="temperature_sensor",
            sensors=[SensorType.TEMPERATURE, SensorType.HUMIDITY],
        )

        manager.register_device(device)
        assert "device_001" in manager.devices

        # Update device status
        success = manager.update_device_status("device_001", DeviceStatus.CONNECTED)
        assert success

        status = manager.get_device_status("device_001")
        assert status == DeviceStatus.CONNECTED


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_complete_workflow(self):
        """Test a complete physical management workflow."""
        # Create manager
        manager = PhysicalObjectManager()

        # Create objects
        sensor = manager.create_object(
            "sensor_001", "Temperature Sensor", ObjectType.SENSOR, 0, 0, 0
        )

        actuator = manager.create_object(
            "actuator_001", "Heater", ObjectType.ACTUATOR, 1, 0, 0
        )

        # Create sensor manager
        sensor_manager = SensorManager()

        # Add sensor readings
        reading = SensorReading("sensor_001", SensorType.TEMPERATURE, 18.5, "°C")
        sensor_manager.add_reading(reading)

        # Create physics simulator
        sim = PhysicsSimulator()
        sim.register_object("sensor_001", mass=0.1, position=Vector3D(0, 0, 0))

        # Run a few simulation steps
        for _ in range(10):
            sim.update_physics(0.1)

        # Verify everything works together
        assert len(manager.registry.objects) == 2
        assert len(sensor_manager.readings) == 1
        assert len(sim.objects) == 1

        # Get final statistics
        manager_stats = manager.get_statistics()
        sensor_stats = sensor_manager.get_statistics()
        sim_stats = sim.get_simulation_stats()

        assert manager_stats["total_objects"] == 2
        assert sensor_stats["total_readings"] == 1
        assert sim_stats["total_objects"] == 1


if __name__ == "__main__":
    pytest.main([__file__])
