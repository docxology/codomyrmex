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

# Push changes
python scripts/git_operations/orchestrate.py push --branch main --remote origin

# Pull changes
python scripts/git_operations/orchestrate.py pull --remote origin --branch main

# Clone repository
python scripts/git_operations/orchestrate.py clone https://github.com/user/repo.git --destination ./repo

# Initialize repository
python scripts/git_operations/orchestrate.py init --path .

# Show commit history
python scripts/git_operations/orchestrate.py history --limit 10

# Check git availability
python scripts/git_operations/orchestrate.py check
```

## Commands

- `status` - Show git status
- `branch` - Branch operations (current, create, switch)
- `add` - Add files to staging
- `commit` - Commit changes
- `push` - Push changes to remote
- `pull` - Pull changes from remote
- `clone` - Clone repository
- `init` - Initialize git repository
- `history` - Show commit history
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

