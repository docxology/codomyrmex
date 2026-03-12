#!/usr/bin/env python3
"""
MLX Generate — CLI text generation with preset support, streaming, and system prompts.

Usage:
    python mlx_generate.py "Your prompt here"
    python mlx_generate.py "Help me code" --preset coding --stream
    python mlx_generate.py --chat --system "You are a pirate."
    python mlx_generate.py "Summarize this" --preset precise --model ORG/MODEL

Thin orchestration script delegating to codomyrmex.llm.mlx.
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import importlib.util

PRESET_NAMES = ["creative", "precise", "fast", "comprehensive", "coding"]


def _build_config(args):
    """Build an MLXConfig from CLI args, applying preset if given."""
    from codomyrmex.llm.mlx.config import MLXConfig, MLXConfigPresets

    if args.preset:
        preset_fn = getattr(MLXConfigPresets, args.preset, None)
        if preset_fn is None:
            print(f"❌ Unknown preset '{args.preset}'. Valid: {', '.join(PRESET_NAMES)}", file=sys.stderr)
            sys.exit(1)
        config = preset_fn()
        # Override model/temperature/max-tokens if explicitly provided
        if args.model != "mlx-community/Llama-3.2-3B-Instruct-4bit":
            config.model = args.model
        if args.max_tokens != 500:
            config.max_tokens = args.max_tokens
        if args.temperature != 0.7:
            config.temperature = args.temperature
    else:
        config = MLXConfig(
            model=args.model,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
        )
    return config


def generate_once(config, prompt: str, stream: bool) -> int:
    """Run a single generation and print the result."""
    from codomyrmex.llm.mlx.runner import MLXRunner

    runner = MLXRunner(config)

    if stream:
        print(end="", flush=True)
        total_tokens = 0
        import time
        t0 = time.perf_counter()
        for chunk in runner.stream_generate(prompt, config=config):
            if chunk.done:
                total_tokens = chunk.token_count or total_tokens
                break
            print(chunk.content, end="", flush=True)
            total_tokens += 1
        elapsed = time.perf_counter() - t0
        tps = total_tokens / elapsed if elapsed > 0 else 0
        print(
            f"\n\n--- {total_tokens} tokens in {elapsed:.2f}s ({tps:.1f} tok/s) ---",
            file=sys.stderr,
        )
        runner.unload_model()
        return 0

    result = runner.generate(prompt, config=config)

    if result.success:
        print(result.response)
        print(
            f"\n--- {result.tokens_generated} tokens in {result.execution_time:.2f}s "
            f"({result.tokens_per_second:.1f} tok/s) ---",
            file=sys.stderr,
        )
        runner.unload_model()
        return 0
    print(f"Error: {result.error_message}", file=sys.stderr)
    runner.unload_model()
    return 1


def interactive_chat(config, system_prompt: str | None) -> int:
    """Run an interactive chat loop."""
    from codomyrmex.llm.mlx.runner import MLXRunner

    runner = MLXRunner(config)

    print(f"💬 MLX Chat — {config.model}")
    if system_prompt:
        print(f"📋 System: {system_prompt[:60]}{'...' if len(system_prompt) > 60 else ''}")
    print("Type 'quit' or Ctrl-C to exit.\n")

    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                break

            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                break
            if user_input.lower() == "/clear":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                print("🗑️  Chat history cleared.\n")
                continue
            if user_input.lower() == "/stats":
                stats = runner.get_performance_stats()
                print(f"📊 Model: {stats['loaded_model']}")
                print(f"   Load time: {stats['load_time_seconds']:.2f}s")
                print(f"   Messages: {len(messages)}")
                print()
                continue

            messages.append({"role": "user", "content": user_input})
            result = runner.chat(messages, config=config)

            if result.success:
                print(f"\nAssistant: {result.response}")
                print(
                    f"  [{result.tokens_generated} tok, "
                    f"{result.tokens_per_second:.0f} tok/s, "
                    f"{result.execution_time:.1f}s]\n"
                )
                messages.append({"role": "assistant", "content": result.response})
            else:
                print(f"\n❌ Error: {result.error_message}\n")

    except KeyboardInterrupt:
        print("\n")

    runner.unload_model()
    print("👋 Goodbye!")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Generate text with MLX",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"Available presets: {', '.join(PRESET_NAMES)}",
    )
    parser.add_argument("prompt", nargs="?", default=None, help="Prompt to generate from")
    parser.add_argument(
        "--model",
        default="mlx-community/Llama-3.2-3B-Instruct-4bit",
        help="Model to use",
    )
    parser.add_argument("--max-tokens", type=int, default=500, help="Max tokens")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature")
    parser.add_argument("--preset", choices=PRESET_NAMES, help="Use a named config preset")
    parser.add_argument("--stream", action="store_true", help="Stream output token-by-token")
    parser.add_argument("--chat", action="store_true", help="Interactive chat mode")
    parser.add_argument("--system", default=None, help="System prompt for chat mode")
    args = parser.parse_args()

    if not importlib.util.find_spec("mlx"):
        print("❌ MLX is not installed. Install with: pip install mlx-lm", file=sys.stderr)
        return 1

    config = _build_config(args)

    if args.chat:
        return interactive_chat(config, args.system)

    if not args.prompt:
        parser.print_help()
        return 1

    return generate_once(config, args.prompt, args.stream)


if __name__ == "__main__":
    sys.exit(main())
