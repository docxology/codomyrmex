#!/usr/bin/env python3
"""
google_reason_stream.py

Thinking Budget Reasoning Streamer.
Streams model "thoughts" + final answer for complex logic with configurable budgets.

Usage:
  ./google_reason_stream.py "Solve this logic puzzle..." --budget=2048 --show-thoughts
"""

import argparse
import sys

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def main():
    parser = argparse.ArgumentParser(description="Google Reason Stream (Thinking Models)")
    parser.add_argument("prompt", type=str, help="The complex prompt or puzzle to solve")
    parser.add_argument("--budget", type=int, default=1024, help="Thinking token budget")
    parser.add_argument("--model", type=str, default="gemini-2.5-pro", help="Model to use")
    parser.add_argument("--show-thoughts", action="store_true", help="Stream the thoughts live")
    args = parser.parse_args()

    if not GENAI_AVAILABLE:
        logger.error("google-genai SDK not available.")
        sys.exit(1)

    client = genai.Client()

    logger.info("Initializing streaming reasoning session with budget %d...", args.budget)
    try:
        response = client.models.generate_content_stream(
            model=args.model,
            contents=args.prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    thinking_budget=args.budget,
                    include_thoughts=args.show_thoughts
                )
            )
        )
        
        all_thoughts = ""
        final_answer = ""
        
        print("\n=== REASONING PROCESS ===\n")
        
        for chunk in response:
            if chunk.candidates and chunk.candidates[0].content:
                for part in chunk.candidates[0].content.parts:
                    if getattr(part, 'thought', False):
                        if args.show_thoughts:
                            sys.stderr.write(f"\033[90m{part.text}\033[0m")
                            sys.stderr.flush()
                        all_thoughts += part.text
                    else:
                        if args.show_thoughts:
                            sys.stdout.write(f"\033[92m{part.text}\033[0m")
                        else:
                            sys.stdout.write(part.text)
                        sys.stdout.flush()
                        final_answer += part.text
                        
        print("\n\n=== STREAM COMPLETE ===")
        
    except Exception as e:
        logger.error("Streaming failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
