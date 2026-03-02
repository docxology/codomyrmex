#!/usr/bin/env python3
"""
Agent Setup and Diagnostics Example

Demonstrates the setup() and test_connection() lifecycle for all agent types.
Useful for verifying agent configurations before running workflows.
"""
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import (
    ClaudeClient,
    CodexClient,
    GeminiClient,
    JulesClient,
    OpenCodeClient,
    CodeEditor,
)
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_success, print_error, print_info, print_section, print_warning
)


AGENT_CLASSES = [
    ("Claude (API)", ClaudeClient),
    ("Codex (API)", CodexClient),
    ("Gemini (CLI)", GeminiClient),
    ("Jules (CLI)", JulesClient),
    ("OpenCode (CLI)", OpenCodeClient),
    ("CodeEditor", CodeEditor),
]


def main():
    setup_logging()
    print_section("Agent Diagnostics")

    results = {}

    for name, agent_class in AGENT_CLASSES:
        print_info(f"\nTesting {name}...")
        try:
            agent = agent_class()
            connected = agent.test_connection()
            if connected:
                print_success(f"  {name}: CONNECTED")
                results[name] = "connected"
            else:
                print_warning(f"  {name}: NOT CONFIGURED")
                results[name] = "not_configured"
        except Exception as e:
            print_error(f"  {name}: ERROR - {e}")
            results[name] = f"error: {e}"

    # Summary
    print_section("Diagnostics Summary")
    connected_count = sum(1 for v in results.values() if v == "connected")
    print_info(f"Connected Agents: {connected_count}/{len(AGENT_CLASSES)}")
    
    for name, status in results.items():
        icon = "✓" if status == "connected" else "✗"
        print_info(f"  {icon} {name}: {status}")

    return 0 if connected_count > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
