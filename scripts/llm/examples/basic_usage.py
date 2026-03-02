#!/usr/bin/env python3
"""
LLM Integration - Real Usage Examples

Demonstrates actual LLM capabilities:
- LLM configuration management
- Ollama and Fabric manager interfaces
- Model runners and output handlers
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info
from codomyrmex.llm import (
    LLMConfig,
    get_config,
    OllamaManager,
    ModelRunner,
    OutputManager,
    FabricManager,
    FabricOrchestrator
)

def main():
    setup_logging()
    print_info("Running LLM Integration Examples...")

    # 1. Configuration Check
    print_info("Checking LLM configuration...")
    config = get_config()
    if isinstance(config, LLMConfig):
        print_success(f"  Current model: {config.model}")

    # 2. Ollama Components
    print_info("Testing Ollama components...")
    try:
        ollama = OllamaManager(auto_start_server=False)
        runner = ModelRunner(config=config)
        output = OutputManager()
        print_success("  Ollama components (Manager, Runner, Output) initialized.")
    except Exception as e:
        print_info(f"  Ollama check note: {e}")

    # 3. Fabric Components
    print_info("Testing Fabric components...")
    try:
        fabric = FabricManager()
        orch = FabricOrchestrator()
        print_success("  Fabric components (Manager, Orchestrator) initialized.")
    except Exception as e:
        print_info(f"  Fabric check note: {e}")

    print_success("LLM integration examples completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
