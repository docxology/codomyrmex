"""Test suite for Physical Management module."""

import pytest
import tempfile
import json
from pathlib import Path
from codomyrmex.physical_management import (
    PhysicalObjectManager, ObjectType, ObjectStatus, PhysicalObject,
    PhysicsSimulator, Vector3D, ForceField, SensorManager, SensorType, SensorReading
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

        force_field = ForceField(
            position=Vector3D(0, 0, 0),
            strength=10.0
        )

        object_pos = Vector3D(1, 0, 0)
        force = force_field.calculate_force(object_pos)

        # Force should point away from field center
        assert force.x > 0
        assert force.y == 0
        assert force.z == 0


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
