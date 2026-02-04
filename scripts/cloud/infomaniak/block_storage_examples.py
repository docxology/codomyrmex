#!/usr/bin/env python3
"""
Infomaniak Block Storage (Cinder) Examples.

Demonstrates all InfomaniakVolumeClient operations:
- Volume CRUD operations
- Volume snapshots
- Volume backups
- Attach/detach operations

Usage:
    python block_storage_examples.py --list-volumes
    python block_storage_examples.py --list-snapshots
    python block_storage_examples.py --list-backups
    python block_storage_examples.py --create-volume --name my-vol --size 10
    python block_storage_examples.py --create-snapshot --volume-id VOL_ID --name snap1
"""

import sys
from pathlib import Path

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
    """Get volume client from environment."""
    from codomyrmex.cloud.infomaniak import InfomaniakVolumeClient
    return InfomaniakVolumeClient.from_env()


def list_volumes(client):
    """List all block storage volumes."""
    print("\n💾 Block Storage Volumes\n" + "=" * 50)
    volumes = client.list_volumes()
    
    if not volumes:
        print("   No volumes found.")
        return
    
    for vol in volumes:
        status_icon = "🟢" if vol["status"] == "available" else "🔵" if vol["status"] == "in-use" else "🔴"
        print(f"   {status_icon} {vol['name']} ({vol['size']}GB)")
        print(f"      ID: {vol['id']}")
        print(f"      Status: {vol['status']}")
        print(f"      Type: {vol.get('volume_type', 'standard')}")
        print(f"      Zone: {vol.get('availability_zone', 'N/A')}")
        if vol.get("attachments"):
            for att in vol["attachments"]:
                print(f"      Attached to: {att.get('server_id')} at {att.get('device')}")
        print()


def list_snapshots(client):
    """List volume snapshots."""
    print("\n📸 Volume Snapshots\n" + "=" * 50)
    snapshots = client.list_snapshots()
    
    if not snapshots:
        print("   No snapshots found.")
        return
    
    for snap in snapshots:
        status_icon = "✅" if snap["status"] == "available" else "⏳"
        print(f"   {status_icon} {snap['name']} ({snap['size']}GB)")
        print(f"      ID: {snap['id']}")
        print(f"      Volume: {snap['volume_id']}")
        print(f"      Status: {snap['status']}")
        print()


def list_backups(client):
    """List volume backups."""
    print("\n💿 Volume Backups\n" + "=" * 50)
    backups = client.list_backups()
    
    if not backups:
        print("   No backups found.")
        return
    
    for backup in backups:
        status_icon = "✅" if backup["status"] == "available" else "⏳"
        print(f"   {status_icon} {backup['name']} ({backup['size']}GB)")
        print(f"      ID: {backup['id']}")
        print(f"      Volume: {backup['volume_id']}")
        print(f"      Status: {backup['status']}")
        print()


def create_volume(client, name: str, size: int, volume_type: str = None, zone: str = None):
    """Create a new volume."""
    print(f"\n💾 Creating volume: {name}")
    print(f"   Size: {size}GB")
    
    result = client.create_volume(
        size=size,
        name=name,
        volume_type=volume_type,
        availability_zone=zone
    )
    
    if result:
        print(f"\n   ✅ Created volume: {result['id']}")
        print(f"   Status: {result['status']}")
    else:
        print("   ❌ Failed to create volume")


def get_volume(client, volume_id: str):
    """Get volume details."""
    print(f"\n💾 Volume Details: {volume_id}\n" + "=" * 50)
    
    vol = client.get_volume(volume_id)
    if vol:
        print(json.dumps(vol, indent=2, default=str))
    else:
        print("   Volume not found")


def create_snapshot(client, volume_id: str, name: str, description: str = None):
    """Create a volume snapshot."""
    print(f"\n📸 Creating snapshot: {name}")
    print(f"   Volume: {volume_id}")
    
    result = client.create_snapshot(
        volume_id=volume_id,
        name=name,
        description=description
    )
    
    if result:
        print(f"\n   ✅ Created snapshot: {result['id']}")
    else:
        print("   ❌ Failed to create snapshot")


def create_backup(client, volume_id: str, name: str, description: str = None, incremental: bool = False):
    """Create a volume backup."""
    print(f"\n💿 Creating backup: {name}")
    print(f"   Volume: {volume_id}")
    print(f"   Incremental: {incremental}")
    
    result = client.create_backup(
        volume_id=volume_id,
        name=name,
        description=description,
        incremental=incremental
    )
    
    if result:
        print(f"\n   ✅ Created backup: {result['id']}")
    else:
        print("   ❌ Failed to create backup")


def extend_volume(client, volume_id: str, new_size: int):
    """Extend a volume."""
    print(f"\n📈 Extending volume {volume_id} to {new_size}GB")
    
    if client.extend_volume(volume_id, new_size):
        print("   ✅ Volume extended successfully")
    else:
        print("   ❌ Failed to extend volume")


def delete_volume(client, volume_id: str, force: bool = False):
    """Delete a volume."""
    print(f"\n🗑️  Deleting volume: {volume_id}")
    
    if client.delete_volume(volume_id, force=force):
        print("   ✅ Volume deleted")
    else:
        print("   ❌ Failed to delete volume")


def main():
    parser = argparse.ArgumentParser(description="Infomaniak Block Storage Examples")
    
    # List operations
    parser.add_argument("--list-volumes", action="store_true", help="List volumes")
    parser.add_argument("--list-snapshots", action="store_true", help="List snapshots")
    parser.add_argument("--list-backups", action="store_true", help="List backups")
    
    # Get operations
    parser.add_argument("--get-volume", type=str, metavar="ID", help="Get volume details")
    
    # Create operations
    parser.add_argument("--create-volume", action="store_true", help="Create a volume")
    parser.add_argument("--create-snapshot", action="store_true", help="Create a snapshot")
    parser.add_argument("--create-backup", action="store_true", help="Create a backup")
    
    # Modify operations
    parser.add_argument("--extend-volume", type=str, metavar="ID", help="Extend a volume")
    parser.add_argument("--delete-volume", type=str, metavar="ID", help="Delete a volume")
    
    # Creation options
    parser.add_argument("--name", type=str, help="Resource name")
    parser.add_argument("--size", type=int, help="Volume size in GB")
    parser.add_argument("--new-size", type=int, help="New size for extend operation")
    parser.add_argument("--volume-id", type=str, help="Volume ID for snapshot/backup")
    parser.add_argument("--volume-type", type=str, help="Volume type (ssd, hdd)")
    parser.add_argument("--zone", type=str, help="Availability zone")
    parser.add_argument("--description", type=str, help="Description")
    parser.add_argument("--incremental", action="store_true", help="Incremental backup")
    parser.add_argument("--force", action="store_true", help="Force operation")
    
    # All operations
    parser.add_argument("--all", action="store_true", help="Show all information")
    
    args = parser.parse_args()
    
    try:
        client = get_client()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return 1
    
    if args.all:
        list_volumes(client)
        list_snapshots(client)
        list_backups(client)
        return 0
    
    if args.list_volumes:
        list_volumes(client)
    elif args.list_snapshots:
        list_snapshots(client)
    elif args.list_backups:
        list_backups(client)
    elif args.get_volume:
        get_volume(client, args.get_volume)
    elif args.create_volume:
        if not args.name or not args.size:
            print("❌ --create-volume requires --name and --size")
            return 1
        create_volume(client, args.name, args.size, args.volume_type, args.zone)
    elif args.create_snapshot:
        if not args.volume_id or not args.name:
            print("❌ --create-snapshot requires --volume-id and --name")
            return 1
        create_snapshot(client, args.volume_id, args.name, args.description)
    elif args.create_backup:
        if not args.volume_id or not args.name:
            print("❌ --create-backup requires --volume-id and --name")
            return 1
        create_backup(client, args.volume_id, args.name, args.description, args.incremental)
    elif args.extend_volume:
        if not args.new_size:
            print("❌ --extend-volume requires --new-size")
            return 1
        extend_volume(client, args.extend_volume, args.new_size)
    elif args.delete_volume:
        delete_volume(client, args.delete_volume, args.force)
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
