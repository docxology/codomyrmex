#!/usr/bin/env python3
"""
Infomaniak Metering Examples.

Demonstrates all InfomaniakMeteringClient operations:
- Resource usage summaries
- Quota information
- Resource listing with metrics

Usage:
    python metering_examples.py --usage
    python metering_examples.py --compute-usage
    python metering_examples.py --quotas
    python metering_examples.py --resources
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_client():
    """Get metering client from environment."""
    from codomyrmex.cloud.infomaniak import InfomaniakMeteringClient
    return InfomaniakMeteringClient.from_env()


def show_compute_usage(client):
    """Show compute resource usage."""
    print("\n💻 Compute Usage\n" + "=" * 50)
    usage = client.get_compute_usage()
    
    if not usage:
        print("   Failed to get compute usage")
        return
    
    print(f"   Instances: {usage.get('instance_count', 0)}")
    print(f"   Total vCPUs: {usage.get('total_vcpus', 0)}")
    print(f"   Total RAM: {usage.get('total_ram_gb', 0):.1f} GB")
    print(f"   Total Disk: {usage.get('total_disk_gb', 0)} GB")


def show_storage_usage(client):
    """Show storage usage."""
    print("\n💾 Storage Usage\n" + "=" * 50)
    usage = client.get_storage_usage()
    
    if not usage:
        print("   Failed to get storage usage")
        return
    
    print(f"   Volumes: {usage.get('volume_count', 0)}")
    print(f"   Total Size: {usage.get('total_size_gb', 0)} GB")
    print(f"   Attached: {usage.get('attached_count', 0)}")
    print(f"   Unattached: {usage.get('unattached_count', 0)}")


def show_network_usage(client):
    """Show network resource usage."""
    print("\n🌐 Network Usage\n" + "=" * 50)
    usage = client.get_network_usage()
    
    if not usage:
        print("   Failed to get network usage")
        return
    
    print(f"   Networks: {usage.get('network_count', 0)}")
    print(f"   Routers: {usage.get('router_count', 0)}")
    print(f"   Security Groups: {usage.get('security_group_count', 0)}")
    print(f"   Floating IPs: {usage.get('floating_ip_count', 0)}")
    print(f"   Floating IPs in Use: {usage.get('floating_ips_in_use', 0)}")


def show_object_storage_usage(client):
    """Show object storage usage."""
    print("\n📦 Object Storage Usage\n" + "=" * 50)
    usage = client.get_object_storage_usage()
    
    if not usage:
        print("   Failed to get object storage usage")
        return
    
    print(f"   Containers: {usage.get('container_count', 0)}")
    print(f"   Objects: {usage.get('object_count', 0)}")
    print(f"   Total Size: {usage.get('total_size_gb', 0):.2f} GB")


def show_all_usage(client):
    """Show comprehensive usage summary."""
    print("\n📊 Comprehensive Usage Summary\n" + "=" * 50)
    
    usage = client.get_all_usage()
    print(f"\n   Timestamp: {usage.get('timestamp')}")
    
    show_compute_usage(client)
    show_storage_usage(client)
    show_network_usage(client)
    show_object_storage_usage(client)


def show_compute_quotas(client):
    """Show compute quotas."""
    print("\n💻 Compute Quotas\n" + "=" * 50)
    quotas = client.get_compute_quotas()
    
    if not quotas:
        print("   Failed to get quotas")
        return
    
    print(f"   Instances: {quotas.get('instances', 'N/A')}")
    print(f"   vCPUs: {quotas.get('cores', 'N/A')}")
    print(f"   RAM: {quotas.get('ram_mb', 0) / 1024:.0f} GB")
    print(f"   Key Pairs: {quotas.get('key_pairs', 'N/A')}")


def show_network_quotas(client):
    """Show network quotas."""
    print("\n🌐 Network Quotas\n" + "=" * 50)
    quotas = client.get_network_quotas()
    
    if not quotas:
        print("   Failed to get quotas")
        return
    
    print(f"   Networks: {quotas.get('networks', 'N/A')}")
    print(f"   Subnets: {quotas.get('subnets', 'N/A')}")
    print(f"   Routers: {quotas.get('routers', 'N/A')}")
    print(f"   Floating IPs: {quotas.get('floating_ips', 'N/A')}")
    print(f"   Security Groups: {quotas.get('security_groups', 'N/A')}")


def show_storage_quotas(client):
    """Show storage quotas."""
    print("\n💾 Storage Quotas\n" + "=" * 50)
    quotas = client.get_storage_quotas()
    
    if not quotas:
        print("   Failed to get quotas")
        return
    
    print(f"   Volumes: {quotas.get('volumes', 'N/A')}")
    print(f"   Gigabytes: {quotas.get('gigabytes', 'N/A')} GB")
    print(f"   Snapshots: {quotas.get('snapshots', 'N/A')}")
    print(f"   Backups: {quotas.get('backups', 'N/A')}")


def show_all_quotas(client):
    """Show all quotas."""
    print("\n📈 All Quotas\n" + "=" * 50)
    show_compute_quotas(client)
    show_network_quotas(client)
    show_storage_quotas(client)


def list_resources(client):
    """List all resources with usage metrics."""
    print("\n🗂️  All Resources\n" + "=" * 50)
    resources = client.list_resources_with_usage()
    
    if not resources:
        print("   No resources found.")
        return
    
    # Group by type
    by_type = {}
    for res in resources:
        res_type = res["type"]
        if res_type not in by_type:
            by_type[res_type] = []
        by_type[res_type].append(res)
    
    for res_type, items in by_type.items():
        print(f"\n   {res_type} ({len(items)}):")
        for item in items:
            name = item.get("name") or item.get("address") or item.get("id")
            status = item.get("status", "N/A")
            print(f"      • {name} ({status})")


def main():
    parser = argparse.ArgumentParser(description="Infomaniak Metering Examples")
    
    # Usage operations
    parser.add_argument("--usage", action="store_true", help="Show all usage")
    parser.add_argument("--compute-usage", action="store_true", help="Show compute usage")
    parser.add_argument("--storage-usage", action="store_true", help="Show storage usage")
    parser.add_argument("--network-usage", action="store_true", help="Show network usage")
    parser.add_argument("--object-storage-usage", action="store_true", help="Show object storage usage")
    
    # Quota operations
    parser.add_argument("--quotas", action="store_true", help="Show all quotas")
    parser.add_argument("--compute-quotas", action="store_true", help="Show compute quotas")
    parser.add_argument("--network-quotas", action="store_true", help="Show network quotas")
    parser.add_argument("--storage-quotas", action="store_true", help="Show storage quotas")
    
    # Resource listing
    parser.add_argument("--resources", action="store_true", help="List all resources")
    
    # All
    parser.add_argument("--all", action="store_true", help="Show everything")
    
    args = parser.parse_args()
    
    try:
        client = get_client()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return 1
    
    if args.all:
        show_all_usage(client)
        show_all_quotas(client)
        list_resources(client)
        return 0
    
    if args.usage:
        show_all_usage(client)
    elif args.compute_usage:
        show_compute_usage(client)
    elif args.storage_usage:
        show_storage_usage(client)
    elif args.network_usage:
        show_network_usage(client)
    elif args.object_storage_usage:
        show_object_storage_usage(client)
    elif args.quotas:
        show_all_quotas(client)
    elif args.compute_quotas:
        show_compute_quotas(client)
    elif args.network_quotas:
        show_network_quotas(client)
    elif args.storage_quotas:
        show_storage_quotas(client)
    elif args.resources:
        list_resources(client)
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
