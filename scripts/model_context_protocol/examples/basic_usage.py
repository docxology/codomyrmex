#!/usr/bin/env python3
"""
Model Context Protocol - Real Usage Examples

Demonstrates actual MCP schemas:
- Tool calls and results
- Message schemas
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error
from codomyrmex.model_context_protocol import (
    MCPToolCall,
    MCPToolResult,
    MCPMessage
)

def main():
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
