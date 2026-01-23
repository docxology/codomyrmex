# Codomyrmex Agents — src/codomyrmex/git_operations/tools

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides utility tools for Git operations including automatic repository library generation from GitHub API. These tools automate the creation of repository library files by fetching and categorizing repositories from GitHub.

## Active Components

- `library_generator.py` - GitHub Repository Library Generator with CLI
- `README.md` - Module documentation

## Key Classes and Functions

### library_generator.py
- **`GitHubLibraryGenerator`** - Generates repository library files from GitHub API
  - `__init__(username, token)` - Initializes generator with GitHub credentials
  - `fetch_repositories()` - Fetches all repositories for a GitHub user with pagination
  - `categorize_repositories(repos)` - Categorizes repos into OWN, interesting_forks, other_forks
  - `generate_library_content(categories)` - Generates formatted library file content
  - `generate_library(output_file)` - Creates complete repository library file
  - `update_existing_library(library_file)` - Updates existing library with backup

### CLI Usage
```bash
# Generate library for a GitHub user
python library_generator.py username

# Save to specific file
python library_generator.py username -o my_repos.txt

# Use personal access token for private repos
python library_generator.py username -t YOUR_TOKEN

# Update existing library
python library_generator.py username --update existing_library.txt
```

### Categorization Logic
- **OWN**: Non-fork repositories (user's original projects)
- **Interesting Forks**: Forks with >100 stars or matching keywords (ai, gpt, claude, agent, etc.)
- **Other Forks**: Remaining forked repositories
- **USE (External)**: Pre-defined essential tools and libraries (openai, anthropic, fastapi, etc.)

## Operating Contracts

- GitHub API rate limits respected with pagination
- Optional token enables access to private repositories
- Backup created before updating existing library files
- Keywords for interesting forks are configurable
- Output includes generation timestamp and summary statistics

## Signposting

- **Dependencies**: Requires `requests` for GitHub API calls
- **Output Location**: Typically `data/` directory for generated libraries
- **Parent Directory**: [git_operations](../README.md) - Parent module documentation
- **Related Modules**:
  - `data/` - Storage location for generated library files
  - `core/repository.py` - Consumes library files
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation
