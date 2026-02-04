#!/usr/bin/env python3
"""
OpenRouter Free Example - Streaming

Simple example demonstrating streaming responses with OpenRouter's free models.

API Key Sources:
    1. OPENROUTER_API_KEY environment variable
    2. ~/.config/openrouter/api_key config file

Usage:
    python openrouter_free_example.py
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.llm.providers import get_provider, ProviderType, ProviderConfig, Message

# Config file locations
CONFIG_PATHS = [
    Path.home() / ".config" / "openrouter" / "api_key",
    Path.home() / ".openrouter_api_key",
]


def get_api_key() -> str | None:
    """Get API key from environment or config file."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key:
        return api_key
    for path in CONFIG_PATHS:
        try:
            if path.exists():
                content = path.read_text().strip()
                if content.startswith("OPENROUTER_API_KEY="):
                    return content.split("=", 1)[1].strip().strip('"').strip("'")
                return content
        except Exception:
            pass
    return None


def main():
    """Demonstrate streaming with OpenRouter free models."""
    print("=" * 60)
    print("  OpenRouter Free Example - Streaming")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = get_api_key()
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        print("   Get your free API key at: https://openrouter.ai/keys")
        print("\n   Setup: export OPENROUTER_API_KEY='key' or ~/.config/openrouter/api_key")
        return 1
    
    config = ProviderConfig(api_key=api_key, timeout=60.0)
    prompt = "Write a short poem about coding (4 lines max)."
    
    print(f"📝 Prompt: \"{prompt}\"")
    print()
    print("📡 Connecting to OpenRouter with free model...")
    print()
    
    with get_provider(ProviderType.OPENROUTER, config=config) as provider:
        messages = [
            Message(role="system", content="You are a creative poet. Be concise."),
            Message(role="user", content=prompt),
        ]
        
        print("🌊 Streaming response:\n")
        print("-" * 40)
        
        total_chars = 0
        chunk_count = 0
        
        for chunk in provider.complete_stream(
            messages=messages,
            model="openrouter/free",
            temperature=0.8,
            max_tokens=100,
        ):
            print(chunk, end="", flush=True)
            total_chars += len(chunk)
            chunk_count += 1
        
        print("\n" + "-" * 40)
        print()
        print(f"📊 Streaming stats:")
        print(f"   Chunks received: {chunk_count}")
        print(f"   Total characters: {total_chars}")
    
    print()
    print("✅ Example completed successfully!")
    print("   💡 Streaming provides real-time output for better UX!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
