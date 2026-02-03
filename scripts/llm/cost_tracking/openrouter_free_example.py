#!/usr/bin/env python3
"""
OpenRouter Free Example - Cost Tracking

Simple example demonstrating cost tracking with OpenRouter's free models.
Uses real API calls to show token counting and cost estimation.

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
    """Demonstrate cost tracking with OpenRouter free models."""
    print("=" * 60)
    print("  OpenRouter Free Example - Cost Tracking")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("   Get your free API key at: https://openrouter.ai/keys")
        print("\n   To run this example:")
        print("   export OPENROUTER_API_KEY='your-key-here'")
        print("   python openrouter_free_example.py")
        return 1
    
    # Create provider
    config = ProviderConfig(api_key=api_key, timeout=60.0)
    
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
            
            print("💰 Cost Tracking:")
            print(f"   Prompt tokens: {prompt_tokens}")
            print(f"   Completion tokens: {completion_tokens}")
            print(f"   Total tokens: {total_tokens}")
            print(f"   Cost: $0.00 (free model!)")
        else:
            print("⚠️  No usage data returned")
        
        print()
        print("✅ Example completed successfully!")
        print("   💡 Free models have no API cost - perfect for development!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
