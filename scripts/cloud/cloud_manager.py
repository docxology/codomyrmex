#!/usr/bin/env python3
"""
Cloud Manager - Unified Cloud Resource Orchestrator

Demonstrates the use of unified cloud interfaces (StorageClient, CloudClient)
to manage resources across different providers (AWS, Coda.io, etc.)
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.cloud import CodaClient, GCSClient, S3Client
from codomyrmex.cloud.common import CloudConfig, CloudProvider, ResourceType
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_section,
    print_success,
    print_warning,
    setup_logging,
)


def demo_storage(config: CloudConfig):
    """Demonstrate unified storage operations."""
    print_section("Unified Storage Operations")

    # Try AWS S3
    if config.has_provider(CloudProvider.AWS):
        print_info("Found AWS credentials. Testing S3Client...")
        try:
            s3 = S3Client()
            buckets = s3.list_buckets()
            print_success(f"  AWS S3 Buckets found: {len(buckets)}")
            for b in buckets[:3]:
                print(f"    - {b}")
        except Exception as e:
            print_error(f"  AWS S3 operation failed: {e}")
    else:
        print_warning("AWS credentials not found. Skipping S3 demo.")

    # Try GCP GCS
    if config.has_provider(CloudProvider.GCP):
        print_info("Found GCP credentials. Testing GCSClient...")
        try:
            gcs = GCSClient()
            buckets = gcs.list_buckets()
            print_success(f"  GCP GCS Buckets found: {len(buckets)}")
        except Exception as e:
            print_error(f"  GCP GCS operation failed: {e}")
    else:
        print_warning("GCP credentials not found. Skipping GCS demo.")

def demo_resources(config: CloudConfig):
    """Demonstrate unified resource management."""
    print_section("Unified Resource Management")

    # Try Coda.io
    if config.has_provider(CloudProvider.CODA):
        print_info("Found Coda.io credentials. Testing CodaClient...")
        try:
            creds = config.get_credentials(CloudProvider.CODA)
            # CodaClient currently takes api_token directly
            client = CodaClient(api_token=creds.access_key)

            resources = client.list_resources(ResourceType.DOCUMENT)
            print_success(f"  Coda Documents found: {len(resources)}")
            for r in resources[:5]:
                print(f"    - {r.name} (ID: {r.id})")
        except Exception as e:
            print_error(f"  Coda.io operation failed: {e}")
    else:
        print_warning("Coda.io credentials not found. Skipping Coda demo.")

def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "cloud" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/cloud/config.yaml")

    setup_logging()
    print_section("Cloud Manager Orchestrator")

    config = CloudConfig.from_env()

    # Show configured providers
    providers = []
    for p in CloudProvider:
        if config.has_provider(p):
            providers.append(p.value)

    if providers:
        print_info(f"Configured providers: {', '.join(providers)}")
    else:
        print_warning("No cloud providers configured in environment.")

    demo_storage(config)
    demo_resources(config)

    print_section("Orchestration Summary")
    print_success("Cloud management tasks completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
