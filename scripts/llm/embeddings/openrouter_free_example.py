#!/usr/bin/env python3
"""
OpenRouter Free Example - Embeddings Comparison

Simple example comparing text similarity using OpenRouter's free models
for semantic understanding (via completion-based similarity scoring).

Note: OpenRouter provides chat completions, not embedding APIs directly.
This example uses an LLM to score semantic similarity.

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


def get_similarity_score(provider, text1: str, text2: str) -> str:
    """Use LLM to assess semantic similarity between two texts."""
    messages = [
        Message(role="system", content="""You are a semantic similarity scorer.
Given two texts, rate their semantic similarity from 0 to 100.
Respond with ONLY a number, nothing else."""),
        Message(role="user", content=f"""Text 1: "{text1}"
Text 2: "{text2}"

Similarity score (0-100):"""),
    ]
    
    response = provider.complete(
        messages=messages,
        model="openrouter/free",
        temperature=0.1,
        max_tokens=10,
    )
    
    return response.content.strip()


def main():
    """Demonstrate semantic similarity with OpenRouter free models."""
    print("=" * 60)
    print("  OpenRouter Free Example - Semantic Similarity")
    print("=" * 60)
    print()
    
    # Check for API key
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("   Get your free API key at: https://openrouter.ai/keys")
        return 1
    
    # Test pairs
    test_pairs = [
        ("The cat sat on the mat", "A feline rested on the rug"),
        ("Python is a programming language", "JavaScript is used for web development"),
        ("The weather is sunny today", "I love eating pizza"),
    ]
    
    config = ProviderConfig(api_key=api_key, timeout=60.0)
    
    print("📡 Connecting to OpenRouter with free model...")
    print()
    
    with get_provider(ProviderType.OPENROUTER, config=config) as provider:
        print("🔍 Comparing semantic similarity:\n")
        
        for i, (text1, text2) in enumerate(test_pairs, 1):
            print(f"  Pair {i}:")
            print(f"    Text 1: \"{text1}\"")
            print(f"    Text 2: \"{text2}\"")
            
            score = get_similarity_score(provider, text1, text2)
            print(f"    Similarity: {score}")
            print()
    
    print("✅ Example completed successfully!")
    print("   💡 Use free models for semantic analysis during development!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
