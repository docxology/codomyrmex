import sys


def main():
    """
    Demonstrates a script that fails due to an invalid prompt.
    """
    print("Initializing prompt processing...")

    # Simulating an invalid condition
    prompt = "invalid prompt that should fail"

    if "invalid" in prompt:
        print(f"Critical Error: The prompt '{prompt}' is not allowed.")
        # Exit with a non-zero status code to indicate failure
        sys.exit(1)

    print("Prompt processed successfully.")


if __name__ == "__main__":
    main()
