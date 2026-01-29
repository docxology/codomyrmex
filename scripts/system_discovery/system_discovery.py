#!/usr/bin/env python3
"""
System discovery utilities.

Usage:
    python system_discovery.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import os
import subprocess
import platform


def get_system_info() -> dict:
    """Get comprehensive system information."""
    info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
    }
    
    # Get CPU info
    try:
        info["cpu"] = platform.processor() or "unknown"
    except:
        info["cpu"] = "unknown"
    
    return info


def discover_services() -> list:
    """Discover running services."""
    services = []
    
    # Common ports to check
    common_services = {
        3000: "Node.js/React",
        3306: "MySQL",
        5432: "PostgreSQL",
        6379: "Redis",
        8000: "Django/FastAPI",
        8080: "HTTP Alt",
        27017: "MongoDB",
        11434: "Ollama",
    }
    
    import socket
    for port, name in common_services.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(("127.0.0.1", port))
            sock.close()
            if result == 0:
                services.append({"port": port, "name": name, "status": "running"})
        except:
            pass
    
    return services


def discover_environment() -> dict:
    """Discover development environment."""
    env = {
        "virtual_env": os.environ.get("VIRTUAL_ENV"),
        "conda_env": os.environ.get("CONDA_DEFAULT_ENV"),
        "node_version": None,
        "python_packages": 0,
    }
    
    # Check Node
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        env["node_version"] = result.stdout.strip()
    except:
        pass
    
    # Count Python packages
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"], 
                              capture_output=True, text=True)
        import json
        env["python_packages"] = len(json.loads(result.stdout))
    except:
        pass
    
    return env


def main():
    parser = argparse.ArgumentParser(description="System discovery")
    subparsers = parser.add_subparsers(dest="command")
    
    # System command
    subparsers.add_parser("system", help="System info")
    
    # Services command
    subparsers.add_parser("services", help="Discover services")
    
    # Environment command
    subparsers.add_parser("env", help="Dev environment")
    
    # All command
    subparsers.add_parser("all", help="Full discovery")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🔍 System Discovery\n")
        print("Commands:")
        print("  system   - System information")
        print("  services - Discover running services")
        print("  env      - Development environment")
        print("  all      - Full discovery")
        return 0
    
    if args.command in ["system", "all"]:
        info = get_system_info()
        print("💻 System Info:\n")
        print(f"   OS: {info['os']} ({info['machine']})")
        print(f"   Hostname: {info['hostname']}")
        print(f"   Python: {info['python_version']}")
        print()
    
    if args.command in ["services", "all"]:
        services = discover_services()
        print("🔌 Services:\n")
        if services:
            for s in services:
                print(f"   ✅ :{s['port']} - {s['name']}")
        else:
            print("   No common services detected")
        print()
    
    if args.command in ["env", "all"]:
        env = discover_environment()
        print("🛠️  Development Environment:\n")
        if env["virtual_env"]:
            print(f"   Virtual env: {Path(env['virtual_env']).name}")
        if env["conda_env"]:
            print(f"   Conda env: {env['conda_env']}")
        if env["node_version"]:
            print(f"   Node.js: {env['node_version']}")
        print(f"   Python packages: {env['python_packages']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
