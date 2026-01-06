# Repository Management System - Complete Guide

## Overview

The Codomyrmex Repository Management System provides a comprehensive solution for managing GitHub repositories, integrating seamlessly with our Git operations. It supports both development repositories (for commits/PRs/issues) and usage repositories (for reference/tools).

## Features

### 🏗️ **Repository Library Management**
- **Plaintext Configuration**: Easy-to-edit repository library in structured format
- **Repository Types**: Support for OWN, USE, and FORK repository categories
- **Bulk Operations**: Clone, update, and manage multiple repositories at once
- **Smart Path Management**: Organized directory structure with configurable base paths

### 🔧 **Git Integration**
- **Seamless Git Operations**: Full integration with all 22 Git operations
- **Development Workflow**: Automatic branch setup for development repositories
- **Status Monitoring**: Real-time repository status and health checks
- **Update Management**: Intelligent pulling and synchronization

### 💻 **Command Line Interface**
- **Intuitive CLI**: Easy-to-use command-line interface for all operations
- **Search & Filter**: Powerful search and filtering capabilities
- **Bulk Operations**: Efficient batch processing of multiple repositories
- **Status Reporting**: Comprehensive status and summary reports

---

## Repository Library Format

### File Structure

The repository library is stored in a plaintext file with the following format:

```
TYPE|OWNER|REPO_NAME|URL|DESCRIPTION|LOCAL_PATH_SUGGESTION
```

### Repository Types

| Type | Purpose | Git Operations |
|------|---------|----------------|
| **OWN** | Your own repositories for development | Full Git workflow (branch, commit, push, PR) |
| **USE** | External repositories for usage/reference | Read-only operations (clone, pull) |
| **FORK** | Forked repositories for contributions | Fork workflow (upstream sync, PR) |

### Example Entries

```bash
# Your development repositories
OWN|docxology|docxology|https://github.com/docxology/docxology.git|Main docxology framework|docxology/docxology
OWN|docxology|docxology-cli|https://github.com/docxology/docxology-cli.git|CLI interface|docxology/docxology-cli

# External libraries for usage
USE|openai|openai-python|https://github.com/openai/openai-python.git|OpenAI Python library|external/openai-python
USE|fastapi|fastapi|https://github.com/fastapi/fastapi.git|FastAPI web framework|external/fastapi

# Forked repositories for contribution
FORK|microsoft|TypeScript|https://github.com/microsoft/TypeScript.git|TypeScript language|forks/TypeScript
```

---

## Command Line Interface

### Installation & Setup

```bash
# The CLI is available at:
python src/codomyrmex/git_operations/repo_cli.py

# Or create an alias for convenience:
alias repo-cli="python /path/to/codomyrmex/src/codomyrmex/git_operations/repo_cli.py"
```

### Basic Commands

#### 1. **Repository Summary**
```bash
# Show complete library overview
python repo_cli.py summary
```

#### 2. **List Repositories**
```bash
# List all repositories
python repo_cli.py list

# List by type
python repo_cli.py list --type own
python repo_cli.py list --type use
python repo_cli.py list --type fork

# List by owner
python repo_cli.py list --owner docxology

# Verbose output with URLs and paths
python repo_cli.py list --type own --verbose
```

#### 3. **Search Repositories**
```bash
# Search by name, owner, or description
python repo_cli.py search docxology
python repo_cli.py search "web framework"
python repo_cli.py search fastapi

# Verbose search results
python repo_cli.py search docxology --verbose
```

#### 4. **Clone Repositories**
```bash
# Clone a specific repository
python repo_cli.py clone docxology/docxology

# Clone to custom path
python repo_cli.py clone docxology/docxology --path /custom/path

# Bulk clone all your repositories
python repo_cli.py clone --all --type own

# Bulk clone by owner
python repo_cli.py clone --all --owner docxology

# Verbose bulk clone
python repo_cli.py clone --all --type own --verbose
```

#### 5. **Update Repositories**
```bash
# Update a specific repository
python repo_cli.py update docxology/docxology

# Update from custom path
python repo_cli.py update docxology/docxology --path /custom/path

# Bulk update all repositories
python repo_cli.py update --all

# Bulk update by type
python repo_cli.py update --all --type use

# Bulk update by owner
python repo_cli.py update --all --owner docxology
```

#### 6. **Repository Status**
```bash
# Check status of a specific repository
python repo_cli.py status docxology/docxology

# Check status with custom path
python repo_cli.py status docxology/docxology --path /custom/path
```

### Advanced Usage Examples

#### Development Workflow
```bash
# 1. Clone all your development repositories
python repo_cli.py clone --all --type own

# 2. Update all external libraries
python repo_cli.py update --all --type use

# 3. Check status of a specific project
python repo_cli.py status docxology/docxology

# 4. Search for specific tools
python repo_cli.py search "testing framework"
```

#### Research & Learning
```bash
# Clone interesting external repositories
python repo_cli.py clone --all --owner papers-we-love
python repo_cli.py clone --all --owner donnemartin

# Keep external libraries updated
python repo_cli.py update --all --type use
```

---

## Python API Usage

### Basic Repository Manager

```python
from codomyrmex.git_operations.repository_manager import RepositoryManager, RepositoryType

# Initialize manager
manager = RepositoryManager()

# List repositories
own_repos = manager.list_repositories(RepositoryType.OWN)
print(f"Found {len(own_repos)} development repositories")

# Search repositories
docx_repos = manager.search_repositories("docxology")
for repo in docx_repos:
    print(f"{repo.full_name}: {repo.description}")

# Get specific repository
repo = manager.get_repository("docxology/docxology")
if repo:
    print(f"Repository: {repo.full_name}")
    print(f"Type: {repo.repo_type.value}")
    print(f"Development repo: {repo.is_development_repo}")
```

### Repository Operations

```python
# Clone a repository
success = manager.clone_repository("docxology/docxology")
if success:
    print("Repository cloned successfully")

# Update a repository
success = manager.update_repository("docxology/docxology")
if success:
    print("Repository updated successfully")

# Get repository status
status = manager.get_repository_status("docxology/docxology")
if status:
    print(f"Branch: {status['branch']}")
    print(f"Clean: {status['status']['clean']}")
```

### Bulk Operations

```python
# Bulk clone all development repositories
results = manager.bulk_clone(RepositoryType.OWN)
successful = sum(1 for success in results.values() if success)
print(f"Cloned {successful}/{len(results)} repositories")

# Bulk update external libraries
results = manager.bulk_update(RepositoryType.USE)
successful = sum(1 for success in results.values() if success)
print(f"Updated {successful}/{len(results)} repositories")

# Bulk clone by owner
results = manager.bulk_clone(owner_filter="docxology")
print(f"Cloned {len(results)} docxology repositories")
```

---

## Directory Structure

### Default Organization

```
~/Documents/GitHub/
├── docxology/                    # Your own repositories
│   ├── docxology/
│   ├── docxology-cli/
│   ├── docxology-core/
│   └── ...
├── external/                     # External libraries
│   ├── fastapi/
│   ├── openai-python/
│   ├── langchain/
│   └── ...
├── forks/                        # Forked repositories
│   ├── react/
│   ├── TypeScript/
│   └── ...
├── research/                     # Research repositories
│   ├── papers-we-love/
│   ├── system-design-primer/
│   └── ...
└── reference/                    # Reference materials
    ├── awesome/
    ├── awesome-python/
    └── ...
```

### Custom Base Path

```python
# Use custom base path
manager = RepositoryManager(base_path="/custom/repos/path")

# Or via CLI
python repo_cli.py --base-path /custom/repos/path summary
```

---

## Integration with Git Operations

### Development Workflow Integration

```python
from codomyrmex.git_operations import *
from codomyrmex.git_operations.repository_manager import RepositoryManager

# Initialize manager
manager = RepositoryManager()

# Clone and set up development repository
repo_name = "docxology/docxology"
if manager.clone_repository(repo_name):
    repo_path = str(manager.get_local_path(manager.get_repository(repo_name)))
    
    # Create feature branch
    create_branch("feature/new-feature", repo_path)
    
    # Make changes and commit
    add_files(["new_feature.py"], repo_path)
    commit_changes("Add new feature", repo_path)
    
    # Push changes
    push_changes("origin", "feature/new-feature", repo_path)
```

### Automated Maintenance

```python
def maintain_repositories():
    """Automated repository maintenance."""
    manager = RepositoryManager()
    
    # Update all external libraries
    print("Updating external libraries...")
    results = manager.bulk_update(RepositoryType.USE)
    
    # Check status of development repositories
    print("Checking development repositories...")
    dev_repos = manager.list_repositories(RepositoryType.OWN)
    
    for repo in dev_repos:
        status = manager.get_repository_status(repo.full_name)
        if status and not status['status']['clean']:
            print(f"⚠️ {repo.full_name} has uncommitted changes")
        elif status:
            print(f"✅ {repo.full_name} is clean")

# Run maintenance
maintain_repositories()
```

---

## Configuration & Customization

### Custom Library File

```python
# Use custom library file
manager = RepositoryManager(
    library_file="/path/to/custom_library.txt",
    base_path="/custom/base/path"
)
```

### Environment Variables

```bash
# Set default paths via environment
export CODOMYRMEX_REPO_BASE="/custom/repos"
export CODOMYRMEX_REPO_LIBRARY="/custom/library.txt"
```

### Adding New Repositories

Edit the `repository_library.txt` file:

```bash
# Add your new repository
OWN|yourusername|newproject|https://github.com/yourusername/newproject.git|New project description|yourusername/newproject

# Add external library
USE|author|library|https://github.com/author/library.git|Useful library|external/library
```

---

## Best Practices

### 1. **Repository Organization**
- Use consistent naming conventions
- Organize by purpose (own/external/forks)
- Keep descriptions clear and informative
- Use meaningful local path suggestions

### 2. **Development Workflow**
- Clone all your development repositories at once
- Regularly update external dependencies
- Use status checks before starting work
- Maintain clean working trees

### 3. **Maintenance**
- Regular bulk updates for external repositories
- Periodic status checks for development repositories
- Keep the library file updated with new repositories
- Use descriptive commit messages when updating the library

### 4. **Security**
- Use SSH URLs for repositories you have write access to
- Keep authentication tokens secure
- Be cautious with bulk operations on important repositories
- Test operations on non-critical repositories first

---

## Troubleshooting

### Common Issues

#### 1. **Repository Not Found**
```bash
# Check if repository exists in library
python repo_cli.py search repository-name

# Verify URL is correct in library file
```

#### 2. **Clone Failures**
```bash
# Check Git availability
git --version

# Verify network connectivity
ping github.com

# Check authentication for private repositories
```

#### 3. **Update Failures**
```bash
# Check repository status
python repo_cli.py status owner/repo

# Verify no uncommitted changes
cd /path/to/repo && git status

# Check remote connectivity
cd /path/to/repo && git remote -v
```

#### 4. **Path Issues**
```bash
# Verify base path exists and is writable
ls -la ~/Documents/GitHub/

# Use custom path if needed
python repo_cli.py clone repo --path /custom/path
```

### Debug Mode

```bash
# Enable verbose output for debugging
python repo_cli.py --verbose clone --all --type own

# Check library loading
python repo_cli.py summary
```

---

## Examples & Use Cases

### 1. **New Developer Setup**
```bash
# Set up complete development environment
python repo_cli.py clone --all --type own
python repo_cli.py clone --all --type use --owner fastapi
python repo_cli.py clone --all --type use --owner openai
```

### 2. **Daily Development Routine**
```bash
# Update all external dependencies
python repo_cli.py update --all --type use

# Check status of current project
python repo_cli.py status docxology/docxology

# Search for new tools
python repo_cli.py search "testing framework"
```

### 3. **Research & Learning**
```bash
# Clone research repositories
python repo_cli.py clone papers-we-love/papers-we-love
python repo_cli.py clone donnemartin/system-design-primer

# Keep reference materials updated
python repo_cli.py update --all --owner papers-we-love
```

### 4. **Contributing to Open Source**
```bash
# Clone potential contribution targets
python repo_cli.py clone --all --type fork

# Search for specific technologies
python repo_cli.py search typescript
python repo_cli.py search react
```

---

## Integration Examples

### With CI/CD

```yaml
# GitHub Actions example
name: Update Dependencies
on:
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Monday

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Update External Repositories
        run: |
          python repo_cli.py update --all --type use
```

### With Development Scripts

```python
#!/usr/bin/env python3
"""Development environment setup script."""

from codomyrmex.git_operations.repository_manager import RepositoryManager

def setup_dev_environment():
    """Set up complete development environment."""
    manager = RepositoryManager()
    
    print("Setting up development environment...")
    
    # Clone all development repositories
    dev_results = manager.bulk_clone(RepositoryType.OWN)
    print(f"Development repos: {sum(dev_results.values())}/{len(dev_results)} cloned")
    
    # Clone essential external tools
    essential_tools = [
        "fastapi/fastapi",
        "openai/openai-python", 
        "pytest-dev/pytest"
    ]
    
    for tool in essential_tools:
        if manager.clone_repository(tool):
            print(f"✅ Cloned {tool}")
        else:
            print(f"❌ Failed to clone {tool}")
    
    print("Development environment setup complete!")

if __name__ == "__main__":
    setup_dev_environment()
```

This comprehensive repository management system provides everything needed to efficiently manage your GitHub repositories with full Git operations integration!

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
