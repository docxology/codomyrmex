#!/usr/bin/env python3
"""
Infomaniak Network (Neutron/Octavia) Examples.

Demonstrates all InfomaniakNetworkClient operations:
- Networks and subnets
- Routers
- Security groups and rules
- Floating IPs
- Load balancers (Octavia)

Usage:
    python network_examples.py --list-networks
    python network_examples.py --list-routers
    python network_examples.py --list-security-groups
    python network_examples.py --list-floating-ips
    python network_examples.py --create-network --name my-net --cidr 10.0.0.0/24
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
    """Get network client from environment."""
    from codomyrmex.cloud.infomaniak import InfomaniakNetworkClient
    return InfomaniakNetworkClient.from_env()


def list_networks(client):
    """List all networks."""
    print("\n🌐 Networks\n" + "=" * 50)
    networks = client.list_networks()
    
    if not networks:
        print("   No networks found.")
        return
    
    for net in networks:
        ext_icon = "🌍" if net.get("is_external") else "🏠"
        print(f"   {ext_icon} {net['name']}")
        print(f"      ID: {net['id']}")
        print(f"      Status: {net['status']}")
        print(f"      Shared: {net.get('is_shared', False)}")
        if net.get("subnets"):
            print(f"      Subnets: {', '.join(net['subnets'])}")
        print()


def list_routers(client):
    """List all routers."""
    print("\n🔀 Routers\n" + "=" * 50)
    routers = client.list_routers()
    
    if not routers:
        print("   No routers found.")
        return
    
    for router in routers:
        status_icon = "🟢" if router["status"] == "ACTIVE" else "🔴"
        print(f"   {status_icon} {router['name']}")
        print(f"      ID: {router['id']}")
        print(f"      Status: {router['status']}")
        if router.get("external_gateway"):
            print(f"      Gateway: {router['external_gateway']}")
        print()


def list_security_groups(client):
    """List all security groups."""
    print("\n🛡️  Security Groups\n" + "=" * 50)
    sgs = client.list_security_groups()
    
    if not sgs:
        print("   No security groups found.")
        return
    
    for sg in sgs:
        print(f"   🔒 {sg['name']}")
        print(f"      ID: {sg['id']}")
        print(f"      Description: {sg.get('description', 'N/A')}")
        print(f"      Rules: {sg.get('rules_count', 0)}")
        print()


def list_floating_ips(client):
    """List all floating IPs."""
    print("\n🌐 Floating IPs\n" + "=" * 50)
    fips = client.list_floating_ips()
    
    if not fips:
        print("   No floating IPs found.")
        return
    
    for fip in fips:
        in_use = "🟢 In Use" if fip.get("port_id") else "⚪ Available"
        print(f"   📍 {fip['floating_ip_address']} ({in_use})")
        print(f"      ID: {fip['id']}")
        print(f"      Status: {fip['status']}")
        if fip.get("fixed_ip_address"):
            print(f"      Fixed IP: {fip['fixed_ip_address']}")
        print()


def list_loadbalancers(client):
    """List all load balancers."""
    print("\n⚖️  Load Balancers\n" + "=" * 50)
    lbs = client.list_loadbalancers()
    
    if not lbs:
        print("   No load balancers found.")
        return
    
    for lb in lbs:
        status_icon = "🟢" if lb["operating_status"] == "ONLINE" else "🔴"
        print(f"   {status_icon} {lb['name']}")
        print(f"      ID: {lb['id']}")
        print(f"      VIP: {lb['vip_address']}")
        print(f"      Status: {lb['operating_status']} / {lb['provisioning_status']}")
        print()


def create_network(client, name: str, cidr: str = None, dns: list = None):
    """Create a network with subnet."""
    print(f"\n🌐 Creating network: {name}")
    
    result = client.create_network(name=name)
    if not result:
        print("   ❌ Failed to create network")
        return
    
    print(f"   ✅ Created network: {result['id']}")
    
    if cidr:
        print(f"\n   Creating subnet with CIDR: {cidr}")
        subnet = client.create_subnet(
            network_id=result['id'],
            name=f"{name}-subnet",
            cidr=cidr,
            dns_nameservers=dns or ["8.8.8.8", "8.8.4.4"]
        )
        if subnet:
            print(f"   ✅ Created subnet: {subnet['id']}")
        else:
            print("   ❌ Failed to create subnet")


def create_router(client, name: str, external_network: str = None):
    """Create a router."""
    print(f"\n🔀 Creating router: {name}")
    
    result = client.create_router(name=name, external_network=external_network)
    if result:
        print(f"   ✅ Created router: {result['id']}")
    else:
        print("   ❌ Failed to create router")


def create_security_group(client, name: str, description: str = None):
    """Create a security group."""
    print(f"\n🛡️  Creating security group: {name}")
    
    result = client.create_security_group(name=name, description=description)
    if result:
        print(f"   ✅ Created security group: {result['id']}")
    else:
        print("   ❌ Failed to create security group")


def add_security_rule(client, sg_id: str, direction: str, protocol: str, 
                      port_min: int = None, port_max: int = None, cidr: str = "0.0.0.0/0"):
    """Add a security group rule."""
    print(f"\n🔒 Adding rule to {sg_id}")
    print(f"   Direction: {direction}, Protocol: {protocol}")
    
    result = client.add_security_group_rule(
        security_group_id=sg_id,
        direction=direction,
        protocol=protocol,
        port_range_min=port_min,
        port_range_max=port_max,
        remote_ip_prefix=cidr
    )
    
    if result:
        print(f"   ✅ Added rule: {result['id']}")
    else:
        print("   ❌ Failed to add rule")


def allocate_floating_ip(client, external_network: str):
    """Allocate a floating IP."""
    print(f"\n📍 Allocating floating IP from {external_network}")
    
    result = client.allocate_floating_ip(external_network)
    if result:
        print(f"   ✅ Allocated: {result['floating_ip_address']}")
        print(f"   ID: {result['id']}")
    else:
        print("   ❌ Failed to allocate floating IP")


def main():
    parser = argparse.ArgumentParser(description="Infomaniak Network Examples")
    
    # List operations
    parser.add_argument("--list-networks", action="store_true", help="List networks")
    parser.add_argument("--list-routers", action="store_true", help="List routers")
    parser.add_argument("--list-security-groups", action="store_true", help="List security groups")
    parser.add_argument("--list-floating-ips", action="store_true", help="List floating IPs")
    parser.add_argument("--list-loadbalancers", action="store_true", help="List load balancers")
    
    # Create operations
    parser.add_argument("--create-network", action="store_true", help="Create network")
    parser.add_argument("--create-router", action="store_true", help="Create router")
    parser.add_argument("--create-security-group", action="store_true", help="Create security group")
    parser.add_argument("--add-rule", type=str, metavar="SG_ID", help="Add security group rule")
    parser.add_argument("--allocate-fip", type=str, metavar="EXT_NET", help="Allocate floating IP")
    
    # Creation options
    parser.add_argument("--name", type=str, help="Resource name")
    parser.add_argument("--cidr", type=str, help="Subnet CIDR")
    parser.add_argument("--external-network", type=str, help="External network name/ID")
    parser.add_argument("--description", type=str, help="Description")
    parser.add_argument("--direction", type=str, choices=["ingress", "egress"], default="ingress")
    parser.add_argument("--protocol", type=str, choices=["tcp", "udp", "icmp"])
    parser.add_argument("--port", type=int, help="Port number")
    parser.add_argument("--port-range", type=str, help="Port range (e.g., 80-443)")
    
    # All operations
    parser.add_argument("--all", action="store_true", help="Show all information")
    
    args = parser.parse_args()
    
    try:
        client = get_client()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return 1
    
    if args.all:
        list_networks(client)
        list_routers(client)
        list_security_groups(client)
        list_floating_ips(client)
        list_loadbalancers(client)
        return 0
    
    if args.list_networks:
        list_networks(client)
    elif args.list_routers:
        list_routers(client)
    elif args.list_security_groups:
        list_security_groups(client)
    elif args.list_floating_ips:
        list_floating_ips(client)
    elif args.list_loadbalancers:
        list_loadbalancers(client)
    elif args.create_network:
        if not args.name:
            print("❌ --create-network requires --name")
            return 1
        create_network(client, args.name, args.cidr)
    elif args.create_router:
        if not args.name:
            print("❌ --create-router requires --name")
            return 1
        create_router(client, args.name, args.external_network)
    elif args.create_security_group:
        if not args.name:
            print("❌ --create-security-group requires --name")
            return 1
        create_security_group(client, args.name, args.description)
    elif args.add_rule:
        port_min = port_max = args.port
        if args.port_range:
            parts = args.port_range.split("-")
            port_min, port_max = int(parts[0]), int(parts[1])
        add_security_rule(client, args.add_rule, args.direction, args.protocol, port_min, port_max)
    elif args.allocate_fip:
        allocate_floating_ip(client, args.allocate_fip)
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
