# Git Operations Example

**Module**: `git_operations` - Version Control Automation

## Overview

This example demonstrates comprehensive Git version control operations using the Codomyrmex `git_operations` module. It showcases repository management, branching workflows, commits, and GitHub integration through a complete development workflow simulation.

## What This Example Demonstrates

### Core Git Operations
- **Repository Management**: Initialize new repositories, validate existing ones
- **Branch Operations**: Create, switch, and merge branches
- **File Operations**: Stage and commit changes
- **Repository Analysis**: Status checks, commit history, branch listing
- **GitHub Integration**: Repository creation and management (when configured)

### Development Workflow
1. Initialize a new Git repository
2. Create and commit initial files
3. Create a feature branch for development
4. Make changes and commit them
5. Merge the feature branch back to main
6. Analyze repository state and history

## Tested Methods

This example references methods verified in the following test files:

- **`test_git_operations.py`** - Basic Git operations testing
- **`test_git_operations_comprehensive.py`** - Advanced operations testing
- **`test_git_operations_advanced.py`** - Complex workflow testing

### Specific Methods Demonstrated

| Method | Test Reference | Description |
|--------|----------------|-------------|
| `check_git_availability()` | `TestGitOperations::test_check_git_availability` | Verify Git installation |
| `initialize_git_repository()` | `TestGitOperations::test_initialize_git_repository` | Create new repository |
| `is_git_repository()` | `TestGitOperations::test_is_git_repository` | Validate repository |
| `create_branch()` | `TestGitOperations::test_create_branch` | Create new branch |
| `switch_branch()` | `TestGitOperations::test_switch_branch` | Switch branches |
| `add_files()` | `TestGitOperations::test_add_files` | Stage files |
| `commit_changes()` | `TestGitOperations::test_commit_changes` | Commit staged changes |
| `get_status()` | `TestGitOperations::test_get_status` | Get repository status |
| `get_commit_history()` | `TestGitOperations::test_get_commit_history` | Retrieve commit history |
| `merge_branch()` | `TestGitOperations::test_merge_branch` | Merge branches |
| `get_current_branch()` | `TestGitOperations::test_get_current_branch` | Get current branch |
| `get_branches()` | `TestGitOperations::test_get_branches` | List all branches |

## Configuration

### YAML Configuration (`config.yaml`)

```yaml
# Repository settings
repository:
  name: "demo_repo"
  description: "Demonstration repository for Git operations"

# Git operations configuration
git:
  initial_commit:
    message: "Initial commit"
    files: ["README.md", "hello.py"]

  branches:
    feature_branch: "feature/add-greeting"
    main_branch: "main"

# GitHub integration (optional)
github:
  enabled: false  # Set to true for GitHub operations
  token: "${GITHUB_TOKEN}"
  repository:
    name: "codomyrmex-git-demo"
    description: "Demo repository created by Codomyrmex"

# Output and logging
output:
  format: json
  file: output/git_operations_results.json

logging:
  level: INFO
  file: logs/git_operations_example.log
```

### JSON Configuration (`config.json`)

The JSON configuration provides the same options in JSON format with environment variable substitution support.

## Running the Example

### Basic Execution

```bash
cd examples/git_operations

# Run with YAML config (default)
python example_basic.py

# Run with JSON config
python example_basic.py --config config.json
```

### With GitHub Integration

To enable GitHub operations, configure the following:

1. Set environment variable: `export GITHUB_TOKEN=your_github_token`
2. Update `config.yaml`:
   ```yaml
   github:
     enabled: true
     token: "${GITHUB_TOKEN}"
   ```
3. Run the example

### Environment Variables

- `GITHUB_TOKEN`: GitHub personal access token for repository operations
- `LOG_LEVEL`: Override logging level (DEBUG, INFO, WARNING, ERROR)

## Expected Output

### Console Output

```
🔍 Checking Git availability...
✓ Git is available

📁 Working in temporary repository: /tmp/tmpXXX/demo_repo

🏗️  Initializing Git repository...
✓ Repository initialized

📝 Creating sample files...
✓ Sample files created

📤 Staging and committing files...
✓ Committed with hash: abc12345

🌿 Creating and switching to feature branch...
✓ Current branch: feature/add-greeting

✏️  Modifying file on feature branch...
✓ Committed feature: def67890

🔄 Switching back to main branch...
✓ Switched to main branch

🔀 Merging feature branch...
✓ Feature branch merged successfully

📊 Getting repository status...
📚 Getting commit history...
🌳 Listing branches...

Operations Summary:
- repository_initialized: true
- files_created_and_committed: true
- branch_created_and_merged: true
- status_retrieved: true
- history_analyzed: true
- branches_listed: true

✅ Git Operations example completed successfully!
```

### Generated Files

- **`output/git_operations_results.json`**: Complete results and metadata
- **`logs/git_operations_example.log`**: Detailed execution logs

### Results Structure

```json
{
  "repository_initialized": true,
  "files_created_and_committed": true,
  "branch_created_and_merged": true,
  "status_retrieved": true,
  "history_analyzed": true,
  "branches_listed": true,
  "github_integration_available": false
}
```

## Workflow Demonstration

The example simulates a complete Git workflow:

1. **Repository Setup**
   - Check Git availability
   - Initialize new repository
   - Create initial files

2. **Feature Development**
   - Create feature branch
   - Make code changes
   - Commit feature work

3. **Integration**
   - Switch back to main
   - Merge feature branch
   - Resolve any conflicts

4. **Analysis**
   - Check repository status
   - Review commit history
   - List available branches

## Configuration Options

### Repository Settings

| Option | Description | Default |
|--------|-------------|---------|
| `repository.name` | Demo repository name | `"demo_repo"` |
| `repository.description` | Repository description | `"Demonstration repository"` |

### Git Operations

| Option | Description | Default |
|--------|-------------|---------|
| `git.initial_commit.message` | Initial commit message | `"Initial commit"` |
| `git.branches.feature_branch` | Feature branch name | `"feature/add-greeting"` |
| `git.commits.feature_commit` | Feature commit message | `"Add welcome message"` |

### GitHub Integration

| Option | Description | Required |
|--------|-------------|----------|
| `github.enabled` | Enable GitHub operations | `false` |
| `github.token` | GitHub personal access token | Required if enabled |
| `github.repository.name` | Repository name to create | Optional |

### Output Settings

| Option | Description | Default |
|--------|-------------|---------|
| `output.format` | Output format (json) | `"json"` |
| `output.file` | Results file path | `"output/git_operations_results.json"` |
| `output.include_logs` | Include logs in output | `true` |

## Error Handling

The example includes comprehensive error handling for:

- **Git Unavailability**: Checks if Git is installed and accessible
- **Repository Operations**: Validates repository creation and operations
- **Branch Operations**: Handles branch creation, switching, and merging
- **File Operations**: Manages staging and committing failures
- **GitHub Operations**: Gracefully handles missing tokens or API failures

## Troubleshooting

### Common Issues

**"Git is not available"**
- Ensure Git is installed: `git --version`
- Check PATH includes Git binary

**"Failed to initialize repository"**
- Verify write permissions in working directory
- Check if directory already contains a `.git` folder

**"GitHub operations failed"**
- Verify `GITHUB_TOKEN` environment variable is set
- Check token has necessary permissions
- Ensure network connectivity to GitHub API

**Permission errors**
- Ensure write access to output and log directories
- Check temporary directory permissions

### Debug Mode

Enable detailed logging:

```bash
LOG_LEVEL=DEBUG python example_basic.py
```

This provides verbose output for troubleshooting issues.

## Integration with Other Modules

This example demonstrates how `git_operations` integrates with:

- **`logging_monitoring`**: All operations are logged
- **`config_management`**: Configuration-driven execution
- **Project Orchestration**: Can be used in automated workflows

## Performance Considerations

- Operations run in temporary directories for isolation
- Repository analysis is limited to recent commits
- GitHub operations are optional and rate-limited

## Security Notes

- GitHub tokens should be stored securely (environment variables)
- Repository operations are isolated to temporary directories
- No sensitive data is committed in demonstrations

## Related Examples

- **Project Orchestration**: Shows Git operations in automated workflows
- **CI/CD Automation**: Demonstrates Git in deployment pipelines
- **Code Review**: Uses Git operations for repository analysis

---

**Module**: `git_operations` | **Status**: ✅ Complete | **Test Coverage**: Comprehensive
