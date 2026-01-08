#!/usr/bin/env python3
"""IDE Status Checker

Check the status of IDE connections and list available capabilities
for all supported IDEs (Antigravity, Cursor, VS Code).

Usage:
    uv run python scripts/ide/ide_status.py
    uv run python scripts/ide/ide_status.py --verbose
    uv run python scripts/ide/ide_status.py --json
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.ide.antigravity import AntigravityClient
from codomyrmex.ide.cursor import CursorClient
from codomyrmex.ide.vscode import VSCodeClient


def check_ide_status(verbose: bool = False) -> dict:
    """Check status of all IDE integrations.
    
    Args:
        verbose: If True, include detailed capability info.
        
    Returns:
        Dict with status for each IDE.
    """
    results = {}
    
    # Check Antigravity
    ag_client = AntigravityClient()
    ag_connected = ag_client.connect()
    results["antigravity"] = {
        "connected": ag_connected,
        "status": ag_client.status.value,
        "conversation_id": ag_client.get_conversation_id()[:8] + "..." if ag_client.get_conversation_id() else None,
    }
    if verbose and ag_connected:
        caps = ag_client.get_capabilities()
        results["antigravity"]["tools"] = len(caps["tools"])
        results["antigravity"]["features"] = caps["features"]
    
    # Check Cursor
    cursor_client = CursorClient()
    cursor_connected = cursor_client.connect()
    results["cursor"] = {
        "connected": cursor_connected,
        "workspace": str(cursor_client.workspace_path) if cursor_connected else None,
    }
    if verbose and cursor_connected:
        caps = cursor_client.get_capabilities()
        results["cursor"]["features"] = caps["features"]
        results["cursor"]["models"] = caps["models"]
    
    # Check VS Code
    vsc_client = VSCodeClient()
    vsc_connected = vsc_client.connect()
    results["vscode"] = {
        "connected": vsc_connected,
        "workspace": str(vsc_client.workspace_path) if vsc_connected else None,
    }
    if verbose and vsc_connected:
        caps = vsc_client.get_capabilities()
        results["vscode"]["features"] = caps["features"]
        results["vscode"]["extensions"] = len(vsc_client.list_extensions())
    
    return results


def print_status(results: dict, use_json: bool = False) -> None:
    """Print IDE status in a readable format.
    
    Args:
        results: Status results dictionary.
        use_json: If True, output as JSON.
    """
    if use_json:
        print(json.dumps(results, indent=2))
        return
    
    print("\n🖥️  IDE Status Report")
    print("=" * 50)
    
    for ide_name, status in results.items():
        icon = "✅" if status.get("connected") else "⚪"
        print(f"\n{icon} {ide_name.title()}")
        
        for key, value in status.items():
            if key != "connected":
                if isinstance(value, list):
                    print(f"   {key}: {len(value)} items")
                else:
                    print(f"   {key}: {value}")
    
    print("\n" + "=" * 50)
    connected_count = sum(1 for s in results.values() if s.get("connected"))
    print(f"Connected: {connected_count}/{len(results)} IDEs")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check IDE connection status",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Include detailed capability information",
    )
    parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output as JSON",
    )
    
    args = parser.parse_args()
    
    results = check_ide_status(verbose=args.verbose)
    print_status(results, use_json=args.json)


if __name__ == "__main__":
    main()
