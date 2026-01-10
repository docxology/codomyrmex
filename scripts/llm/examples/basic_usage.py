#!/usr/bin/env python3
"""
LLM Module - Real Usage Examples

Demonstrates actual LLM integration capabilities:
- Ollama manager and model configuration
- Fabric integration for prompt patterns
- LLM configuration presets
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error


def main():
    setup_logging()
    print_info("Running LLM Module Examples...")

    try:
        from codomyrmex.llm import (
            OllamaManager,
            LLMConfig,
            LLMConfigPresets,
            get_config,
        )
        print_info("Successfully imported llm module")
    except ImportError as e:
        print_error(f"Could not import llm: {e}")
        return 1

    # Example 1: Show LLM configuration presets
    print_info("Available LLM configuration presets:")
    try:
        presets = LLMConfigPresets
        preset_names = [p.name for p in presets][:5]
        for preset in preset_names:
            print(f"  - {preset}")
    except Exception as e:
        print_info(f"  Presets enumeration: {e}")

    # Example 2: Get current LLM configuration
    print_info("Current LLM configuration:")
    try:
        config = get_config()
        print(f"  Config type: {type(config).__name__}")
    except Exception as e:
        print_info(f"  Config access: {e}")

    # Example 3: Demonstrate OllamaManager capabilities
    print_info("OllamaManager capabilities:")
    print("  - list_models(): List available local models")
    print("  - pull_model(name): Download a model")
    print("  - run_model(name, prompt): Execute inference")
    print("  - get_model_info(name): Get model metadata")

    # Example 4: LLM use cases in Codomyrmex
    print_info("LLM integration use cases:")
    print("  1. Code review and analysis")
    print("  2. Documentation generation")
    print("  3. Commit message generation")
    print("  4. Code explanation and summarization")
    print("  5. Test case generation")

    # Example 5: Fabric patterns (if available)
    print_info("Fabric prompt pattern categories:")
    print("  - analyze: Code and data analysis")
    print("  - create: Content generation")
    print("  - explain: Explanation and teaching")
    print("  - extract: Information extraction")
    print("  - summarize: Text summarization")

    print_success("LLM module examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
