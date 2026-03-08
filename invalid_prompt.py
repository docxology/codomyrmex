import sys


def validate_prompt(prompt_text):
    """
    Simulates a prompt validation system that fails on invalid inputs.
    """
    forbidden_terms = ["invalid", "fail", "error"]

    for term in forbidden_terms:
        if term in prompt_text.lower():
            raise ValueError(
                f"Validation Error: Prompt contains forbidden term '{term}'."
            )

    print(f"Prompt accepted: {prompt_text}")


if __name__ == "__main__":
    # Test case: This prompt is designed to fail
    test_prompt = "This is an invalid prompt that should fail"

    print(f"Testing prompt: '{test_prompt}'")
    try:
        validate_prompt(test_prompt)
    except ValueError as e:
        print(f"\nFAILURE SUCCESSFUL:\n{e}", file=sys.stderr)
        sys.exit(1)
