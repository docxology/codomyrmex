#!/usr/bin/env python3
"""
OpenRouter LLM Provider - Real Usage Examples

Demonstrates actual OpenRouter API calls using the codomyrmex.llm.providers module.
OpenRouter provides unified access to multiple LLM providers including free models.

API Key Sources (in order of precedence):
    1. --api-key command line argument
    2. OPENROUTER_API_KEY environment variable
    3. Config file (~/.config/openrouter/api_key or custom path via --config)
    4. Interactive prompt (if --prompt-key is specified)

Usage:
    # List available free models
    python openrouter_usage.py --list-models
    
    # Simple completion with default free model
    python openrouter_usage.py --prompt "Explain Python decorators in one sentence"
    
    # Completion with specific model
    python openrouter_usage.py --prompt "Hello" --model "nvidia/nemotron-3-nano-30b-a3b:free"
    
    # Streaming response
    python openrouter_usage.py --prompt "Write a haiku about coding" --stream
    
    # Using API key from command line
    python openrouter_usage.py --api-key "sk-..." --prompt "Hello"
    
    # Using custom config file
    python openrouter_usage.py --config /path/to/api_key.txt --prompt "Hello"
    
    # Prompt for API key interactively
    python openrouter_usage.py --prompt-key --prompt "Hello"
"""

import sys
import os
import argparse
import getpass
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
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

# Default config file locations
DEFAULT_CONFIG_PATHS = [
    Path.home() / ".config" / "openrouter" / "api_key",
    Path.home() / ".openrouter_api_key",
    Path.cwd() / ".openrouter_api_key",
]


def read_api_key_from_file(config_path: Path) -> str | None:
    """Read API key from a config file."""
    try:
        if config_path.exists():
            content = config_path.read_text().strip()
            # Support both plain key and KEY=value format
            if content.startswith("OPENROUTER_API_KEY="):
                return content.split("=", 1)[1].strip().strip('"').strip("'")
            return content
    except Exception as e:
        print_warning(f"Could not read config file {config_path}: {e}")
    return None


def get_api_key(
    cli_key: str | None = None,
    config_path: str | None = None,
    prompt_for_key: bool = False,
) -> str:
    """Get OpenRouter API key from multiple sources.
    
    Priority:
        1. CLI argument (--api-key)
        2. Environment variable (OPENROUTER_API_KEY)
        3. Config file (--config or default locations)
        4. Interactive prompt (--prompt-key)
    """
    # 1. Command-line argument
    if cli_key:
        print_info("📍 Using API key from command line argument")
        return cli_key
    
    # 2. Environment variable
    env_key = os.environ.get("OPENROUTER_API_KEY")
    if env_key:
        print_info("📍 Using API key from OPENROUTER_API_KEY environment variable")
        return env_key
    
    # 3. Config file
    if config_path:
        # User-specified config file
        path = Path(config_path).expanduser()
        key = read_api_key_from_file(path)
        if key:
            print_info(f"📍 Using API key from config file: {path}")
            return key
        print_warning(f"Config file not found or empty: {path}")
    else:
        # Check default config locations
        for path in DEFAULT_CONFIG_PATHS:
            key = read_api_key_from_file(path)
            if key:
                print_info(f"📍 Using API key from config file: {path}")
                return key
    
    # 4. Interactive prompt
    if prompt_for_key:
        print_info("📍 No API key found. Enter it interactively:")
        key = getpass.getpass("Enter your OpenRouter API key: ").strip()
        if key:
            return key
        print_error("No API key entered")
        sys.exit(1)
    
    # No key found
    print_error("OPENROUTER_API_KEY not found")
    print_info("""
API key sources (in order of precedence):
  1. --api-key <key>           Command line argument
  2. OPENROUTER_API_KEY        Environment variable
  3. ~/.config/openrouter/api_key   Config file
  4. --prompt-key              Interactive prompt

Get your free API key at: https://openrouter.ai/keys

Quick setup:
  export OPENROUTER_API_KEY='your-key-here'
  
Or save to config file:
  mkdir -p ~/.config/openrouter
  echo 'your-key-here' > ~/.config/openrouter/api_key
  chmod 600 ~/.config/openrouter/api_key
""")
    sys.exit(1)


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


def complete_prompt(
    prompt: str,
    model: str | None = None,
    stream: bool = False,
    api_key: str | None = None,
    config_path: str | None = None,
    prompt_for_key: bool = False,
):
    """Run a completion with OpenRouter."""
    key = get_api_key(api_key, config_path, prompt_for_key)
    
    config = ProviderConfig(
        api_key=key,
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


def demonstrate_context_manager(
    api_key: str | None = None,
    config_path: str | None = None,
    prompt_for_key: bool = False,
):
    """Demonstrate context manager pattern for resource cleanup."""
    print_info("🔧 Context Manager Pattern:\n")
    
    key = get_api_key(api_key, config_path, prompt_for_key)
    config = ProviderConfig(api_key=key)
    
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
  python openrouter_usage.py --api-key "sk-..." --prompt "Hello"
  python openrouter_usage.py --config ~/.openrouter_key --prompt "Hi"
  python openrouter_usage.py --prompt-key --prompt "Hello"
  python openrouter_usage.py --demo
        """
    )
    # Action arguments
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
    
    # API key arguments
    parser.add_argument("--api-key", "-k", type=str, default=None,
                        help="OpenRouter API key (overrides env var and config file)")
    parser.add_argument("--config", "-c", type=str, default=None,
                        help="Path to config file containing API key")
    parser.add_argument("--prompt-key", action="store_true",
                        help="Prompt for API key interactively if not found")
    
    args = parser.parse_args()
    
    setup_logging()
    print_info("🚀 OpenRouter LLM Provider Examples\n")
    
    if args.list_models:
        list_models()
        return 0
    
    if args.demo:
        demonstrate_context_manager(
            api_key=args.api_key,
            config_path=args.config,
            prompt_for_key=args.prompt_key,
        )
        return 0
    
    if args.prompt:
        complete_prompt(
            args.prompt,
            model=args.model,
            stream=args.stream,
            api_key=args.api_key,
            config_path=args.config,
            prompt_for_key=args.prompt_key,
        )
        return 0
    
    # No arguments - show help
    parser.print_help()
    print_info("\n💡 Quick start:")
    print("   export OPENROUTER_API_KEY='your-key-here'")
    print("   python openrouter_usage.py --prompt 'Hello, world!'")
    print("\n   Or use --api-key to pass directly:")
    print("   python openrouter_usage.py --api-key 'sk-...' --prompt 'Hello!'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
