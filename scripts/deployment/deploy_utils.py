#!/usr/bin/env python3
"""
Deployment status and utilities.

Usage:
    python deploy_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import subprocess
import os


def find_deploy_configs() -> list:
    """Find deployment configuration files."""
    patterns = [
        "docker-compose*.yml",
        "docker-compose*.yaml",
        "Dockerfile*",
        "kubernetes/*.yaml",
        "k8s/*.yaml",
        "helm/Chart.yaml",
        "terraform/*.tf",
        "serverless.yml",
        "vercel.json",
        "netlify.toml",
    ]
    found = []
    for pattern in patterns:
        found.extend(Path(".").glob(pattern))
    return found


def get_docker_compose_services() -> list:
    """Get services from docker-compose."""
    try:
        result = subprocess.run(
            ["docker", "compose", "config", "--services"],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip().split("\n") if result.stdout else []
    except:
        return []


def check_deploy_env() -> dict:
    """Check deployment environment variables."""
    envs = {
        "production": ["PRODUCTION", "PROD", "NODE_ENV=production"],
        "staging": ["STAGING", "STAGE"],
        "development": ["DEVELOPMENT", "DEV", "NODE_ENV=development"],
    }
    
    for env_name, vars in envs.items():
        for var in vars:
            if "=" in var:
                key, val = var.split("=")
                if os.environ.get(key) == val:
                    return {"env": env_name, "source": var}
            elif os.environ.get(var):
                return {"env": env_name, "source": var}
    
    return {"env": "unknown", "source": "none"}


def main():
    parser = argparse.ArgumentParser(description="Deployment utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Status command
    subparsers.add_parser("status", help="Show deployment status")
    
    # Configs command
    subparsers.add_parser("configs", help="Find deployment configs")
    
    # Checklist command
    subparsers.add_parser("checklist", help="Pre-deploy checklist")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🚀 Deployment Utilities\n")
        print("Commands:")
        print("  status    - Show deployment status")
        print("  configs   - Find deployment configs")
        print("  checklist - Pre-deploy checklist")
        return 0
    
    if args.command == "status":
        env = check_deploy_env()
        print(f"🚀 Deployment Status\n")
        print(f"   Environment: {env['env'].upper()}")
        
        services = get_docker_compose_services()
        if services:
            print(f"\n   Docker Compose services ({len(services)}):")
            for s in services[:10]:
                print(f"      - {s}")
    
    elif args.command == "configs":
        configs = find_deploy_configs()
        print(f"📋 Deployment Configs ({len(configs)}):\n")
        for c in configs:
            print(f"   📄 {c}")
        if not configs:
            print("   No deployment configs found")
    
    elif args.command == "checklist":
        print("✅ Pre-Deploy Checklist:\n")
        checks = [
            ("Tests passing", "Run: python -m pytest"),
            ("Linting clean", "Run: ruff check ."),
            ("Dependencies locked", "Check: requirements.txt or lock file"),
            ("Environment variables", "Check: .env.example vs production"),
            ("Database migrations", "Check: pending migrations"),
            ("Build successful", "Run: docker build ."),
        ]
        for check, hint in checks:
            print(f"   [ ] {check}")
            print(f"       {hint}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
