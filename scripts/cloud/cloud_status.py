#!/usr/bin/env python3
"""
Cloud service status and resource utilities.

Usage:
    python cloud_status.py [--provider PROVIDER]
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
import subprocess
import shutil


def check_aws_cli() -> dict:
    """Check AWS CLI status."""
    if not shutil.which("aws"):
        return {"installed": False}
    
    try:
        result = subprocess.run(["aws", "--version"], capture_output=True, text=True)
        version = result.stdout.strip().split()[0] if result.stdout else "unknown"
        
        # Check for credentials
        has_creds = bool(os.environ.get("AWS_ACCESS_KEY_ID")) or \
                    Path.home().joinpath(".aws/credentials").exists()
        
        return {"installed": True, "version": version, "configured": has_creds}
    except:
        return {"installed": True, "version": "unknown", "configured": False}


def check_gcloud() -> dict:
    """Check Google Cloud CLI status."""
    if not shutil.which("gcloud"):
        return {"installed": False}
    
    try:
        result = subprocess.run(["gcloud", "--version"], capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().split("\n")
        version = lines[0] if lines else "unknown"
        
        return {"installed": True, "version": version}
    except:
        return {"installed": True, "version": "unknown"}


def check_azure() -> dict:
    """Check Azure CLI status."""
    if not shutil.which("az"):
        return {"installed": False}
    
    try:
        result = subprocess.run(["az", "version", "-o", "json"], capture_output=True, text=True, timeout=10)
        import json
        data = json.loads(result.stdout)
        version = data.get("azure-cli", "unknown")
        return {"installed": True, "version": version}
    except:
        return {"installed": True, "version": "unknown"}


def check_cloud_env_vars() -> dict:
    """Check cloud-related environment variables."""
    providers = {
        "aws": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION", "AWS_PROFILE"],
        "gcp": ["GOOGLE_APPLICATION_CREDENTIALS", "GOOGLE_CLOUD_PROJECT", "GCP_PROJECT"],
        "azure": ["AZURE_SUBSCRIPTION_ID", "AZURE_TENANT_ID", "AZURE_CLIENT_ID"],
    }
    
    found = {}
    for provider, vars in providers.items():
        found[provider] = [v for v in vars if os.environ.get(v)]
    
    return found


def main():
    parser = argparse.ArgumentParser(description="Cloud service status")
    parser.add_argument("--provider", "-p", choices=["aws", "gcp", "azure", "all"], default="all")
    parser.add_argument("--env", "-e", action="store_true", help="Show environment variables")
    args = parser.parse_args()
    
    print("☁️  Cloud Status\n")
    
    providers = {
        "aws": ("AWS", check_aws_cli),
        "gcp": ("Google Cloud", check_gcloud),
        "azure": ("Azure", check_azure),
    }
    
    to_check = providers if args.provider == "all" else {args.provider: providers[args.provider]}
    
    for key, (name, check_fn) in to_check.items():
        status = check_fn()
        icon = "✅" if status.get("installed") else "⚪"
        print(f"{icon} {name}:")
        if status.get("installed"):
            print(f"   Version: {status.get('version', 'unknown')}")
            if "configured" in status:
                print(f"   Configured: {'Yes' if status['configured'] else 'No'}")
        else:
            print("   Not installed")
        print()
    
    if args.env:
        env_vars = check_cloud_env_vars()
        print("🔧 Environment Variables:\n")
        for provider, vars in env_vars.items():
            if vars:
                print(f"   {provider.upper()}: {', '.join(vars)}")
        if not any(env_vars.values()):
            print("   No cloud environment variables set")
    
    print("\n💡 Tips:")
    print("   - AWS: aws configure")
    print("   - GCP: gcloud auth login")
    print("   - Azure: az login")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
