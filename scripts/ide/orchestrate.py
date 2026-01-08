#!/usr/bin/env python3
"""IDE Orchestrator

Main orchestration script for managing all IDE integrations.
Provides a unified interface for Antigravity, Cursor, and VS Code.

Usage:
    uv run python scripts/ide/orchestrate.py
    uv run python scripts/ide/orchestrate.py status
    uv run python scripts/ide/orchestrate.py antigravity [command]
    uv run python scripts/ide/orchestrate.py cursor [command]
    uv run python scripts/ide/orchestrate.py vscode [command]
"""

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import argparse
import json
# Import shared utilities
from codomyrmex.utils.cli_helpers import (
    format_output,
    print_error,
    print_section,
    print_success,
    print_warning,
)

from codomyrmex.ide.antigravity import AntigravityClient 
from codomyrmex.ide.cursor import CursorClient
from codomyrmex.ide.vscode import VSCodeClient


def get_all_clients():
    """Initialize all IDE clients."""
    return {
        "antigravity": AntigravityClient(),
        "cursor": CursorClient(),
        "vscode": VSCodeClient(),
    }


def cmd_status(args):
    """Show status of all IDEs."""
    clients = get_all_clients()
    
    print("\n🖥️  IDE Integration Status")
    print("=" * 60)
    
    for name, client in clients.items():
        connected = client.connect()
        icon = "✅" if connected else "⚪"
        caps = client.get_capabilities()
        
        print(f"\n{icon} {caps['name']}")
        print(f"   Connected: {connected}")
        
        if connected:
            if name == "antigravity":
                conv_id = client.get_conversation_id()
                print(f"   Conversation: {conv_id[:12]}..." if conv_id else "   Conversation: None")
                print(f"   Tools: {len(caps['tools'])}")
            elif name == "cursor":
                print(f"   Workspace: {client.workspace_path}")
                print(f"   Models: {', '.join(caps['models'][:3])}...")
            elif name == "vscode":
                print(f"   Workspace: {client.workspace_path}")
                print(f"   Extensions: {len(client.list_extensions())}")


def cmd_antigravity(args):
    """Handle Antigravity commands."""
    client = AntigravityClient()
    connected = client.connect()
    
    if not connected:
        print("⚠️  Not connected to Antigravity")
        return 1
    
    if args.subcommand == "conversations":
        for conv in client.list_conversations(limit=args.limit):
            current = " ⬅️" if conv.get("is_current") else ""
            print(f"  {conv['id'][:12]}... ({conv['artifact_count']} artifacts){current}")
    
    elif args.subcommand == "artifacts":
        for artifact in client.list_artifacts():
            print(f"  📝 {artifact['name']} ({artifact['type']})")
    
    elif args.subcommand == "tools":
        caps = client.get_capabilities()
        for tool in caps["tools"]:
            print(f"  • {tool}")
    
    elif args.subcommand == "stats":
        stats = client.get_session_stats()
        print(json.dumps(stats, indent=2, default=str))
    
    else:
        # Default: show overview
        caps = client.get_capabilities()
        print(f"\n📋 Antigravity Session")
        print(f"   Conversation: {client.get_conversation_id()[:12]}...")
        print(f"   Tools: {len(caps['tools'])}")
        print(f"   Artifacts: {len(client.list_artifacts())}")
    
    return 0


def cmd_cursor(args):
    """Handle Cursor commands."""
    client = CursorClient()
    connected = client.connect()
    
    if not connected:
        print("⚠️  Not connected to Cursor workspace")
        return 1
    
    if args.subcommand == "rules":
        rules = client.get_rules()
        if rules.get("exists", True):
            print(rules.get("content", "No rules defined"))
        else:
            print("No .cursorrules file found")
    
    elif args.subcommand == "models":
        for model in client.get_models():
            print(f"  • {model}")
    
    else:
        caps = client.get_capabilities()
        print(f"\n📋 Cursor Session")
        print(f"   Workspace: {client.workspace_path}")
        print(f"   Features: {', '.join(caps['features'][:5])}...")
    
    return 0


def cmd_vscode(args):
    """Handle VS Code commands."""  
    client = VSCodeClient()
    connected = client.connect()
    
    if not connected:
        print("⚠️  Not connected to VS Code workspace")
        return 1
    
    if args.subcommand == "extensions":
        for ext in client.list_extensions():
            print(f"  • {ext['publisher']}.{ext['name']} (v{ext['version']})")
    
    elif args.subcommand == "settings":
        settings = client.get_settings()
        print(json.dumps(settings, indent=2))
    
    elif args.subcommand == "commands":
        for cmd in client.list_commands():
            print(f"  • {cmd}")
    
    else:
        caps = client.get_capabilities()
        print(f"\n📋 VS Code Session")
        print(f"   Workspace: {client.workspace_path}")
        print(f"   Extensions: {len(client.list_extensions())}")
        print(f"   Features: {', '.join(caps['features'][:5])}...")
    
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="IDE Integration Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show all IDE status")
    status_parser.set_defaults(func=cmd_status)
    
    # Antigravity commands
    ag_parser = subparsers.add_parser("antigravity", aliases=["ag"], help="Antigravity commands")
    ag_parser.add_argument("subcommand", nargs="?", default=None,
                          choices=["conversations", "artifacts", "tools", "stats"],
                          help="Subcommand")
    ag_parser.add_argument("--limit", type=int, default=10, help="Limit for lists")
    ag_parser.set_defaults(func=cmd_antigravity)
    
    # Cursor commands
    cursor_parser = subparsers.add_parser("cursor", help="Cursor commands")
    cursor_parser.add_argument("subcommand", nargs="?", default=None,
                              choices=["rules", "models"],
                              help="Subcommand")
    cursor_parser.set_defaults(func=cmd_cursor)
    
    # VS Code commands
    vsc_parser = subparsers.add_parser("vscode", aliases=["vsc"], help="VS Code commands")
    vsc_parser.add_argument("subcommand", nargs="?", default=None,
                           choices=["extensions", "settings", "commands"],
                           help="Subcommand")
    vsc_parser.set_defaults(func=cmd_vscode)
    
    args = parser.parse_args()
    
    if args.command is None:
        # Default: show status
        cmd_status(args)
        return 0
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())