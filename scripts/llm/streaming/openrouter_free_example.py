#!/usr/bin/env python3
"""
OpenRouter Free Example - Streaming

Simple example demonstrating streaming responses with OpenRouter's free models.

Usage:
    export OPENROUTER_API_KEY='your-key-here'
    python openrouter_free_example.py
"""

import sys
import os
from pathlib import Path

# Ensure codomyrmex is in path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.llm.providers import get_provider, ProviderType, ProviderConfig, Message


def main():
    """Demonstrate streaming with OpenRouter free models."""
    print("=" * 60)
    print("  OpenRouter Free Example - Streaming")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("   Get your free API key at: https://openrouter.ai/keys")
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
