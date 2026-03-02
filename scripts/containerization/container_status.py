#!/usr/bin/env python3
"""
Check container runtime and list running containers.

Usage:
    python container_status.py [--all] [--json]
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import subprocess
import json as json_lib


def run_command(cmd: list) -> tuple:
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        return False, "Command not found"
    except Exception as e:
        return False, str(e)


def check_docker() -> dict:
    """Check Docker status."""
    status = {"installed": False, "running": False, "version": None}
    
    success, version = run_command(["docker", "--version"])
    if success:
        status["installed"] = True
        status["version"] = version.replace("Docker version ", "").split(",")[0]
        
        success, _ = run_command(["docker", "info"])
        status["running"] = success
    
    return status


def get_containers(all_containers: bool = False) -> list:
    """Get list of containers."""
    cmd = ["docker", "ps", "--format", "{{.ID}}|{{.Image}}|{{.Status}}|{{.Names}}"]
    if all_containers:
        cmd.append("-a")
    
    success, output = run_command(cmd)
    if not success or not output:
        return []
    
    containers = []
    for line in output.split("\n"):
        parts = line.split("|")
        if len(parts) >= 4:
            containers.append({
                "id": parts[0][:12],
                "image": parts[1],
                "status": parts[2],
                "name": parts[3],
            })
    
    return containers


def get_images() -> list:
    """Get list of Docker images."""
    cmd = ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}|{{.Size}}|{{.ID}}"]
    
    success, output = run_command(cmd)
    if not success or not output:
        return []
    
    images = []
    for line in output.split("\n"):
        parts = line.split("|")
        if len(parts) >= 3:
            images.append({
                "name": parts[0],
                "size": parts[1],
                "id": parts[2][:12],
            })
    
    return images


def main():
    parser = argparse.ArgumentParser(description="Check container status")
    parser.add_argument("--all", "-a", action="store_true", help="Show all containers")
    parser.add_argument("--images", "-i", action="store_true", help="Show images")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    print("🐳 Container Status\n")
    
    docker_status = check_docker()
    
    if not docker_status["installed"]:
        print("❌ Docker not installed")
        print("   Install from: https://docs.docker.com/get-docker/")
        return 1
    
    if not docker_status["running"]:
        print(f"⚠️  Docker installed (v{docker_status['version']}) but not running")
        print("   Start Docker Desktop or run: sudo systemctl start docker")
        return 1
    
    print(f"✅ Docker v{docker_status['version']}")
    
    containers = get_containers(args.all)
    
    if args.json:
        output = {
            "docker": docker_status,
            "containers": containers,
        }
        if args.images:
            output["images"] = get_images()
        print(json_lib.dumps(output, indent=2))
        return 0
    
    print(f"\n📦 Containers ({len(containers)}):")
    if containers:
        running = sum(1 for c in containers if "Up" in c["status"])
        print(f"   Running: {running}, Stopped: {len(containers) - running}")
        print()
        for c in containers[:10]:
            icon = "🟢" if "Up" in c["status"] else "⚫"
            print(f"   {icon} {c['name']}")
            print(f"      Image: {c['image']}")
            print(f"      Status: {c['status']}")
    else:
        print("   No containers found")
    
    if args.images:
        images = get_images()
        print(f"\n🖼️  Images ({len(images)}):")
        for img in images[:10]:
            print(f"   - {img['name']} ({img['size']})")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
