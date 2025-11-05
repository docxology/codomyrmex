"""Advanced usage examples for Physical Management module."""

import random
import time

from codomyrmex.logging_monitoring.logger_config import get_logger
from codomyrmex.physical_management import (
    EventType,
    MaterialType,
    ObjectType,
    PhysicalObjectManager,
)

logger = get_logger(__name__)

from codomyrmex.physical_management import (
    ForceField,
    PhysicsSimulator,
    PredictiveAnalytics,
    SensorManager,
    SensorReading,
    SensorType,
    StreamingAnalytics,
    Vector3D,
)


def example_smart_factory_monitoring():
    """Example: Smart factory with sensors, machines, and real-time monitoring."""
    print("=== Smart Factory Monitoring Example ===")

    # Create manager
    manager = PhysicalObjectManager()

    # Create factory floor objects with materials and properties
    conveyor = manager.create_object(
        "conveyor_001",
        "Main Conveyor Belt",
        ObjectType.DEVICE,
        x=0,
        y=0,
        z=0,
        material=MaterialType.METAL,
        mass=500.0,
        temperature=298.15,
    )
    conveyor.add_tag("production")
    conveyor.add_tag("critical")

    # Create temperature sensors
    for i in range(5):
        sensor = manager.create_object(
            f"temp_sensor_{i:03d}",
            f"Temperature Sensor {i}",
            ObjectType.SENSOR,
            x=i * 10,
            y=5,
            z=2,
            material=MaterialType.PLASTIC,
            mass=0.1,
        )
        sensor.add_tag("temperature")
        sensor.add_tag("monitoring")

        # Connect sensors to conveyor (network topology)
        sensor.connect_to("conveyor_001")
        conveyor.connect_to(sensor.id)

    # Create robotic arms
    for i in range(3):
        robot = manager.create_object(
            f"robot_arm_{i:03d}",
            f"Robotic Arm {i}",
            ObjectType.ACTUATOR,
            x=i * 15 + 5,
            y=-5,
            z=3,
            material=MaterialType.COMPOSITE,
            mass=200.0,
        )
        robot.add_tag("automation")
        robot.add_tag("robot")

    print(f"Created factory with {len(manager.registry.objects)} objects")

    # Analyze factory layout
    center_of_mass = manager.calculate_center_of_mass()
    boundary = manager.get_boundary_box()

    print(f"Factory center of mass: {center_of_mass}")
    print(f"Factory dimensions: {boundary}")

    # Find all critical equipment
    critical_objects = manager.registry.get_objects_by_tags({"critical"})
    print(f"Critical equipment: {[obj.name for obj in critical_objects]}")

    # Analyze network connectivity
    network_metrics = manager.registry.analyze_network_metrics()
    print(
        f"Network connectivity: {network_metrics['average_degree']:.2f} avg connections per object"
    )

    # Set up event monitoring
    def factory_event_handler(event):
        print(f"Factory Event: {event.event_type.value} for {event.object_id}")

    manager.registry.add_event_handler(EventType.CREATED, factory_event_handler)
    manager.registry.add_event_handler(EventType.STATUS_CHANGED, factory_event_handler)

    return manager


def example_iot_sensor_network():
    """Example: IoT sensor network with real-time analytics."""
    print("\n=== IoT Sensor Network Example ===")

    # Create sensor manager and analytics
    sensor_manager = SensorManager()
    analytics = StreamingAnalytics()

    # Create data streams for different sensor types
    temp_stream = analytics.create_stream(
        "temperature", buffer_size=5000, window_duration=30.0
    )
    analytics.create_stream(
        "humidity", buffer_size=5000, window_duration=30.0
    )
    analytics.create_stream(
        "pressure", buffer_size=5000, window_duration=30.0
    )

    # Set up predictive analytics
    predictor = PredictiveAnalytics(min_data_points=10)

    # Set up alert conditions
    analytics.create_alert("temperature", "above", 40.0, "High temperature alert!")
    analytics.create_alert("humidity", "below", 20.0, "Low humidity warning!")

    # Simulate sensor data collection
    print("Generating sensor data...")

    for minute in range(10):  # Simulate 10 minutes
        base_temp = 25.0 + minute * 0.5  # Gradually increasing temperature
        base_humidity = 60.0 - minute * 0.3  # Gradually decreasing humidity
        base_pressure = 1013.25 + random.uniform(-2, 2)

        for _second in range(60):  # One reading per second
            # Add some noise
            temp = base_temp + random.uniform(-1, 1)
            humidity = base_humidity + random.uniform(-2, 2)
            pressure = base_pressure + random.uniform(-0.5, 0.5)

            # Add to streams
            analytics.add_data("temperature", temp, "sensor_001")
            analytics.add_data("humidity", humidity, "sensor_002")
            analytics.add_data("pressure", pressure, "sensor_003")

            # Also add to sensor manager for calibration/health monitoring
            sensor_manager.add_reading(
                SensorReading("sensor_001", SensorType.TEMPERATURE, temp, "°C")
            )
            sensor_manager.add_reading(
                SensorReading("sensor_002", SensorType.HUMIDITY, humidity, "%")
            )
            sensor_manager.add_reading(
                SensorReading("sensor_003", SensorType.PRESSURE, pressure, "hPa")
            )

    print("Data collection complete")

    # Get analytics summary
    summary = analytics.get_analytics_summary()
    print(f"Total streams: {summary['total_streams']}")

    # Get current metrics for temperature stream
    temp_metrics = temp_stream.get_current_metrics()
    if temp_metrics:
        print("Current temperature metrics:")
        for metric, value in temp_metrics.items():
            print(f"  {metric.value}: {value:.2f}")

    # Test predictive analytics
    temp_data = temp_stream.get_recent_data(300)  # Last 5 minutes
    if temp_data:
        prediction = predictor.predict_linear_trend(
            temp_data, 60.0
        )  # Predict 1 minute ahead
        if prediction:
            print(f"Temperature prediction (1 min): {prediction:.2f}°C")

    # Detect anomalies
    anomalies = predictor.detect_anomalies(temp_data)
    print(f"Detected {len(anomalies)} temperature anomalies")

    # Test sensor health
    temp_health = sensor_manager.get_sensor_health("sensor_001")
    print(f"Temperature sensor health: {temp_health['status']}")

    return analytics, sensor_manager


def example_physics_simulation_network():
    """Example: Physics simulation with connected objects and energy analysis."""
    print("\n=== Physics Simulation Network Example ===")

    # Create physics simulator
    sim = PhysicsSimulator()

    # Create object manager for tracking
    manager = PhysicalObjectManager()

    # Create a pendulum system with multiple masses
    pendulum_objects = []

    for i in range(5):
        # Create pendulum bob
        bob = manager.create_object(
            f"pendulum_bob_{i}",
            f"Pendulum Bob {i}",
            ObjectType.DEVICE,
            x=i * 2,
            y=10 - i * 0.5,
            z=0,
            material=MaterialType.METAL,
            mass=1.0 + i * 0.2,
        )
        bob.add_tag("pendulum")
        bob.add_tag("physics")

        pendulum_objects.append(bob)

        # Register in physics simulation
        position = Vector3D(i * 2, 10 - i * 0.5, 0)
        velocity = Vector3D(random.uniform(-1, 1), 0, 0)
        sim.register_object(bob.id, mass=bob.mass, position=position, velocity=velocity)

        # Connect to previous bob with spring
        if i > 0:
            prev_bob = pendulum_objects[i - 1]
            bob.connect_to(prev_bob.id)
            prev_bob.connect_to(bob.id)

            # Add spring constraint in physics
            sim.add_spring_constraint(
                prev_bob.id, bob.id, rest_length=2.0, spring_constant=100.0, damping=0.5
            )

    # Add some force fields
    attractor = ForceField(position=Vector3D(5, 0, 0), strength=50.0, falloff=2.0)
    sim.add_force_field(attractor)

    print(f"Created pendulum system with {len(pendulum_objects)} connected masses")

    # Run simulation and collect data
    analytics = StreamingAnalytics()
    energy_stream = analytics.create_stream("total_energy", window_duration=10.0)
    analytics.create_stream("kinetic_energy", window_duration=10.0)
    analytics.create_stream("potential_energy", window_duration=10.0)

    simulation_time = 0.0
    dt = 0.016  # 60 FPS

    print("Running physics simulation...")

    for step in range(600):  # 10 seconds of simulation
        sim.update_physics(dt)
        simulation_time += dt

        # Collect energy data every 10 steps
        if step % 10 == 0:
            stats = sim.get_simulation_stats()

            analytics.add_data("total_energy", stats["total_energy"], "simulator")
            analytics.add_data(
                "kinetic_energy", stats["total_kinetic_energy"], "simulator"
            )
            analytics.add_data(
                "potential_energy", stats["total_potential_energy"], "simulator"
            )

            # Update object positions in manager
            for obj in pendulum_objects:
                state = sim.get_object_state(obj.id)
                if state:
                    new_pos = state["position"]
                    manager.update_object_location(
                        obj.id, new_pos.x, new_pos.y, new_pos.z
                    )

    print(f"Simulation completed: {simulation_time:.2f}s simulated")

    # Analyze energy conservation
    energy_metrics = energy_stream.get_current_metrics()
    if energy_metrics:
        print("Energy analysis:")
        print(f"  Average total energy: {energy_metrics.get('mean', 0):.2f}")
        print(f"  Energy variation (std): {energy_metrics.get('std_dev', 0):.2f}")

    # Analyze network after simulation
    final_network_metrics = manager.registry.analyze_network_metrics()
    print(
        f"Network maintained {final_network_metrics['total_connections']} connections"
    )

    return sim, manager, analytics


def example_thermal_management():
    """Example: Thermal management system with heat transfer."""
    print("\n=== Thermal Management Example ===")

    manager = PhysicalObjectManager()
    analytics = StreamingAnalytics()

    # Create thermal management system
    heat_source = manager.create_object(
        "heat_source",
        "Heat Source",
        ObjectType.DEVICE,
        x=0,
        y=0,
        z=0,
        material=MaterialType.METAL,
        mass=50.0,
        temperature=373.15,  # 100°C
    )
    heat_source.add_tag("heat_source")

    # Create heat sinks around the source
    heat_sinks = []
    for i in range(8):
        angle = i * 45  # degrees
        x = 5 * math.cos(math.radians(angle))
        y = 5 * math.sin(math.radians(angle))

        sink = manager.create_object(
            f"heat_sink_{i}",
            f"Heat Sink {i}",
            ObjectType.DEVICE,
            x=x,
            y=y,
            z=0,
            material=MaterialType.METAL,
            mass=10.0,
            temperature=293.15,  # 20°C
        )
        sink.add_tag("heat_sink")
        heat_sinks.append(sink)

        # Connect to heat source for thermal network
        sink.connect_to("heat_source")
        heat_source.connect_to(sink.id)

    # Create temperature monitoring streams
    temp_streams = {}
    for sink in heat_sinks:
        stream_id = f"temp_{sink.id}"
        temp_streams[stream_id] = analytics.create_stream(
            stream_id, window_duration=20.0
        )

    # Simulate thermal equilibration
    print("Simulating thermal equilibration...")

    import math  # For thermal calculations

    for minute in range(5):  # 5 minutes of thermal simulation
        for second in range(60):
            current_time = minute * 60 + second

            # Simple thermal diffusion model
            for sink in heat_sinks:
                distance = sink.distance_to_point(0, 0, 0)  # Distance from heat source

                # Calculate temperature based on distance and time
                thermal_diffusion = math.exp(-distance / 10.0) * math.exp(
                    -current_time / 300.0
                )
                new_temp = 293.15 + (80 * thermal_diffusion)

                sink.update_temperature(new_temp)

                # Add to analytics
                stream_id = f"temp_{sink.id}"
                analytics.add_data(
                    stream_id, new_temp - 273.15, sink.id
                )  # Convert to Celsius

    print("Thermal simulation complete")

    # Analyze thermal distribution
    final_temps = [sink.temperature for sink in heat_sinks]
    avg_temp = sum(final_temps) / len(final_temps)
    temp_range = max(final_temps) - min(final_temps)

    print(f"Final average temperature: {avg_temp - 273.15:.2f}°C")
    print(f"Temperature range: {temp_range:.2f}K")

    # Calculate total thermal energy
    total_thermal = sum(sink.calculate_thermal_energy() for sink in heat_sinks)
    total_thermal += heat_source.calculate_thermal_energy()

    print(f"Total thermal energy: {total_thermal:.2f}J")

    return manager, analytics


def example_autonomous_vehicle_fleet():
    """Example: Autonomous vehicle fleet management with pathfinding."""
    print("\n=== Autonomous Vehicle Fleet Example ===")

    manager = PhysicalObjectManager()

    # Create charging stations
    charging_stations = []
    for i in range(4):
        station = manager.create_object(
            f"charging_station_{i}",
            f"Charging Station {i}",
            ObjectType.STRUCTURE,
            x=i * 50,
            y=0,
            z=0,
            material=MaterialType.METAL,
            mass=1000.0,
        )
        station.add_tag("charging")
        station.add_tag("infrastructure")
        charging_stations.append(station)

    # Create fleet of autonomous vehicles
    vehicles = []
    for i in range(10):
        vehicle = manager.create_object(
            f"vehicle_{i:03d}",
            f"Autonomous Vehicle {i}",
            ObjectType.VEHICLE,
            x=random.uniform(0, 150),
            y=random.uniform(-20, 20),
            z=0,
            material=MaterialType.COMPOSITE,
            mass=1500.0,
            charge_level=random.uniform(20, 100),
        )
        vehicle.add_tag("autonomous")
        vehicle.add_tag("fleet")
        vehicles.append(vehicle)

    # Create waypoints for navigation
    waypoints = []
    for i in range(20):
        waypoint = manager.create_object(
            f"waypoint_{i:02d}",
            f"Navigation Waypoint {i}",
            ObjectType.STRUCTURE,
            x=(i % 5) * 30,
            y=((i // 5) % 4) * 15 - 30,
            z=0,
            material=MaterialType.UNKNOWN,
            mass=0.1,
        )
        waypoint.add_tag("navigation")
        waypoints.append(waypoint)

    print(
        f"Fleet setup: {len(vehicles)} vehicles, {len(charging_stations)} charging stations, {len(waypoints)} waypoints"
    )

    # Connect waypoints to create navigation network
    for i, waypoint in enumerate(waypoints):
        # Connect to nearby waypoints
        for other in waypoints:
            if waypoint.id != other.id and waypoint.distance_to(other) < 35:
                waypoint.connect_to(other.id)

    # Connect vehicles to nearby waypoints
    for vehicle in vehicles:
        nearest_waypoint = manager.registry.find_nearest_object(
            *vehicle.location, ObjectType.STRUCTURE
        )
        if nearest_waypoint and nearest_waypoint.has_tag("navigation"):
            vehicle.connect_to(nearest_waypoint.id)

    # Find routes for low-charge vehicles to charging stations
    low_charge_vehicles = [
        v for v in vehicles if v.properties.get("charge_level", 100) < 30
    ]

    print(f"Found {len(low_charge_vehicles)} vehicles needing charge")

    for vehicle in low_charge_vehicles:
        # Find nearest charging station
        nearest_station = manager.registry.find_nearest_object(
            *vehicle.location, ObjectType.STRUCTURE
        )

        if nearest_station and nearest_station.has_tag("charging"):
            # Try to find path through waypoint network
            path = manager.find_path_between_objects(vehicle.id, nearest_station.id)
            if path:
                print(
                    f"Route found for {vehicle.name}: {len(path)} waypoints to {nearest_station.name}"
                )
            else:
                print(f"No route found for {vehicle.name}")

    # Analyze fleet metrics
    fleet_stats = manager.get_statistics()
    network_stats = manager.registry.analyze_network_metrics()

    print("Fleet statistics:")
    print(f"  Total objects: {fleet_stats['total_objects']}")
    print(f"  Network density: {network_stats['density']:.3f}")
    print(f"  Average connections: {network_stats['average_degree']:.1f}")

    return manager


def example_distributed_sensor_calibration():
    """Example: Distributed sensor calibration and drift detection."""
    print("\n=== Distributed Sensor Calibration Example ===")

    sensor_manager = SensorManager()

    # Create multiple temperature sensors with slight variations
    sensor_ids = [f"temp_sensor_{i:03d}" for i in range(10)]

    # Generate baseline readings with slight sensor bias
    sensor_bias = {sensor_id: random.uniform(-0.5, 0.5) for sensor_id in sensor_ids}

    print("Generating baseline sensor data...")

    # Generate 24 hours of baseline data
    base_time = time.time() - 86400  # 24 hours ago
    true_temperature = 25.0

    for hour in range(24):
        # Daily temperature variation
        daily_temp = true_temperature + 5 * math.sin((hour / 24) * 2 * math.pi)

        for sensor_id in sensor_ids:
            # Each sensor has its own bias and noise
            bias = sensor_bias[sensor_id]
            noise = random.uniform(-0.2, 0.2)
            measured_temp = daily_temp + bias + noise

            reading = SensorReading(
                sensor_id,
                SensorType.TEMPERATURE,
                measured_temp,
                "°C",
                timestamp=base_time + hour * 3600,
            )
            sensor_manager.add_reading(reading)

    # Calibrate sensors using reference measurements
    print("Calibrating sensors...")

    calibration_results = {}
    for sensor_id in sensor_ids:
        # Create reference points (simulated calibration chamber readings)
        reference_temps = [15.0, 25.0, 35.0]  # Known reference temperatures
        reference_points = []

        for ref_temp in reference_temps:
            # Simulate what sensor would read at reference temperature
            bias = sensor_bias[sensor_id]
            measured = ref_temp + bias + random.uniform(-0.05, 0.05)
            reference_points.append((measured, ref_temp))

        # Calibrate
        calibration = sensor_manager.calibrate_sensor(
            sensor_id, reference_points, SensorType.TEMPERATURE
        )
        calibration_results[sensor_id] = calibration

    print(f"Calibrated {len(calibration_results)} sensors")

    # Generate recent data with drift for some sensors
    print("Simulating sensor drift...")

    recent_time = time.time() - 3600  # 1 hour ago
    drifting_sensors = sensor_ids[:3]  # First 3 sensors will drift

    for minute in range(60):
        current_temp = 24.0 + random.uniform(-1, 1)

        for sensor_id in sensor_ids:
            bias = sensor_bias[sensor_id]

            # Add drift for some sensors
            if sensor_id in drifting_sensors:
                drift_amount = minute * 0.02  # Gradual drift
                bias += drift_amount

            noise = random.uniform(-0.1, 0.1)
            measured_temp = current_temp + bias + noise

            reading = SensorReading(
                sensor_id,
                SensorType.TEMPERATURE,
                measured_temp,
                "°C",
                timestamp=recent_time + minute * 60,
            )
            sensor_manager.add_reading(reading)

    # Analyze sensor health and drift
    print("Analyzing sensor performance...")

    for sensor_id in sensor_ids:
        health = sensor_manager.get_sensor_health(sensor_id)
        drift = sensor_manager.detect_sensor_drift(sensor_id)

        status_indicator = "⚠️" if health["status"] != "healthy" else "✅"
        drift_indicator = "📈" if "drift" in drift["status"] else "📊"

        print(
            f"  {sensor_id}: {status_indicator} {health['status']}, {drift_indicator} {drift['status']}"
        )

    return sensor_manager, calibration_results


if __name__ == "__main__":
    # Run all examples
    import math

    print("Running Physical Management Advanced Examples")
    print("=" * 50)

    try:
        factory_manager = example_smart_factory_monitoring()
        print("✅ Smart factory example completed")

        iot_analytics, iot_sensors = example_iot_sensor_network()
        print("✅ IoT sensor network example completed")

        sim, physics_manager, physics_analytics = example_physics_simulation_network()
        print("✅ Physics simulation example completed")

        sensors, calibrations = example_distributed_sensor_calibration()
        print("✅ Sensor calibration example completed")

        print("\n" + "=" * 50)
        print("All examples completed successfully! 🎉")

        # Summary statistics
        total_objects = sum(
            len(m.registry.objects) for m in [factory_manager, physics_manager] if m
        )
        print(f"Total objects created across examples: {total_objects}")

    except Exception as e:
        print(f"Error in examples: {e}")
        raise
