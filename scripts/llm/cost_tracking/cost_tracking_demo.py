#!/usr/bin/env python3
"""
Cost Tracking Demo Script

Demonstrates token counting and cost estimation for LLM API usage.
Uses the codomyrmex.llm.providers module for real API interactions.

Features:
    - Token counting for prompts and responses
    - Cost estimation based on model pricing
    - Usage analytics and reporting
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_warning


def estimate_tokens(text: str) -> int:
    """Estimate token count using simple heuristic.
    
    Rough approximation: ~4 characters per token for English text.
    For accurate counts, use tiktoken or the API's token counter.
    """
    return len(text) // 4


def estimate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: str = "openrouter/free"
) -> dict:
    """Estimate cost based on model pricing.
    
    Pricing as of 2026 (per 1M tokens):
    - Free models: $0 (rate limited)
    - GPT-4o: ~$5/1M input, ~$15/1M output
    - Claude 3.5 Sonnet: ~$3/1M input, ~$15/1M output
    """
    # Pricing per million tokens (input, output)
    PRICING = {
        "openrouter/free": (0.0, 0.0),
        "gpt-4o": (5.0, 15.0),
        "gpt-4o-mini": (0.15, 0.60),
        "claude-3-5-sonnet": (3.0, 15.0),
        "claude-3-5-haiku": (0.25, 1.25),
    }
    
    input_price, output_price = PRICING.get(model, (0.0, 0.0))
    
    input_cost = (prompt_tokens / 1_000_000) * input_price
    output_cost = (completion_tokens / 1_000_000) * output_price
    
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "input_cost_usd": input_cost,
        "output_cost_usd": output_cost,
        "total_cost_usd": input_cost + output_cost,
        "model": model,
    }


def demo_token_counting():
    """Demonstrate token counting."""
    print_info("📊 Token Counting Demo\n")
    
    sample_prompts = [
        "Hello, how are you?",
        "Explain the concept of recursion in programming with examples.",
        "Write a detailed essay about the history of artificial intelligence, "
        "covering key milestones from the 1950s to present day, including "
        "the work of pioneers like Alan Turing, John McCarthy, and recent "
        "advances in deep learning.",
    ]
    
    for i, prompt in enumerate(sample_prompts, 1):
        tokens = estimate_tokens(prompt)
        print(f"  Prompt {i}: ~{tokens} tokens ({len(prompt)} chars)")
        print(f"    \"{prompt[:50]}{'...' if len(prompt) > 50 else ''}\"")
        print()


def demo_cost_estimation():
    """Demonstrate cost estimation for different models."""
    print_info("💰 Cost Estimation Demo\n")
    
    # Simulate a typical conversation
    prompt_tokens = 500
    completion_tokens = 1000
    
    models = [
        "openrouter/free",
        "gpt-4o-mini",
        "gpt-4o",
        "claude-3-5-haiku",
        "claude-3-5-sonnet",
    ]
    
    print(f"  Scenario: {prompt_tokens} input + {completion_tokens} output tokens\n")
    print(f"  {'Model':<25} {'Input Cost':>12} {'Output Cost':>12} {'Total':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*12}")
    
    for model in models:
        cost = estimate_cost(prompt_tokens, completion_tokens, model)
        input_str = f"${cost['input_cost_usd']:.6f}"
        output_str = f"${cost['output_cost_usd']:.6f}"
        total_str = f"${cost['total_cost_usd']:.6f}"
        print(f"  {model:<25} {input_str:>12} {output_str:>12} {total_str:>12}")


def demo_usage_tracking():
    """Demonstrate usage tracking over multiple requests."""
    print_info("\n📈 Usage Tracking Demo\n")
    
    # Simulate usage over time
    usage_log = []
    
    requests = [
        {"prompt_tokens": 100, "completion_tokens": 200, "model": "openrouter/free"},
        {"prompt_tokens": 500, "completion_tokens": 1000, "model": "gpt-4o-mini"},
        {"prompt_tokens": 250, "completion_tokens": 500, "model": "gpt-4o-mini"},
        {"prompt_tokens": 1000, "completion_tokens": 2000, "model": "gpt-4o"},
    ]
    
    total_cost = 0.0
    total_tokens = 0
    
    for req in requests:
        cost = estimate_cost(req["prompt_tokens"], req["completion_tokens"], req["model"])
        total_cost += cost["total_cost_usd"]
        total_tokens += cost["total_tokens"]
        usage_log.append(cost)
    
    print(f"  Total requests: {len(requests)}")
    print(f"  Total tokens: {total_tokens:,}")
    print(f"  Total cost: ${total_cost:.6f}")
    
    print_warning("\n  💡 Tip: Use free models for development to minimize costs!")


def main():
    """Main demonstration."""
    setup_logging()
    print("=" * 60)
    print("  Cost Tracking Demo - Token Counting & Billing Estimation")
    print("=" * 60)
    print()
    
    demo_token_counting()
    demo_cost_estimation()
    demo_usage_tracking()
    
    print()
    print_success("✅ Demo completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
