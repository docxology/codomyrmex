import sys


def process_prompt(prompt_text):
    """
    Processes a prompt and raises an error if it's invalid.
    """
    print(f"Processing prompt: '{prompt_text}'")
    if "invalid" in prompt_text.lower():
        raise ValueError(
            "Error: The provided prompt is invalid and processing cannot continue."
        )
    print("Prompt processed successfully.")


if __name__ == "__main__":
    # Example usage with an invalid prompt that should fail
    try:
        process_prompt("This is an invalid prompt that should fail")
    except ValueError as e:
        print(f"Caught expected failure: {e}")
        sys.exit(1)
