# Codomyrmex Agents — src/codomyrmex/code_review

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing automated code review and quality assessment capabilities for the Codomyrmex platform. This module performs intelligent analysis of code changes, provides actionable feedback, and supports both automated and human-in-the-loop code review workflows.

The code_review module serves as the quality assurance backbone, enabling consistent and intelligent code review processes throughout the platform.

## Module Overview

### Key Capabilities
- **Automated Code Analysis**: Intelligent review of code changes and pull requests
- **Quality Metrics**: Code quality scoring and improvement recommendations
- **Style Consistency**: Automated style guide enforcement and suggestions
- **Security Review**: Integration with security scanning for vulnerability detection
- **Performance Analysis**: Identification of performance bottlenecks and optimization opportunities
- **Documentation Review**: Assessment of code documentation completeness

### Key Features
- Multi-language code review support
- Configurable review rules and policies
- Integration with version control systems
- Automated feedback generation
- Review metrics and trend analysis
- Custom rule engine for organization-specific standards

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `code_review.py` – Main code review engine and analysis
- `demo_review.py` – Review demonstration and examples

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for code review
- `CHANGELOG.md` – Version history and updates

### Testing
- `test_simple.py` – Simple test examples
- `tests/` – Comprehensive test suite

### Supporting Files
- `requirements.txt` – Module dependencies (code analysis tools, AI libraries)
- `docs/` – Additional documentation

## Operating Contracts

### Universal Code Review Protocols

All code review activities within the Codomyrmex platform must:

1. **Consistent Standards** - Apply uniform review criteria across all codebases
2. **Actionable Feedback** - Provide specific, fixable recommendations
3. **Educational Focus** - Help developers improve code quality over time
4. **Performance Aware** - Review processes don't significantly impact development velocity
5. **Security Integration** - Include security considerations in review feedback

### Module-Specific Guidelines

#### Review Automation
- Support both pre-commit and continuous integration review workflows
- Provide configurable review thresholds and policies
- Include review result caching to avoid redundant analysis
- Support incremental review of code changes

#### Quality Assessment
- Implement multi-dimensional quality scoring (style, performance, security, etc.)
- Provide severity levels for different types of issues
- Include automated fix suggestions where possible
- Track review quality trends over time

#### Integration Support
- Integrate with popular version control platforms (GitHub, GitLab, etc.)
- Support webhook-based automated reviews
- Provide API endpoints for custom integrations
- Include review result export capabilities

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations

### Related Modules
- **Static Analysis**: [../static_analysis/](../../static_analysis/) - Code quality analysis integration
- **Security Audit**: [../security_audit/](../../security_audit/) - Security review enhancement
- **Git Operations**: [../git_operations/](../../git_operations/) - Version control integration

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **CI/CD Integration** - Provide automated review gates in pipelines
2. **Version Control** - Coordinate with Git operations for change analysis
3. **Quality Metrics** - Contribute to overall platform quality measurements
4. **Security Enhancement** - Include security findings in review feedback

### Quality Gates

Before code review changes are accepted:

1. **Accuracy Validated** - Review findings are accurate and helpful
2. **Performance Tested** - Review processes complete within acceptable timeframes
3. **False Positive Minimized** - Low rate of incorrect review feedback
4. **Integration Verified** - Works correctly with supported version control systems
5. **Customization Supported** - Allows organization-specific review rules

## Version History

- **v0.1.0** (December 2025) - Initial automated code review system with quality analysis and feedback generation
