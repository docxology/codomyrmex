#!/usr/bin/env python3
"""
OpenRouter LLM Provider - Real Usage Examples

Demonstrates actual OpenRouter API calls using the codomyrmex.llm.providers module.
OpenRouter provides unified access to multiple LLM providers including free models.

Environment:
    OPENROUTER_API_KEY: Your OpenRouter API key (get one at https://openrouter.ai/keys)

Usage:
    # List available free models
    python openrouter_usage.py --list-models
    
    # Simple completion with default free model
    python openrouter_usage.py --prompt "Explain Python decorators in one sentence"
    
    # Completion with specific model
    python openrouter_usage.py --prompt "Hello" --model "nvidia/nemotron-3-nano-30b-a3b:free"
    
    # Streaming response
    python openrouter_usage.py --prompt "Write a haiku about coding" --stream
"""

import sys
import os
import argparse
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.utils.cli_helpers import setup_logging, print_success, print_info, print_error, print_warning
from codomyrmex.llm.providers import (
    get_provider,
    ProviderType,
    ProviderConfig,
    Message,
    OpenRouterProvider,
)


def get_api_key() -> str:
    """Get OpenRouter API key from environment."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print_error("OPENROUTER_API_KEY environment variable not set")
        print_info("Get your API key at: https://openrouter.ai/keys")
        sys.exit(1)
    return api_key


def list_models():
    """List available free models on OpenRouter."""
    print_info("📋 Available Free Models on OpenRouter:\n")
    
    # Create provider without API key just to list models
    config = ProviderConfig(api_key="dummy")
    provider = OpenRouterProvider(config)
    
    for model in provider.list_models():
        if model == "openrouter/free":
            print(f"  ✨ {model} (auto-selects best available)")
        else:
            print(f"  • {model}")
    
    print_info("\nFor full model list, see: https://openrouter.ai/models")


def complete_prompt(prompt: str, model: str | None = None, stream: bool = False):
    """Run a completion with OpenRouter."""
    api_key = get_api_key()
    
    config = ProviderConfig(
        api_key=api_key,
        timeout=60.0,
        max_retries=3,
    )
    
    with get_provider(ProviderType.OPENROUTER, config=config) as provider:
        messages = [
            Message(role="system", content="You are a helpful assistant. Be concise."),
            Message(role="user", content=prompt),
        ]
        
        model_name = model or provider._default_model()
        print_info(f"🤖 Model: {model_name}")
        print_info(f"📝 Prompt: {prompt}\n")
        
        if stream:
            print_info("📡 Streaming response:\n")
            print("─" * 50)
            full_response = ""
            for chunk in provider.complete_stream(messages, model=model):
                print(chunk, end="", flush=True)
                full_response += chunk
            print("\n" + "─" * 50)
            print_success(f"\n✅ Streaming complete ({len(full_response)} chars)")
        else:
            response = provider.complete(messages, model=model)
            print("─" * 50)
            print(response.content)
            print("─" * 50)
            
            if response.usage:
                print_info(f"\n📊 Token usage:")
                print(f"   Prompt: {response.usage.get('prompt_tokens', 'N/A')}")
                print(f"   Completion: {response.usage.get('completion_tokens', 'N/A')}")
                print(f"   Total: {response.usage.get('total_tokens', 'N/A')}")
            
            print_success(f"\n✅ Completion successful (model: {response.model})")


def demonstrate_context_manager():
    """Demonstrate context manager pattern for resource cleanup."""
    print_info("🔧 Context Manager Pattern:\n")
    
    api_key = get_api_key()
    config = ProviderConfig(api_key=api_key)
    
    # Using context manager ensures cleanup
    with get_provider(ProviderType.OPENROUTER, config=config) as provider:
        print_info(f"  Provider type: {provider.provider_type.value}")
        print_info(f"  Base URL: {provider.config.base_url}")
        print_info(f"  Default model: {provider._default_model()}")
        # Client is automatically cleaned up on exit
    
    print_success("  ✅ Resources cleaned up automatically")


def main():
    parser = argparse.ArgumentParser(
        description="OpenRouter LLM Provider Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python openrouter_usage.py --list-models
  python openrouter_usage.py --prompt "What is Python?"
  python openrouter_usage.py --prompt "Write a poem" --stream
  python openrouter_usage.py --demo
        """
    )
    parser.add_argument("--list-models", "-l", action="store_true",
                        help="List available free models")
    parser.add_argument("--prompt", "-p", type=str,
                        help="Prompt to send to the model")
    parser.add_argument("--model", "-m", type=str, default=None,
                        help="Model to use (default: openrouter/free)")
    parser.add_argument("--stream", "-s", action="store_true",
                        help="Use streaming response")
    parser.add_argument("--demo", "-d", action="store_true",
                        help="Run demonstration of features")
    args = parser.parse_args()
    
    setup_logging()
    print_info("🚀 OpenRouter LLM Provider Examples\n")
    
    if args.list_models:
        list_models()
        return 0
    
    if args.demo:
        demonstrate_context_manager()
        return 0
    
    if args.prompt:
        complete_prompt(args.prompt, model=args.model, stream=args.stream)
        return 0
    
    # No arguments - show help
    parser.print_help()
    print_info("\n💡 Quick start:")
    print("   export OPENROUTER_API_KEY='your-key-here'")
    print("   python openrouter_usage.py --prompt 'Hello, world!'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
