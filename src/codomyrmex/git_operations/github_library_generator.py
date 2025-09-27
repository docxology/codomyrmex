#!/usr/bin/env python3
"""
GitHub Repository Library Generator

This script automatically generates a repository library file by fetching
repositories from the GitHub API for a specified user.
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)



class GitHubLibraryGenerator:
    """Generator for repository library from GitHub API."""

    def __init__(self, username: str, token: Optional[str] = None):
        """
        Initialize the generator.

        Args:
            username: GitHub username
            token: Optional GitHub personal access token for private repos
        """
        self.username = username
        self.token = token
        self.headers = {}

        if token:
            self.headers["Authorization"] = f"token {token}"
            self.headers["Accept"] = "application/vnd.github.v3+json"

    def fetch_repositories(self) -> List[Dict]:
        """
        Fetch all repositories for the user.

        Returns:
            List of repository dictionaries
        """
        repos = []
        page = 1
        per_page = 100

        while True:
            url = f"https://api.github.com/users/{self.username}/repos"
            params = {
                "per_page": per_page,
                "page": page,
                "sort": "updated",
                "direction": "desc",
            }

            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                page_repos = response.json()
                if not page_repos:
                    break

                repos.extend(page_repos)
                page += 1

                print(f"Fetched page {page-1}: {len(page_repos)} repositories")

            except requests.RequestException as e:
                print(f"Error fetching repositories: {e}")
                break

        print(f"Total repositories fetched: {len(repos)}")
        return repos

    def categorize_repositories(self, repos: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize repositories into OWN, FORK, and interesting categories.

        Args:
            repos: List of repository dictionaries

        Returns:
            Dictionary with categorized repositories
        """
        categories = {"own": [], "interesting_forks": [], "other_forks": []}

        # Keywords for interesting forks
        interesting_keywords = [
            "active",
            "inference",
            "ai",
            "gpt",
            "claude",
            "agent",
            "fabric",
            "cadcad",
            "manim",
            "foam",
            "buzz",
            "firecrawl",
            "eliza",
            "auto-gpt",
            "langchain",
            "openai",
            "anthropic",
            "research",
            "knowledge",
            "memory",
        ]

        for repo in repos:
            if not repo["fork"]:
                categories["own"].append(repo)
            else:
                # Check if fork is interesting
                name_lower = repo["name"].lower()
                desc_lower = (repo["description"] or "").lower()

                is_interesting = repo["stargazers_count"] > 100 or any(
                    keyword in name_lower or keyword in desc_lower
                    for keyword in interesting_keywords
                )

                if is_interesting:
                    categories["interesting_forks"].append(repo)
                else:
                    categories["other_forks"].append(repo)

        print(
            f"Categorized: {len(categories['own'])} own, "
            f"{len(categories['interesting_forks'])} interesting forks, "
            f"{len(categories['other_forks'])} other forks"
        )

        return categories

    def generate_library_content(self, categories: Dict[str, List[Dict]]) -> str:
        """
        Generate the repository library file content.

        Args:
            categories: Categorized repositories

        Returns:
            Library file content as string
        """
        content = f"""# {self.username.title()} Repository Library - REAL GITHUB REPOSITORIES
# Generated from GitHub API: https://api.github.com/users/{self.username}/repos
# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Format: TYPE|OWNER|REPO_NAME|URL|DESCRIPTION|LOCAL_PATH_SUGGESTION

# =============================================================================
# {self.username.upper()} ORIGINAL REPOSITORIES (Development/Contribution) - {len(categories['own'])} repositories
# =============================================================================

"""

        # Add original repositories
        for repo in sorted(categories["own"], key=lambda x: x["name"].lower()):
            name = repo["name"]
            desc = repo["description"] or "No description"
            url = repo["clone_url"]
            path = f"{self.username}/{name}"

            content += f"OWN|{self.username}|{name}|{url}|{desc}|{path}\n"

        content += f"""
# =============================================================================
# INTERESTING FORKED REPOSITORIES (For Contribution/Study) - {len(categories['interesting_forks'])} repositories
# =============================================================================

"""

        # Add interesting forks
        for repo in sorted(
            categories["interesting_forks"], key=lambda x: x["name"].lower()
        ):
            name = repo["name"]
            desc = repo["description"] or "No description"
            url = repo["clone_url"]
            path = f"forks/{name}"

            content += f"FORK|{self.username}|{name}|{url}|{desc}|{path}\n"

        content += """
# =============================================================================
# EXTERNAL REPOSITORIES (Usage Only) - Essential Tools & Libraries
# =============================================================================

# AI/ML Libraries
USE|openai|openai-python|https://github.com/openai/openai-python.git|Official OpenAI Python library|external/openai-python
USE|anthropic-ai|anthropic-sdk-python|https://github.com/anthropic-ai/anthropic-sdk-python.git|Anthropic Claude SDK|external/anthropic-sdk-python
USE|huggingface|transformers|https://github.com/huggingface/transformers.git|Transformers library for NLP|external/transformers
USE|langchain-ai|langchain|https://github.com/langchain-ai/langchain.git|LangChain framework|external/langchain

# Development Tools
USE|microsoft|vscode|https://github.com/microsoft/vscode.git|Visual Studio Code|external/vscode
USE|git|git|https://github.com/git/git.git|Git source code|external/git
USE|python|cpython|https://github.com/python/cpython.git|Python source code|external/cpython

# Web Frameworks
USE|fastapi|fastapi|https://github.com/fastapi/fastapi.git|FastAPI web framework|external/fastapi
USE|pallets|flask|https://github.com/pallets/flask.git|Flask web framework|external/flask
USE|django|django|https://github.com/django/django.git|Django web framework|external/django

# Data Science
USE|pandas-dev|pandas|https://github.com/pandas-dev/pandas.git|Pandas data analysis library|external/pandas
USE|numpy|numpy|https://github.com/numpy/numpy.git|NumPy numerical computing|external/numpy
USE|matplotlib|matplotlib|https://github.com/matplotlib/matplotlib.git|Matplotlib plotting library|external/matplotlib
USE|scikit-learn|scikit-learn|https://github.com/scikit-learn/scikit-learn.git|Scikit-learn ML library|external/scikit-learn

# Testing and Quality
USE|pytest-dev|pytest|https://github.com/pytest-dev/pytest.git|Pytest testing framework|external/pytest
USE|PyCQA|black|https://github.com/PyCQA/black.git|Black code formatter|external/black
USE|PyCQA|flake8|https://github.com/PyCQA/flake8.git|Flake8 linter|external/flake8

# Documentation Tools
USE|mkdocs|mkdocs|https://github.com/mkdocs/mkdocs.git|MkDocs documentation generator|external/mkdocs
USE|sphinx-doc|sphinx|https://github.com/sphinx-doc/sphinx.git|Sphinx documentation|external/sphinx

# Research and Reference
USE|papers-we-love|papers-we-love|https://github.com/papers-we-love/papers-we-love.git|Computer science papers|research/papers-we-love
USE|donnemartin|system-design-primer|https://github.com/donnemartin/system-design-primer.git|System design guide|research/system-design-primer
USE|sindresorhus|awesome|https://github.com/sindresorhus/awesome.git|Awesome lists|reference/awesome
USE|vinta|awesome-python|https://github.com/vinta/awesome-python.git|Awesome Python resources|reference/awesome-python

# =============================================================================
# CONFIGURATION NOTES
# =============================================================================

# Repository Types:
# - OWN: Your original repositories for development, commits, PRs, issues
# - FORK: Your forked repositories for potential contributions
# - USE: External repositories for reference/usage, typically read-only
#
# Local Path Suggestions:
# - {self.username}/*: Your original projects
# - forks/*: Your forked repositories
# - external/*: External libraries and tools
# - research/*: Research and reference materials
# - reference/*: Documentation and awesome lists
#
# Total Repositories: {len(categories['own']) + len(categories['interesting_forks']) + 23}
# - Original: {len(categories['own'])}
# - Interesting Forks: {len(categories['interesting_forks'])}
# - External Tools: 23
#
# Usage with Git Operations:
# - Use clone_repository() for initial setup
# - Use pull_changes() for updates on USE repositories
# - Use full Git workflow (branch, commit, push) for OWN repositories
# - Use fork workflow for FORK repositories (upstream sync, PR creation)
"""

        return content

    def generate_library(self, output_file: Optional[str] = None) -> str:
        """
        Generate the complete repository library.

        Args:
            output_file: Optional output file path

        Returns:
            Generated library content
        """
        print(f"Generating repository library for GitHub user: {self.username}")

        # Fetch repositories
        repos = self.fetch_repositories()
        if not repos:
            print("No repositories found!")
            return ""

        # Categorize repositories
        categories = self.categorize_repositories(repos)

        # Generate content
        content = self.generate_library_content(categories)

        # Write to file if specified
        if output_file:
            with open(output_file, "w") as f:
                f.write(content)
            print(f"Repository library written to: {output_file}")

        return content

    def update_existing_library(self, library_file: str) -> bool:
        """
        Update an existing library file with fresh GitHub data.

        Args:
            library_file: Path to existing library file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate new content
            new_content = self.generate_library()

            # Backup existing file
            backup_file = (
                f"{library_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            if os.path.exists(library_file):
                os.rename(library_file, backup_file)
                print(f"Backed up existing library to: {backup_file}")

            # Write new content
            with open(library_file, "w") as f:
                f.write(new_content)

            print(f"Updated repository library: {library_file}")
            return True

        except Exception as e:
            print(f"Error updating library: {e}")
            return False


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate repository library from GitHub API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s docxology                                    # Generate for docxology user
  %(prog)s docxology -o my_repos.txt                    # Save to specific file
  %(prog)s docxology -t YOUR_TOKEN                      # Use personal access token
  %(prog)s docxology --update existing_library.txt      # Update existing library
        """,
    )

    parser.add_argument("username", help="GitHub username")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-t", "--token", help="GitHub personal access token")
    parser.add_argument("--update", help="Update existing library file")

    args = parser.parse_args()

    # Initialize generator
    generator = GitHubLibraryGenerator(args.username, args.token)

    if args.update:
        # Update existing library
        success = generator.update_existing_library(args.update)
        sys.exit(0 if success else 1)
    else:
        # Generate new library
        content = generator.generate_library(args.output)

        if not args.output:
            # Print to stdout if no output file specified
            print("\n" + "=" * 80)
            print("GENERATED REPOSITORY LIBRARY:")
            print("=" * 80)
            print(content)


if __name__ == "__main__":
    main()
