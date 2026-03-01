#!/usr/bin/env python3
"""
Embodiment utilities for physical/robotic integrations.

Usage:
    python embodiment_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse


def check_hardware_interfaces() -> dict:
    """Check available hardware interfaces."""
    interfaces = {
        "serial": {"available": False, "ports": []},
        "usb": {"available": False},
        "gpio": {"available": False},
        "camera": {"available": False},
    }
    
    # Check for serial ports
    try:
        import glob
        ports = glob.glob("/dev/tty.*") + glob.glob("/dev/cu.*")
        interfaces["serial"]["available"] = len(ports) > 0
        interfaces["serial"]["ports"] = ports[:5]
    except:
        pass
    
    # Check for USB
    try:
        import subprocess
        result = subprocess.run(["system_profiler", "SPUSBDataType"], capture_output=True, text=True)
        interfaces["usb"]["available"] = "USB" in result.stdout
    except:
        pass
    
    return interfaces


def simulate_sensor(sensor_type: str, samples: int = 5) -> list:
    """Simulate sensor readings."""
    import random
    
    sensors = {
        "temperature": lambda: round(20 + random.uniform(-5, 15), 1),
        "humidity": lambda: round(40 + random.uniform(-10, 30), 1),
        "distance": lambda: round(random.uniform(0.1, 5.0), 2),
        "light": lambda: round(random.uniform(0, 1000)),
        "pressure": lambda: round(1013 + random.uniform(-50, 50), 1),
    }
    
    generator = sensors.get(sensor_type, sensors["temperature"])
    return [generator() for _ in range(samples)]


def main():
    parser = argparse.ArgumentParser(description="Embodiment utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Check command
    subparsers.add_parser("check", help="Check hardware interfaces")
    
    # Simulate command
    sim = subparsers.add_parser("simulate", help="Simulate sensor")
    sim.add_argument("sensor", choices=["temperature", "humidity", "distance", "light", "pressure"])
    sim.add_argument("--samples", "-n", type=int, default=5)
    
    args = parser.parse_args()
    
    if not args.command:
        print("🤖 Embodiment Utilities\n")
        print("Physical/robotic integration tools.\n")
        print("Commands:")
        print("  check    - Check hardware interfaces")
        print("  simulate - Simulate sensor readings")
        return 0
    
    if args.command == "check":
        interfaces = check_hardware_interfaces()
        print("🔌 Hardware Interfaces:\n")
        for name, info in interfaces.items():
            status = "✅" if info["available"] else "⚪"
            print(f"   {status} {name.upper()}")
            if info.get("ports"):
                for p in info["ports"][:3]:
                    print(f"      - {p}")
    
    elif args.command == "simulate":
        readings = simulate_sensor(args.sensor, args.samples)
        units = {"temperature": "°C", "humidity": "%", "distance": "m", "light": "lux", "pressure": "hPa"}
        unit = units.get(args.sensor, "")
        
        print(f"📊 Simulated {args.sensor.title()} readings:\n")
        for i, val in enumerate(readings, 1):
            print(f"   {i}. {val} {unit}")
        print(f"\n   Avg: {sum(readings)/len(readings):.1f} {unit}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
