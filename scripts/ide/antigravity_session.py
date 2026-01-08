#!/usr/bin/env python3
"""Antigravity Session Manager

Manage Antigravity IDE sessions, list conversations, view/create artifacts,
and get session statistics.

Usage:
    uv run python scripts/ide/antigravity_session.py
    uv run python scripts/ide/antigravity_session.py --list-conversations
    uv run python scripts/ide/antigravity_session.py --list-artifacts
    uv run python scripts/ide/antigravity_session.py --stats
    uv run python scripts/ide/antigravity_session.py --get-artifact task
    uv run python scripts/ide/antigravity_session.py --tools
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.ide.antigravity import AntigravityClient, Artifact


def format_timestamp(ts: float) -> str:
    """Format a timestamp as a readable string."""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def list_conversations(client: AntigravityClient, limit: int = 10) -> None:
    """List recent conversations."""
    conversations = client.list_conversations(limit=limit)
    
    if not conversations:
        print("No conversations found.")
        return
    
    print(f"\n📂 Recent Conversations (showing {len(conversations)})")
    print("=" * 70)
    
    for conv in conversations:
        current = " ⬅️ current" if conv.get("is_current") else ""
        modified = format_timestamp(conv["modified"])
        print(f"\n  ID: {conv['id'][:12]}...{current}")
        print(f"     Artifacts: {conv['artifact_count']}")
        print(f"     Modified: {modified}")


def list_artifacts(client: AntigravityClient) -> None:
    """List artifacts in current conversation."""
    artifacts = client.list_artifacts()
    
    if not artifacts:
        print("No artifacts in current conversation.")
        return
    
    print(f"\n📄 Artifacts ({len(artifacts)})")
    print("=" * 50)
    
    for artifact in artifacts:
        modified = format_timestamp(artifact["modified"])
        print(f"\n  📝 {artifact['name']}")
        print(f"     Type: {artifact['type']}")
        print(f"     Size: {artifact['size']} bytes")
        print(f"     Modified: {modified}")


def get_artifact(client: AntigravityClient, name: str) -> None:
    """Get and display a specific artifact."""
    artifact = client.get_artifact(name)
    
    if not artifact:
        print(f"Artifact '{name}' not found.")
        return
    
    if "error" in artifact:
        print(f"Error: {artifact['error']}")
        return
    
    print(f"\n📝 Artifact: {artifact['name']}")
    print("=" * 50)
    print(artifact["content"])


def show_stats(client: AntigravityClient) -> None:
    """Show session statistics."""
    stats = client.get_session_stats()
    
    print("\n📊 Session Statistics")
    print("=" * 50)
    
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n  {key}:")
            for k, v in value.items():
                print(f"     {k}: {v}")
        else:
            print(f"  {key}: {value}")


def show_tools(client: AntigravityClient) -> None:
    """Show available tools."""
    caps = client.get_capabilities()
    
    print("\n🔧 Available Tools")
    print("=" * 50)
    
    for tool in caps["tools"]:
        info = client.get_tool_info(tool)
        if info:
            print(f"\n  • {tool}")
            print(f"    {info.get('description', 'No description')}")
        else:
            print(f"\n  • {tool}")


def invoke_tool(client: AntigravityClient, tool_name: str, params_json: str) -> None:
    """Invoke a specific tool with parameters."""
    try:
        params = json.loads(params_json) if params_json else {}
    except json.JSONDecodeError as e:
        print(f"Invalid JSON parameters: {e}")
        return
    
    result = client.invoke_tool(tool_name, params)
    
    print(f"\n🔧 Tool Invocation: {tool_name}")
    print("=" * 50)
    print(f"  Success: {result.success}")
    print(f"  Execution time: {result.execution_time:.3f}s")
    
    if result.success:
        print(f"  Output: {json.dumps(result.output, indent=2)}")
    else:
        print(f"  Error: {result.error}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage Antigravity IDE sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--list-conversations", "-lc",
        action="store_true",
        help="List recent conversations",
    )
    parser.add_argument(
        "--list-artifacts", "-la",
        action="store_true",
        help="List artifacts in current conversation",
    )
    parser.add_argument(
        "--get-artifact", "-ga",
        type=str,
        metavar="NAME",
        help="Get a specific artifact by name",
    )
    parser.add_argument(
        "--stats", "-s",
        action="store_true",
        help="Show session statistics",
    )
    parser.add_argument(
        "--tools", "-t",
        action="store_true",
        help="Show available tools",
    )
    parser.add_argument(
        "--invoke", "-i",
        type=str,
        metavar="TOOL",
        help="Invoke a specific tool",
    )
    parser.add_argument(
        "--params", "-p",
        type=str,
        default="{}",
        help="JSON parameters for tool invocation",
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit for list operations",
    )
    
    args = parser.parse_args()
    
    # Initialize client and connect
    client = AntigravityClient()
    connected = client.connect()
    
    if not connected:
        print("⚠️  Not connected to Antigravity. No active session found.")
        print(f"   Looking in: {client.artifact_dir}")
        return 1
    
    print(f"✅ Connected to Antigravity")
    print(f"   Conversation: {client.get_conversation_id()[:12]}...")
    
    # Handle commands
    if args.list_conversations:
        list_conversations(client, limit=args.limit)
    elif args.list_artifacts:
        list_artifacts(client)
    elif args.get_artifact:
        get_artifact(client, args.get_artifact)
    elif args.stats:
        show_stats(client)
    elif args.tools:
        show_tools(client)
    elif args.invoke:
        invoke_tool(client, args.invoke, args.params)
    else:
        # Default: show overview
        print(f"\n📋 Current Session Overview")
        print("=" * 50)
        
        context = client.get_context()
        if context:
            print(f"   Task: {context.task_name or 'None'}")
            print(f"   Artifacts: {len(context.artifacts)}")
        
        caps = client.get_capabilities()
        print(f"   Tools: {len(caps['tools'])}")
        print(f"   Features: {', '.join(caps['features'][:3])}...")
        
        print("\nUse --help to see available commands")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
