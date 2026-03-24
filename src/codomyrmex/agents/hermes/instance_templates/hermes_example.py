#!/usr/bin/env python3
"""
Example Python script demonstrating Hermes tool usage.
This script shows how to use the hermes_tools module to interact with the Hermes environment.
"""

# Import the Hermes tools
import os

from hermes_tools import read_file, search_files, terminal


def main():
    print("=== Hermes Python Tools Example ===\n")

    # Example 1: Search for template files
    print("1. Searching for template files...")
    search_result = search_files(
        pattern=".*template.*\\.(yaml|yml|md)$", target="files", path=".", limit=10
    )

    if search_result["matches"]:
        print(f"   Found {len(search_result['matches'])} template-related files:")
        for match in search_result["matches"][:5]:  # Show first 5
            print(f"   - {match}")
    else:
        print("   No template files found")
    print()

    # Example 2: Read a specific file if it exists
    print("2. Reading TEMPLATE.md (if it exists)...")
    template_path = "TEMPLATE.md"
    if os.path.exists(template_path):
        file_content = read_file(template_path, offset=1, limit=20)
        print(f"   File has {file_content['total_lines']} total lines")
        print("   First 20 lines:")
        for line in file_content["content"].split("\n")[:20]:
            if line:  # Skip empty lines
                print(f"   {line}")
    else:
        print(f"   {template_path} not found in current directory")
    print()

    # Example 3: Run a terminal command
    print("3. Running terminal command to check Python version...")
    term_result = terminal("python3 --version")
    if term_result["exit_code"] == 0:
        print(f"   Output: {term_result['output'].strip()}")
    else:
        print(f"   Command failed with exit code {term_result['exit_code']}")
        print(f"   Error: {term_result['output']}")
    print()

    # Example 4: Search for Hermes-related content
    print("4. Searching for 'Hermes' in markdown files...")
    content_result = search_files(
        pattern="Hermes",
        target="content",
        path=".",
        file_glob="*.md",
        limit=5,
        output_mode="count",
    )

    print(f"   Found 'Hermes' in {len(content_result['matches'])} files:")
    for file_match in content_result["matches"]:
        print(f"   - {file_match['file']}: {file_match['count']} occurrences")
    print()

    print("=== Example completed ===")


if __name__ == "__main__":
    main()
