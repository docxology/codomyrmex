# GitHub Configuration

This directory contains GitHub Actions workflows, issue templates, pull request templates, and other repository configuration files.

## Overview

The Codomyrmex repository uses a comprehensive set of GitHub Actions workflows for continuous integration, security scanning, documentation management, and repository maintenance. All workflows follow best practices and are designed to be efficient, reliable, and cost-effective.

## Workflows

### Core CI/CD Workflows

#### 1. Continuous Integration (`ci.yml`)
- **Purpose**: Comprehensive code quality checks, testing, and package building
- **Triggers**: Push to `main`/`develop`, pull requests, manual dispatch
- **Key Features**:
  - Code quality checks (Ruff, Black, MyPy, Pylint, Flake8)
  - Security scanning (Bandit)
  - Complexity analysis (Radon, Lizard)
  - Multi-OS/Python version test matrix
  - Coverage reporting with Codecov integration
  - Package build and validation
- **Duration**: ~15-20 minutes (full matrix)

#### 2. Pre-commit Checks (`pre-commit.yml`)
- **Purpose**: Validate commits and pull requests before merge
- **Triggers**: Pull requests, pushes to `main`/`develop`
- **Key Features**:
  - Pre-commit hooks execution
  - Commit message validation (conventional commits)
  - File change analysis and categorization
  - PR size checking and labeling
  - Quality gates enforcement
- **Duration**: ~2-5 minutes

#### 3. Security Scanning (`security.yml`)
- **Purpose**: Comprehensive security analysis and dependency management
- **Triggers**: Scheduled (daily), dependency changes, manual dispatch
- **Key Features**:
  - Dependency vulnerability scanning (pip-audit, Safety)
  - Static security analysis (Bandit, Semgrep, CodeQL)
  - License compliance checking
  - Secret detection (TruffleHog)
  - SARIF uploads to GitHub Security tab
  - Automated dependency updates with PR creation
- **Duration**: ~10-15 minutes

#### 4. Documentation Build and Deploy (`documentation.yml`)
- **Purpose**: Build, validate, and deploy documentation
- **Triggers**: Documentation file changes, manual dispatch
- **Key Features**:
  - Documentation structure validation
  - Module documentation aggregation
  - Static site generation (Docusaurus/Node.js)
  - Link checking (internal and external)
  - GitHub Pages deployment (main branch)
  - PR preview deployments
- **Duration**: ~5-10 minutes

#### 5. Documentation Validation (`documentation-validation.yml`)
- **Purpose**: Quality gates for documentation changes
- **Triggers**: Documentation changes, pull requests, scheduled weekly
- **Key Features**:
  - Link validation (comprehensive)
  - Content quality analysis
  - AGENTS.md structure validation
  - Quality gate enforcement
  - PR comments with results
- **Duration**: ~3-5 minutes

### Release and Performance

#### 6. Release and Deployment (`release.yml`)
- **Purpose**: Automated release creation and PyPI publishing
- **Triggers**: Version tags (`v*.*.*`), manual dispatch
- **Key Features**:
  - Version extraction and validation
  - Quality gate checks (tests, security, linting)
  - Package building (source and wheel)
  - GitHub Release creation with notes
  - PyPI/Test PyPI publishing
  - Release verification (installation testing)
  - Documentation updates
- **Duration**: ~20-30 minutes

#### 7. Performance Benchmarks (`benchmarks.yml`)
- **Purpose**: Performance testing and monitoring
- **Triggers**: Push to `main`, pull requests, scheduled (weekly), manual dispatch
- **Key Features**:
  - Unit performance benchmarks
  - Integration performance tests
  - Memory profiling and analysis
  - Comprehensive benchmark reporting
- **Duration**: ~5-10 minutes

### Maintenance and Coordination

#### 8. Repository Maintenance (`maintenance.yml`)
- **Purpose**: Automated repository housekeeping
- **Triggers**: Scheduled (weekly), manual dispatch
- **Key Features**:
  - Stale issue/PR management
  - Artifact cleanup (old workflow runs)
  - Repository metrics generation
  - Health checks and reporting
- **Duration**: ~2-5 minutes

#### 9. Workflow Coordinator (`workflow-coordinator.yml`)
- **Purpose**: Smart workflow orchestration and change detection
- **Triggers**: Push to `main`/`develop`, pull requests, manual dispatch
- **Key Features**:
  - Intelligent change detection (source, tests, docs, dependencies)
  - Conditional workflow triggering
  - Smart testing strategy selection
  - Parallel execution coordination
  - Cost optimization through targeted runs
- **Duration**: ~1-2 minutes (coordination only)

#### 10. Workflow Status Dashboard (`workflow-status.yml`)
- **Purpose**: Real-time workflow health monitoring
- **Triggers**: After workflow completion, scheduled (daily), manual dispatch
- **Key Features**:
  - Workflow status aggregation
  - Health metrics calculation
  - Status dashboard generation
  - Success rate tracking
- **Duration**: ~1-2 minutes

## Issue Templates

### Bug Report (`ISSUE_TEMPLATE/bug_report.yml`)
- **Purpose**: Structured bug reporting
- **Fields**: Description, reproduction steps, expected/actual behavior, code samples, environment details, severity
- **Labels**: `bug`, `needs-triage`

### Feature Request (`ISSUE_TEMPLATE/feature_request.yml`)
- **Purpose**: Feature suggestions and enhancements
- **Fields**: Problem statement, proposed solution, use cases, API design, priority, complexity
- **Labels**: `enhancement`, `needs-triage`

### Documentation Issue (`ISSUE_TEMPLATE/documentation.yml`)
- **Purpose**: Documentation improvements and issues
- **Fields**: Issue type, page location, module, current/suggested content, examples needed
- **Labels**: `documentation`, `needs-triage`

## Pull Request Template

### Pull Request Template (`PULL_REQUEST_TEMPLATE.md`)
- **Purpose**: Standardized PR submission format
- **Sections**:
  - Description and type of change
  - Related issues
  - Changes made (added/changed/removed/fixed)
  - Module(s) affected
  - Testing information
  - Documentation updates
  - Breaking changes
  - Performance impact
  - Security considerations
  - Deployment notes
  - Screenshots/examples
  - Comprehensive checklists

## Configuration Files

### Required Secrets
- `CODECOV_TOKEN` - Code coverage reporting (optional but recommended)
- `SEMGREP_APP_TOKEN` - Enhanced Semgrep security scanning (optional)
- `GITHUB_TOKEN` - Automatically provided for all workflows

### Required Settings
- **GitHub Pages**: Enabled for documentation deployment
- **Security Tab**: Enabled for SARIF uploads
- **Actions Permissions**: Configured for workflow coordination

## Workflow Dependencies

```
Workflow Coordinator
    ├── CI Pipeline (on source/test changes)
    ├── Security Scan (on source/dependency changes)
    ├── Documentation (on doc changes)
    └── Benchmarks (on main branch changes)

CI Pipeline
    ├── Lint and Format
    ├── Security Scan
    ├── Complexity Analysis
    ├── Test Matrix
    └── Package Build

Security Workflow
    ├── Dependency Scan
    ├── Bandit Analysis
    ├── Semgrep Scan
    ├── CodeQL Analysis
    ├── License Scan
    └── Secret Detection
```

## Usage Guidelines

### For Contributors
1. **Creating Issues**: Use the appropriate issue template for bugs, features, or documentation
2. **Pull Requests**: Fill out the PR template completely, especially testing and documentation sections
3. **Commit Messages**: Follow conventional commit format (enforced by pre-commit workflow)
4. **Workflow Triggers**: Workflows run automatically on push/PR; use manual dispatch for testing

### For Maintainers
1. **Workflow Monitoring**: Check the Workflow Status Dashboard for health metrics
2. **Security**: Review security scan results in the Security tab
3. **Releases**: Use version tags (`v1.0.0`) to trigger release workflow
4. **Maintenance**: Weekly maintenance runs automatically; manual dispatch available

## Best Practices

### Workflow Design
- ✅ All workflows use consistent versions (Python 3.11, UV 0.5.7, Node.js 20)
- ✅ Comprehensive error handling with `continue-on-error` where appropriate
- ✅ Artifact retention set to 30 days
- ✅ Caching strategies for dependencies and tools
- ✅ GitHub Step Summaries for easy result viewing

### Security
- ✅ Minimal permissions (principle of least privilege)
- ✅ Secrets properly scoped
- ✅ SARIF uploads for security findings
- ✅ Automated dependency updates with testing

### Performance
- ✅ Smart change detection to avoid unnecessary runs
- ✅ Parallel job execution where possible
- ✅ Efficient caching strategies
- ✅ Conditional job execution based on changes

## Troubleshooting

### Common Issues

**Workflow not triggering:**
- Check if file paths match workflow `paths:` filters
- Verify branch names match workflow triggers
- Ensure workflow file syntax is correct

**Workflow failing:**
- Check workflow run logs for specific error messages
- Verify required secrets are configured
- Ensure dependencies are up to date

**Permission errors:**
- Check workflow `permissions:` section
- Verify repository settings allow workflow execution
- Ensure GitHub Pages/Security tab are enabled if needed

### Getting Help

- Review workflow logs in the Actions tab
- Check [WORKFLOW_TESTING_GUIDE.md](WORKFLOW_TESTING_GUIDE.md) for testing procedures
- See [WORKFLOW_IMPROVEMENTS.md](WORKFLOW_IMPROVEMENTS.md) for recent changes
- Open an issue using the documentation template for workflow questions

## Related Documentation

- [Workflow Testing Guide](WORKFLOW_TESTING_GUIDE.md) - How to test workflows
- [Workflow Improvements](WORKFLOW_IMPROVEMENTS.md) - Recent improvements summary
- [Contributing Guidelines](../docs/project/contributing.md) - General contribution guide
- [Project README](../README.md) - Main project documentation

## Version Information

- **Python**: 3.11 (consistent across all workflows)
- **UV Package Manager**: 0.5.7
- **Node.js**: 20
- **Last Updated**: January 2026

---

*This configuration ensures professional, efficient, and reliable CI/CD operations for the Codomyrmex project.*


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../AGENTS.md)
- **Documentation**: [Reference Guides](../docs/README.md)
- **Home**: [Root README](../README.md)

## Example Usage

```python
from codomyrmex import core

def main():
    # Standard usage pattern
    app = core.Application()
    app.run()
```
