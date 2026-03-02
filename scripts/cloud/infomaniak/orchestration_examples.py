#!/usr/bin/env python3
"""
Infomaniak Orchestration (Heat) Examples.

Demonstrates all InfomaniakHeatClient operations:
- Stack CRUD operations
- Template validation
- Stack resources and events
- Stack outputs

Usage:
    python orchestration_examples.py --list-stacks
    python orchestration_examples.py --get-stack STACK_ID
    python orchestration_examples.py --create-stack --name my-stack --template template.yaml
    python orchestration_examples.py --validate --template template.yaml
"""

import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_client():
    """Get Heat client from environment."""
    from codomyrmex.cloud.infomaniak import InfomaniakHeatClient
    return InfomaniakHeatClient.from_env()


def list_stacks(client):
    """List all Heat stacks."""
    print("\n📚 Heat Stacks\n" + "=" * 50)
    stacks = client.list_stacks()
    
    if not stacks:
        print("   No stacks found.")
        return
    
    for stack in stacks:
        if "COMPLETE" in stack["status"]:
            icon = "🟢"
        elif "IN_PROGRESS" in stack["status"]:
            icon = "🔄"
        elif "FAILED" in stack["status"]:
            icon = "🔴"
        else:
            icon = "⚪"
        
        print(f"   {icon} {stack['name']}")
        print(f"      ID: {stack['id']}")
        print(f"      Status: {stack['status']}")
        if stack.get("status_reason"):
            print(f"      Reason: {stack['status_reason'][:50]}...")
        print()


def get_stack(client, stack_id: str):
    """Get stack details."""
    print(f"\n📚 Stack Details: {stack_id}\n" + "=" * 50)
    
    stack = client.get_stack(stack_id)
    if not stack:
        print("   Stack not found")
        return
    
    print(f"   Name: {stack['name']}")
    print(f"   ID: {stack['id']}")
    print(f"   Status: {stack['status']}")
    print(f"   Description: {stack.get('description', 'N/A')}")
    print(f"   Created: {stack.get('creation_time')}")
    print(f"   Updated: {stack.get('updated_time')}")
    
    if stack.get("parameters"):
        print("\n   Parameters:")
        for k, v in stack["parameters"].items():
            print(f"      {k}: {v}")
    
    if stack.get("outputs"):
        print("\n   Outputs:")
        for out in stack["outputs"]:
            print(f"      {out.get('output_key')}: {out.get('output_value')}")


def list_resources(client, stack_id: str):
    """List resources in a stack."""
    print(f"\n🧱 Stack Resources: {stack_id}\n" + "=" * 50)
    
    resources = client.list_stack_resources(stack_id)
    if not resources:
        print("   No resources found.")
        return
    
    for res in resources:
        if "COMPLETE" in res["status"]:
            icon = "🟢"
        elif "IN_PROGRESS" in res["status"]:
            icon = "🔄"
        else:
            icon = "🔴"
        
        print(f"   {icon} {res['name']} ({res['resource_type']})")
        print(f"      Physical ID: {res.get('physical_resource_id', 'N/A')}")
        print(f"      Status: {res['status']}")
        print()


def list_events(client, stack_id: str):
    """List events for a stack."""
    print(f"\n📜 Stack Events: {stack_id}\n" + "=" * 50)
    
    events = client.list_stack_events(stack_id)
    if not events:
        print("   No events found.")
        return
    
    # Show most recent 10 events
    for event in events[:10]:
        print(f"   {event.get('event_time', 'N/A')}")
        print(f"      Resource: {event['resource_name']}")
        print(f"      Status: {event['resource_status']}")
        if event.get("resource_status_reason"):
            print(f"      Reason: {event['resource_status_reason'][:50]}...")
        print()
    
    if len(events) > 10:
        print(f"   ... and {len(events) - 10} more events")


def create_stack(client, name: str, template_path: str, parameters: dict = None):
    """Create a Heat stack from template file."""
    print(f"\n🚀 Creating stack: {name}")
    print(f"   Template: {template_path}")
    
    result = client.create_stack_from_file(
        name=name,
        template_path=template_path,
        parameters=parameters
    )
    
    if result:
        print(f"\n   ✅ Created stack: {result['id']}")
    else:
        print("   ❌ Failed to create stack")


def validate_template(client, template_path: str):
    """Validate a Heat template."""
    print(f"\n🔍 Validating template: {template_path}")
    
    try:
        with open(template_path, 'r') as f:
            template = f.read()
    except Exception as e:
        print(f"   ❌ Failed to read template: {e}")
        return
    
    result = client.validate_template(template)
    
    if result.get("valid"):
        print("   ✅ Template is valid")
        print(f"\n   Description: {result.get('description', 'N/A')}")
        
        if result.get("parameters"):
            print("\n   Parameters:")
            for name, params in result["parameters"].items():
                param_type = params.get("type", "String")
                default = params.get("default", "N/A")
                print(f"      {name} ({param_type}): default={default}")
    else:
        print(f"   ❌ Template is invalid: {result.get('error')}")


def get_outputs(client, stack_id: str):
    """Get stack outputs."""
    print(f"\n📤 Stack Outputs: {stack_id}\n" + "=" * 50)
    
    outputs = client.get_stack_outputs(stack_id)
    if not outputs:
        print("   No outputs found.")
        return
    
    for key, value in outputs.items():
        print(f"   {key}: {value}")


def delete_stack(client, stack_id: str):
    """Delete a stack."""
    print(f"\n🗑️  Deleting stack: {stack_id}")
    
    if client.delete_stack(stack_id):
        print("   ✅ Stack deletion initiated")
    else:
        print("   ❌ Failed to delete stack")


def suspend_stack(client, stack_id: str):
    """Suspend a stack."""
    print(f"\n⏸️  Suspending stack: {stack_id}")
    
    if client.suspend_stack(stack_id):
        print("   ✅ Stack suspended")
    else:
        print("   ❌ Failed to suspend stack")


def resume_stack(client, stack_id: str):
    """Resume a stack."""
    print(f"\n▶️  Resuming stack: {stack_id}")
    
    if client.resume_stack(stack_id):
        print("   ✅ Stack resumed")
    else:
        print("   ❌ Failed to resume stack")


def main():
    parser = argparse.ArgumentParser(description="Infomaniak Orchestration (Heat) Examples")
    
    # List/Get operations
    parser.add_argument("--list-stacks", action="store_true", help="List stacks")
    parser.add_argument("--get-stack", type=str, metavar="ID", help="Get stack details")
    parser.add_argument("--list-resources", type=str, metavar="ID", help="List stack resources")
    parser.add_argument("--list-events", type=str, metavar="ID", help="List stack events")
    parser.add_argument("--get-outputs", type=str, metavar="ID", help="Get stack outputs")
    
    # Create/Modify operations
    parser.add_argument("--create-stack", action="store_true", help="Create a stack")
    parser.add_argument("--delete-stack", type=str, metavar="ID", help="Delete a stack")
    parser.add_argument("--suspend-stack", type=str, metavar="ID", help="Suspend a stack")
    parser.add_argument("--resume-stack", type=str, metavar="ID", help="Resume a stack")
    
    # Validation
    parser.add_argument("--validate", action="store_true", help="Validate template")
    
    # Options
    parser.add_argument("--name", type=str, help="Stack name")
    parser.add_argument("--template", type=str, help="Template file path")
    parser.add_argument("--params", type=str, help="Parameters as JSON")
    
    args = parser.parse_args()
    
    try:
        client = get_client()
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        return 1
    
    if args.list_stacks:
        list_stacks(client)
    elif args.get_stack:
        get_stack(client, args.get_stack)
    elif args.list_resources:
        list_resources(client, args.list_resources)
    elif args.list_events:
        list_events(client, args.list_events)
    elif args.get_outputs:
        get_outputs(client, args.get_outputs)
    elif args.create_stack:
        if not args.name or not args.template:
            print("❌ --create-stack requires --name and --template")
            return 1
        params = json.loads(args.params) if args.params else None
        create_stack(client, args.name, args.template, params)
    elif args.delete_stack:
        delete_stack(client, args.delete_stack)
    elif args.suspend_stack:
        suspend_stack(client, args.suspend_stack)
    elif args.resume_stack:
        resume_stack(client, args.resume_stack)
    elif args.validate:
        if not args.template:
            print("❌ --validate requires --template")
            return 1
        validate_template(client, args.template)
    else:
        parser.print_help()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
