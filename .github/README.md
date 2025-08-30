# GitHub Actions Workflows Documentation

This directory contains comprehensive GitHub Actions workflows for the Codomyrmex project. These workflows provide automated CI/CD, security scanning, documentation building, and maintenance capabilities.

## 📋 Workflow Overview

| Workflow | File | Triggers | Purpose |
|----------|------|----------|---------|
| **CI/CD Pipeline** | [`ci.yml`](workflows/ci.yml) | Push, PR | Comprehensive testing, linting, and quality checks |
| **Documentation** | [`documentation.yml`](workflows/documentation.yml) | Doc changes | Build and deploy documentation website |
| **Release Management** | [`release.yml`](workflows/release.yml) | Tags, manual | Automated releases to GitHub and PyPI |
| **Security Scanning** | [`security.yml`](workflows/security.yml) | Schedule, changes | Vulnerability scanning and dependency updates |
| **Pre-commit Checks** | [`pre-commit.yml`](workflows/pre-commit.yml) | PR, Push | Code quality and commit message validation |
| **Repository Maintenance** | [`maintenance.yml`](workflows/maintenance.yml) | Weekly schedule | Cleanup, metrics, and health checks |
| **Performance Benchmarks** | [`benchmarks.yml`](workflows/benchmarks.yml) | Push, schedule | Performance testing and regression detection |

## 🚀 Workflow Details

### 1. CI/CD Pipeline (`ci.yml`)

**Comprehensive continuous integration with multiple quality gates.**

**Features:**
- ✅ Multi-OS testing (Ubuntu, macOS, Windows)
- ✅ Python 3.10-3.13 matrix testing
- ✅ Code formatting (Black, Ruff)
- ✅ Static analysis (MyPy, Pylint, Flake8)
- ✅ Security scanning (Bandit)
- ✅ Complexity analysis (Radon, Lizard)
- ✅ Test coverage reporting (Codecov)
- ✅ Package building and validation
- ✅ Comprehensive module testing

**Triggers:**
- Push to `main`, `develop`
- Pull requests to `main`, `develop`
- Manual dispatch

**Key Jobs:**
1. **lint-and-format**: Code quality checks
2. **security-scan**: Bandit security analysis
3. **complexity-analysis**: Code complexity metrics
4. **test-matrix**: Cross-platform testing
5. **comprehensive-tests**: Module-specific deep testing
6. **build-package**: Package creation and validation
7. **validate-dependencies**: Dependency conflict checking

### 2. Documentation (`documentation.yml`)

**Automated documentation building and deployment using Docusaurus.**

**Features:**
- ✅ Module documentation aggregation
- ✅ Docusaurus website building
- ✅ GitHub Pages deployment
- ✅ PR preview deployments
- ✅ Link validation
- ✅ Documentation quality checks

**Triggers:**
- Documentation file changes
- Push to `main`
- Pull requests with doc changes
- Manual dispatch

**Key Jobs:**
1. **validate-documentation**: Structure and quality validation
2. **aggregate-documentation**: Collect module docs
3. **build-documentation**: Docusaurus build process
4. **deploy-documentation**: GitHub Pages deployment
5. **link-checker**: Validate all documentation links
6. **documentation-pr-preview**: PR preview generation

### 3. Release Management (`release.yml`)

**Automated release process with GitHub and PyPI publishing.**

**Features:**
- ✅ Semantic version validation
- ✅ Quality gate enforcement
- ✅ Multi-format package building
- ✅ GitHub release creation
- ✅ PyPI/Test PyPI publishing
- ✅ Cross-platform installation verification
- ✅ Documentation updates

**Triggers:**
- Version tags (`v*.*.*`)
- Manual dispatch with version input

**Key Jobs:**
1. **prepare-release**: Version validation and setup
2. **quality-gate**: Comprehensive testing before release
3. **build-artifacts**: Source and wheel building
4. **create-release**: GitHub release creation
5. **publish-pypi**: PyPI publication
6. **publish-test-pypi**: Test PyPI for prereleases
7. **verify-release**: Installation verification
8. **update-documentation**: Version reference updates

### 4. Security Scanning (`security.yml`)

**Comprehensive security analysis and dependency management.**

**Features:**
- ✅ Dependency vulnerability scanning (pip-audit, Safety)
- ✅ Static security analysis (Bandit, Semgrep)
- ✅ Code analysis (CodeQL)
- ✅ License compliance checking
- ✅ Secret detection (TruffleHog)
- ✅ Automated dependency updates
- ✅ Security reporting and alerts

**Triggers:**
- Daily schedule (2 AM UTC)
- Dependency file changes
- Manual dispatch

**Key Jobs:**
1. **dependency-scan**: Vulnerability and dependency analysis
2. **bandit-scan**: Static security analysis
3. **semgrep-scan**: Additional security patterns
4. **codeql-analysis**: GitHub security analysis
5. **license-scan**: License compliance checking
6. **secret-scan**: Secret detection
7. **dependency-update**: Automated dependency updates
8. **security-report**: Comprehensive security reporting

### 5. Pre-commit Checks (`pre-commit.yml`)

**Code quality enforcement and PR validation.**

**Features:**
- ✅ Pre-commit hooks execution
- ✅ Conventional commit validation
- ✅ File change analysis
- ✅ PR size analysis
- ✅ Quality gate enforcement

**Triggers:**
- Pull requests
- Push to main branches

**Key Jobs:**
1. **pre-commit**: Hook execution and validation
2. **commit-message-check**: Conventional commit enforcement
3. **file-changes-check**: Change impact analysis
4. **size-check**: PR size validation
5. **quality-gates**: Overall quality validation

### 6. Repository Maintenance (`maintenance.yml`)

**Automated repository maintenance and health monitoring.**

**Features:**
- ✅ Stale issue/PR management
- ✅ Artifact cleanup
- ✅ Repository metrics generation
- ✅ Health check reporting
- ✅ Maintenance summaries

**Triggers:**
- Weekly schedule (Sundays 6 AM UTC)
- Manual dispatch with task selection

**Key Jobs:**
1. **stale-issues**: Automated stale issue handling
2. **cleanup-artifacts**: Old workflow run cleanup
3. **generate-metrics**: Repository statistics
4. **health-check**: Repository health assessment
5. **maintenance-summary**: Comprehensive reporting

### 7. Performance Benchmarks (`benchmarks.yml`)

**Performance testing and regression detection.**

**Features:**
- ✅ Unit performance benchmarks
- ✅ Integration workflow benchmarks  
- ✅ Memory usage profiling
- ✅ Performance threshold validation
- ✅ Regression detection
- ✅ Benchmark reporting

**Triggers:**
- Push to main
- Pull requests
- Weekly schedule (Wednesdays 3 AM UTC)
- Manual dispatch

**Key Jobs:**
1. **benchmark-setup**: Benchmark environment preparation
2. **unit-benchmarks**: Individual function performance
3. **integration-benchmarks**: Workflow performance
4. **memory-benchmarks**: Memory usage analysis
5. **benchmark-comparison**: Performance trend analysis

## 🔧 Configuration and Setup

### Required Secrets

For full functionality, configure these repository secrets:

```yaml
CODECOV_TOKEN: # For coverage reporting
SEMGREP_APP_TOKEN: # For Semgrep security scanning (optional)
```

### Required Permissions

The workflows require these GitHub Actions permissions:

- **contents**: read/write (for releases and updates)
- **pages**: write (for documentation deployment)  
- **security-events**: write (for security scanning)
- **issues**: write (for stale issue management)
- **pull-requests**: write (for PR comments and updates)
- **actions**: write (for artifact cleanup)
- **id-token**: write (for PyPI publishing)

### Environment Setup

Workflows are configured for:
- **Python**: 3.10, 3.11, 3.12, 3.13
- **OS**: Ubuntu (primary), macOS, Windows
- **Package Manager**: UV (recommended) with fallback to pip
- **Dependencies**: Managed via `pyproject.toml` and `uv.lock`

## 📊 Monitoring and Reporting

### Workflow Status Badges

Add these badges to your README:

```markdown
[![CI/CD](https://github.com/your-org/codomyrmex/workflows/Continuous%20Integration/badge.svg)](https://github.com/your-org/codomyrmex/actions/workflows/ci.yml)
[![Documentation](https://github.com/your-org/codomyrmex/workflows/Documentation/badge.svg)](https://github.com/your-org/codomyrmex/actions/workflows/documentation.yml)
[![Security](https://github.com/your-org/codomyrmex/workflows/Security/badge.svg)](https://github.com/your-org/codomyrmex/actions/workflows/security.yml)
```

### Artifacts and Reports

Each workflow generates detailed artifacts:

- **Test Results**: JUnit XML, coverage reports
- **Security Reports**: Vulnerability scans, license compliance
- **Documentation**: Built website, validation reports
- **Benchmarks**: Performance metrics, trend analysis
- **Metrics**: Repository statistics, health checks

### Notifications

Workflows provide notifications via:
- ✅ PR comments with results
- ✅ GitHub step summaries
- ✅ Issue creation for failures
- ✅ Status checks for branch protection

## 🛠️ Customization

### Modifying Workflows

To customize workflows for your needs:

1. **Adjust Python versions** in the matrix
2. **Modify test paths** and coverage thresholds
3. **Update security scan configurations**
4. **Customize notification settings**
5. **Add module-specific jobs**

### Adding New Workflows

Follow this structure for new workflows:

```yaml
name: Your Workflow Name
on:
  # Appropriate triggers
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
env:
  # Environment variables
jobs:
  # Your jobs here
```

## 🚦 Branch Protection

Configure these branch protection rules for `main`:

- ✅ Require status checks: CI/CD, Documentation, Security
- ✅ Require up-to-date branches
- ✅ Require signed commits (recommended)
- ✅ Restrict pushes to administrators
- ✅ Require pull request reviews

## 📈 Performance and Cost Optimization

### Optimization Features

- **Concurrency control**: Prevents resource waste
- **Conditional execution**: Skips unnecessary jobs
- **Caching**: Dependencies, pre-commit hooks, build artifacts
- **Matrix optimization**: Reduced combinations for efficiency
- **Parallel execution**: Jobs run concurrently where possible

### Cost Management

- **Artifact cleanup**: Automatic old artifact removal
- **Scheduled maintenance**: Prevents resource accumulation
- **Smart triggers**: Path-based execution
- **Timeout limits**: Prevents runaway jobs

## 🔍 Troubleshooting

### Common Issues

1. **Workflow failures**: Check step summaries and logs
2. **Test failures**: Review test artifacts and coverage
3. **Security scan issues**: Check vulnerability reports
4. **Documentation build failures**: Validate markdown and links
5. **Permission errors**: Verify repository settings

### Debug Mode

Enable debug logging by setting:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

## 🎯 Best Practices

### Commit Messages

Use conventional commit format:
```
type(scope): description

feat: add new authentication module
fix(auth): resolve token validation issue  
docs: update API documentation
test: add unit tests for user service
```

### PR Guidelines

- Keep PRs focused and small
- Include comprehensive descriptions
- Add appropriate labels
- Request reviews from relevant maintainers
- Ensure all checks pass before merging

### Security

- Never commit secrets or credentials
- Use appropriate secret management
- Keep dependencies up to date
- Review security scan results regularly
- Follow security best practices

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codomyrmex Contributing Guide](../CONTRIBUTING.md)
- [Project Documentation](../docs/)
- [Security Policy](../SECURITY.md)

**Maintained by**: Codomyrmex Contributors  
**Last Updated**: $(date)  
**Version**: 1.0.0

