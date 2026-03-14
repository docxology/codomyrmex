#!/usr/bin/env python3
"""Core — Thin Script Orchestrator.

Exercises core agent infrastructure: config, capabilities, parsers.

Usage:
    python scripts/agents/core/run_core.py
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    sys.path.insert(
        0, str(Path(__file__).resolve().parent.parent.parent.parent / "src")
    )

from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main() -> int:
    setup_logging()
    print_info("Core — exercising agent infrastructure...")

    try:
        from codomyrmex.agents.core import (
            AgentCapabilities,
            AgentConfig,
            AgentRequest,
            AgentResponse,
            clean_response,
            get_config,
            parse_code_blocks,
            parse_json_response,
            reset_config,
            set_config,
        )
    except ImportError as e:
        print_error(f"Import failed: {e}")
        return 1

    # Config roundtrip
    config = get_config()
    print_success(f"Config loaded: {type(config).__name__}")
    print_info(f"  Capabilities: {[c.name for c in AgentCapabilities]}")

    # Parser exercise
    json_result = parse_json_response('{"answer": 42}')
    print_info(f"  parse_json_response: {json_result}")

    code_blocks = parse_code_blocks("```python\nprint('hello')\n```")
    print_info(f"  parse_code_blocks: {len(code_blocks)} block(s)")

    cleaned = clean_response("  hello world  \n\n")
    print_info(f"  clean_response: '{cleaned}'")

    print_success("Core infrastructure probe complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
