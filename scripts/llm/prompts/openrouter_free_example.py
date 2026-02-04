#!/usr/bin/env python3
"""
OpenRouter Free Example - Prompt Templates

Simple example demonstrating prompt template usage with OpenRouter's free models.

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


# Simple prompt templates
TEMPLATES = {
    "explain": """Explain {topic} to someone who is a {audience}.
Be clear and use appropriate language for this audience.
Keep your explanation under 100 words.""",

    "summarize": """Summarize the following text in a {style} style:

{text}

Summary (under 50 words):""",

    "translate": """Translate the following text from {source} to {target}:

{text}

Translation:""",
}


def render_template(template_name: str, **kwargs) -> str:
    """Render a template with provided variables."""
    template = TEMPLATES.get(template_name, "")
    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", str(value))
    return template


def main():
    """Demonstrate prompt templates with OpenRouter free models."""
    print("=" * 60)
    print("  OpenRouter Free Example - Prompt Templates")
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
    
    print("📡 Connecting to OpenRouter with free model...")
    print()
    
    # Example: Explain template
    print("📝 Template: 'explain'")
    prompt = render_template(
        "explain",
        topic="recursion in programming",
        audience="beginner"
    )
    print(f"   Rendered prompt: \"{prompt[:60]}...\"")
    print()
    
    with get_provider(ProviderType.OPENROUTER, config=config) as provider:
        messages = [Message(role="user", content=prompt)]
        
        print("🤖 Calling OpenRouter free model...")
        response = provider.complete(
            messages=messages,
            model="openrouter/free",
            temperature=0.7,
            max_tokens=150,
        )
        
        print(f"\n📤 Response:\n")
        print(f"   {response.content}")
        print()
        
        if response.usage:
            print(f"📊 Tokens used: {response.usage.get('total_tokens', 'N/A')}")
    
    print()
    print("✅ Example completed successfully!")
    print("   💡 Templates help create consistent, reusable prompts!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
