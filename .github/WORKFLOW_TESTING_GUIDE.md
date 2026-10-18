# 🧪 GitHub Actions Workflow Testing Guide

## Testing Overview

This guide outlines how to test all GitHub Actions workflows to ensure they function correctly after the comprehensive improvements made.

## 🚦 Pre-Testing Checklist

### Repository Setup
- [ ] ✅ **Workflows committed** - All improved workflows are in main branch
- [ ] 🔐 **Secrets configured** - Required repository secrets are set
- [ ] 📚 **GitHub Pages enabled** - For documentation deployment
- [ ] 🛡️ **Security tab enabled** - For SARIF uploads
- [ ] ⚡ **Actions enabled** - Workflow permissions configured

### Required Secrets
```bash
# Repository Secrets Needed:
CODECOV_TOKEN=<your_codecov_token>        # Optional but recommended
SEMGREP_APP_TOKEN=<your_semgrep_token>    # Optional for enhanced security
# GITHUB_TOKEN is automatically provided
```

## 🎯 Testing Strategy

### 1. **Automated Testing (Recommended)**
The workflows are designed to test themselves through the **Workflow Coordinator**:

```bash
# Trigger comprehensive testing
gh workflow run workflow-coordinator.yml -f workflows=all
```

### 2. **Manual Testing by Workflow**
Test each workflow individually:

```bash
# Test individual workflows
gh workflow run ci.yml
gh workflow run security.yml
gh workflow run documentation.yml
gh workflow run benchmarks.yml
```

### 3. **Event-Based Testing**
Test workflows through natural triggers:

## 📋 Detailed Testing Plan

### A. **CI Pipeline Testing (`ci.yml`)**

#### Trigger Methods:
1. **Push to main/develop**:
   ```bash
   git checkout -b test-ci-workflow
   echo "# Test change" >> README.md
   git add . && git commit -m "test: trigger CI workflow"
   git push origin test-ci-workflow
   # Create PR to main
   ```

2. **Manual trigger**:
   ```bash
   gh workflow run ci.yml
   ```

#### Expected Results:
- ✅ **Code Quality**: Ruff, Black, MyPy, Pylint checks pass
- ✅ **Security**: Bandit scan completes
- ✅ **Complexity**: Radon and Lizard analysis
- ✅ **Tests**: Multi-OS/Python matrix execution
- ✅ **Coverage**: Coverage reports generated and uploaded to Codecov
- ✅ **Artifacts**: Test results and coverage uploaded
- ✅ **Package Build**: Successfully builds and tests package

#### Success Indicators:
```
✅ Code Quality: Passed
✅ Security Scan: Passed
✅ Complexity Analysis: Passed
✅ Test Matrix: Passed
✅ Package Build: Passed
✅ Dependencies: Validated
🎉 Overall Result: SUCCESS
```

### B. **Pre-commit Testing (`pre-commit.yml`)**

#### Trigger Methods:
1. **Pull Request**:
   ```bash
   # Create PR - automatically triggers
   ```

2. **Push to main/develop**:
   ```bash
   git push origin main
   ```

#### Expected Results:
- ✅ **Pre-commit hooks** run successfully
- ✅ **Commit message validation** (for PRs)
- ✅ **File changes analysis** with categorization
- ✅ **PR size checking** and labeling
- ✅ **Quality gates** pass

#### Success Indicators:
```
✅ Pre-commit Hooks: Passed
✅ Commit Messages: Valid
✅ File Changes: Analyzed
✅ PR Size: Checked
✅ All quality gates passed!
```

### C. **Security Workflow Testing (`security.yml`)**

#### Trigger Methods:
1. **Dependency changes**:
   ```bash
   echo "requests>=2.25.0" >> requirements.txt
   git add . && git commit -m "test: trigger security scan"
   git push
   ```

2. **Manual/Scheduled**:
   ```bash
   gh workflow run security.yml
   ```

#### Expected Results:
- ✅ **Dependency scan**: pip-audit and safety checks
- ✅ **Bandit analysis**: Static security analysis with SARIF upload
- ✅ **Semgrep scan**: Advanced security patterns (if token configured)
- ✅ **CodeQL analysis**: GitHub's security analysis
- ✅ **License compliance**: License scanning and validation
- ✅ **Secret detection**: TruffleHog secret scanning
- ✅ **Comprehensive reporting**: Security summary generated

#### Success Indicators:
```
✅ Dependency Scan: Completed
✅ Bandit Security Analysis: Completed
✅ Semgrep Analysis: Completed
✅ CodeQL Analysis: Completed
✅ License Compliance: Completed
✅ Secret Detection: Completed
```

### D. **Documentation Testing (`documentation.yml`)**

#### Trigger Methods:
1. **Documentation changes**:
   ```bash
   echo "## Test Update" >> README.md
   git add . && git commit -m "docs: test documentation workflow"
   git push
   ```

2. **Manual trigger**:
   ```bash
   gh workflow run documentation.yml
   ```

#### Expected Results:
- ✅ **Structure validation**: Required files checked
- ✅ **Documentation aggregation**: Module docs collected
- ✅ **Website build**: Docusaurus/static site generation
- ✅ **Link checking**: Internal and external links verified
- ✅ **GitHub Pages deployment**: Site deployed (on main branch)
- ✅ **PR preview**: Preview deployment for PRs

#### Success Indicators:
```
✅ Validation: Passed
✅ Aggregation: Passed
✅ Build: Passed
✅ Link Check: Completed
✅ Deployment: Success (main branch)
```

### E. **Workflow Coordination Testing (`workflow-coordinator.yml`)**

#### Trigger Methods:
1. **Smart triggering**:
   ```bash
   # Make source changes
   echo "print('test')" >> src/codomyrmex/__init__.py
   git add . && git commit -m "test: trigger smart coordination"
   git push
   ```

2. **Manual with specific workflows**:
   ```bash
   gh workflow run workflow-coordinator.yml -f workflows=ci,security,docs
   ```

#### Expected Results:
- ✅ **Change detection**: Correctly identifies changed file types
- ✅ **Smart triggering**: Only runs relevant workflows
- ✅ **Parallel execution**: Workflows run concurrently
- ✅ **Testing strategy**: Appropriate testing level selected
- ✅ **Coordination summary**: Detailed reporting

#### Success Indicators:
```
✅ Source Code: Changed
✅ CI Pipeline: Completed successfully
✅ Security Scan: Completed successfully
⏭️ Documentation: Skipped (no doc changes)
🎯 Targeted Testing: Focus on changed modules
```

### F. **Workflow Status Dashboard (`workflow-status.yml`)**

#### Trigger Methods:
1. **After other workflows**:
   ```bash
   # Runs automatically after workflow completion
   ```

2. **Manual update**:
   ```bash
   gh workflow run workflow-status.yml
   ```

#### Expected Results:
- ✅ **Status collection**: Gathers data from all workflows
- ✅ **Dashboard generation**: Creates markdown status report
- ✅ **Health metrics**: Calculates success rates
- ✅ **Artifact upload**: Status reports available

#### Success Indicators:
```
✅ Continuous Integration: Success
✅ Pre-commit Checks: Success
✅ Security Scanning: Success
Overall Health: 10/10 workflows successful (100.0%)
```

## 🔍 Troubleshooting Guide

### Common Issues and Solutions

#### Issue: "UV version not found"
**Solution**: Update `UV_VERSION` in workflow files
```yaml
env:
  UV_VERSION: "0.5.7"  # Use latest version
```

#### Issue: "SARIF upload failed"
**Solution**: Check repository security settings
```bash
# Ensure Security tab is enabled in repository settings
# SARIF uploads require security-events: write permission
```

#### Issue: "Codecov upload failed"
**Solution**: Check CODECOV_TOKEN secret
```bash
gh secret set CODECOV_TOKEN --body="your-codecov-token"
```

#### Issue: "Documentation build failed"
**Solution**: Check Node.js and dependency installation
```yaml
# Ensure Node.js version is correct
node-version: '20'
```

#### Issue: "Pre-commit hook timeout"
**Solution**: Check pre-commit configuration
```bash
# Verify .pre-commit-config.yaml exists or gets generated
```

### Debugging Commands

#### View workflow runs:
```bash
gh run list --workflow=ci.yml --limit=5
gh run view <run-id> --log
```

#### Check workflow files:
```bash
gh workflow list
gh workflow view ci.yml
```

#### Monitor real-time:
```bash
gh run watch
```

## ✅ Test Completion Checklist

### Basic Functionality
- [ ] ✅ **CI Pipeline**: Passes with code changes
- [ ] ✅ **Pre-commit**: Validates PRs and commits
- [ ] ✅ **Security**: Scans and uploads to Security tab
- [ ] ✅ **Documentation**: Builds and deploys correctly
- [ ] ✅ **Benchmarks**: Runs performance tests
- [ ] ✅ **Coordination**: Smart triggering works
- [ ] ✅ **Status Dashboard**: Updates correctly

### Advanced Features
- [ ] 🎯 **Smart Testing**: Correct strategy selection
- [ ] 📊 **Comprehensive Reporting**: GitHub Step Summaries
- [ ] 🔒 **Security Integration**: SARIF uploads to Security tab
- [ ] 📈 **Performance Metrics**: Benchmarks and coverage
- [ ] 🚀 **Caching**: Faster execution times
- [ ] 💰 **Cost Optimization**: Reduced unnecessary runs

### Error Handling
- [ ] 🛡️ **Graceful Failures**: Continue-on-error where appropriate
- [ ] 🔄 **Retry Logic**: Automatic retry for flaky operations
- [ ] 📋 **Comprehensive Logging**: Clear error messages
- [ ] 🚨 **Failure Notifications**: Proper status reporting

## 🎉 Success Criteria

The workflows are considered **100% functional** when:

1. **✅ All core workflows execute successfully**
2. **✅ Smart coordination reduces unnecessary runs**
3. **✅ Security scanning integrates with GitHub Security tab**
4. **✅ Documentation builds and deploys automatically**
5. **✅ Status dashboard provides real-time health metrics**
6. **✅ Error handling provides clear feedback**
7. **✅ Performance is optimized with caching**
8. **✅ Cost is optimized through smart triggering**

## 🚀 Post-Testing Actions

After successful testing:

1. **📊 Monitor Usage**: Check workflow execution patterns
2. **🔧 Fine-tune**: Adjust change detection patterns if needed
3. **📈 Optimize**: Improve performance based on usage data
4. **🎯 Enhance**: Add new workflows or features as needed
5. **📚 Document**: Update this guide based on testing experience

---

*This testing guide ensures all GitHub Actions workflows function at 100% efficiency and reliability.* 🎯

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../AGENTS.md)
- **Documentation**: [Reference Guides](../docs/README.md)
- **Home**: [Repository Root](../README.md)
