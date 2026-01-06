# Git Operations - Usage Examples

This document provides practical examples of how to use all 22 Git operations in scenarios, from basic repository management to fractal workflows.

## Table of Contents

1. [Basic Repository Setup](#basic-repository-setup)
2. [Branch Management](#branch-management)
3. [File Operations](#file-operations)
4. [Workflows](#advanced-workflows)
5. [Remote Operations](#remote-operations)
6. [Tag Management](#tag-management)
7. [Stash Operations](#stash-operations)
8. [Development Scenarios](#complete-development-scenarios)
9. [Error Handling Examples](#error-handling-examples)
10. [Performance Optimization](#performance-optimization)

---

## Basic Repository Setup

### Creating a New Project

```python
from codomyrmex.git_operations import (
    check_git_availability,
    initialize_git_repository,
    add_files,
    commit_changes,
    get_status
)

def setup_new_project(project_path, project_name):
    """Set up a new Git project with initial structure."""
    
    # Always check Git availability first
    if not check_git_availability():
        print("Error: Git is not available on this system")
        return False
    
    print(f"Setting up new project: {project_name}")
    
    # Initialize repository with initial commit
    success = initialize_git_repository(project_path, initial_commit=True)
    if not success:
        print("Failed to initialize repository")
        return False
    
    # Create project structure
    project_files = [
        "src/__init__.py",
        "src/main.py", 
        "tests/__init__.py",
        "tests/test_main.py",
        "requirements.txt",
        ".gitignore"
    ]
    
    # Create directories and files (simplified for example)
    import os
    for file_path in project_files:
        full_path = os.path.join(project_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(f"# {file_path}
")
    
    # Add all files to Git
    success = add_files(project_files, project_path)
    if not success:
        print("Failed to add files")
        return False
    
    # Commit the project structure
    success = commit_changes("Initial project structure", project_path)
    if not success:
        print("Failed to create initial commit")
        return False
    
    # Verify setup
    status = get_status(project_path)
    if status.get("clean"):
        print(f"✅ Project {project_name} set up successfully!")
        return True
    else:
        print("⚠️ Project setup completed but working tree is not clean")
        return False

# Usage
setup_new_project("/path/to/new/project", "MyAwesomeProject")
```

### Checking Repository Status

```python
from codomyrmex.git_operations import is_git_repository, get_status, get_current_branch

def check_repository_info(repo_path):
    """Get repository information."""
    
    # Check if it's a Git repository
    if not is_git_repository(repo_path):
        print(f"❌ {repo_path} is not a Git repository")
        return None
    
    # Get current branch
    current_branch = get_current_branch(repo_path)
    print(f"📍 Current branch: {current_branch}")
    
    # Get repository status
    status = get_status(repo_path)
    if status.get("error"):
        print(f"❌ Error getting status: {status['error']}")
        return None
    
    if status.get("clean"):
        print("✅ Working tree is clean")
    else:
        print("📝 Repository has changes:")
        if status["modified"]:
            print(f"   Modified: {', '.join(status['modified'])}")
        if status["added"]:
            print(f"   Added: {', '.join(status['added'])}")
        if status["deleted"]:
            print(f"   Deleted: {', '.join(status['deleted'])}")
        if status["untracked"]:
            print(f"   Untracked: {', '.join(status['untracked'])}")
    
    return {
        "branch": current_branch,
        "status": status
    }

# Usage
repo_info = check_repository_info("/path/to/repo")
```

---

## Branch Management

### Feature Branch Workflow

```python
from codomyrmex.git_operations import (
    create_branch, switch_branch, get_current_branch,
    add_files, commit_changes, merge_branch
)

def feature_branch_workflow(repo_path, feature_name):
    """Complete feature branch workflow."""
    
    print(f"🚀 Starting feature: {feature_name}")
    
    # Ensure we're on main branch
    main_branch = "main"  # or "master"
    if not switch_branch(main_branch, repo_path):
        print(f"❌ Failed to switch to {main_branch}")
        return False
    
    # Create feature branch
    feature_branch = f"feature/{feature_name}"
    if not create_branch(feature_branch, repo_path):
        print(f"❌ Failed to create branch {feature_branch}")
        return False
    
    print(f"✅ Created and switched to {feature_branch}")
    
    # Simulate feature development
    feature_files = [
        f"src/{feature_name}.py",
        f"tests/test_{feature_name}.py"
    ]
    
    # Create feature files (simplified)
    import os
    for file_path in feature_files:
        full_path = os.path.join(repo_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(f"# {feature_name} implementation
")
    
    # Add and commit feature files
    if not add_files(feature_files, repo_path):
        print("❌ Failed to add feature files")
        return False
    
    if not commit_changes(f"Implement {feature_name} feature", repo_path):
        print("❌ Failed to commit feature")
        return False
    
    print(f"✅ Feature {feature_name} implemented and committed")
    
    # Switch back to main and merge
    if not switch_branch(main_branch, repo_path):
        print(f"❌ Failed to switch back to {main_branch}")
        return False
    
    if not merge_branch(feature_branch, repository_path=repo_path):
        print(f"❌ Failed to merge {feature_branch}")
        return False
    
    print(f"✅ Feature {feature_name} merged successfully!")
    return True

# Usage
feature_branch_workflow("/path/to/repo", "user_authentication")
```

### Advanced Branch Operations

```python
from codomyrmex.git_operations import (
    create_branch, switch_branch, merge_branch, 
    rebase_branch, get_current_branch
)

def branch_operations(repo_path):
    """Demonstrate advanced branch operations."""
    
    # Create multiple feature branches
    features = ["feature_a", "feature_b", "feature_c"]
    
    for feature in features:
        # Create branch from main
        switch_branch("main", repo_path)
        create_branch(f"feature/{feature}", repo_path)
        
        # Add some work (simplified)
        import os
        feature_file = os.path.join(repo_path, f"{feature}.txt")
        with open(feature_file, 'w') as f:
            f.write(f"Implementation of {feature}")
        
        add_files([f"{feature}.txt"], repo_path)
        commit_changes(f"Add {feature}", repo_path)
        print(f"✅ Created feature branch: feature/{feature}")
    
    # Demonstrate rebase workflow
    print("
🔄 Demonstrating rebase workflow...")
    
    # Switch to feature_b and rebase onto main
    switch_branch("feature/feature_b", repo_path)
    current = get_current_branch(repo_path)
    print(f"📍 Currently on: {current}")
    
    # Rebase onto main (this will work if there are no conflicts)
    success = rebase_branch("main", repo_path)
    if success:
        print("✅ Rebase successful")
    else:
        print("⚠️ Rebase failed (possibly due to conflicts)")
    
    # Demonstrate merge with strategy
    switch_branch("main", repo_path)
    success = merge_branch("feature/feature_a", strategy="recursive", repository_path=repo_path)
    if success:
        print("✅ Merge with strategy successful")
    
    return True

# Usage
advanced_branch_operations("/path/to/repo")
```

---

## File Operations

### Comprehensive File Management

```python
from codomyrmex.git_operations import (
    add_files, commit_changes, get_status, 
    get_diff, reset_changes
)

def file_operations(repo_path):
    """Demonstrate file operations."""
    
    import os
    
    # Create multiple files with different states
    files_to_create = {
        "new_feature.py": "# New feature implementation
print('Hello, World!')",
        "updated_file.py": "# Updated existing file
print('Updated!')",
        "config.json": '{"setting": "value"}',
        "temp_file.txt": "Temporary content"
    }
    
    # Create files
    for filename, content in files_to_create.items():
        file_path = os.path.join(repo_path, filename)
        with open(file_path, 'w') as f:
            f.write(content)
    
    print("📁 Created multiple files")
    
    # Check status before adding
    status = get_status(repo_path)
    print(f"📊 Untracked files: {status.get('untracked', [])}")
    
    # Add files selectively
    important_files = ["new_feature.py", "updated_file.py", "config.json"]
    success = add_files(important_files, repo_path)
    if success:
        print(f"✅ Added files: {', '.join(important_files)}")
    
    # Check status after adding
    status = get_status(repo_path)
    print(f"📊 Staged files: {status.get('added', [])}")
    print(f"📊 Untracked files: {status.get('untracked', [])}")
    
    # Get diff of staged changes
    staged_diff = get_diff(staged=True, repository_path=repo_path)
    if staged_diff:
        print("📋 Staged changes preview:")
        print(staged_diff[:200] + "..." if len(staged_diff) > 200 else staged_diff)
    
    # Commit staged files
    success = commit_changes("Add new features and configuration", repo_path)
    if success:
        print("✅ Committed staged files")
    
    # Modify an existing file
    config_path = os.path.join(repo_path, "config.json")
    with open(config_path, 'w') as f:
        f.write('{"setting": "updated_value", "new_setting": true}')
    
    # Get diff of working tree changes
    working_diff = get_diff("config.json", repository_path=repo_path)
    if working_diff:
        print("📋 Working tree changes:")
        print(working_diff)
    
    # Demonstrate reset operations
    print("
🔄 Demonstrating reset operations...")
    
    # Add the modified file
    add_files(["config.json"], repo_path)
    print("✅ Staged config.json changes")
    
    # Mixed reset (unstage changes)
    success = reset_changes("mixed", "HEAD", repo_path)
    if success:
        print("✅ Mixed reset: changes unstaged but preserved")
    
    # Check final status
    final_status = get_status(repo_path)
    print(f"📊 Final status - Modified: {final_status.get('modified', [])}")
    
    return True

# Usage
file_operations("/path/to/repo")
```

---

## Advanced Workflows

### Release Management Workflow

```python
from codomyrmex.git_operations import (
    switch_branch, create_branch, merge_branch,
    create_tag, list_tags, get_commit_history,
    add_files, commit_changes
)

def release_management_workflow(repo_path, version):
    """Complete release management workflow."""
    
    print(f"🚀 Starting release workflow for version {version}")
    
    # Step 1: Ensure we're on main branch
    if not switch_branch("main", repo_path):
        print("❌ Failed to switch to main branch")
        return False
    
    # Step 2: Create release branch
    release_branch = f"release/{version}"
    if not create_branch(release_branch, repo_path):
        print(f"❌ Failed to create release branch {release_branch}")
        return False
    
    print(f"✅ Created release branch: {release_branch}")
    
    # Step 3: Prepare release (update version files, etc.)
    import os
    version_file = os.path.join(repo_path, "VERSION")
    with open(version_file, 'w') as f:
        f.write(version)
    
    changelog_file = os.path.join(repo_path, "CHANGELOG.md")
    
    # Get recent commits for changelog
    recent_commits = get_commit_history(limit=10, repository_path=repo_path)
    changelog_content = f"# Changelog

## Version {version}

"
    for commit in recent_commits[:5]:  # Last 5 commits
        changelog_content += f"- {commit['message']} ({commit['hash'][:8]})
"
    
    with open(changelog_file, 'w') as f:
        f.write(changelog_content)
    
    # Commit release preparation
    add_files(["VERSION", "CHANGELOG.md"], repo_path)
    commit_changes(f"Prepare release {version}", repo_path)
    
    print(f"✅ Prepared release {version}")
    
    # Step 4: Merge release branch back to main
    if not switch_branch("main", repo_path):
        print("❌ Failed to switch back to main")
        return False
    
    if not merge_branch(release_branch, repository_path=repo_path):
        print(f"❌ Failed to merge {release_branch}")
        return False
    
    print(f"✅ Merged {release_branch} to main")
    
    # Step 5: Create release tag
    tag_message = f"Release version {version}"
    if not create_tag(f"v{version}", tag_message, repo_path):
        print(f"❌ Failed to create tag v{version}")
        return False
    
    print(f"✅ Created tag: v{version}")
    
    # Step 6: Verify tags
    tags = list_tags(repo_path)
    print(f"📋 Available tags: {', '.join(tags[-5:])}")  # Show last 5 tags
    
    print(f"🎉 Release {version} completed successfully!")
    return True

# Usage
release_management_workflow("/path/to/repo", "1.2.0")
```

---

## Remote Operations

### Complete Remote Workflow

```python
from codomyrmex.git_operations import (
    clone_repository, push_changes, pull_changes,
    create_branch, add_files, commit_changes, switch_branch
)

def remote_collaboration_workflow():
    """Demonstrate complete remote collaboration workflow."""
    
    # Step 1: Clone repository
    remote_url = "https://github.com/user/project.git"
    local_path = "/path/to/local/clone"
    
    print(f"📥 Cloning repository from {remote_url}")
    success = clone_repository(remote_url, local_path)
    if not success:
        print("❌ Failed to clone repository")
        return False
    
    print("✅ Repository cloned successfully")
    
    # Step 2: Create feature branch for collaboration
    feature_branch = "feature/collaborative-feature"
    if not create_branch(feature_branch, local_path):
        print("❌ Failed to create feature branch")
        return False
    
    # Step 3: Make changes
    import os
    feature_file = os.path.join(local_path, "collaborative_feature.py")
    with open(feature_file, 'w') as f:
        f.write("""# Collaborative feature implementation
def collaborative_function():
    return "This feature was developed collaboratively"
""")
    
    # Step 4: Commit changes
    add_files(["collaborative_feature.py"], local_path)
    commit_changes("Add collaborative feature", local_path)
    
    print("✅ Changes committed locally")
    
    # Step 5: Push feature branch to remote
    success = push_changes("origin", feature_branch, local_path)
    if success:
        print(f"✅ Pushed {feature_branch} to remote")
    else:
        print("⚠️ Push failed (possibly due to authentication or network)")
    
    # Step 6: Simulate pulling updates from remote
    # Switch to main and pull latest changes
    switch_branch("main", local_path)
    success = pull_changes("origin", "main", local_path)
    if success:
        print("✅ Pulled latest changes from remote main")
    else:
        print("⚠️ Pull failed (possibly due to network)")
    
    return True

# Usage (commented out for safety)
# remote_collaboration_workflow()
```

---

## Tag Management

### Comprehensive Tagging Strategy

```python
from codomyrmex.git_operations import (
    create_tag, list_tags, get_commit_history,
    add_files, commit_changes
)

def tagging_strategy(repo_path):
    """Demonstrate tagging strategy."""

    print("🏷️ Implementing tagging strategy")
    
    # Step 1: Create different types of tags
    tag_strategies = [
        ("v1.0.0", "Major release: Initial stable version"),
        ("v1.1.0", "Minor release: New features added"),
        ("v1.1.1", "Patch release: Bug fixes"),
        ("beta-v1.2.0", "Beta release: Testing new features"),
        ("rc-v1.2.0", "Release candidate: Pre-release testing")
    ]
    
    for tag_name, tag_message in tag_strategies:
        # Create some commits to tag (simplified)
        import os
        commit_file = os.path.join(repo_path, f"release_{tag_name.replace('.', '_')}.txt")
        with open(commit_file, 'w') as f:
            f.write(f"Release notes for {tag_name}")
        
        add_files([f"release_{tag_name.replace('.', '_')}.txt"], repo_path)
        commit_changes(f"Prepare {tag_name}", repo_path)
        
        # Create annotated tag
        success = create_tag(tag_name, tag_message, repo_path)
        if success:
            print(f"✅ Created tag: {tag_name}")
        else:
            print(f"❌ Failed to create tag: {tag_name}")
    
    # Step 2: List and analyze tags
    all_tags = list_tags(repo_path)
    print(f"
📋 Repository tags ({len(all_tags)} total):")
    
    # Categorize tags
    release_tags = [tag for tag in all_tags if tag.startswith('v') and not any(x in tag for x in ['beta', 'rc', 'alpha'])]
    beta_tags = [tag for tag in all_tags if 'beta' in tag]
    rc_tags = [tag for tag in all_tags if 'rc' in tag]
    
    print(f"   📦 Release tags: {', '.join(release_tags)}")
    print(f"   🧪 Beta tags: {', '.join(beta_tags)}")
    print(f"   🚀 RC tags: {', '.join(rc_tags)}")
    
    # Step 3: Tag-based release notes
    print(f"
📝 Generating release notes...")
    
    for tag in release_tags[-3:]:  # Last 3 releases
        print(f"
🏷️ {tag}:")
        # In a real scenario, you'd get commits between tags
        commits = get_commit_history(limit=5, repository_path=repo_path)
        for commit in commits[:3]:
            if f"Prepare {tag}" not in commit['message']:
                print(f"   - {commit['message']} ({commit['hash'][:8]})")
    
    return True

# Usage
comprehensive_tagging_strategy("/path/to/repo")
```

---

## Stash Operations

### Advanced Stash Management

```python
from codomyrmex.git_operations import (
    stash_changes, apply_stash, list_stashes,
    get_status, switch_branch, add_files, commit_changes
)

def advanced_stash_workflow(repo_path):
    """Demonstrate advanced stash management workflow."""
    
    print("📦 Advanced stash management workflow")
    
    # Step 1: Create work in progress
    import os
    
    # Simulate multiple files being worked on
    wip_files = {
        "feature_a.py": "# Work in progress on feature A
print('Feature A - 50% complete')",
        "feature_b.py": "# Work in progress on feature B
print('Feature B - 25% complete')",
        "config_update.json": '{"new_setting": "work_in_progress"}'
    }
    
    for filename, content in wip_files.items():
        file_path = os.path.join(repo_path, filename)
        with open(file_path, 'w') as f:
            f.write(content)
    
    print("✅ Created work-in-progress files")
    
    # Step 2: Check status before stashing
    status = get_status(repo_path)
    print(f"📊 Files to stash: {status.get('untracked', [])} (untracked)")
    
    # Step 3: Stash work with descriptive messages
    stash_scenarios = [
        ("WIP: Feature A implementation - core logic", ["feature_a.py"]),
        ("WIP: Feature B implementation - initial setup", ["feature_b.py"]),
        ("WIP: Configuration updates for new features", ["config_update.json"])
    ]
    
    for stash_message, files in stash_scenarios:
        # Add files to staging area first
        add_files(files, repo_path)
        
        # Stash with descriptive message
        success = stash_changes(stash_message, repo_path)
        if success:
            print(f"✅ Stashed: {stash_message}")
        else:
            print(f"❌ Failed to stash: {stash_message}")
    
    # Step 4: List and analyze stashes
    stashes = list_stashes(repo_path)
    print(f"
📋 Available stashes ({len(stashes)} total):")
    
    for i, stash in enumerate(stashes):
        print(f"   {stash['ref']}: {stash['message']}")
        if i < len(stashes) - 1:  # Not the last one
            print(f"      Branch: {stash['branch_info']}")
    
    # Step 5: Demonstrate stash application workflow
    print(f"
🔄 Demonstrating stash application workflow...")
    
    # Apply specific stash for urgent work
    if stashes:
        # Apply the most recent stash (Feature A)
        success = apply_stash(stashes[0]['ref'], repo_path)
        if success:
            print(f"✅ Applied stash: {stashes[0]['ref']}")
            
            # Check what was restored
            status = get_status(repo_path)
            print(f"📊 Restored files: {status.get('modified', [])} (modified)")
        else:
            print("❌ Failed to apply stash")
    
    return True

# Usage
advanced_stash_workflow("/path/to/repo")
```

---

## Complete Development Scenarios

### Full-Stack Development Workflow

```python
from codomyrmex.git_operations import *

def fullstack_development_workflow(repo_path):
    """Complete full-stack development workflow with Git operations."""
    
    print("🌐 Full-stack development workflow")
    
    # Project structure
    components = {
        "backend": ["api.py", "models.py", "database.py"],
        "frontend": ["app.js", "components.js", "styles.css"],
        "tests": ["test_api.py", "test_frontend.js"],
        "docs": ["api_docs.md", "user_guide.md"]
    }
    
    # Step 1: Initialize project structure
    switch_branch("main", repo_path)
    
    import os
    for component, files in components.items():
        component_branch = f"feature/{component}-implementation"
        
        # Create component branch
        create_branch(component_branch, repo_path)
        print(f"✅ Created branch: {component_branch}")
        
        # Implement component files
        for file in files:
            file_path = os.path.join(repo_path, component, file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(f"# {component.title()} - {file}
")
                f.write(f"# Implementation for {file}
")
                if file.endswith('.py'):
                    f.write(f"def {file.replace('.py', '')}_function():
    pass
")
                elif file.endswith('.js'):
                    f.write(f"function {file.replace('.js', '')}Function() {{}}
")
        
        # Commit component implementation
        component_files = [os.path.join(component, f) for f in files]
        add_files(component_files, repo_path)
        commit_changes(f"Implement {component} component", repo_path)
        
        print(f"✅ Implemented {component} component")
        
        # Switch back to main for next component
        switch_branch("main", repo_path)
    
    # Step 2: Integration phase - merge components
    print("
🔗 Integration phase")
    
    for component in components.keys():
        component_branch = f"feature/{component}-implementation"
        success = merge_branch(component_branch, repository_path=repo_path)
        if success:
            print(f"✅ Integrated {component}")
        else:
            print(f"❌ Failed to integrate {component}")
    
    # Step 3: Create integration tests
    integration_branch = "feature/integration-tests"
    create_branch(integration_branch, repo_path)
    
    integration_files = ["integration_test.py", "e2e_test.js"]
    for file in integration_files:
        file_path = os.path.join(repo_path, "tests", file)
        with open(file_path, 'w') as f:
            f.write(f"# Integration test - {file}
")
            f.write("# Test full-stack integration
")
    
    add_files([os.path.join("tests", f) for f in integration_files], repo_path)
    commit_changes("Add integration tests", repo_path)
    
    # Merge integration tests
    switch_branch("main", repo_path)
    merge_branch(integration_branch, repository_path=repo_path)
    
    # Step 4: Release preparation
    print("
🚀 Release preparation")
    
    # Create release tag
    create_tag("v1.0.0", "Full-stack application v1.0.0 - Initial release", repo_path)
    
    # Generate project summary
    commits = get_commit_history(limit=20, repository_path=repo_path)
    
    print(f"
📊 Project Summary:")
    print(f"   - Total commits: {len(commits)}")
    print(f"   - Components: {', '.join(components.keys())}")
    
    tags = list_tags(repo_path)
    print(f"   - Tags: {', '.join(tags)}")
    
    status = get_status(repo_path)
    if status.get("clean"):
        print("   - Status: ✅ Ready for deployment")
    else:
        print("   - Status: ⚠️ Has uncommitted changes")
    
    print("🎉 Full-stack development workflow completed!")
    return True

# Usage
# fullstack_development_workflow("/path/to/fullstack/project")
```

---

## Error Handling Examples

### Comprehensive Error Handling

```python
from codomyrmex.git_operations import *

def robust_git_operations(repo_path):
    """Demonstrate robust error handling for Git operations."""
    
    print("🛡️ Robust Git operations with comprehensive error handling")
    
    def safe_operation(operation_name, operation_func, *args, **kwargs):
        """Wrapper for safe Git operations with error handling."""
        try:
            print(f"🔄 Attempting: {operation_name}")
            result = operation_func(*args, **kwargs)
            
            if result:
                print(f"✅ Success: {operation_name}")
                return True
            else:
                print(f"❌ Failed: {operation_name}")
                return False
                
        except Exception as e:
            print(f"💥 Exception in {operation_name}: {str(e)}")
            return False
    
    # Step 1: Validate environment
    if not safe_operation("Git availability check", check_git_availability):
        print("🚨 Git is not available - cannot proceed")
        return False
    
    if not safe_operation("Repository validation", is_git_repository, repo_path):
        print("🚨 Invalid repository - attempting to initialize")
        if not safe_operation("Repository initialization", initialize_git_repository, repo_path):
            print("🚨 Cannot initialize repository - aborting")
            return False
    
    # Step 2: Safe branch operations
    current_branch = get_current_branch(repo_path)
    if not current_branch:
        print("⚠️ Could not determine current branch")
        current_branch = "main"  # Assume main
    
    print(f"📍 Working on branch: {current_branch}")
    
    # Step 3: Safe file operations with validation
    def safe_file_operations():
        """Perform file operations with validation."""
        
        # Check repository status first
        status = get_status(repo_path)
        if status.get("error"):
            print(f"❌ Cannot get repository status: {status['error']}")
            return False
        
        # Create test file
        import os
        test_file = os.path.join(repo_path, "error_handling_test.py")
        
        try:
            with open(test_file, 'w') as f:
                f.write("# Error handling test file
print('Testing error handling')
")
            print("✅ Created test file")
        except IOError as e:
            print(f"❌ Failed to create test file: {e}")
            return False
        
        # Safe add operation
        if not safe_operation("Add files", add_files, ["error_handling_test.py"], repo_path):
            return False
        
        # Safe commit operation
        if not safe_operation("Commit changes", commit_changes, "Test error handling", repo_path):
            return False
        
        return True
    
    if not safe_file_operations():
        print("❌ File operations failed")
        return False
    
    # Step 4: Safe branch operations
    test_branch = "test/error-handling"
    
    # Try to create branch (might fail if exists)
    if not safe_operation("Create test branch", create_branch, test_branch, repo_path):
        print("⚠️ Branch creation failed - might already exist")
        # Try to switch to existing branch
        safe_operation("Switch to test branch", switch_branch, test_branch, repo_path)
    
    # Step 5: Safe merge operations (might have conflicts)
    switch_branch(current_branch, repo_path)
    if not safe_operation("Merge test branch", merge_branch, test_branch, repository_path=repo_path):
        print("⚠️ Merge failed - possibly due to conflicts")
        
        # Get diff to understand the issue
        diff = get_diff(repository_path=repo_path)
        if diff:
            print("📋 Current diff (might help diagnose issues):")
            print(diff[:200] + "..." if len(diff) > 200 else diff)
    
    print("🎉 Robust error handling demonstration completed")
    return True

# Usage
# robust_git_operations("/path/to/repo")
```

---

## Performance Optimization

### Efficient Git Operations

```python
from codomyrmex.git_operations import *
import time

def performance_optimized_operations(repo_path):
    """Demonstrate performance-optimized Git operations."""
    
    print("⚡ Performance-optimized Git operations")
    
    def time_operation(operation_name, operation_func, *args, **kwargs):
        """Time Git operations for performance analysis."""
        start_time = time.time()
        result = operation_func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        status = "✅" if result else "❌"
        print(f"{status} {operation_name}: {duration:.3f}s")
        return result, duration
    
    # Performance test 1: Batch vs individual file operations
    print("
📊 Performance Test 1: Batch vs Individual Operations")
    
    import os
    
    # Create multiple files
    test_files = []
    for i in range(20):
        file_name = f"perf_test_{i:02d}.py"
        file_path = os.path.join(repo_path, file_name)
        with open(file_path, 'w') as f:
            f.write(f"# Performance test file {i}
print('File {i}')
")
        test_files.append(file_name)
    
    # Method 1: Batch operation (efficient)
    batch_result, batch_time = time_operation(
        "Batch add (20 files)", 
        add_files, 
        test_files, 
        repo_path
    )
    
    if batch_result:
        time_operation("Batch commit", commit_changes, "Batch commit - 20 files", repo_path)
    
    print(f"
📈 Performance Summary:")
    print(f"   Batch operation: {batch_time:.3f}s for 20 files")
    print(f"   Recommendation: Use batch operations for multiple files")
    
    # Performance test 2: Repository status optimization
    print("
📊 Performance Test 2: Status Operations")
    
    # Test status operation performance
    for i in range(3):
        time_operation(f"Status check {i+1}", get_status, repo_path)
    
    # Performance test 3: History retrieval optimization
    print("
📊 Performance Test 3: History Operations")
    
    history_limits = [5, 10, 20]
    for limit in history_limits:
        time_operation(f"History (limit={limit})", get_commit_history, limit, repo_path)
    
    print("⚡ Performance optimization demonstration completed")
    return True

# Usage
# performance_optimized_operations("/path/to/repo")
```

---

## Running the Examples

To run these examples, make sure you have:

1. **Git installed** on your system
2. **Codomyrmex Git Operations module** properly installed
3. **Appropriate permissions** for the target directories

### Basic Usage Pattern

```python
# Import the operations you need
from codomyrmex.git_operations import (
    check_git_availability, initialize_git_repository,
    create_branch, add_files, commit_changes
)

# Always check Git availability first
if check_git_availability():
    # Your Git operations here
    pass
else:
    print("Git is not available")
```

### Error Handling Pattern

```python
# Robust error handling pattern
def safe_git_workflow(repo_path):
    try:
        # Check prerequisites
        if not check_git_availability():
            return False
        
        if not is_git_repository(repo_path):
            if not initialize_git_repository(repo_path):
                return False
        
        # Perform operations
        # ... your Git operations here ...
        
        return True
        
    except Exception as e:
        print(f"Workflow failed: {e}")
        return False
```

This comprehensive usage guide demonstrates all 22 Git operations in practical, real-world scenarios with proper error handling and performance considerations.
