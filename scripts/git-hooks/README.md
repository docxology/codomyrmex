# Git Hooks

Custom git hooks for Codomyrmex project validation and quality checks.

## Overview

This directory contains custom bash scripts that are installed as git hooks. These hooks run automatically when certain git events occur (e.g., before commits) to ensure code and documentation quality.

## Installation

Install the hooks using the provided installation script:

```bash
# From project root
src/codomyrmex/environment_setup/scripts/install_hooks.sh
```

Or via Makefile (if configured):

```bash
make setup
```

The installation script creates symlinks from `scripts/git-hooks/*` to `.git/hooks/*`, allowing the hooks to be version-controlled while still being executed by git.

## Available Hooks

### pre-commit

Runs before each commit to validate documentation quality.

**What it does:**
1. Checks if any documentation files (`.md`, `.rst`, `.txt`) in `docs/`, `README`, `CHANGELOG`, or `API_SPECIFICATION` are being committed
2. If documentation files are changed:
   - Aggregates documentation (`documentation_website.py aggregate_docs`)
   - Validates documentation versions (`documentation_website.py validate_docs`)
   - Runs comprehensive quality checks (`scripts/validate_docs_quality.py`)
   - Checks for uncommitted aggregated documentation changes
3. Blocks the commit if validation fails

**Requirements:**
- `uv` package manager
- Python 3
- Access to `src/codomyrmex/documentation/` directory

**Example output:**
```
Running pre-commit documentation validation...
Documentation files changed. Running validation...
Aggregating documentation...
Validating documentation versions...
Running comprehensive documentation quality check...
✅ All documentation validation checks passed!
Pre-commit hook completed successfully.
```

## Relationship to Pre-commit Framework

This repository uses **two separate hook systems**:

1. **`.pre-commit-config.yaml`** - Pre-commit framework hooks
   - Installed via: `pre-commit install`
   - Handles: Code formatting, linting, type checking, security scanning
   - Runs: Before custom git hooks

2. **`scripts/git-hooks/`** - Custom bash hooks (this directory)
   - Installed via: `install_hooks.sh`
   - Handles: Project-specific validation (documentation aggregation, quality checks)
   - Runs: After pre-commit framework hooks

Both systems can coexist and run in sequence. The pre-commit framework handles general code quality, while these custom hooks handle Codomyrmex-specific documentation validation.

## Manual Execution

You can run hooks manually for testing:

```bash
# Test pre-commit hook
.git/hooks/pre-commit

# Or directly
scripts/git-hooks/pre-commit
```

## Troubleshooting

### Hook not running

1. Verify hooks are installed:
   ```bash
   ls -la .git/hooks/pre-commit
   ```
   Should show a symlink to `scripts/git-hooks/pre-commit`

2. Reinstall hooks:
   ```bash
   src/codomyrmex/environment_setup/scripts/install_hooks.sh
   ```

### Validation fails

If documentation validation fails:
1. Check the error message for specific issues
2. Run validation manually:
   ```bash
   cd src/codomyrmex/documentation
   uv run python3 documentation_website.py validate_docs
   ```
3. Fix the issues and try committing again

### uv or Python not found

The hook will skip validation if `uv` or `python3` are not available. Install them and try again:
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Python should be available via uv or system installation
```

## Adding New Hooks

To add a new hook:

1. Create the hook script in `scripts/git-hooks/`:
   ```bash
   # Example: scripts/git-hooks/pre-push
   #!/bin/bash
   echo "Running pre-push checks..."
   # Your validation logic here
   exit 0
   ```

2. Make it executable:
   ```bash
   chmod +x scripts/git-hooks/pre-push
   ```

3. Reinstall hooks:
   ```bash
   src/codomyrmex/environment_setup/scripts/install_hooks.sh
   ```

4. Test the hook manually before committing

## Related Documentation

- [Documentation Maintenance Guide](../../src/codomyrmex/documentation/docs/development/DocumentationMaintenance.md)
- [Development Documentation](../../docs/development/documentation.md)
- [Pre-commit Framework Configuration](../../.pre-commit-config.yaml)

