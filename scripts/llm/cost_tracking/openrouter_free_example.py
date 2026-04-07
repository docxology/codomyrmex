#!/usr/bin/env python3
"""
OpenRouter Free Example - Cost Tracking

Simple example demonstrating cost tracking with OpenRouter's free models.
Uses real API calls to show token counting and cost estimation.

API Key Sources:
    1. OPENROUTER_API_KEY environment variable
    2. ~/.config/openrouter/api_key config file

Usage:
    python openrouter_free_example.py
"""

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# Ensure codomyrmex is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.llm.providers import Message, ProviderConfig, ProviderType, get_provider

# Config file locations
CONFIG_PATHS = [
    Path.home() / ".config" / "openrouter" / "api_key",
    Path.home() / ".openrouter_api_key",
]


def get_api_key() -> str | None:
    """Get API key from environment or config file."""
    # Check environment variable first
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        return api_key

    # Check config files
    for path in CONFIG_PATHS:
        try:
            if path.exists():
                content = path.read_text().strip()
                if content.startswith("OPENROUTER_API_KEY="):
                    return content.split("=", 1)[1].strip().strip('"').strip("'")
                return content
        except Exception as exc:
            logger.debug(
                "Could not read config from %s: %s", path, type(exc).__name__
            )

    return None


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent / "config" / "llm" / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/llm/config.yaml")

    """Demonstrate cost tracking with OpenRouter free models."""
    print("=" * 60)
    print("  OpenRouter Free Example - Cost Tracking")
    print("=" * 60)
    print()

    auth = get_api_key()
    if not auth:
        print("OpenRouter auth not configured.")
        print("   See https://openrouter.ai/ and the module docstring for setup.")
        return 1

    # Create provider
    config = ProviderConfig(api_key=auth, timeout=60.0)

    print("📡 Connecting to OpenRouter with free model...")
    print()

    with get_provider(ProviderType.OPENROUTER, config=config) as provider:
        # Simple request
        messages = [
            Message(role="system", content="You are helpful. Be very brief."),
            Message(role="user", content="What is 2+2? Answer in one word."),
        ]

        print("📤 Sending request...")
        response = provider.complete(
            messages=messages,
            model="openrouter/free",  # Free model auto-selection
            temperature=0.1,
            max_tokens=50,
        )

        print("📥 Response received!\n")
        print(f"  Model: {response.model}")
        print(f"  Content: {response.content}")
        print()

        # Cost tracking
        if response.usage:
            prompt_tokens = response.usage.get("prompt_tokens", 0)
            completion_tokens = response.usage.get("completion_tokens", 0)
            total_tokens = response.usage.get("total_tokens", 0)

            print("💰 Usage (from API):")
            print(f"   Input units: {prompt_tokens}")
            print(f"   Output units: {completion_tokens}")
            print(f"   Total units: {total_tokens}")
            print("   Cost: $0.00 (free model!)")
        else:
            print("⚠️  No usage data returned")

        print()
        print("✅ Example completed successfully!")
        print("   💡 Free models have no API cost - perfect for development!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
