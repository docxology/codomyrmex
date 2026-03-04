#!/usr/bin/env python3
"""
Demonstrates handling of an invalid prompt that triggers a failure.
"""

import sys


def process_prompt(prompt: str) -> None:
    """
    Processes the given prompt.
    Raises ValueError if the prompt is deemed invalid.
    """
    if "invalid" in prompt.lower():
        raise ValueError(f"Prompt rejected: '{prompt}' is invalid.")
    print(f"Successfully processed: {prompt}")


def main():
    test_prompt = "invalid prompt that should fail"
    print(f"Input: '{test_prompt}'")

    try:
        process_prompt(test_prompt)
    except ValueError as e:
        print(f"Fatal Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
