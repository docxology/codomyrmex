#!/usr/bin/env python3
"""
Orchestrator example for the 'ide' module.
Demonstrates using various IDE clients to manage workspace and execute commands.
"""

import sys
import tempfile
from pathlib import Path

# Ensure codomyrmex is in path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.ide import AntigravityClient, CursorClient, VSCodeClient


def demonstrate_cursor(workspace_path):
    print("\n--- Demonstrating CursorClient ---")
    client = CursorClient(workspace_path=workspace_path)
    if client.connect():
        print(f"Connected to Cursor at {workspace_path}")
        print(f"Capabilities: {client.get_capabilities()['features']}")

        # Create a test file
        test_file = Path(workspace_path) / "demo.py"
        test_file.write_text("print('hello from cursor demo')")

        client.open_file(str(test_file))
        print(f"Active file: {client.get_active_file()}")

        # Execute a command
        result = client.execute_command_safe("editor.action.formatDocument")
        print(f"Command result: {result.success}, Time: {result.execution_time:.4f}s")

        # Get rules
        rules = client.get_rules()
        print(f"Cursor rules exist: {rules.get('exists', False)}")

        client.disconnect()
    else:
        print("Failed to connect to Cursor")


def demonstrate_vscode(workspace_path):
    print("\n--- Demonstrating VSCodeClient ---")
    client = VSCodeClient(workspace_path=workspace_path)
    if client.connect():
        print(f"Connected to VS Code at {workspace_path}")

        # Update settings
        client.update_settings({"editor.fontSize": 14, "editor.tabSize": 2})
        print("Updated VS Code settings")

        # List extensions (simulated)
        extensions = client.list_extensions()
        print(f"Found {len(extensions)} extensions")

        client.disconnect()
    else:
        print("Failed to connect to VS Code")


def demonstrate_antigravity(artifact_dir):
    print("\n--- Demonstrating AntigravityClient ---")
    # Setup dummy artifact dir
    conv_dir = Path(artifact_dir) / "demo_conversation"
    conv_dir.mkdir(parents=True, exist_ok=True)
    (conv_dir / "task.md").write_text(
        "# Demo Task\nComplete the ide module improvements."
    )

    client = AntigravityClient(artifact_dir=str(artifact_dir))
    if client.connect():
        print(f"Connected to Antigravity, Session: {client.get_conversation_id()}")

        # List artifacts
        artifacts = client.list_artifacts()
        print(f"Artifacts: {[a['name'] for a in artifacts]}")

        # Create a new artifact
        client.create_artifact(
            "plan", "1. Implementation\n2. Testing", artifact_type="implementation_plan"
        )
        print("Created 'plan' artifact")

        # Stats
        stats = client.get_session_stats()
        print(
            f"Session stats: {stats['artifact_count']} artifacts, {stats['success_rate'] * 100}% success rate"
        )

        client.disconnect()
    else:
        print("Failed to connect to Antigravity")


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent / "config" / "ide" / "config.yaml"
    )
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    print("Codomyrmex IDE Module Orchestrator Demo")

    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir) / "workspace"
        workspace.mkdir()

        artifact_dir = Path(tmpdir) / "artifacts"
        artifact_dir.mkdir()

        demonstrate_cursor(str(workspace))
        demonstrate_vscode(str(workspace))
        demonstrate_antigravity(artifact_dir)

    print("\nDemo completed successfully!")


if __name__ == "__main__":
    main()
