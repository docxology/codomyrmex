#!/usr/bin/env python3
"""
Display telemetry configuration and recent metrics.

Usage:
    python telemetry_status.py [--verbose]
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
import json
from datetime import datetime


def get_telemetry_config() -> dict:
    """Get telemetry configuration from environment."""
    config = {
        "enabled": os.environ.get("TELEMETRY_ENABLED", "true").lower() == "true",
        "endpoint": os.environ.get("TELEMETRY_ENDPOINT", ""),
        "service_name": os.environ.get("OTEL_SERVICE_NAME", "codomyrmex"),
        "exporter": os.environ.get("OTEL_TRACES_EXPORTER", "console"),
    }
    return config


def find_telemetry_files() -> list:
    """Find telemetry/metrics files."""
    patterns = ["*.metrics", "*.spans", "telemetry*.json", "metrics*.json"]
    found = []
    
    search_dirs = [
        Path("output") / "telemetry",
        Path(".codomyrmex") / "telemetry",
        Path("logs"),
    ]
    
    for d in search_dirs:
        if d.exists():
            for pattern in patterns:
                found.extend(d.glob(pattern))
    
    return found


def parse_metrics_file(path: Path) -> list:
    """Parse a metrics file."""
    metrics = []
    try:
        with open(path) as f:
            content = f.read()
            for line in content.strip().split("\n"):
                if line.strip():
                    try:
                        metrics.append(json.loads(line))
                    except:
                        pass
    except:
        pass
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Display telemetry status")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed info")
    parser.add_argument("--config", "-c", action="store_true", help="Show configuration only")
    args = parser.parse_args()
    
    print("📊 Telemetry Status\n")
    
    # Configuration
    config = get_telemetry_config()
    
    status_icon = "🟢" if config["enabled"] else "🔴"
    print(f"{status_icon} Telemetry: {'Enabled' if config['enabled'] else 'Disabled'}")
    print(f"   Service: {config['service_name']}")
    print(f"   Exporter: {config['exporter']}")
    if config["endpoint"]:
        print(f"   Endpoint: {config['endpoint']}")
    
    if args.config:
        return 0
    
    print()
    
    # Find telemetry files
    files = find_telemetry_files()
    
    if not files:
        print("📁 No telemetry files found")
        print("   Telemetry data typically stored in output/telemetry/")
        return 0
    
    print(f"📁 Found {len(files)} telemetry file(s):\n")
    
    total_metrics = 0
    
    for f in files[:5]:
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        size = f.stat().st_size
        
        print(f"   📄 {f.name}")
        print(f"      Modified: {mtime.strftime('%Y-%m-%d %H:%M')}")
        print(f"      Size: {size / 1024:.1f} KB")
        
        if args.verbose:
            metrics = parse_metrics_file(f)
            if metrics:
                print(f"      Entries: {len(metrics)}")
                total_metrics += len(metrics)
                
                # Show sample
                if metrics:
                    sample = metrics[-1]
                    print(f"      Latest: {json.dumps(sample)[:80]}...")
    
    if args.verbose and total_metrics:
        print(f"\n📈 Total metric entries: {total_metrics}")
    
    print("\n💡 Tips:")
    print("   - Set TELEMETRY_ENABLED=false to disable")
    print("   - Set OTEL_TRACES_EXPORTER=otlp for production")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
