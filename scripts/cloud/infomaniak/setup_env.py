#!/usr/bin/env python3
"""
Infomaniak Environment Setup Script.

Creates a .env template and validates the configuration for Infomaniak Public Cloud.

Usage:
    python setup_env.py --create-template    # Create .env.infomaniak template
    python setup_env.py --validate           # Validate current environment
    python setup_env.py --test-connection    # Test OpenStack connection
"""

import argparse
import os
import sys
from pathlib import Path

ENV_TEMPLATE = """# Infomaniak Public Cloud Configuration
# ======================================
# Created for agent@activeinference.tech
# Organization: Active Inference Agent (ID: 1709827)

# OpenStack Authentication (Application Credentials)
# --------------------------------------------------
# Get these from: Infomaniak Manager -> Public Cloud -> Identity -> Application Credentials
INFOMANIAK_APP_CREDENTIAL_ID=your_app_credential_id
INFOMANIAK_APP_CREDENTIAL_SECRET=your_app_credential_secret

# API Endpoints
# -------------
INFOMANIAK_AUTH_URL=https://api.pub1.infomaniak.cloud/identity/v3/
INFOMANIAK_REGION=dc3-a

# S3-Compatible Object Storage
# ----------------------------
# Get these from: Infomaniak Manager -> Public Cloud -> Identity -> EC2 Credentials
INFOMANIAK_S3_ACCESS_KEY=your_s3_access_key
INFOMANIAK_S3_SECRET_KEY=your_s3_secret_key
INFOMANIAK_S3_ENDPOINT=https://s3.pub1.infomaniak.cloud

# Optional: Project ID (auto-detected from credentials if not set)
# INFOMANIAK_PROJECT_ID=your_project_id
"""


def create_template(output_path: str = None):
    """Create the environment template file."""
    if output_path is None:
        output_path = ".env.infomaniak"

    path = Path(output_path)
    if path.exists():
        print(f"⚠️  File already exists: {path}")
        response = input("Overwrite? [y/N]: ")
        if response.lower() != "y":
            print("Aborted.")
            return False

    path.write_text(ENV_TEMPLATE)
    print(f"✅ Created template: {path}")
    print("\n📋 Next steps:")
    print("   1. Complete Infomaniak ID verification")
    print("   2. Create Application Credentials in Public Cloud dashboard")
    print("   3. Copy credentials into the .env file")
    print("   4. Run: source .env.infomaniak")
    print("   5. Test: python setup_env.py --validate")
    return True


def validate_environment():
    """Validate that all required environment variables are set."""
    print("\n🔍 Validating Infomaniak Environment\n" + "=" * 50)

    required = {
        "INFOMANIAK_APP_CREDENTIAL_ID": "Application Credential ID",
        "INFOMANIAK_APP_CREDENTIAL_SECRET": "Application Credential Secret",
        "INFOMANIAK_AUTH_URL": "OpenStack Auth URL",
        "INFOMANIAK_REGION": "Region",
    }

    optional = {
        "INFOMANIAK_S3_ACCESS_KEY": "S3 Access Key",
        "INFOMANIAK_S3_SECRET_KEY": "S3 Secret Key",
        "INFOMANIAK_S3_ENDPOINT": "S3 Endpoint",
        "INFOMANIAK_PROJECT_ID": "Project ID",
    }

    missing = []
    found = []

    for var, desc in required.items():
        value = os.environ.get(var)
        if value and value != f"your_{var.lower().replace('infomaniak_', '')}":
            found.append((desc, "✅"))
        else:
            missing.append((desc, "❌"))

    print("\n📌 Required Variables:")
    for desc, status in found:
        print(f"   {status} {desc}")
    for desc, status in missing:
        print(f"   {status} {desc}")

    print("\n📌 Optional Variables:")
    for var, desc in optional.items():
        value = os.environ.get(var)
        if value and not value.startswith("your_"):
            print(f"   ✅ {desc}")
        else:
            print(f"   ⚪ {desc} (not set)")

    if missing:
        print(f"\n❌ Missing {len(missing)} required variable(s)")
        return False
    else:
        print("\n✅ All required variables are set")
        return True


def test_connection():
    """Test the OpenStack connection."""
    print("\n🔌 Testing Infomaniak Connection\n" + "=" * 50)

    try:
        from codomyrmex.cloud.infomaniak import InfomaniakComputeClient

        print("   Creating compute client...")
        client = InfomaniakComputeClient.from_env()

        print("   Testing API connectivity...")
        flavors = client.list_flavors()

        print("\n   ✅ Connection successful!")
        print(f"   📊 Found {len(flavors)} available flavors")

        # Show some flavors
        if flavors:
            print("\n   Sample flavors:")
            for f in flavors[:5]:
                print(
                    f"      - {f['name']}: {f.get('vcpus', '?')} vCPUs, {f.get('ram', 0) // 1024}GB RAM"
                )

        return True

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Install: pip install openstacksdk")
        return False
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False


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
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/cloud/config.yaml")

    parser = argparse.ArgumentParser(description="Infomaniak Environment Setup")
    parser.add_argument(
        "--create-template", action="store_true", help="Create .env.infomaniak template"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate environment variables"
    )
    parser.add_argument(
        "--test-connection", action="store_true", help="Test OpenStack connection"
    )
    parser.add_argument(
        "--output", type=str, default=".env.infomaniak", help="Output file for template"
    )
    parser.add_argument("--all", action="store_true", help="Run all checks")

    args = parser.parse_args()

    if args.all:
        create_template(args.output)
        validate_environment()
        test_connection()
        return 0

    if args.create_template:
        create_template(args.output)
    elif args.validate:
        if not validate_environment():
            return 1
    elif args.test_connection:
        if not test_connection():
            return 1
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":
    sys.exit(main())
