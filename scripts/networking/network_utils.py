#!/usr/bin/env python3
"""
Network utilities and diagnostics.

Usage:
    python network_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import socket
import urllib.request
import urllib.error
import time


def check_port(host: str, port: int, timeout: float = 2) -> bool:
    """Check if a port is open."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def get_public_ip() -> str:
    """Get public IP address."""
    services = [
        "https://api.ipify.org",
        "https://icanhazip.com",
        "https://checkip.amazonaws.com",
    ]
    for url in services:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                return response.read().decode().strip()
        except:
            continue
    return "unknown"


def check_dns(hostname: str) -> dict:
    """Check DNS resolution."""
    try:
        start = time.time()
        ips = socket.gethostbyname_ex(hostname)
        elapsed = time.time() - start
        return {
            "hostname": hostname,
            "ips": ips[2],
            "aliases": ips[1],
            "time_ms": int(elapsed * 1000)
        }
    except socket.gaierror as e:
        return {"hostname": hostname, "error": str(e)}


def check_http(url: str, timeout: float = 10) -> dict:
    """Check HTTP endpoint."""
    try:
        start = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "codomyrmex-network-check/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            elapsed = time.time() - start
            return {
                "url": url,
                "status": response.status,
                "time_ms": int(elapsed * 1000),
                "headers": dict(response.headers)
            }
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "error": str(e.reason)}
    except Exception as e:
        return {"url": url, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Network utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Port check
    port_cmd = subparsers.add_parser("port", help="Check if port is open")
    port_cmd.add_argument("host", help="Host to check")
    port_cmd.add_argument("port", type=int, help="Port number")
    
    # DNS lookup
    dns_cmd = subparsers.add_parser("dns", help="DNS lookup")
    dns_cmd.add_argument("hostname", help="Hostname to resolve")
    
    # HTTP check
    http_cmd = subparsers.add_parser("http", help="Check HTTP endpoint")
    http_cmd.add_argument("url", help="URL to check")
    
    # Public IP
    subparsers.add_parser("ip", help="Get public IP")
    
    # Common ports scan
    scan_cmd = subparsers.add_parser("scan", help="Scan common ports")
    scan_cmd.add_argument("host", help="Host to scan")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🌐 Network Utilities\n")
        print("Commands:")
        print("  port HOST PORT - Check if port is open")
        print("  dns HOSTNAME   - DNS lookup")
        print("  http URL       - Check HTTP endpoint")
        print("  ip             - Get public IP")
        print("  scan HOST      - Scan common ports")
        return 0
    
    if args.command == "port":
        is_open = check_port(args.host, args.port)
        icon = "✅" if is_open else "❌"
        status = "open" if is_open else "closed"
        print(f"{icon} {args.host}:{args.port} is {status}")
    
    elif args.command == "dns":
        result = check_dns(args.hostname)
        print(f"🔍 DNS: {args.hostname}\n")
        if "error" in result:
            print(f"   ❌ {result['error']}")
        else:
            print(f"   IPs: {', '.join(result['ips'])}")
            if result["aliases"]:
                print(f"   Aliases: {', '.join(result['aliases'])}")
            print(f"   Time: {result['time_ms']}ms")
    
    elif args.command == "http":
        result = check_http(args.url)
        print(f"🌐 HTTP: {args.url}\n")
        if "error" in result:
            print(f"   ❌ {result.get('status', 'N/A')}: {result['error']}")
        else:
            print(f"   ✅ Status: {result['status']}")
            print(f"   Time: {result['time_ms']}ms")
    
    elif args.command == "ip":
        ip = get_public_ip()
        print(f"🌍 Public IP: {ip}")
    
    elif args.command == "scan":
        common_ports = [22, 80, 443, 3000, 3306, 5432, 6379, 8000, 8080, 27017]
        print(f"🔍 Scanning {args.host}...\n")
        for port in common_ports:
            is_open = check_port(args.host, port)
            if is_open:
                print(f"   ✅ {port}")
        print("\n   Done")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
