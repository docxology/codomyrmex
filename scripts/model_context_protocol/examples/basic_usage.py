#!/usr/bin/env python3
"""
Model Context Protocol - Real Usage Examples

Demonstrates actual MCP schemas:
- Tool calls and results
- Message schemas
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.model_context_protocol import MCPMessage, MCPToolCall, MCPToolResult
from codomyrmex.utils.cli_helpers import print_info, print_success, setup_logging


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "model_context_protocol" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/model_context_protocol/config.yaml")

    setup_logging()
    print_info("Running MCP Examples...")

    # 1. Tool Call
    print_info("Testing MCPToolCall schema...")
    call = MCPToolCall(
        tool_name="read_file",
        arguments={"path": "test.txt"}
    )
    if call.tool_name == "read_file":
        print_success("  MCPToolCall functional.")

    # 2. Tool Result
    print_info("Testing MCPToolResult schema...")
    result = MCPToolResult(
        status="success",
        data={"output": "File content here"}
    )
    if result.status == "success":
        print_success("  MCPToolResult functional.")

    # 3. Message
    print_info("Testing MCPMessage schema...")
    msg = MCPMessage(
        role="user",
        content="Hello MCP"
    )
    if msg.role == "user":
        print_success("  MCPMessage functional.")

    print_success("MCP examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
