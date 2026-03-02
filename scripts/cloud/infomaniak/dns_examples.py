#!/usr/bin/env python3
"""
Infomaniak DNS (Designate) Examples.

Demonstrates all InfomaniakDNSClient operations:
- Zone management
- Record set management
- Reverse DNS (PTR records)

Usage:
    python dns_examples.py --list-zones
    python dns_examples.py --list-records --zone ZONE_ID
    python dns_examples.py --create-zone --name example.com --email admin@example.com
    python dns_examples.py --create-record --zone ZONE_ID --name www --type A --value 1.2.3.4
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_client():
    """Get DNS client from environment."""
    from codomyrmex.cloud.infomaniak import InfomaniakDNSClient
    return InfomaniakDNSClient.from_env()


def list_zones(client):
    """List all DNS zones."""
    print("\n🌐 DNS Zones\n" + "=" * 50)
    zones = client.list_zones()
    
    if not zones:
        print("   No zones found.")
        return
    
    for zone in zones:
        status_icon = "🟢" if zone["status"] == "ACTIVE" else "⏳"
        print(f"   {status_icon} {zone['name']}")
        print(f"      ID: {zone['id']}")
        print(f"      Type: {zone['type']}")
        print(f"      Email: {zone['email']}")
        print(f"      TTL: {zone['ttl']}")
        print()


def get_zone(client, zone_id: str):
    """Get zone details."""
    print(f"\n🌐 Zone Details: {zone_id}\n" + "=" * 50)
    zone = client.get_zone(zone_id)
    
    if zone:
        for k, v in zone.items():
            print(f"   {k}: {v}")
    else:
        print("   Zone not found")


def list_records(client, zone_id: str):
    """List records in a zone."""
    print(f"\n📝 Records in {zone_id}\n" + "=" * 50)
    records = client.list_records(zone_id)
    
    if not records:
        print("   No records found.")
        return
    
    for record in records:
        status_icon = "🟢" if record["status"] == "ACTIVE" else "⏳"
        print(f"   {status_icon} {record['name']} ({record['type']})")
        print(f"      ID: {record['id']}")
        print(f"      Values: {record['records']}")
        print(f"      TTL: {record['ttl']}")
        print()


def create_zone(client, name: str, email: str, ttl: int = 3600, description: str = None):
    """Create a DNS zone."""
    print(f"\n🌐 Creating zone: {name}")
    
    result = client.create_zone(
        name=name,
        email=email,
        ttl=ttl,
        description=description
    )
    
    if result:
        print(f"\n   ✅ Created zone: {result['id']}")
        print(f"   Name: {result['name']}")
    else:
        print("   ❌ Failed to create zone")


def delete_zone(client, zone_id: str):
    """Delete a DNS zone."""
    print(f"\n🗑️  Deleting zone: {zone_id}")
    
    if client.delete_zone(zone_id):
        print("   ✅ Zone deleted")
    else:
        print("   ❌ Failed to delete zone")


def create_record(client, zone_id: str, name: str, record_type: str, 
                  values: list, ttl: int = 3600, description: str = None):
    """Create a DNS record."""
    print(f"\n📝 Creating record: {name} ({record_type})")
    print(f"   Zone: {zone_id}")
    print(f"   Values: {values}")
    
    result = client.create_record(
        zone_id=zone_id,
        name=name,
        record_type=record_type,
        records=values,
        ttl=ttl,
        description=description
    )
    
    if result:
        print(f"\n   ✅ Created record: {result['id']}")
    else:
        print("   ❌ Failed to create record")


def update_record(client, zone_id: str, record_id: str, 
                  values: list = None, ttl: int = None):
    """Update a DNS record."""
    print(f"\n✏️  Updating record: {record_id}")
    
    if client.update_record(zone_id, record_id, records=values, ttl=ttl):
        print("   ✅ Record updated")
    else:
        print("   ❌ Failed to update record")


def delete_record(client, zone_id: str, record_id: str):
    """Delete a DNS record."""
    print(f"\n🗑️  Deleting record: {record_id}")
    
    if client.delete_record(zone_id, record_id):
        print("   ✅ Record deleted")
    else:
        print("   ❌ Failed to delete record")


def list_ptr_records(client):
    """List PTR (reverse DNS) records."""
    print("\n🔄 PTR Records (Reverse DNS)\n" + "=" * 50)
    ptrs = client.list_ptr_records()
    
    if not ptrs:
        print("   No PTR records found.")
        return
    
    for ptr in ptrs:
        status_icon = "🟢" if ptr["status"] == "ACTIVE" else "⏳"
        print(f"   {status_icon} {ptr['address']} → {ptr['ptrdname']}")
        print(f"      ID: {ptr['id']}")
        print()


def set_reverse_dns(client, floating_ip: str, hostname: str, ttl: int = 3600):
    """Set reverse DNS for a floating IP."""
    print(f"\n🔄 Setting reverse DNS")
    print(f"   IP: {floating_ip}")
    print(f"   Hostname: {hostname}")
    
    result = client.set_reverse_dns(floating_ip, hostname, ttl=ttl)
    if result:
        print(f"\n   ✅ Set reverse DNS: {result['id']}")
    else:
        print("   ❌ Failed to set reverse DNS")


def main():
    parser = argparse.ArgumentParser(description="Infomaniak DNS Examples")
    
    # Zone operations
    parser.add_argument("--list-zones", action="store_true", help="List DNS zones")
    parser.add_argument("--get-zone", type=str, metavar="ID", help="Get zone details")
    parser.add_argument("--create-zone", action="store_true", help="Create a zone")
    parser.add_argument("--delete-zone", type=str, metavar="ID", help="Delete a zone")
    
    # Record operations
    parser.add_argument("--list-records", action="store_true", help="List records in zone")
    parser.add_argument("--create-record", action="store_true", help="Create a record")
    parser.add_argument("--update-record", type=str, metavar="ID", help="Update a record")
    parser.add_argument("--delete-record", type=str, metavar="ID", help="Delete a record")
    
    # PTR operations
    parser.add_argument("--list-ptr", action="store_true", help="List PTR records")
    parser.add_argument("--set-ptr", action="store_true", help="Set reverse DNS")
    
    # Options
    parser.add_argument("--zone", type=str, help="Zone ID or name")
    parser.add_argument("--name", type=str, help="Record/zone name")
    parser.add_argument("--email", type=str, help="Admin email for zone")
    parser.add_argument("--type", type=str, choices=["A", "AAAA", "CNAME", "MX", "TXT", "NS", "SRV"])
    parser.add_argument("--value", type=str, action="append", help="Record value (can specify multiple)")
    parser.add_argument("--ttl", type=int, default=3600, help="TTL in seconds")
    parser.add_argument("--description", type=str, help="Description")
    parser.add_argument("--ip", type=str, help="Floating IP for PTR record")
    parser.add_argument("--hostname", type=str, help="Hostname for PTR record")
    
    # All operations
    parser.add_argument("--all", action="store_true", help="Show all information")
    
    args = parser.parse_args()
    
    try:
        client = get_client()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return 1
    
    if args.all:
        list_zones(client)
        list_ptr_records(client)
        return 0
    
    if args.list_zones:
        list_zones(client)
    elif args.get_zone:
        get_zone(client, args.get_zone)
    elif args.create_zone:
        if not args.name or not args.email:
            print("❌ --create-zone requires --name and --email")
            return 1
        create_zone(client, args.name, args.email, args.ttl, args.description)
    elif args.delete_zone:
        delete_zone(client, args.delete_zone)
    elif args.list_records:
        if not args.zone:
            print("❌ --list-records requires --zone")
            return 1
        list_records(client, args.zone)
    elif args.create_record:
        if not all([args.zone, args.name, args.type, args.value]):
            print("❌ --create-record requires --zone, --name, --type, --value")
            return 1
        create_record(client, args.zone, args.name, args.type, args.value, args.ttl)
    elif args.update_record:
        if not args.zone:
            print("❌ --update-record requires --zone")
            return 1
        update_record(client, args.zone, args.update_record, args.value, args.ttl)
    elif args.delete_record:
        if not args.zone:
            print("❌ --delete-record requires --zone")
            return 1
        delete_record(client, args.zone, args.delete_record)
    elif args.list_ptr:
        list_ptr_records(client)
    elif args.set_ptr:
        if not args.ip or not args.hostname:
            print("❌ --set-ptr requires --ip and --hostname")
            return 1
        set_reverse_dns(client, args.ip, args.hostname, args.ttl)
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
