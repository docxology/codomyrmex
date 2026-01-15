# Repository Metadata System - Complete Guide

## Overview

The Repository Metadata System provides comprehensive tracking and management of repository metadata including read/write permissions, clone status, version information, synchronization dates, and much more. This system creates a structured database of all repository information for intelligent management and automation.

## Features

### 🏗️ **Comprehensive Metadata Tracking**
- **Access & Permissions**: Read/write status, admin rights, private/public status
- **Clone & Sync Status**: Clone dates, sync status, local repository information
- **Version Information**: Branches, tags, releases, commit tracking
- **Statistics**: Stars, forks, watchers, issues, repository size, activity
- **Local Repository Info**: Git status, uncommitted changes, branch information
- **Custom Fields**: Tags, priority, category, notes for organization

### 🔧 **GitHub API Integration**
- **Automatic Data Fetching**: Real-time repository information from GitHub
- **Permission Detection**: Automatic access level determination
- **Statistics Updates**: Live stats including stars, forks, issues
- **Language Analysis**: Repository language breakdown
- **Activity Tracking**: Last activity and update timestamps

### 💻 **Command Line Interface**
- **Metadata Management**: Update, show, and manage repository metadata
- **Comprehensive Reporting**: Detailed reports with filtering and analysis
- **Sync Status Monitoring**: Track repository synchronization status
- **Cleanup Tools**: Remove metadata for non-existent repositories

---

## Metadata Structure

### Core Repository Information
```json
{
  "full_name": "docxology/codomyrmex",
  "owner": "docxology",
  "name": "codomyrmex",
  "repo_type": "OWN",
  "url": "https://github.com/docxology/codomyrmex.git",
  "clone_url": "https://github.com/docxology/codomyrmex.git",
  "description": "Repository description"
}
```

### Access & Permissions
```json
{
  "access_level": "read_write",
  "is_private": false,
  "is_fork": false,
  "can_push": true,
  "can_admin": false
}
```

### Clone & Sync Information
```json
{
  "clone_status": "cloned",
  "sync_status": "up_to_date",
  "local_path": "/Users/user/repos/project",
  "clone_date": "2025-08-29T14:30:00Z",
  "last_sync_date": "2025-08-29T14:35:00Z",
  "last_fetch_date": "2025-08-29T14:35:00Z"
}
```

### Version Information
```json
{
  "default_branch": "main",
  "current_local_branch": "feature/new-feature",
  "latest_remote_commit": "abc123...",
  "latest_local_commit": "def456...",
  "version_tags": ["v1.0.0", "v1.1.0"],
  "latest_release": "v1.1.0"
}
```

### Repository Statistics
```json
{
  "total_commits": 150,
  "contributors": 5,
  "stars": 25,
  "forks": 8,
  "watchers": 12,
  "issues": 3,
  "pull_requests": 2,
  "size_kb": 1755,
  "languages": {"Python": 85, "JavaScript": 15},
  "last_activity": "2025-08-29T14:14:15Z"
}
```

### Local Repository Information
```json
{
  "path": "/Users/user/repos/project",
  "exists": true,
  "is_git_repo": true,
  "current_branch": "main",
  "uncommitted_changes": true,
  "untracked_files": ["new_file.py"],
  "modified_files": ["existing_file.py"],
  "staged_files": ["ready_file.py"],
  "last_commit_hash": "c70676d4",
  "last_commit_date": "2025-08-29T07:14:09",
  "last_commit_message": "Add new feature",
  "total_local_commits": 150
}
```

### Custom Fields
```json
{
  "tags": ["important", "active-development"],
  "notes": "Primary development repository",
  "priority": 1,
  "category": "core-project"
}
```

---

## Command Line Interface

### Installation & Setup

```bash
# The metadata CLI is available at:
python src/codomyrmex/git_operations/metadata_cli.py

# Or create an alias for convenience:
alias metadata-cli="python /path/to/codomyrmex/src/codomyrmex/git_operations/metadata_cli.py"
```

### Basic Commands

#### 1. **Update Metadata**
```bash
# Update single repository
python metadata_cli.py update --repository docxology/codomyrmex --type OWN --path /local/path

# Update from repository library
python metadata_cli.py update --from-library repository_library.txt

# Update with GitHub token for enhanced data
python metadata_cli.py --token YOUR_GITHUB_TOKEN update --repository docxology/codomyrmex
```

#### 2. **Show Metadata**
```bash
# Show specific repository
python metadata_cli.py show --repository docxology/codomyrmex

# Show all repositories summary
python metadata_cli.py show

# Show with verbose details
python metadata_cli.py -v show
```

#### 3. **Generate Reports**
```bash
# Basic report
python metadata_cli.py report

# Detailed report with analysis
python metadata_cli.py report --detailed

# Export report to JSON
python metadata_cli.py report --detailed --export report.json
```

#### 4. **Check Sync Status**
```bash
# Check synchronization status
python metadata_cli.py sync-status

# Verbose sync status with details
python metadata_cli.py -v sync-status
```

#### 5. **Cleanup Metadata**
```bash
# Dry run to see what would be removed
python metadata_cli.py cleanup --dry-run

# Actually remove metadata for non-existent repositories
python metadata_cli.py cleanup
```

---

## Python API Usage

### Basic Metadata Management

```python
from codomyrmex.git_operations.repository_metadata import (
    RepositoryMetadataManager, AccessLevel, CloneStatus
)

# Initialize manager
manager = RepositoryMetadataManager(
    metadata_file="custom_metadata.json",
    github_token="your_github_token"
)

# Create or update metadata
metadata = manager.create_or_update_metadata(
    full_name="docxology/codomyrmex",
    owner="docxology",
    name="codomyrmex",
    repo_type="OWN",
    url="https://github.com/docxology/codomyrmex.git",
    description="Main project repository",
    local_path="/Users/user/repos/codomyrmex"
)

# Save metadata
manager.save_metadata()
```

### Querying Metadata

```python
# Get specific repository metadata
metadata = manager.get_repository_metadata("docxology/codomyrmex")
if metadata:
    print(f"Clone Status: {metadata.clone_status.value}")
    print(f"Stars: {metadata.stats.stars}")
    print(f"Last Activity: {metadata.stats.last_activity}")

# Get repositories by status
cloned_repos = manager.get_repositories_by_status(CloneStatus.CLONED)
print(f"Cloned repositories: {len(cloned_repos)}")

# Get repositories by access level
writable_repos = manager.get_repositories_by_access(AccessLevel.READ_WRITE)
print(f"Writable repositories: {len(writable_repos)}")

# Get outdated repositories
outdated = manager.get_outdated_repositories(days=30)
print(f"Repositories not synced in 30 days: {len(outdated)}")
```

### Bulk Operations

```python
# Bulk update from repository list
repositories = [
    {
        'owner': 'docxology',
        'name': 'codomyrmex',
        'type': 'OWN',
        'url': 'https://github.com/docxology/codomyrmex.git',
        'description': 'Main project',
        'local_path': 'docxology/codomyrmex'
    },
    # ... more repositories
]

results = manager.bulk_update_metadata(repositories, "/Users/user/repos")
successful = sum(1 for success in results.values() if success)
print(f"Updated {successful}/{len(results)} repositories")
```

### Generating Reports

```python
# Generate comprehensive report
report = manager.generate_metadata_report()

print(f"Total repositories: {report['total_repositories']}")
print(f"Clone status breakdown: {report['status_breakdown']}")
print(f"Access level breakdown: {report['access_breakdown']}")
print(f"Total stars: {report['total_stars']}")
print(f"Outdated repositories: {report['outdated_repositories']}")
```

---

## Integration with Repository Manager

### Enhanced Repository Manager

```python
from codomyrmex.git_operations.repository_manager import RepositoryManager

# Initialize with metadata support
manager = RepositoryManager(
    library_file="repository_library.txt",
    base_path="/Users/user/repos",
    metadata_file="metadata.json",
    github_token="your_github_token"
)

# Clone repository with automatic metadata tracking
success = manager.clone_repository("docxology/codomyrmex")
# Metadata is automatically created and updated with:
# - Clone date and status
# - Local repository information
# - GitHub statistics
# - Access permissions
```

### Automatic Metadata Updates

```python
# The repository manager automatically:
# 1. Creates metadata when cloning repositories
# 2. Updates clone status and dates
# 3. Tracks local repository information
# 4. Fetches GitHub statistics and permissions
# 5. Saves metadata after operations

# Example workflow
repos_to_clone = ["docxology/codomyrmex", "docxology/docxology"]
for repo_name in repos_to_clone:
    success = manager.clone_repository(repo_name)
    if success:
        # Metadata automatically updated with:
        # - clone_date
        # - clone_status = CLONED
        # - local_info (branch, commits, etc.)
        # - GitHub stats (stars, forks, etc.)
        print(f"✅ Cloned {repo_name} with metadata tracking")
```

---

## Metadata Fields Reference

### Repository Types
- **OWN**: Your original repositories for development
- **FORK**: Forked repositories for contributions
- **USE**: External repositories for reference/usage

### Access Levels
- **READ_ONLY**: Can read repository content
- **READ_WRITE**: Can read and push changes
- **ADMIN**: Full administrative access
- **UNKNOWN**: Access level not determined

### Clone Status
- **NOT_CLONED**: Repository not cloned locally
- **CLONED**: Repository successfully cloned
- **OUTDATED**: Local copy needs updating
- **ERROR**: Error during clone/sync operations
- **UNKNOWN**: Status not determined

### Sync Status
- **UP_TO_DATE**: Local and remote are synchronized
- **AHEAD**: Local has commits not pushed to remote
- **BEHIND**: Remote has commits not pulled locally
- **DIVERGED**: Local and remote have different commits
- **UNKNOWN**: Sync status not determined

---

## Advanced Usage Examples

### Repository Health Monitoring

```python
def monitor_repository_health(manager):
    """Monitor repository health and generate alerts."""
    
    # Check for repositories with uncommitted changes
    all_repos = list(manager.metadata.values())
    uncommitted = [r for r in all_repos if r.local_info.uncommitted_changes]
    
    if uncommitted:
        print("⚠️ Repositories with uncommitted changes:")
        for repo in uncommitted:
            print(f"   {repo.full_name}: {len(repo.local_info.modified_files)} modified files")
    
    # Check for outdated repositories
    outdated = manager.get_outdated_repositories(7)  # 7 days
    if outdated:
        print("📅 Repositories not synced in 7 days:")
        for repo in outdated:
            print(f"   {repo.full_name}: {repo.last_sync_date or 'Never'}")
    
    # Check for repositories with issues
    issues = [r for r in all_repos if r.stats.issues > 0]
    if issues:
        print("🐛 Repositories with open issues:")
        for repo in issues:
            print(f"   {repo.full_name}: {repo.stats.issues} issues")

# Usage
monitor_repository_health(manager)
```

### Development Workflow Integration

```python
def development_workflow_status(manager):
    """Check development workflow status."""
    
    # Get development repositories
    dev_repos = [r for r in manager.metadata.values() if r.repo_type == "OWN"]
    
    print(f"📊 Development Repository Status ({len(dev_repos)} repos)")
    print("-" * 50)
    
    for repo in dev_repos:
        status_icon = "✅" if repo.clone_status.value == "cloned" else "❌"
        changes_icon = "📝" if repo.local_info.uncommitted_changes else "🔒"
        
        print(f"{status_icon} {changes_icon} {repo.full_name}")
        print(f"   Branch: {repo.local_info.current_branch}")
        print(f"   Last Commit: {repo.local_info.last_commit_date}")
        print(f"   Stars: {repo.stats.stars}, Forks: {repo.stats.forks}")
        
        if repo.local_info.uncommitted_changes:
            print(f"   ⚠️ {len(repo.local_info.modified_files)} modified, "
                  f"{len(repo.local_info.untracked_files)} untracked files")
        print()

# Usage
development_workflow_status(manager)
```

### Automated Reporting

```python
def generate_weekly_report(manager):
    """Generate weekly repository activity report."""
    
    from datetime import datetime, timedelta
    
    # Get repositories active in the last week
    week_ago = datetime.now() - timedelta(days=7)
    
    active_repos = []
    for repo in manager.metadata.values():
        if repo.stats.last_activity:
            try:
                last_activity = datetime.fromisoformat(
                    repo.stats.last_activity.replace('Z', '+00:00')
                )
                if last_activity > week_ago:
                    active_repos.append((repo, last_activity))
            except ValueError:
                continue
    
    # Sort by activity
    active_repos.sort(key=lambda x: x[1], reverse=True)
    
    print("📊 WEEKLY REPOSITORY ACTIVITY REPORT")
    print("=" * 50)
    print(f"Report Period: {week_ago.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Active Repositories: {len(active_repos)}")
    print()
    
    for repo, activity_date in active_repos[:10]:  # Top 10
        print(f"🔥 {repo.full_name}")
        print(f"   Last Activity: {activity_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Type: {repo.repo_type}")
        print(f"   Stars: {repo.stats.stars}, Issues: {repo.stats.issues}")
        print()

# Usage
generate_weekly_report(manager)
```

---

## Best Practices

### 1. **Regular Metadata Updates**
```bash
# Set up a cron job or scheduled task to update metadata regularly
# Daily update of all repositories
python metadata_cli.py update --from-library repository_library.txt

# Weekly detailed report
python metadata_cli.py report --detailed --export weekly_report.json
```

### 2. **GitHub Token Usage**
```bash
# Use GitHub token for enhanced metadata and higher API limits
export GITHUB_TOKEN="your_personal_access_token"
python metadata_cli.py --token $GITHUB_TOKEN update --from-library library.txt
```

### 3. **Metadata Organization**
```python
# Use custom fields for organization
metadata.tags = ["important", "active-development", "python"]
metadata.priority = 1  # 0=normal, 1=high, 2=critical
metadata.category = "core-project"
metadata.notes = "Primary development repository with CI/CD"
```

### 4. **Monitoring and Alerts**
```python
# Set up monitoring for important repositories
def check_critical_repos(manager):
    critical_repos = [r for r in manager.metadata.values() if r.priority >= 1]
    
    for repo in critical_repos:
        if repo.local_info.uncommitted_changes:
            print(f"🚨 CRITICAL: {repo.full_name} has uncommitted changes")
        
        if not repo.last_sync_date:
            print(f"⚠️ WARNING: {repo.full_name} never synced")
```

### 5. **Backup and Recovery**
```bash
# Regular backup of metadata
cp repository_metadata.json repository_metadata.backup.$(date +%Y%m%d)

# Recovery from backup
cp repository_metadata.backup.20250829 repository_metadata.json
```

---

## Troubleshooting

### Common Issues

#### 1. **Metadata Not Saving**
```python
# Check if metadata manager is properly initialized
manager = RepositoryMetadataManager()
print(f"Metadata file: {manager.metadata_file}")
print(f"File exists: {manager.metadata_file.exists()}")

# Manually save metadata
success = manager.save_metadata()
print(f"Save successful: {success}")
```

#### 2. **GitHub API Rate Limits**
```bash
# Use GitHub token to increase rate limits
python metadata_cli.py --token YOUR_TOKEN update --repository owner/repo

# Check rate limit status
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
```

#### 3. **Local Repository Detection Issues**
```python
# Check local repository information
metadata = manager.get_repository_metadata("owner/repo")
if metadata:
    print(f"Local path: {metadata.local_path}")
    print(f"Path exists: {Path(metadata.local_path).exists()}")
    print(f"Is git repo: {metadata.local_info.is_git_repo}")
```

#### 4. **Permission Issues**
```bash
# Check file permissions
ls -la repository_metadata.json

# Fix permissions if needed
chmod 644 repository_metadata.json
```

---

## Integration Examples

### With CI/CD Pipelines

```yaml
# GitHub Actions example
name: Update Repository Metadata
on:
  schedule:
    - cron: '0 6 * * *'  # Daily at 6 AM

jobs:
  update-metadata:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Update Metadata
        run: |
          python metadata_cli.py --token ${{ secrets.GITHUB_TOKEN }} \
            update --from-library repository_library.txt
          python metadata_cli.py report --export metadata_report.json
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: metadata-report
          path: metadata_report.json
```

### With Development Scripts

```python
#!/usr/bin/env python3
"""Development environment status checker."""

from codomyrmex.git_operations.repository_metadata import RepositoryMetadataManager

def main():
    manager = RepositoryMetadataManager()
    
    # Check development environment status
    dev_repos = [r for r in manager.metadata.values() if r.repo_type == "OWN"]
    
    print("🔧 Development Environment Status")
    print("=" * 40)
    
    for repo in dev_repos:
        if repo.clone_status.value == "cloned":
            if repo.local_info.uncommitted_changes:
                print(f"⚠️ {repo.full_name}: Has uncommitted changes")
            else:
                print(f"✅ {repo.full_name}: Clean")
        else:
            print(f"❌ {repo.full_name}: Not cloned")

if __name__ == "__main__":
    main()
```

This comprehensive metadata system provides complete visibility and control over your repository ecosystem, enabling intelligent automation and informed decision-making for your development workflow!

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
