#!/usr/bin/env python3
"""
Infomaniak Compute (Nova) Examples.

Demonstrates all InfomaniakComputeClient operations:
- List/manage instances
- List/manage flavors and images
- Keypair management
- Availability zones

Usage:
    python compute_examples.py --list-instances
    python compute_examples.py --list-flavors
    python compute_examples.py --list-images
    python compute_examples.py --list-keypairs
    python compute_examples.py --create-keypair my-key
    python compute_examples.py --create-instance --name test-vm --flavor a1-ram2-disk20-perf1 --image Ubuntu
"""

import sys
from pathlib import Path

# Add project src to path if needed
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_client():
    """Get compute client from environment."""
    from codomyrmex.cloud.infomaniak import InfomaniakComputeClient
    return InfomaniakComputeClient.from_env()


def list_instances(client):
    """List all compute instances."""
    print("\n📦 Compute Instances\n" + "=" * 50)
    instances = client.list_instances()
    
    if not instances:
        print("   No instances found.")
        return
    
    for inst in instances:
        status_icon = "🟢" if inst["status"] == "ACTIVE" else "🔴"
        print(f"   {status_icon} {inst['name']}")
        print(f"      ID: {inst['id']}")
        print(f"      Status: {inst['status']}")
        print(f"      Flavor: {inst['flavor']}")
        if inst.get("addresses"):
            for net, addrs in inst["addresses"].items():
                ips = [a.get("addr") for a in addrs if a.get("addr")]
                print(f"      {net}: {', '.join(ips)}")
        print()


def list_flavors(client):
    """List available flavors."""
    print("\n🍦 Available Flavors\n" + "=" * 50)
    flavors = client.list_flavors()
    
    # Sort by vCPUs and RAM
    flavors.sort(key=lambda f: (f["vcpus"], f["ram"]))
    
    print(f"   {'Name':<30} {'vCPUs':>6} {'RAM':>8} {'Disk':>8}")
    print("   " + "-" * 54)
    
    for f in flavors:
        ram_gb = f["ram"] / 1024
        print(f"   {f['name']:<30} {f['vcpus']:>6} {ram_gb:>6.1f}GB {f['disk']:>6}GB")


def list_images(client):
    """List available images."""
    print("\n💿 Available Images\n" + "=" * 50)
    images = client.list_images()
    
    for img in images[:20]:  # Limit to first 20
        status_icon = "✅" if img["status"] == "active" else "⏳"
        size_gb = (img.get("size") or 0) / (1024**3)
        print(f"   {status_icon} {img['name']}")
        print(f"      ID: {img['id']}")
        print(f"      Size: {size_gb:.2f}GB")
        print()
    
    if len(images) > 20:
        print(f"   ... and {len(images) - 20} more images")


def list_keypairs(client):
    """List SSH keypairs."""
    print("\n🔑 SSH Keypairs\n" + "=" * 50)
    keypairs = client.list_keypairs()
    
    if not keypairs:
        print("   No keypairs found.")
        return
    
    for kp in keypairs:
        print(f"   🔐 {kp['name']}")
        print(f"      Fingerprint: {kp['fingerprint']}")
        print(f"      Type: {kp.get('type', 'ssh')}")
        print()


def create_keypair(client, name: str):
    """Create a new SSH keypair."""
    print(f"\n🔑 Creating keypair: {name}")
    
    result = client.create_keypair(name)
    if result:
        print(f"   ✅ Created keypair: {result['name']}")
        print(f"   Fingerprint: {result['fingerprint']}")
        if result.get("private_key"):
            print("\n   ⚠️  SAVE THIS PRIVATE KEY - it cannot be retrieved later!\n")
            print(result["private_key"])
    else:
        print("   ❌ Failed to create keypair")


def list_availability_zones(client):
    """List availability zones."""
    print("\n🌍 Availability Zones\n" + "=" * 50)
    zones = client.list_availability_zones()
    
    for zone in zones:
        state = "🟢 Available" if zone.get("state") else "🔴 Unavailable"
        print(f"   {zone['name']}: {state}")


def create_instance(client, name: str, flavor: str, image: str, network: str, key_name: str = None):
    """Create a new compute instance."""
    print(f"\n🚀 Creating instance: {name}")
    print(f"   Flavor: {flavor}")
    print(f"   Image: {image}")
    print(f"   Network: {network}")
    
    result = client.create_instance(
        name=name,
        flavor=flavor,
        image=image,
        network=network,
        key_name=key_name
    )
    
    if result:
        print(f"\n   ✅ Created instance: {result['id']}")
        print(f"   Status: {result['status']}")
    else:
        print("   ❌ Failed to create instance")


def get_instance(client, instance_id: str):
    """Get instance details."""
    print(f"\n📦 Instance Details: {instance_id}\n" + "=" * 50)
    
    inst = client.get_instance(instance_id)
    if inst:
        print(json.dumps(inst, indent=2, default=str))
    else:
        print("   Instance not found")


def main():
    parser = argparse.ArgumentParser(description="Infomaniak Compute Examples")
    
    # List operations
    parser.add_argument("--list-instances", action="store_true", help="List compute instances")
    parser.add_argument("--list-flavors", action="store_true", help="List available flavors")
    parser.add_argument("--list-images", action="store_true", help="List available images")
    parser.add_argument("--list-keypairs", action="store_true", help="List SSH keypairs")
    parser.add_argument("--list-zones", action="store_true", help="List availability zones")
    
    # Get operations
    parser.add_argument("--get-instance", type=str, metavar="ID", help="Get instance details")
    
    # Create operations
    parser.add_argument("--create-keypair", type=str, metavar="NAME", help="Create SSH keypair")
    parser.add_argument("--create-instance", action="store_true", help="Create an instance")
    
    # Instance creation options
    parser.add_argument("--name", type=str, help="Instance name")
    parser.add_argument("--flavor", type=str, help="Flavor name or ID")
    parser.add_argument("--image", type=str, help="Image name or ID")
    parser.add_argument("--network", type=str, help="Network name or ID")
    parser.add_argument("--key-name", type=str, help="SSH key name")
    
    # All operations
    parser.add_argument("--all", action="store_true", help="Show all information")
    
    args = parser.parse_args()
    
    try:
        client = get_client()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        print("\nMake sure environment variables are set:")
        print("  INFOMANIAK_APP_CREDENTIAL_ID")
        print("  INFOMANIAK_APP_CREDENTIAL_SECRET")
        return 1
    
    if args.all:
        list_instances(client)
        list_flavors(client)
        list_images(client)
        list_keypairs(client)
        list_availability_zones(client)
        return 0
    
    if args.list_instances:
        list_instances(client)
    elif args.list_flavors:
        list_flavors(client)
    elif args.list_images:
        list_images(client)
    elif args.list_keypairs:
        list_keypairs(client)
    elif args.list_zones:
        list_availability_zones(client)
    elif args.get_instance:
        get_instance(client, args.get_instance)
    elif args.create_keypair:
        create_keypair(client, args.create_keypair)
    elif args.create_instance:
        if not all([args.name, args.flavor, args.image, args.network]):
            print("❌ --create-instance requires --name, --flavor, --image, --network")
            return 1
        create_instance(client, args.name, args.flavor, args.image, args.network, args.key_name)
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
