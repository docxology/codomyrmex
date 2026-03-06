"""
This script demonstrates handling of an invalid prompt by raising an exception.
It is designed to fail when the input prompt contains the word 'invalid'.
"""

import sys


def process_prompt(prompt: str) -> None:
    """
    Processes a prompt. Fails if the prompt is invalid.

    Args:
        prompt (str): The input prompt to process.

    Raises:
        ValueError: If the prompt contains 'invalid'.
    """
    if "invalid" in prompt.lower():
        raise ValueError(f"Prompt rejected: '{prompt}' contains forbidden keywords.")

    print(f"Successfully processed prompt: {prompt}")


if __name__ == "__main__":
    # This prompt is designed to fail based on the logic above
    test_prompt = "This is an invalid prompt that should fail"

    print(f"Testing prompt: '{test_prompt}'")
    try:
        process_prompt(test_prompt)
    except ValueError as e:
        print(f"Caught expected failure: {e}")
        # Re-raising to demonstrate failure if run directly as requested
        raise
