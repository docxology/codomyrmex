"""Comprehensive examples for the Physical Management module."""

from codomyrmex.physical_management import (
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

    PhysicalObjectManager, ObjectType, ObjectStatus, PhysicsSimulator,
    Vector3D, ForceField, SensorManager, SensorType, SensorReading
)


def object_management_example():
    """Demonstrate basic object management."""

    print("🏭 Physical Object Management Example")
    print("=" * 50)

    # Create object manager
    manager = PhysicalObjectManager()

    # Create different types of objects
    objects = [
        manager.create_object("sensor_001", "Temperature Sensor", ObjectType.SENSOR, 0, 0, 0),
        manager.create_object("actuator_001", "LED Light", ObjectType.ACTUATOR, 1, 0, 0),
        manager.create_object("device_001", "Smart Thermostat", ObjectType.DEVICE, 2, 0, 0),
    ]

    print(f"Created {len(objects)} objects")

    # Update object locations
    manager.update_object_location("sensor_001", 0.5, 0.5, 0.5)

    # Get nearby objects
    nearby = manager.get_nearby_objects(0.5, 0.5, 0.5, 1.0)
    print(f"Objects near (0.5, 0.5, 0.5): {len(nearby)}")

    # Get statistics
    stats = manager.get_statistics()
    print(f"Total objects: {stats['total_objects']}")

    return manager


def physics_simulation_example():
    """Demonstrate physics simulation."""

    print("\n⚡ Physics Simulation Example")
    print("=" * 50)

    # Create simulator
    sim = PhysicsSimulator()

    # Add force field
    force_field = ForceField(
        position=Vector3D(0, 0, 0),
        strength=5.0
    )
    sim.add_force_field(force_field)

    # Register objects
    sim.register_object("ball1", mass=1.0, position=Vector3D(0, 5, 0))
    sim.register_object("ball2", mass=2.0, position=Vector3D(3, 5, 0))

    # Run simulation for 2 seconds
    for i in range(120):  # 60 FPS * 2 seconds
        sim.update_physics(1/60)

        if i % 30 == 0:  # Print every 0.5 seconds
            ball1_state = sim.get_object_state("ball1")
            ball2_state = sim.get_object_state("ball2")
            print(f"t={i/60:.1f}s: Ball1 at {ball1_state['position']}, Ball2 at {ball2_state['position']}")

    return sim


def sensor_integration_example():
    """Demonstrate sensor integration."""

    print("\n📡 Sensor Integration Example")
    print("=" * 50)

    # Create sensor manager
    sensor_manager = SensorManager()

    # Simulate sensor readings
    readings = [
        SensorReading("temp_001", SensorType.TEMPERATURE, 23.5, "°C"),
        SensorReading("humid_001", SensorType.HUMIDITY, 65.2, "%"),
        SensorReading("press_001", SensorType.PRESSURE, 1013.25, "hPa"),
    ]

    for reading in readings:
        sensor_manager.add_reading(reading)
        print(f"Added reading: {reading.sensor_type.value} = {reading.value} {reading.unit}")

    # Get latest temperature
    latest_temp = sensor_manager.get_latest_reading(SensorType.TEMPERATURE)
    if latest_temp:
        print(f"Latest temperature: {latest_temp.value} {latest_temp.unit}")

    # Export data
    sensor_manager.export_readings("sensor_data.json")

    return sensor_manager


def comprehensive_demo():
    """Run comprehensive demonstration."""

    print("🚀 Codomyrmex Physical Management Module Demo")
    print("=" * 60)

    # Object management
    manager = object_management_example()

    # Physics simulation
    sim = physics_simulation_example()

    # Sensor integration
    sensor_manager = sensor_integration_example()

    # Final statistics
    print("\n📊 Final Statistics:")
    print(f"Object Manager: {manager.get_statistics()}")
    print(f"Physics Simulator: {sim.get_simulation_stats()}")
    print(f"Sensor Manager: {sensor_manager.get_statistics()}")

    print("\n✅ Demo completed successfully!")


if __name__ == "__main__":
    comprehensive_demo()
