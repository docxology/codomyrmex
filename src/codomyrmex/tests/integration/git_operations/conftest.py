"""pytest conftest for git_operations integration tests.

Excludes standalone demo scripts (not test files) from collection.
To run them directly: python test_github_operations_demo.py
"""

collect_ignore = [
    "test_github_operations_demo.py",  # standalone demo script — run with python directly
    "test_real_github_repos.py",       # standalone demo script — run with python directly
]
