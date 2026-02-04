#!/usr/bin/env python3
"""
Infomaniak Identity (Keystone) Examples.

Demonstrates all InfomaniakIdentityClient operations:
- User and project information
- Application credentials management
- Role management
- EC2 credentials for S3

Usage:
    python identity_examples.py --user
    python identity_examples.py --projects
    python identity_examples.py --app-credentials
    python identity_examples.py --create-app-cred --name my-cred
    python identity_examples.py --roles
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
    """Get identity client from environment."""
    from codomyrmex.cloud.infomaniak import InfomaniakIdentityClient
    return InfomaniakIdentityClient.from_env()


def show_current_user(client):
    """Show current user information."""
    print("\n👤 Current User\n" + "=" * 50)
    user = client.get_current_user()
    
    if user:
        print(f"   Name: {user.get('name')}")
        print(f"   ID: {user.get('id')}")
        print(f"   Email: {user.get('email', 'N/A')}")
        print(f"   Domain: {user.get('domain_id')}")
        print(f"   Enabled: {user.get('is_enabled')}")
    else:
        print("   ❌ Failed to get user info")


def show_current_project(client):
    """Show current project information."""
    print("\n📁 Current Project\n" + "=" * 50)
    project = client.get_current_project()
    
    if project:
        print(f"   Name: {project.get('name')}")
        print(f"   ID: {project.get('id')}")
        print(f"   Description: {project.get('description', 'N/A')}")
    else:
        print("   ❌ Failed to get project info")


def list_projects(client):
    """List accessible projects."""
    print("\n📁 Projects\n" + "=" * 50)
    projects = client.list_projects()
    
    if not projects:
        print("   No projects found.")
        return
    
    for p in projects:
        enabled = "🟢" if p.get("is_enabled") else "🔴"
        print(f"   {enabled} {p['name']}")
        print(f"      ID: {p['id']}")
        if p.get("description"):
            print(f"      Description: {p['description']}")
        print()


def list_app_credentials(client):
    """List application credentials."""
    print("\n🔑 Application Credentials\n" + "=" * 50)
    creds = client.list_application_credentials()
    
    if not creds:
        print("   No application credentials found.")
        return
    
    for cred in creds:
        expires = cred.get("expires_at", "Never")
        print(f"   🔐 {cred['name']}")
        print(f"      ID: {cred['id']}")
        print(f"      Expires: {expires}")
        if cred.get("roles"):
            print(f"      Roles: {', '.join(cred['roles'])}")
        print()


def create_app_credential(client, name: str, description: str = None, expires: str = None):
    """Create an application credential."""
    print(f"\n🔑 Creating application credential: {name}")
    
    result = client.create_application_credential(
        name=name,
        description=description,
        expires_at=expires
    )
    
    if result:
        print(f"\n   ✅ Created application credential")
        print(f"   ID: {result['id']}")
        print(f"   Name: {result['name']}")
        print(f"\n   ⚠️  SAVE THESE CREDENTIALS - the secret cannot be retrieved later!")
        print(f"\n   Application Credential ID: {result['id']}")
        print(f"   Application Credential Secret: {result.get('secret')}")
    else:
        print("   ❌ Failed to create application credential")


def delete_app_credential(client, cred_id: str):
    """Delete an application credential."""
    print(f"\n🗑️  Deleting application credential: {cred_id}")
    
    if client.delete_application_credential(cred_id):
        print("   ✅ Credential deleted")
    else:
        print("   ❌ Failed to delete credential")


def list_roles(client):
    """List available roles."""
    print("\n👑 Available Roles\n" + "=" * 50)
    roles = client.list_roles()
    
    if not roles:
        print("   No roles found.")
        return
    
    for role in roles:
        print(f"   🎭 {role['name']}")
        print(f"      ID: {role['id']}")
        if role.get("description"):
            print(f"      Description: {role['description']}")
        print()


def list_user_roles(client):
    """List roles assigned to current user."""
    print("\n👑 User Roles\n" + "=" * 50)
    roles = client.list_user_roles()
    
    if not roles:
        print("   No roles assigned.")
        return
    
    for role in roles:
        print(f"   🎭 {role['name']} (ID: {role['id']})")


def list_ec2_credentials(client):
    """List EC2 credentials (for S3)."""
    print("\n🔑 EC2 Credentials (S3 Access)\n" + "=" * 50)
    creds = client.list_ec2_credentials()
    
    if not creds:
        print("   No EC2 credentials found.")
        return
    
    for cred in creds:
        print(f"   🔐 Access Key: {cred['access']}")
        print(f"      ID: {cred['id']}")
        print(f"      Project: {cred['project_id']}")
        print()


def create_ec2_credentials(client):
    """Create EC2 credentials for S3 access."""
    print("\n🔑 Creating EC2 credentials for S3 access")
    
    result = client.create_ec2_credentials()
    if result:
        print(f"\n   ✅ Created EC2 credentials")
        print(f"\n   ⚠️  SAVE THESE CREDENTIALS!")
        print(f"\n   Access Key: {result.get('access')}")
        print(f"   Secret Key: {result.get('secret')}")
    else:
        print("   ❌ Failed to create EC2 credentials")


def main():
    parser = argparse.ArgumentParser(description="Infomaniak Identity Examples")
    
    # User/Project info
    parser.add_argument("--user", action="store_true", help="Show current user")
    parser.add_argument("--project", action="store_true", help="Show current project")
    parser.add_argument("--projects", action="store_true", help="List all projects")
    
    # Application credentials
    parser.add_argument("--app-credentials", action="store_true", help="List app credentials")
    parser.add_argument("--create-app-cred", action="store_true", help="Create app credential")
    parser.add_argument("--delete-app-cred", type=str, metavar="ID", help="Delete app credential")
    
    # Roles
    parser.add_argument("--roles", action="store_true", help="List available roles")
    parser.add_argument("--user-roles", action="store_true", help="List user's roles")
    
    # EC2 credentials
    parser.add_argument("--ec2-credentials", action="store_true", help="List EC2 credentials")
    parser.add_argument("--create-ec2-cred", action="store_true", help="Create EC2 credentials")
    
    # Options
    parser.add_argument("--name", type=str, help="Credential name")
    parser.add_argument("--description", type=str, help="Description")
    parser.add_argument("--expires", type=str, help="Expiration datetime (ISO format)")
    
    # All operations
    parser.add_argument("--all", action="store_true", help="Show all information")
    
    args = parser.parse_args()
    
    try:
        client = get_client()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return 1
    
    if args.all:
        show_current_user(client)
        show_current_project(client)
        list_projects(client)
        list_user_roles(client)
        list_app_credentials(client)
        list_ec2_credentials(client)
        return 0
    
    if args.user:
        show_current_user(client)
    elif args.project:
        show_current_project(client)
    elif args.projects:
        list_projects(client)
    elif args.app_credentials:
        list_app_credentials(client)
    elif args.create_app_cred:
        if not args.name:
            print("❌ --create-app-cred requires --name")
            return 1
        create_app_credential(client, args.name, args.description, args.expires)
    elif args.delete_app_cred:
        delete_app_credential(client, args.delete_app_cred)
    elif args.roles:
        list_roles(client)
    elif args.user_roles:
        list_user_roles(client)
    elif args.ec2_credentials:
        list_ec2_credentials(client)
    elif args.create_ec2_cred:
        create_ec2_credentials(client)
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
