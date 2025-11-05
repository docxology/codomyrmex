# Git Operations Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.git_operations` module.

## Purpose

This orchestrator provides command-line interface for Git workflow automation and repository management.

## Usage

```bash
# Show git status
python scripts/git_operations/orchestrate.py status

# Branch operations
python scripts/git_operations/orchestrate.py branch current
python scripts/git_operations/orchestrate.py branch create feature/new-feature
python scripts/git_operations/orchestrate.py branch switch main

# Stage files
python scripts/git_operations/orchestrate.py add file1.py file2.py

# Commit changes
python scripts/git_operations/orchestrate.py commit -m "Add new feature"
python scripts/git_operations/orchestrate.py commit -m "Add new feature" --author-name "John Doe" --author-email "john@example.com"
python scripts/git_operations/orchestrate.py commit -m "Add new feature" file1.py file2.py

# Amend last commit
python scripts/git_operations/orchestrate.py amend -m "Updated commit message"
python scripts/git_operations/orchestrate.py amend --no-edit

# Push changes
python scripts/git_operations/orchestrate.py push --branch main --remote origin

# Pull changes
python scripts/git_operations/orchestrate.py pull --remote origin --branch main

# Fetch changes (without merging)
python scripts/git_operations/orchestrate.py fetch --remote origin --branch main
python scripts/git_operations/orchestrate.py fetch --remote origin --prune

# Clone repository
python scripts/git_operations/orchestrate.py clone https://github.com/user/repo.git --destination ./repo

# Initialize repository
python scripts/git_operations/orchestrate.py init --path .

# Show commit history
python scripts/git_operations/orchestrate.py history --limit 10
python scripts/git_operations/orchestrate.py history --limit 20 --author "John Doe"
python scripts/git_operations/orchestrate.py history --since "2 weeks ago" --until "1 week ago"
python scripts/git_operations/orchestrate.py history --file "src/main.py"

# Remote operations
python scripts/git_operations/orchestrate.py remote list
python scripts/git_operations/orchestrate.py remote add upstream https://github.com/user/repo.git
python scripts/git_operations/orchestrate.py remote remove upstream

# Config operations
python scripts/git_operations/orchestrate.py config get user.name
python scripts/git_operations/orchestrate.py config set user.name "John Doe"
python scripts/git_operations/orchestrate.py config set user.email "john@example.com" --global

# Cherry-pick a commit
python scripts/git_operations/orchestrate.py cherry-pick abc1234
python scripts/git_operations/orchestrate.py cherry-pick abc1234 --no-commit

# Check git availability
python scripts/git_operations/orchestrate.py check
```

## Commands

- `status` - Show git status
- `branch` - Branch operations (current, create, switch)
- `add` - Add files to staging
- `commit` - Commit changes (with optional author override and file selection)
- `amend` - Amend last commit (with optional message and author override)
- `push` - Push changes to remote
- `pull` - Pull changes from remote
- `fetch` - Fetch changes from remote (without merging)
- `clone` - Clone repository
- `init` - Initialize git repository
- `history` - Show commit history (with optional filters: since, until, author, branch, file)
- `remote` - Remote operations (list, add, remove)
- `config` - Config operations (get, set)
- `cherry-pick` - Cherry-pick a commit
- `check` - Check git availability

## Related Documentation

- **[Module README](../../src/codomyrmex/git_operations/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/git_operations/API_SPECIFICATION.md)**: Detailed API reference
- **[MCP Tools](../../src/codomyrmex/git_operations/MCP_TOOL_SPECIFICATION.md)**: AI integration tools
- **[Usage Examples](../../src/codomyrmex/git_operations/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.git_operations.get_status`
- `codomyrmex.git_operations.get_current_branch`
- `codomyrmex.git_operations.create_branch`
- `codomyrmex.git_operations.switch_branch`
- `codomyrmex.git_operations.add_files`
- `codomyrmex.git_operations.commit_changes`
- `codomyrmex.git_operations.push_changes`
- `codomyrmex.git_operations.pull_changes`
- `codomyrmex.git_operations.clone_repository`
- `codomyrmex.git_operations.initialize_git_repository`
- `codomyrmex.git_operations.get_commit_history`
- `codomyrmex.git_operations.check_git_availability`

See `codomyrmex.cli.py` for main CLI integration.

