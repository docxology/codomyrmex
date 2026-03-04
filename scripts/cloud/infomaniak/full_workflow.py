#!/usr/bin/env python3
"""
Complete Infomaniak Deployment Workflow.

Demonstrates a full infrastructure deployment:
1. Create network and router
2. Configure security groups
3. Create SSH keypair
4. Launch compute instance
5. Attach floating IP
6. Create and attach volume
7. Set up S3 bucket for backups

Usage:
    python full_workflow.py --deploy --name my-project
    python full_workflow.py --teardown --name my-project
    python full_workflow.py --status --name my-project
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
import logging
import time

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def get_clients():
    """Get all required clients."""
    from codomyrmex.cloud.infomaniak import (
        InfomaniakComputeClient,
        InfomaniakNetworkClient,
        InfomaniakS3Client,
        InfomaniakVolumeClient,
    )

    return {
        "compute": InfomaniakComputeClient.from_env(),
        "volume": InfomaniakVolumeClient.from_env(),
        "network": InfomaniakNetworkClient.from_env(),
        "s3": InfomaniakS3Client.from_env(),
    }


def deploy_infrastructure(
    clients,
    name: str,
    flavor: str = "a1-ram2-disk20-perf1",
    image_pattern: str = "Ubuntu",
    volume_size: int = 50,
    external_network: str = "ext-net",
):
    """
    Deploy a complete infrastructure stack.

    Creates:
    - Private network with subnet
    - Router connected to external network
    - Security group with SSH access
    - SSH keypair
    - Compute instance
    - Floating IP
    - Block storage volume
    - S3 bucket for backups
    """
    print(f"\n🚀 Deploying Infrastructure: {name}\n" + "=" * 60)

    resources = {}

    try:
        # 1. Create Network
        print("\n📡 Step 1: Creating Network...")
        network = clients["network"].create_network(name=f"{name}-network")
        if network:
            resources["network"] = network["id"]
            print(f"   ✅ Network: {network['id']}")

            # Create subnet
            subnet = clients["network"].create_subnet(
                network_id=network["id"],
                name=f"{name}-subnet",
                cidr="10.0.0.0/24",
                dns_nameservers=["8.8.8.8", "8.8.4.4"],
            )
            if subnet:
                resources["subnet"] = subnet["id"]
                print(f"   ✅ Subnet: {subnet['id']}")

        # 2. Create Router
        print("\n🔀 Step 2: Creating Router...")
        router = clients["network"].create_router(
            name=f"{name}-router", external_network=external_network
        )
        if router:
            resources["router"] = router["id"]
            print(f"   ✅ Router: {router['id']}")

            # Attach subnet to router
            if resources.get("subnet"):
                clients["network"].add_router_interface(
                    router["id"], resources["subnet"]
                )
                print("   ✅ Attached subnet to router")

        # 3. Create Security Group
        print("\n🛡️  Step 3: Creating Security Group...")
        sg = clients["network"].create_security_group(
            name=f"{name}-sg", description=f"Security group for {name}"
        )
        if sg:
            resources["security_group"] = sg["id"]
            print(f"   ✅ Security Group: {sg['id']}")

            # Add SSH rule
            clients["network"].add_security_group_rule(
                security_group_id=sg["id"],
                direction="ingress",
                protocol="tcp",
                port_range_min=22,
                port_range_max=22,
                remote_ip_prefix="0.0.0.0/0",
            )
            print("   ✅ Added SSH rule (port 22)")

            # Add HTTP rule
            clients["network"].add_security_group_rule(
                security_group_id=sg["id"],
                direction="ingress",
                protocol="tcp",
                port_range_min=80,
                port_range_max=80,
                remote_ip_prefix="0.0.0.0/0",
            )
            print("   ✅ Added HTTP rule (port 80)")

            # Add HTTPS rule
            clients["network"].add_security_group_rule(
                security_group_id=sg["id"],
                direction="ingress",
                protocol="tcp",
                port_range_min=443,
                port_range_max=443,
                remote_ip_prefix="0.0.0.0/0",
            )
            print("   ✅ Added HTTPS rule (port 443)")

        # 4. Create SSH Keypair
        print("\n🔑 Step 4: Creating SSH Keypair...")
        keypair = clients["compute"].create_keypair(f"{name}-key")
        if keypair:
            resources["keypair"] = keypair["name"]
            print(f"   ✅ Keypair: {keypair['name']}")

            # Save private key
            key_file = Path(f"{name}-key.pem")
            if keypair.get("private_key"):
                key_file.write_text(keypair["private_key"])
                key_file.chmod(0o600)
                print(f"   ✅ Private key saved: {key_file}")

        # 5. Find Image
        print("\n💿 Step 5: Finding Image...")
        images = clients["compute"].list_images()
        image = None
        for img in images:
            if image_pattern.lower() in img["name"].lower():
                image = img
                break

        if image:
            resources["image"] = image["id"]
            print(f"   ✅ Found image: {image['name']}")
        else:
            print(f"   ⚠️  No image matching '{image_pattern}' found")
            return resources

        # 6. Create Instance
        print("\n💻 Step 6: Creating Instance...")
        instance = clients["compute"].create_instance(
            name=f"{name}-server",
            flavor=flavor,
            image=image["id"],
            network=resources.get("network"),
            key_name=resources.get("keypair"),
            security_groups=[resources.get("security_group")],
        )
        if instance:
            resources["instance"] = instance["id"]
            print(f"   ✅ Instance: {instance['id']}")
            print("   ⏳ Waiting for instance to become ACTIVE...")

            # Wait for instance
            for _ in range(30):
                time.sleep(5)
                inst = clients["compute"].get_instance(instance["id"])
                if inst and inst["status"] == "ACTIVE":
                    print("   ✅ Instance is ACTIVE")
                    break
                elif inst and inst["status"] == "ERROR":
                    print("   ❌ Instance failed")
                    break

        # 7. Allocate and Assign Floating IP
        print("\n🌍 Step 7: Allocating Floating IP...")
        fip = clients["network"].allocate_floating_ip(external_network)
        if fip:
            resources["floating_ip"] = fip["id"]
            resources["floating_ip_address"] = fip["floating_ip_address"]
            print(f"   ✅ Floating IP: {fip['floating_ip_address']}")

            # Associate with instance
            if resources.get("instance"):
                # Get instance port
                inst = clients["compute"].get_instance(resources["instance"])
                if inst and inst.get("addresses"):
                    for _net_name, addrs in inst["addresses"].items():
                        for addr in addrs:
                            port_id = addr.get("port_id")
                            if port_id:
                                clients["network"].associate_floating_ip(
                                    fip["id"], port_id
                                )
                                print("   ✅ Associated with instance")
                                break

        # 8. Create Volume
        print("\n💾 Step 8: Creating Volume...")
        volume = clients["volume"].create_volume(size=volume_size, name=f"{name}-data")
        if volume:
            resources["volume"] = volume["id"]
            print(f"   ✅ Volume: {volume['id']} ({volume_size}GB)")
            print("   ⏳ Waiting for volume to become available...")

            # Wait for volume
            for _ in range(12):
                time.sleep(5)
                vol = clients["volume"].get_volume(volume["id"])
                if vol and vol["status"] == "available":
                    print("   ✅ Volume is available")

                    # Attach to instance
                    if resources.get("instance"):
                        clients["volume"].attach_volume(
                            volume["id"], resources["instance"]
                        )
                        print("   ✅ Attached to instance")
                    break

        # 9. Create S3 Bucket
        print("\n📦 Step 9: Creating S3 Bucket...")
        bucket_name = f"{name}-backups".lower().replace("_", "-")
        if clients["s3"].create_bucket(bucket_name):
            resources["bucket"] = bucket_name
            print(f"   ✅ S3 Bucket: {bucket_name}")

        # Summary
        print("\n" + "=" * 60)
        print("✅ DEPLOYMENT COMPLETE")
        print("=" * 60)
        print(
            f"\n   📍 SSH: ssh -i {name}-key.pem ubuntu@{resources.get('floating_ip_address')}"
        )
        print(f"   📦 S3:  s3://{resources.get('bucket')}")
        print("\n   Resources created:")
        for key, value in resources.items():
            print(f"      {key}: {value}")

        # Save state
        state_file = Path(f"{name}.state.json")
        state_file.write_text(json.dumps(resources, indent=2))
        print(f"\n   💾 State saved: {state_file}")

    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        logger.exception(e)

    return resources


def teardown_infrastructure(clients, name: str):
    """Tear down all infrastructure resources."""
    print(f"\n🗑️  Tearing Down Infrastructure: {name}\n" + "=" * 60)

    # Load state
    state_file = Path(f"{name}.state.json")
    if not state_file.exists():
        print(f"   ❌ State file not found: {state_file}")
        return

    resources = json.loads(state_file.read_text())

    # Delete in reverse order
    if resources.get("bucket"):
        print("\n   Deleting S3 bucket...")
        clients["s3"].delete_bucket(resources["bucket"])
        print("   ✅ Deleted bucket")

    if resources.get("volume"):
        print("\n   Detaching and deleting volume...")
        clients["volume"].detach_volume(resources["volume"])
        time.sleep(5)
        clients["volume"].delete_volume(resources["volume"])
        print("   ✅ Deleted volume")

    if resources.get("floating_ip"):
        print("\n   Releasing floating IP...")
        clients["network"].release_floating_ip(resources["floating_ip"])
        print("   ✅ Released floating IP")

    if resources.get("instance"):
        print("\n   Deleting instance...")
        clients["compute"].delete_instance(resources["instance"])
        print("   ✅ Deleted instance")

    if resources.get("keypair"):
        print("\n   Deleting keypair...")
        clients["compute"].delete_keypair(resources["keypair"])
        print("   ✅ Deleted keypair")

    if resources.get("router"):
        print("\n   Removing router interfaces and deleting...")
        if resources.get("subnet"):
            clients["network"].remove_router_interface(
                resources["router"], resources["subnet"]
            )
        clients["network"].delete_router(resources["router"])
        print("   ✅ Deleted router")

    if resources.get("security_group"):
        print("\n   Deleting security group...")
        time.sleep(5)  # Wait for instance to be fully deleted
        clients["network"].delete_security_group(resources["security_group"])
        print("   ✅ Deleted security group")

    if resources.get("network"):
        print("\n   Deleting network...")
        clients["network"].delete_network(resources["network"])
        print("   ✅ Deleted network")

    # Remove state file
    state_file.unlink()
    print("\n✅ Teardown complete")


def check_status(clients, name: str):
    """Check status of deployed infrastructure."""
    print(f"\n📊 Infrastructure Status: {name}\n" + "=" * 60)

    # Load state
    state_file = Path(f"{name}.state.json")
    if not state_file.exists():
        print(f"   ❌ State file not found: {state_file}")
        return

    resources = json.loads(state_file.read_text())

    if resources.get("instance"):
        inst = clients["compute"].get_instance(resources["instance"])
        if inst:
            print(f"\n   💻 Instance: {inst['status']}")

    if resources.get("volume"):
        vol = clients["volume"].get_volume(resources["volume"])
        if vol:
            print(f"   💾 Volume: {vol['status']}")

    if resources.get("floating_ip_address"):
        print(f"   🌍 IP: {resources['floating_ip_address']}")

    if resources.get("bucket"):
        objects = clients["s3"].list_objects(resources["bucket"])
        print(f"   📦 Bucket: {len(objects)} objects")


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "cloud"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/cloud/config.yaml")

    parser = argparse.ArgumentParser(description="Infomaniak Full Workflow")

    # Operations
    parser.add_argument("--deploy", action="store_true", help="Deploy infrastructure")
    parser.add_argument(
        "--teardown", action="store_true", help="Tear down infrastructure"
    )
    parser.add_argument("--status", action="store_true", help="Check status")

    # Options
    parser.add_argument("--name", type=str, required=True, help="Project name")
    parser.add_argument(
        "--flavor", type=str, default="a1-ram2-disk20-perf1", help="Instance flavor"
    )
    parser.add_argument(
        "--image", type=str, default="Ubuntu", help="Image name pattern"
    )
    parser.add_argument("--volume-size", type=int, default=50, help="Volume size (GB)")
    parser.add_argument(
        "--external-network", type=str, default="ext-net", help="External network"
    )

    args = parser.parse_args()

    try:
        clients = get_clients()
    except Exception as e:
        print(f"❌ Failed to create clients: {e}")
        return 1

    if args.deploy:
        deploy_infrastructure(
            clients,
            args.name,
            flavor=args.flavor,
            image_pattern=args.image,
            volume_size=args.volume_size,
            external_network=args.external_network,
        )
    elif args.teardown:
        teardown_infrastructure(clients, args.name)
    elif args.status:
        check_status(clients, args.name)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
