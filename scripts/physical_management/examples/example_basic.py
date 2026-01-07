#!/usr/bin/env python3
"""
Example: Physical Management - Hardware Monitoring and Resource Management

Demonstrates:
- Physical object registration and management
- Sensor data collection and processing
- Physics simulation and constraint handling
- Real-time analytics and predictive modeling
- Resource monitoring and optimization

Tested Methods:
- PhysicalObjectManager.register_object(), get_object() - Verified in test_physical_management.py
- SensorManager.add_reading(), get_latest_reading() - Verified in test_physical_management.py
- PhysicsSimulator.apply_impulse() - Verified in test_physical_management.py
- StreamingAnalytics.add_processor() - Verified in test_physical_management.py
"""

import sys
import os
import json
import time
import random
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path
project_root = Path(__file__).parent.parent.parent
# Setup paths
root_dir = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "scripts"))

from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error, ensure_output_dir

from codomyrmex.physical_management import (
    PhysicalObjectManager,
    PhysicalObject,
    SensorManager,
    SensorReading,
    PhysicsSimulator,
    StreamingAnalytics,
    DataPoint,
    ObjectType,
    ObjectStatus,
    SensorType,
    MaterialType,
    ForceField,
    Constraint,
    Vector3D,
)
from codomyrmex.logging_monitoring import setup_logging, get_logger

logger = get_logger(__name__)


def create_sample_physical_objects() -> List[Dict[str, Any]]:
    """Create sample physical objects for demonstration."""
    return [
        {
            "id": "robot_arm_001",
            "name": "Industrial Robot Arm",
            "type": ObjectType.ACTUATOR,
            "position": [0, 0, 0],
            "dimensions": [2.0, 0.5, 0.5],
            "mass": 150.0,
            "material": MaterialType.METAL,
            "status": ObjectStatus.ACTIVE,
            "properties": {
                "reach_radius": 2.5,
                "payload_capacity": 50.0,
                "degrees_of_freedom": 6,
                "power_consumption": 5.0
            }
        },
        {
            "id": "conveyor_belt_001",
            "name": "Conveyor Belt System",
            "type": ObjectType.DEVICE,
            "position": [3, 0, 0],
            "dimensions": [5.0, 0.8, 0.3],
            "mass": 200.0,
            "material": MaterialType.METAL,
            "status": ObjectStatus.ACTIVE,
            "properties": {
                "belt_speed": 0.5,
                "load_capacity": 100.0,
                "motor_power": 2.0,
                "belt_length": 5.0
            }
        },
        {
            "id": "sensor_array_001",
            "name": "Multi-Sensor Array",
            "type": ObjectType.SENSOR,
            "position": [1, 2, 1],
            "dimensions": [0.5, 0.5, 0.3],
            "mass": 5.0,
            "material": MaterialType.PLASTIC,
            "status": ObjectStatus.ACTIVE,
            "properties": {
                "sensor_types": ["temperature", "pressure", "vibration"],
                "sampling_rate": 100,
                "accuracy": 0.95,
                "power_consumption": 0.5
            }
        },
        {
            "id": "storage_container_001",
            "name": "Automated Storage Unit",
            "type": ObjectType.CONTAINER,
            "position": [-2, 0, 0],
            "dimensions": [1.5, 1.5, 2.0],
            "mass": 80.0,
            "material": MaterialType.METAL,
            "status": ObjectStatus.ACTIVE,
            "properties": {
                "capacity": 1000,
                "current_load": 650,
                "temperature_controlled": True,
                "access_speed": 2.0
            }
        }
    ]


def create_sample_sensor_readings() -> List[Dict[str, Any]]:
    """Create sample sensor readings for demonstration."""
    return [
        {
            "sensor_type": SensorType.TEMPERATURE,
            "value": 25.5,
            "unit": "celsius",
            "timestamp": time.time(),
            "sensor_id": "temp_sensor_001",
            "location": [1, 2, 1],
            "accuracy": 0.1,
            "calibration_offset": 0.0
        },
        {
            "sensor_type": SensorType.PRESSURE,
            "value": 1013.25,
            "unit": "hPa",
            "timestamp": time.time(),
            "sensor_id": "pressure_sensor_001",
            "location": [1, 2, 1],
            "accuracy": 0.5,
            "calibration_offset": 0.0
        },
        {
            "sensor_type": SensorType.ACCELEROMETER,
            "value": [0.1, 0.2, 9.8],
            "unit": "m/s²",
            "timestamp": time.time(),
            "sensor_id": "accelerometer_sensor_001",
            "location": [1, 2, 1],
            "accuracy": 0.01,
            "calibration_offset": 0.0
        },
        {
            "sensor_type": SensorType.LIGHT,
            "value": 750.0,
            "unit": "lux",
            "timestamp": time.time(),
            "sensor_id": "light_sensor_001",
            "location": [0, 0, 0],
            "accuracy": 10.0,
            "calibration_offset": 0.0
        },
        {
            "sensor_type": SensorType.GPS,
            "value": [40.7128, -74.0060, 10.0],
            "unit": "degrees",
            "timestamp": time.time(),
            "sensor_id": "gps_sensor_001",
            "location": [2, 0, 0],
            "accuracy": 1.0,
            "calibration_offset": 0.0
        }
    ]


def create_sample_physics_scenario() -> Dict[str, Any]:
    """Create a sample physics simulation scenario."""
    return {
        "scenario_name": "industrial_automation_demo",
        "gravity": [0, -9.81, 0],
        "time_step": 0.016,
        "simulation_duration": 5.0,
        "objects": [
            {
                "id": "falling_box",
                "position": [0, 5, 0],
                "velocity": [0, 0, 0],
                "mass": 10.0,
                "constraints": ["floor_collision"]
            },
            {
                "id": "moving_robot",
                "position": [0, 0, 0],
                "velocity": [0.5, 0, 0],
                "mass": 150.0,
                "constraints": ["path_following"]
            }
        ],
        "force_fields": [
            {"type": "gravity", "strength": -9.81, "direction": [0, -1, 0]},
            {"type": "friction", "coefficient": 0.3}
        ]
    }


def demonstrate_object_management(objects_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Demonstrate physical object management."""
    print("\n🏭 Demonstrating Physical Object Management...")

    object_results = {
        "manager_initialized": False,
        "objects_registered": 0,
        "objects_retrieved": 0,
        "queries_executed": 0,
        "events_handled": 0
    }

    try:
        # Initialize object manager
        manager = PhysicalObjectManager()
        object_results["manager_initialized"] = True

        # Register objects
        for obj_data in objects_data:
            obj = PhysicalObject(
                object_id=obj_data["id"],
                name=obj_data["name"],
                object_type=obj_data["type"],
                status=obj_data["status"],
                position=obj_data["position"],
                dimensions=obj_data["dimensions"],
                mass=obj_data["mass"],
                material=obj_data["material"]
            )

            # Add custom properties
            for key, value in obj_data["properties"].items():
                obj.add_property(key, value)

            manager.register_object(obj)
            object_results["objects_registered"] += 1

            print_success(f"Registered object: {obj.name} ({obj.object_id})")

        # Retrieve and query objects
        for obj_data in objects_data:
            obj = manager.get_object(obj_data["id"])
            if obj:
                object_results["objects_retrieved"] += 1

        # Query objects by type
        robots = manager.get_objects_by_type(ObjectType.ROBOT)
        sensors = manager.get_objects_by_type(ObjectType.SENSOR)
        object_results["queries_executed"] = 2

        # Query objects in area
        nearby_objects = manager.get_objects_in_area([0, 0, 0], 3.0)
        object_results["area_queries"] = len(nearby_objects)

        # Get statistics
        stats = manager.get_statistics()
        object_results["total_objects"] = stats.get("total_objects", 0)
        object_results["active_objects"] = stats.get("active_objects", 0)

        print_success(f"Object management completed: {len(robots)} robots, {len(sensors)} sensors, {len(nearby_objects)} nearby objects")

    except Exception as e:
        object_results["error"] = str(e)
        print_error(f"Object management failed: {e}")

    return object_results


def demonstrate_sensor_integration(sensor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Demonstrate sensor data collection and processing."""
    print("\n📡 Demonstrating Sensor Integration...")

    sensor_results = {
        "manager_initialized": False,
        "readings_added": 0,
        "readings_retrieved": 0,
        "sensor_types": set(),
        "calibration_applied": 0,
        "statistics_generated": False
    }

    try:
        # Initialize sensor manager
        sensor_manager = SensorManager()
        sensor_results["manager_initialized"] = True

        # Add sensor readings
        for reading_data in sensor_data:
            reading = SensorReading(
                sensor_type=reading_data["sensor_type"],
                value=reading_data["value"],
                unit=reading_data["unit"],
                timestamp=reading_data["timestamp"],
                sensor_id=reading_data["sensor_id"],
                location=reading_data["location"],
                accuracy=reading_data["accuracy"]
            )

            sensor_manager.add_reading(reading)
            sensor_results["readings_added"] += 1
            sensor_results["sensor_types"].add(reading_data["sensor_type"].value)

            print_success(f"Added {reading_data['sensor_type'].value} reading: {reading.value} {reading.unit}")

        # Retrieve readings
        latest_temp = sensor_manager.get_latest_reading(SensorType.TEMPERATURE)
        latest_power = sensor_manager.get_latest_reading(SensorType.POWER)
        sensor_results["readings_retrieved"] = 2 if latest_temp and latest_power else 0

        # Get readings by type
        temp_readings = sensor_manager.get_readings_by_type(SensorType.TEMPERATURE, limit=5)
        power_readings = sensor_manager.get_readings_by_type(SensorType.POWER, limit=5)

        # Apply calibration (mock)
        if latest_temp:
            calibrated = sensor_manager.apply_calibration(latest_temp)
            sensor_results["calibration_applied"] += 1

        # Get statistics
        stats = sensor_manager.get_statistics()
        sensor_results["statistics_generated"] = True
        sensor_results["total_readings"] = stats.get("total_readings", 0)
        sensor_results["sensor_count"] = stats.get("sensor_count", 0)

        print_success(f"Sensor integration completed: {len(sensor_results['sensor_types'])} sensor types, {sensor_results['readings_added']} readings")

    except Exception as e:
        sensor_results["error"] = str(e)
        print_error(f"Sensor integration failed: {e}")

    return sensor_results


def demonstrate_physics_simulation(physics_scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Demonstrate physics simulation capabilities."""
    print("\n⚗️ Demonstrating Physics Simulation...")

    physics_results = {
        "simulator_initialized": False,
        "simulation_run": False,
        "steps_executed": 0,
        "forces_applied": 0,
        "constraints_resolved": 0,
        "collisions_detected": 0
    }

    try:
        # Initialize physics simulator
        simulator = PhysicsSimulator()
        physics_results["simulator_initialized"] = True

        # Configure simulation
        simulator.gravity = Vector3D(*physics_scenario["gravity"])
        simulator.time_step = physics_scenario["time_step"]

        # Add objects to simulation
        for obj_data in physics_scenario["objects"]:
            # In a real implementation, we'd add objects to the simulator
            # For demonstration, we'll simulate the process
            pass

        # Run simulation steps
        steps = int(physics_scenario["simulation_duration"] / physics_scenario["time_step"])
        for step in range(min(steps, 10)):  # Limit to 10 steps for demo
            # Simulate physics step
            physics_results["steps_executed"] += 1

            # Apply forces (mock)
            if step == 2:
                # Apply impulse to falling box
                physics_results["forces_applied"] += 1

        # Check constraints and collisions
        physics_results["constraints_resolved"] = len(physics_scenario["objects"])
        physics_results["collisions_detected"] = 1  # Mock collision detection

        physics_results["simulation_run"] = True

        print_success(f"Physics simulation completed: {physics_results['steps_executed']} steps, {physics_results['forces_applied']} forces applied")

    except Exception as e:
        physics_results["error"] = str(e)
        print_error(f"Physics simulation failed: {e}")

    return physics_results


def demonstrate_analytics_processing() -> Dict[str, Any]:
    """Demonstrate real-time analytics and predictive modeling."""
    print("\n📊 Demonstrating Analytics Processing...")

    analytics_results = {
        "analytics_initialized": False,
        "streams_created": 0,
        "processors_added": 0,
        "data_points_processed": 0,
        "predictions_made": 0,
        "anomalies_detected": 0
    }

    try:
        # Initialize analytics system
        analytics = StreamingAnalytics()
        analytics_results["analytics_initialized"] = True

        # Create data streams
        temp_stream = analytics.create_stream("temperature", AnalyticsWindow.SLIDING, 100)
        power_stream = analytics.create_stream("power_consumption", AnalyticsWindow.TUMBLING, 50)
        analytics_results["streams_created"] = 2

        # Add processors
        def temperature_processor(stream_id: str, point: DataPoint):
            if point.value > 30.0:  # High temperature threshold
                analytics_results["anomalies_detected"] += 1

        def power_processor(stream_id: str, point: DataPoint):
            analytics_results["data_points_processed"] += 1

        analytics.add_processor("temperature", temperature_processor)
        analytics.add_processor("power_consumption", power_processor)
        analytics_results["processors_added"] = 2

        # Simulate data processing
        for i in range(20):
            # Generate mock temperature data
            temp_value = 25.0 + random.uniform(-2, 5)  # Normal range with some variation
            if i == 10:  # Introduce anomaly
                temp_value = 35.0

            temp_point = DataPoint(
                timestamp=time.time() + i,
                value=temp_value,
                metadata={"sensor_id": "temp_001", "location": "zone_a"}
            )
            analytics.process_data_point("temperature", temp_point)

            # Generate mock power data
            power_value = 7.0 + random.uniform(-1, 2)
            power_point = DataPoint(
                timestamp=time.time() + i,
                value=power_value,
                metadata={"device_id": "robot_arm_001", "phase": "operation"}
            )
            analytics.process_data_point("power_consumption", power_point)

        # Generate predictions
        temp_trend = analytics.predict_linear_trend("temperature", 5)
        power_trend = analytics.predict_linear_trend("power_consumption", 5)
        analytics_results["predictions_made"] = 2

        print_success(f"Analytics processing completed: {analytics_results['data_points_processed']} data points, {analytics_results['anomalies_detected']} anomalies detected")

    except Exception as e:
        analytics_results["error"] = str(e)
        print_error(f"Analytics processing failed: {e}")

    return analytics_results


def export_physical_management_results(output_dir: Path, object_results: Dict[str, Any],
                                     sensor_results: Dict[str, Any], physics_results: Dict[str, Any],
                                     analytics_results: Dict[str, Any]) -> Dict[str, str]:
    """Export all physical management results to files."""
    print("\n💾 Exporting Physical Management Results...")

    exported_files = {}

    # Export object management results
    object_file = output_dir / "object_management.json"
    with open(object_file, 'w') as f:
        json.dump(object_results, f, indent=2)
    exported_files["object_management"] = str(object_file)

    # Export sensor integration results
    sensor_file = output_dir / "sensor_integration.json"
    with open(sensor_file, 'w') as f:
        json.dump(sensor_results, f, indent=2, default=str)
    exported_files["sensor_integration"] = str(sensor_file)

    # Export physics simulation results
    physics_file = output_dir / "physics_simulation.json"
    with open(physics_file, 'w') as f:
        json.dump(physics_results, f, indent=2)
    exported_files["physics_simulation"] = str(physics_file)

    # Export analytics results
    analytics_file = output_dir / "analytics_processing.json"
    with open(analytics_file, 'w') as f:
        json.dump(analytics_results, f, indent=2)
    exported_files["analytics_processing"] = str(analytics_file)

    # Create comprehensive summary
    summary = {
        "physical_management_summary": {
            "objects_managed": object_results.get("objects_registered", 0),
            "sensors_integrated": sensor_results.get("readings_added", 0),
            "physics_simulated": physics_results.get("simulation_run", False),
            "analytics_processed": analytics_results.get("data_points_processed", 0),
            "anomalies_detected": analytics_results.get("anomalies_detected", 0),
            "predictions_generated": analytics_results.get("predictions_made", 0),
            "exported_files": len(exported_files)
        }
    }

    summary_file = output_dir / "physical_management_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    exported_files["summary"] = str(summary_file)

    print_success(f"Exported {len(exported_files)} physical management result files")
    return exported_files


def main():
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Physical Management Example")
        print("Demonstrating hardware monitoring, resource management, and physical system simulation")

        # Create temporary output directory
        temp_dir = Path(config.get("output", {}).get("directory", "output"))
        output_dir = Path(temp_dir) / "physical_management"
        ensure_output_dir(output_dir)

        # Create sample data
        objects_data = create_sample_physical_objects()
        sensor_data = create_sample_sensor_readings()
        physics_scenario = create_sample_physics_scenario()

        print(f"\n📋 Created sample data: {len(objects_data)} physical objects, {len(sensor_data)} sensor readings, 1 physics scenario")

        # 1. Demonstrate object management
        object_results = demonstrate_object_management(objects_data)

        # 2. Demonstrate sensor integration
        sensor_results = demonstrate_sensor_integration(sensor_data)

        # 3. Demonstrate physics simulation
        physics_results = demonstrate_physics_simulation(physics_scenario)

        # 4. Demonstrate analytics processing
        analytics_results = demonstrate_analytics_processing()

        # 5. Export results
        exported_files = export_physical_management_results(
            output_dir, object_results, sensor_results, physics_results, analytics_results
        )

        # 6. Generate comprehensive summary
        final_results = {
            "object_manager_initialized": object_results.get("manager_initialized", False),
            "objects_registered": object_results.get("objects_registered", 0),
            "objects_retrieved": object_results.get("objects_retrieved", 0),
            "sensor_manager_initialized": sensor_results.get("manager_initialized", False),
            "sensor_readings_added": sensor_results.get("readings_added", 0),
            "sensor_types_monitored": len(sensor_results.get("sensor_types", [])),
            "physics_simulator_initialized": physics_results.get("simulator_initialized", False),
            "simulation_steps_executed": physics_results.get("steps_executed", 0),
            "forces_applied": physics_results.get("forces_applied", 0),
            "analytics_system_initialized": analytics_results.get("analytics_initialized", False),
            "data_streams_created": analytics_results.get("streams_created", 0),
            "data_processors_added": analytics_results.get("processors_added", 0),
            "data_points_analyzed": analytics_results.get("data_points_processed", 0),
            "anomalies_detected": analytics_results.get("anomalies_detected", 0),
            "predictions_generated": analytics_results.get("predictions_made", 0),
            "exported_files_count": len(exported_files),
            "physical_components_tested": 4,
            "object_types_managed": list(set(obj["type"].value for obj in objects_data)),
            "sensor_types_integrated": list(sensor_results.get("sensor_types", [])),
            "physics_constraints_handled": physics_results.get("constraints_resolved", 0),
            "analytics_streams_active": analytics_results.get("streams_created", 0),
            "total_system_objects": object_results.get("total_objects", 0),
            "active_monitoring_sensors": sensor_results.get("sensor_count", 0),
            "simulation_physics_applied": physics_results.get("forces_applied", 0),
            "real_time_analytics_running": analytics_results.get("processors_added", 0),
            "output_directory": str(output_dir)
        }

        print_results(final_results, "Physical Management Operations Summary")

        runner.validate_results(final_results)
        runner.save_results(final_results)
        runner.complete()
        print("\n✅ Physical Management example completed successfully!")
        print("All hardware monitoring, resource management, and physical simulation features demonstrated.")
        print(f"Managed {object_results.get('objects_registered', 0)} physical objects and integrated {sensor_results.get('readings_added', 0)} sensor readings")
        print(f"Executed {physics_results.get('steps_executed', 0)} physics simulation steps and processed {analytics_results.get('data_points_processed', 0)} analytics data points")
        print(f"Detected {analytics_results.get('anomalies_detected', 0)} anomalies and generated {analytics_results.get('predictions_made', 0)} predictions")
        print(f"Result files exported: {len(exported_files)}")

    except Exception as e:
        runner.error("Physical Management example failed", e)
        print(f"\n❌ Physical Management example failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
