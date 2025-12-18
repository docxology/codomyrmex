# cursorrules

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

The cursorrules directory contains the comprehensive coding standards, style guidelines, and automation rules that ensure consistent, high-quality code across the entire Codomyrmex project. These rules guide both human developers and AI agents in maintaining professional, maintainable, and reliable code.

## Rule Hierarchy

### Understanding Rule Priority

Rules are organized hierarchically with clear precedence:

1. **General Rules** (`general.cursorrules`) - Universal standards for all code
2. **Cross-Module Rules** (`cross-module/`) - Standards for inter-module coordination
3. **Module-Specific Rules** (`modules/`) - Standards tailored to individual modules
4. **File-Specific Rules** (`file-specific/`) - Standards for specific file types

When rules conflict, more specific rules take precedence over general ones.

## Getting Started

### Reading the Rules

```bash
# Start with the general rules
cat general.cursorrules

# Check module-specific rules
cat modules/ai_code_editing.cursorrules

# Review cross-module coordination
cat cross-module/logging_monitoring.cursorrules
```

### Applying the Rules

Rules are automatically enforced through:
- **IDE Integration** - Real-time validation in development environments
- **Pre-commit Hooks** - Automatic checking before code commits
- **CI/CD Pipeline** - Automated validation in continuous integration
- **Code Reviews** - Peer validation of rule compliance

## Core Principles

### Universal Standards

**Clarity and Readability**
- Write code that is easily understandable by human developers
- Use descriptive names and clear structure
- Include comprehensive documentation

**Consistency**
- Follow established patterns and conventions
- Maintain consistent formatting and style
- Use uniform naming conventions

**Quality and Reliability**
- Implement comprehensive error handling
- Write thorough tests for all functionality
- Follow security best practices

## Directory Contents

### Core Rule Files
- `README.md` – This documentation
- `general.cursorrules` – Universal coding standards and principles

### Cross-Module Coordination (`cross-module/`)
Rules for how modules interact and coordinate:
- `build_synthesis.cursorrules` – Build system standards
- `code_execution_sandbox.cursorrules` – Safe execution guidelines
- `data_visualization.cursorrules` – Visualization consistency
- `logging_monitoring.cursorrules` – Logging standards
- `model_context_protocol.cursorrules` – MCP compliance

### Module-Specific Rules (`modules/`)
Rules tailored to individual modules:
- `ai_code_editing.cursorrules` – AI-assisted coding standards
- `api_documentation.cursorrules` – API documentation guidelines
- `environment_setup.cursorrules` – Environment configuration
- `git_operations.cursorrules` – Version control standards
- `static_analysis.cursorrules` – Code analysis standards

### File-Specific Rules (`file-specific/`)
Standards for specific file types:
- `README.md.cursorrules` – Documentation file standards
- Additional file-type specific rules

## Rule Categories

### Code Style and Structure

**Python Standards**
- PEP 8 compliance for formatting
- Type hints for all function parameters and return values
- Descriptive variable and function names
- Consistent import organization

**Error Handling**
- Comprehensive exception handling
- Meaningful error messages
- Appropriate logging levels
- Graceful failure recovery

**Documentation**
- Docstrings for all public functions and classes
- Clear code comments explaining complex logic
- API documentation for module interfaces
- Usage examples in documentation

### Testing Standards

**Test Coverage**
- Unit tests for all functions and classes
- Integration tests for module interactions
- Performance benchmarks where applicable
- Edge case and error condition testing

**Test Quality**
- Descriptive test names and assertions
- Isolation of test cases
- Realistic test data (no mocks)
- Continuous validation

### Security Practices

**Input Validation**
- Validate all external inputs
- Sanitize data to prevent injection attacks
- Use secure defaults for configurations

**Authentication and Authorization**
- Implement proper access controls
- Secure credential management
- Audit logging for security events

## Enforcement and Validation

### Automated Checking

```bash
# Run style and linting checks
python scripts/static_analysis/lint.py

# Validate rule compliance
python scripts/static_analysis/validate_rules.py

# Check documentation standards
python scripts/documentation/validate_docs.py
```

### Manual Review Process

Code changes undergo review for:
- **Rule Compliance** - Adherence to established standards
- **Code Quality** - Clarity, maintainability, and performance
- **Test Coverage** - Appropriate testing for new functionality
- **Documentation** - Complete and accurate documentation

## Contributing to Rules

### Proposing New Rules

1. **Identify Need** - Document the problem the rule addresses
2. **Research Solutions** - Review industry best practices
3. **Draft Rule** - Write clear, enforceable rule with rationale
4. **Validate Impact** - Test rule against existing codebase
5. **Get Consensus** - Discuss with team and get approval

### Rule Modification Process

Changing existing rules requires:
- **Impact Assessment** - Evaluate effects on existing code
- **Migration Plan** - Plan for updating existing code
- **Clear Communication** - Notify all contributors of changes
- **Gradual Implementation** - Allow time for compliance

## Common Rule Violations

### Most Frequent Issues

**Style Inconsistencies**
- Inconsistent naming conventions
- Mixed formatting styles
- Non-standard code organization

**Documentation Gaps**
- Missing docstrings
- Incomplete API documentation
- Unclear code comments

**Testing Shortcomings**
- Insufficient test coverage
- Mock usage instead of real data
- Missing edge case testing

### Quick Fixes

```bash
# Auto-format code
black src/ scripts/

# Sort imports
isort src/ scripts/

# Run tests with coverage
pytest --cov=src/codomyrmex --cov-report=html
```

## Navigation

### Rule Reference
- **General Standards**: [general.cursorrules](general.cursorrules) - Core coding principles
- **Module Rules**: [modules/](modules/) - Module-specific guidelines
- **Cross-Module**: [cross-module/](cross-module/) - Inter-module coordination

### Implementation
- **Validation Tools**: [scripts/static_analysis/](../../scripts/static_analysis/) - Rule enforcement utilities
- **Testing**: [testing/README.md](../../testing/README.md) - Testing standards and practices

### Related Documentation
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Contributing**: [docs/project/contributing.md](../../docs/project/contributing.md)
- **Architecture**: [docs/project/architecture.md](../../docs/project/architecture.md)

## Compliance Metrics

### Quality Indicators

**Rule Compliance Rate**
- Percentage of code meeting established standards
- Trend analysis of compliance over time
- Identification of frequently violated rules

**Code Quality Scores**
- Automated quality metrics from linting tools
- Complexity measurements and maintainability scores
- Technical debt tracking

**Review Efficiency**
- Time spent on style-related review comments
- Reduction in repetitive feedback
- Consistency in code review standards

## Troubleshooting

### Rule Conflicts

When rules appear to conflict:
1. Check rule hierarchy and specificity
2. Review rule rationales for context
3. Consult with team leads for clarification
4. Document conflicts for rule refinement

### Enforcement Issues

If automated enforcement fails:
- Verify tool versions and configurations
- Check for false positives in validation
- Update rules to be more enforceable
- Consider manual review processes

### Adoption Challenges

For teams struggling with rule adoption:
- Provide clear examples and training
- Start with high-impact, easy-to-adopt rules
- Gradually introduce more complex standards
- Recognize and celebrate compliance achievements
