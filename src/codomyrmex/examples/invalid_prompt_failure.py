"""
Example of handling an invalid prompt that triggers a failure condition.
This script defines a validator that raises an error for specific inputs.
"""

import sys


def validate_and_execute(prompt: str) -> str:
    """
    Validates the prompt. Raises ValueError if the prompt is considered invalid.
    """
    if not prompt:
        raise ValueError("Prompt cannot be empty.")

    if "fail" in prompt.lower():
        # Simulate a failure condition requested by the prompt
        raise ValueError(f"Invalid prompt detected: '{prompt}' triggers failure mode.")

    return f"Successfully processed: {prompt}"


def main():
    # Example 1: Valid prompt
    try:
        print(validate_and_execute("Hello, world!"))
    except ValueError as e:
        print(f"Error: {e}")

    # Example 2: Invalid prompt that should fail
    print("-" * 20)
    print("Attempting to process invalid prompt...")
    try:
        validate_and_execute("This prompt should fail")
    except ValueError as e:
        print(f"Success! Caught expected error: {e}")
        # Exiting with non-zero code to indicate failure to the caller if needed
        sys.exit(1)


if __name__ == "__main__":
    main()
