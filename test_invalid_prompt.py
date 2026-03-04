import sys


def process_prompt(prompt: str) -> None:
    """
    Processes a prompt, strictly rejecting known invalid patterns.
    """
    if "invalid" in prompt.lower():
        raise ValueError(f"Prompt rejected: '{prompt}' contains forbidden keywords.")
    print(f"Prompt processed successfully: {prompt}")


def main():
    test_input = "invalid prompt that should fail"
    print(f"--- Attempting to process: '{test_input}' ---")

    try:
        process_prompt(test_input)
        print("ERROR: Code did not fail as expected.")
        sys.exit(1)
    except ValueError as e:
        print(f"SUCCESS: Caught expected error: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()
