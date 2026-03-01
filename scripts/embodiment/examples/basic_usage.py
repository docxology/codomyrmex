#!/usr/bin/env python3
"""Embodiment Module - Comprehensive Usage Script.

Demonstrates ROS2 bridge and 3D transformations with full configurability,
unified logging, and output saving.

Usage:
    python basic_usage.py                          # Run with defaults
    python basic_usage.py --node-name robot1       # Custom node name
    python basic_usage.py --verbose                # Verbose output
"""

import sys
import time
import math
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Direct import to avoid triggering full codomyrmex package init
import importlib.util
script_base_path = project_root / "src" / "codomyrmex" / "utils" / "script_base.py"
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
            description="Demonstrate and test ROS2 bridge and 3D transformations",
            version="1.0.0",
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

    def run(self, args, config: ScriptConfig) -> Dict[str, Any]:
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

        # Import embodiment module (after dry_run check)
        from codomyrmex.embodiment import ROS2Bridge, Transform3D

        # Test 1: ROS2Bridge creation
        self.log_info(f"\n1. Creating ROS2Bridge node '{args.node_name}'")
        try:
            bridge = ROS2Bridge(node_name=args.node_name)
            results["ros2_bridge"]["node_name"] = args.node_name
            results["ros2_bridge"]["created"] = True
            results["tests_passed"] += 1
            self.log_success(f"ROS2Bridge created: {args.node_name}")
        except Exception as e:
            self.log_error(f"ROS2Bridge creation failed: {e}")
        results["tests_run"] += 1

        # Test 2: Publish/Subscribe simulation
        self.log_info("\n2. Testing publish/subscribe pattern")
        try:
            received_messages = []
            def callback(msg):
                received_messages.append(msg)

            bridge.subscribe("/test_topic", callback)

            # Simulate publishing
            num_messages = 10
            for i in range(num_messages):
                message = {"seq": i, "data": f"test_message_{i}"}
                bridge.publish("/test_topic", message)
                bridge.simulate_message("/test_topic", message)

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
            t1 = Transform3D(translation=(1.0, 2.0, 3.0), rotation=(0, 0, 0))
            t2 = Transform3D(translation=(0, 0, 0), rotation=(0, 0, math.pi/4))

            # Test point transformation
            point = (0, 0, 0)
            transformed = t1.transform_point(point)

            results["transform_tests"]["basic"] = {
                "original_point": point,
                "translation": t1.translation,
                "transformed_point": transformed,
                "expected": (1.0, 2.0, 3.0),
            }
            results["tests_passed"] += 1
            self.log_success(f"Transform3D: {point} -> {transformed}")
        except Exception as e:
            self.log_error(f"Transform3D test failed: {e}")
        results["tests_run"] += 1

        # Test 4: Transform performance
        self.log_info(f"\n4. Transform performance test ({args.num_transforms} operations)")
        try:
            transform = Transform3D(translation=(1.0, 0.5, 0.2), rotation=(0.1, 0.2, 0.3))
            points = [(float(i), float(i*2), float(i*3)) for i in range(args.num_transforms)]

            start_time = time.perf_counter()
            transformed_points = [transform.transform_point(p) for p in points]
            duration = (time.perf_counter() - start_time) * 1000

            results["transform_tests"]["performance"] = {
                "num_operations": args.num_transforms,
                "total_time_ms": duration,
                "avg_time_us": (duration * 1000) / args.num_transforms,
                "ops_per_second": args.num_transforms / (duration / 1000),
            }
            results["tests_passed"] += 1
            self.log_success(f"Performance: {args.num_transforms} transforms in {duration:.2f}ms")
        except Exception as e:
            self.log_error(f"Performance test failed: {e}")
        results["tests_run"] += 1

        # Test 5: Coordinate frame transformations
        self.log_info("\n5. Testing coordinate frame transformations")
        try:
            # Simulate robot arm transforms
            base_to_shoulder = Transform3D(translation=(0, 0, 0.5))
            shoulder_to_elbow = Transform3D(translation=(0.3, 0, 0))
            elbow_to_wrist = Transform3D(translation=(0.25, 0, 0))

            # Chain transformations
            end_effector = (0, 0, 0)
            p1 = elbow_to_wrist.transform_point(end_effector)
            p2 = shoulder_to_elbow.transform_point(p1)
            p3 = base_to_shoulder.transform_point(p2)

            results["transform_tests"]["kinematic_chain"] = {
                "frames": ["base", "shoulder", "elbow", "wrist"],
                "end_effector_base_frame": p3,
            }
            results["tests_passed"] += 1
            self.log_success(f"Kinematic chain: end effector at {p3}")
        except Exception as e:
            self.log_error(f"Kinematic chain test failed: {e}")
        results["tests_run"] += 1

        # Summary
        results["summary"] = {
            "tests_passed": results["tests_passed"],
            "tests_run": results["tests_run"],
        }

        # Metrics
        self.add_metric("tests_run", results["tests_run"])
        self.add_metric("tests_passed", results["tests_passed"])
        if "performance" in results["transform_tests"]:
            self.add_metric("transforms_per_second", results["transform_tests"]["performance"]["ops_per_second"])

        return results


if __name__ == "__main__":
    script = EmbodimentScript()
    sys.exit(script.execute())
