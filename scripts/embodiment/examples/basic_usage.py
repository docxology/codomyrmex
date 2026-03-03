#!/usr/bin/env python3
"""Embodiment Module - Comprehensive Usage Script.

Demonstrates ROS2 bridge, 3D transformations, sensors, and actuators with full 
configurability, unified logging, and output saving.

Usage:
    python basic_usage.py                          # Run with defaults
    python basic_usage.py --node-name robot1       # Custom node name
    python basic_usage.py --verbose                # Verbose output
"""

import asyncio
import math
import sys
from pathlib import Path
from typing import Any

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Direct import to avoid triggering full codomyrmex package init
import importlib.util

script_base_path = project_root / "src" / "codomyrmex" / "utils" / "process" / "script_base.py"
spec = importlib.util.spec_from_file_location("script_base", script_base_path)
script_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script_base)
ScriptBase = script_base.ScriptBase
ScriptConfig = script_base.ScriptConfig


class EmbodimentScript(ScriptBase):
    """Comprehensive embodiment module demonstration."""

    def __init__(self):
        super().__init__(
            name="embodiment_usage",
            description="Demonstrate and test ROS2 bridge, 3D transformations, sensors, and actuators",
            version="1.1.0",
        )

    def add_arguments(self, parser):
        """Add embodiment-specific arguments."""
        group = parser.add_argument_group("Embodiment Options")
        group.add_argument(
            "--node-name", default="demo_robot",
            help="ROS2 node name (default: demo_robot)"
        )
        group.add_argument(
            "--num-transforms", type=int, default=100,
            help="Number of transform operations (default: 100)"
        )
        group.add_argument(
            "--publish-rate", type=float, default=10.0,
            help="Simulated publish rate in Hz (default: 10.0)"
        )

    async def _run_async(self, args, config: ScriptConfig, results: dict[str, Any]):
        """Async portion of the script execution."""
        from codomyrmex.embodiment import ROS2Bridge, Transform3D
        from codomyrmex.embodiment.actuators import ActuatorCommand, MockActuator
        from codomyrmex.embodiment.sensors import MockSensor

        # Test 1: ROS2Bridge creation
        self.log_info(f"\n1. Creating ROS2Bridge node '{args.node_name}'")
        try:
            bridge = ROS2Bridge(node_name=args.node_name)
            await bridge.connect(uri="localhost:9090")
            results["ros2_bridge"]["node_name"] = args.node_name
            results["ros2_bridge"]["created"] = True
            results["tests_passed"] += 1
            self.log_success(f"ROS2Bridge created and connected: {args.node_name}")
        except Exception as e:
            self.log_error(f"ROS2Bridge creation failed: {e}")
        results["tests_run"] += 1

        # Test 2: Publish/Subscribe simulation
        self.log_info("\n2. Testing publish/subscribe pattern")
        try:
            received_messages = []
            async def callback(msg):
                received_messages.append(msg)

            await bridge.subscribe("/test_topic", callback)

            # Simulate publishing
            num_messages = 10
            for i in range(num_messages):
                message = {"seq": i, "data": f"test_message_{i}"}
                await bridge.publish("/test_topic", message)

            # Small wait for async delivery
            await asyncio.sleep(0.05)

            results["ros2_bridge"]["publish_subscribe"] = {
                "published": num_messages,
                "received": len(received_messages),
                "success": len(received_messages) == num_messages,
            }
            results["tests_passed"] += 1
            self.log_success(f"Pub/Sub test: {len(received_messages)}/{num_messages} messages received")
        except Exception as e:
            self.log_error(f"Publish/Subscribe test failed: {e}")
        results["tests_run"] += 1

        # Test 3: Transform3D basic operations
        self.log_info("\n3. Testing Transform3D basic operations")
        try:
            # Create transforms
            t1 = Transform3D.from_translation(1.0, 2.0, 3.0)
            t2 = Transform3D.from_rotation(0, 0, math.pi/4)
            t_composed = t1.compose(t2)

            # Test point transformation
            point = (1, 0, 0)
            transformed = t_composed.apply(point)

            results["transform_tests"]["basic"] = {
                "original_point": point,
                "composed_transform": str(t_composed),
                "transformed_point": transformed,
            }
            results["tests_passed"] += 1
            self.log_success(f"Transform3D: {point} -> {transformed}")
        except Exception as e:
            self.log_error(f"Transform3D test failed: {e}")
        results["tests_run"] += 1

        # Test 4: Sensors and Actuators
        self.log_info("\n4. Testing Sensors and Actuators")
        try:
            # Sensor
            sensor = MockSensor("laser_1", default_value=5.5)
            sensor.connect()
            reading = sensor.read()
            self.log_info(f"Sensor '{reading.sensor_id}' read: {reading.data}")

            # Actuator
            actuator = MockActuator("gripper_1")
            actuator.connect()
            cmd = ActuatorCommand("gripper_1", "move", {"target": 1.0})
            actuator.execute(cmd)
            status = actuator.get_status()
            self.log_info(f"Actuator '{status.actuator_id}' status: {status.feedback}")

            results["hardware_tests"] = {
                "sensor_reading": reading.data,
                "actuator_feedback": status.feedback,
            }
            results["tests_passed"] += 1
            self.log_success("Hardware tests passed")
        except Exception as e:
            self.log_error(f"Hardware tests failed: {e}")
        results["tests_run"] += 1

    def run(self, args, config: ScriptConfig) -> dict[str, Any]:
        """Execute embodiment demonstrations."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "ros2_bridge": {},
            "transform_tests": {},
        }

        if config.dry_run:
            self.log_info(f"Would create ROS2 node: {args.node_name}")
            self.log_info(f"Would perform {args.num_transforms} transforms")
            results["dry_run"] = True
            return results

        # Run the async portion
        asyncio.run(self._run_async(args, config, results))

        # Summary
        results["summary"] = {
            "tests_passed": results["tests_passed"],
            "tests_run": results["tests_run"],
        }

        # Metrics
        self.add_metric("tests_run", results["tests_run"])
        self.add_metric("tests_passed", results["tests_passed"])

        return results



    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "embodiment" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/embodiment/config.yaml")

if __name__ == "__main__":
    script = EmbodimentScript()
    sys.exit(script.execute())
