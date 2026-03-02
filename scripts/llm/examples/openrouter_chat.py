#!/usr/bin/env python3
"""
OpenRouter Interactive Chat - Multi-turn Conversation Example

Demonstrates multi-turn conversations with OpenRouter's free models.
Supports configurable system prompts, conversation history, and model selection.

API Key Sources:
    1. --api-key command line argument
    2. OPENROUTER_API_KEY environment variable
    3. ~/.config/openrouter/api_key config file

Usage:
    # Interactive chat with default settings
    python openrouter_chat.py
    
    # With custom system prompt
    python openrouter_chat.py --system "You are a pirate captain"
    
    # With specific model
    python openrouter_chat.py --model "google/gemma-3-12b-it:free"
    
    # Save conversation to file
    python openrouter_chat.py --save-to chat_log.json
    
    # Non-interactive mode with preset messages
    python openrouter_chat.py --batch "Hello" "How are you?" "Tell me a joke"
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.llm.providers import (
    get_provider,
    ProviderType,
    ProviderConfig,
    Message,
    OpenRouterProvider,
)

# Default config file locations
CONFIG_PATHS = [
    Path.home() / ".config" / "openrouter" / "api_key",
    Path.home() / ".openrouter_api_key",
    Path.cwd() / ".openrouter_api_key",
]


def get_api_key(cli_key: str | None = None) -> str | None:
    """Get API key from multiple sources."""
    if cli_key:
        return cli_key
    
    env_key = os.environ.get("OPENROUTER_API_KEY")
    if env_key:
        return env_key
    
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


class ChatSession:
    """Multi-turn chat session manager."""
    
    def __init__(
        self,
        provider,
        model: str = "openrouter/free",
        system_prompt: str | None = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
    ):
        self.provider = provider
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.messages: list[Message] = []
        self.conversation_log: list[dict] = []
        
        if system_prompt:
            self.messages.append(Message(role="system", content=system_prompt))
            self.conversation_log.append({
                "role": "system",
                "content": system_prompt,
                "timestamp": datetime.now().isoformat(),
            })
    
    def send(self, user_message: str, stream: bool = False) -> str:
        """Send a message and get a response."""
        # Add user message to history
        self.messages.append(Message(role="user", content=user_message))
        self.conversation_log.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat(),
        })
        
        if stream:
            # Streaming response
            full_response = ""
            for chunk in self.provider.complete_stream(
                messages=self.messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            ):
                print(chunk, end="", flush=True)
                full_response += chunk
            print()  # Newline after streaming
            response_content = full_response
        else:
            # Standard completion
            response = self.provider.complete(
                messages=self.messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            response_content = response.content
        
        # Add assistant response to history
        self.messages.append(Message(role="assistant", content=response_content))
        self.conversation_log.append({
            "role": "assistant",
            "content": response_content,
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
        })
        
        return response_content
    
    def save(self, filepath: str | Path) -> None:
        """Save conversation to JSON file."""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "model": self.model,
            "started_at": self.conversation_log[0]["timestamp"] if self.conversation_log else None,
            "messages": self.conversation_log,
        }
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Conversation saved to: {filepath}")
    
    def display_history(self) -> None:
        """Display conversation history."""
        print("\n📜 Conversation History:")
        print("=" * 50)
        for msg in self.conversation_log:
            role = msg["role"].upper()
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            print(f"[{role}] {content}")
        print("=" * 50)


def run_interactive_chat(
    api_key: str,
    model: str = "openrouter/free",
    system_prompt: str | None = None,
    max_tokens: int = 500,
    temperature: float = 0.7,
    stream: bool = True,
    save_to: str | None = None,
) -> int:
    """Run an interactive chat session."""
    print("=" * 60)
    print("  OpenRouter Interactive Chat")
    print("=" * 60)
    print(f"\n🤖 Model: {model}")
    if system_prompt:
        print(f"📋 System: {system_prompt[:50]}...")
    print(f"🌡️  Temperature: {temperature} | Max Tokens: {max_tokens}")
    print("\nCommands: /quit, /save <file>, /history, /clear, /model <name>")
    print("-" * 60 + "\n")
    
    config = ProviderConfig(api_key=api_key, timeout=120.0)
    
    with get_provider(ProviderType.OPENROUTER, config=config) as provider:
        session = ChatSession(
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                cmd_parts = user_input.split(maxsplit=1)
                cmd = cmd_parts[0].lower()
                arg = cmd_parts[1] if len(cmd_parts) > 1 else None
                
                if cmd == "/quit":
                    print("\n👋 Goodbye!")
                    break
                elif cmd == "/save":
                    filepath = arg or save_to or f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    session.save(filepath)
                elif cmd == "/history":
                    session.display_history()
                elif cmd == "/clear":
                    session.messages.clear()
                    session.conversation_log.clear()
                    if system_prompt:
                        session.messages.append(Message(role="system", content=system_prompt))
                    print("🗑️  Conversation cleared!")
                elif cmd == "/model":
                    if arg:
                        session.model = arg
                        print(f"🔄 Switched to model: {arg}")
                    else:
                        print(f"📋 Current model: {session.model}")
                        print("   Available free models:")
                        for m in OpenRouterProvider.FREE_MODELS[:8]:
                            print(f"     • {m}")
                else:
                    print(f"❓ Unknown command: {cmd}")
                continue
            
            # Send message and get response
            print("\n🤖 Assistant: ", end="" if stream else "\n")
            try:
                response = session.send(user_input, stream=stream)
                if not stream:
                    print(response)
            except Exception as e:
                print(f"\n❌ Error: {e}")
        
        # Auto-save on exit if save_to specified
        if save_to and session.conversation_log:
            session.save(save_to)
    
    return 0


def run_batch_chat(
    api_key: str,
    messages: list[str],
    model: str = "openrouter/free",
    system_prompt: str | None = None,
    max_tokens: int = 500,
    temperature: float = 0.7,
    save_to: str | None = None,
) -> int:
    """Run a batch of messages in sequence."""
    print("=" * 60)
    print("  OpenRouter Batch Chat")
    print("=" * 60)
    print(f"\n🤖 Model: {model}")
    print(f"📝 Messages to process: {len(messages)}")
    print("-" * 60 + "\n")
    
    config = ProviderConfig(api_key=api_key, timeout=120.0)
    
    with get_provider(ProviderType.OPENROUTER, config=config) as provider:
        session = ChatSession(
            provider=provider,
            model=model,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        for i, msg in enumerate(messages, 1):
            print(f"\n[{i}/{len(messages)}] 👤 User: {msg}")
            print("\n🤖 Assistant:")
            try:
                response = session.send(msg, stream=True)
            except Exception as e:
                print(f"❌ Error: {e}")
            print()
        
        if save_to:
            session.save(save_to)
    
    print("\n✅ Batch chat completed!")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="OpenRouter Interactive Chat - Multi-turn Conversations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python openrouter_chat.py
  python openrouter_chat.py --system "You are a helpful coding tutor"
  python openrouter_chat.py --model "google/gemma-3-12b-it:free"
  python openrouter_chat.py --batch "Hello" "How are you?"
  python openrouter_chat.py --save-to conversation.json
        """
    )
    
    # Model and behavior
    parser.add_argument("--model", "-m", type=str, default="openrouter/free",
                        help="Model to use (default: openrouter/free)")
    parser.add_argument("--system", "-s", type=str, default=None,
                        help="System prompt to set assistant behavior")
    parser.add_argument("--max-tokens", type=int, default=500,
                        help="Maximum tokens per response (default: 500)")
    parser.add_argument("--temperature", type=float, default=0.7,
                        help="Response temperature 0.0-2.0 (default: 0.7)")
    parser.add_argument("--no-stream", action="store_true",
                        help="Disable streaming responses")
    
    # Batch mode
    parser.add_argument("--batch", nargs="+", type=str,
                        help="Run in batch mode with preset messages")
    
    # Save/load
    parser.add_argument("--save-to", type=str, default=None,
                        help="Save conversation to JSON file")
    
    # API key
    parser.add_argument("--api-key", "-k", type=str, default=None,
                        help="OpenRouter API key")
    
    # List models
    parser.add_argument("--list-models", "-l", action="store_true",
                        help="List available free models")
    
    args = parser.parse_args()
    
    if args.list_models:
        print("\n📋 Available Free Models:\n")
        for m in OpenRouterProvider.FREE_MODELS:
            marker = "✨" if m == "openrouter/free" else "•"
            print(f"  {marker} {m}")
        return 0
    
    # Get API key
    api_key = get_api_key(args.api_key)
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        print("   Get your free API key at: https://openrouter.ai/keys")
        print("\n   Setup options:")
        print("     1. export OPENROUTER_API_KEY='your-key'")
        print("     2. echo 'your-key' > ~/.config/openrouter/api_key")
        print("     3. python openrouter_chat.py --api-key 'your-key'")
        return 1
    
    if args.batch:
        return run_batch_chat(
            api_key=api_key,
            messages=args.batch,
            model=args.model,
            system_prompt=args.system,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            save_to=args.save_to,
        )
    else:
        return run_interactive_chat(
            api_key=api_key,
            model=args.model,
            system_prompt=args.system,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            stream=not args.no_stream,
            save_to=args.save_to,
        )


if __name__ == "__main__":
    sys.exit(main())
