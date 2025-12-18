# scripts

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

The scripts directory contains maintenance and automation utilities that support the entire Codomyrmex development workflow. These utilities handle everything from environment setup and code quality checks to documentation generation and system maintenance.

Scripts are organized by functionality and follow consistent patterns for execution, error handling, and logging.

## Script Categories

### Development Workflow
Scripts that support day-to-day development activities:

**development/**
- `setup.sh` - Environment setup and dependency installation
- `lint.sh` - Code linting and style checking
- `test.sh` - Test execution and coverage reporting
- `format.sh` - Code formatting and import organization

### Documentation Management
Automated tools for documentation generation and maintenance:

**documentation/**
- `generate_api_docs.py` - API documentation generation
- `validate_links.py` - Link validation across documentation
- `audit_completeness.py` - Documentation completeness auditing

### System Maintenance
Utilities for system health and maintenance:

**maintenance/**
- `cleanup.py` - File and directory cleanup
- `backup.py` - Database and configuration backups
- `health_check.py` - System health monitoring

### Module-Specific Automation
Per-module utilities that handle specialized tasks:

**ai_code_editing/**
- `generate_code.py` - AI-assisted code generation
- `refactor.py` - Code refactoring automation

**build_synthesis/**
- `build.py` - Multi-language build orchestration
- `package.py` - Package creation and distribution

**git_operations/**
- `commit_automation.py` - Automated commit management
- `branch_management.py` - Branch lifecycle management

## Usage Examples

### Environment Setup

```bash
# Complete development environment setup
./scripts/development/setup.sh

# Quick environment validation
./scripts/environment_setup/validate.py
```

### Code Quality

```bash
# Run full quality suite
./scripts/development/lint.sh && ./scripts/development/test.sh

# Format code only
./scripts/development/format.sh
```

### Documentation

```bash
# Generate API documentation
python scripts/documentation/generate_api_docs.py

# Audit documentation completeness
python scripts/documentation/audit_completeness.py
```

### Maintenance

```bash
# System cleanup
python scripts/maintenance/cleanup.py

# Health check
python scripts/maintenance/health_check.py
```

## Script Standards

### Execution Patterns

All scripts follow consistent execution patterns:

1. **Argument Validation** - Check required parameters and environment
2. **Logging Setup** - Initialize structured logging
3. **Error Handling** - Comprehensive try/catch with informative messages
4. **Cleanup** - Ensure proper resource cleanup on exit

### Output Standards

Scripts provide consistent output:

- **Success Messages** - Clear indication of successful completion
- **Error Messages** - Detailed error information with resolution steps
- **Progress Indicators** - Status updates for long-running operations
- **Structured Logging** - JSON-formatted logs for monitoring

### File Organization

Scripts are organized following these principles:

- **One Purpose Per Script** - Each script has a single, clear responsibility
- **Configuration Files** - External configuration for flexibility
- **Shared Utilities** - Common functions in `_orchestrator_utils.py`
- **Documentation** - Inline help and usage documentation

## Directory Contents

### Core Infrastructure
- `README.md` – This documentation
- `_orchestrator_utils.py` – Shared utilities for script coordination

### Development Tools
- `development/` – Development workflow automation
- `environment_setup/` – Environment validation and setup

### Content Management
- `documentation/` – Documentation generation and maintenance
- `docs/` – Documentation utilities
- `examples/` – Example script management

### Module Automation
- `ai_code_editing/` – AI-assisted development tools
- `api_documentation/` – API documentation generation
- `build_synthesis/` – Build orchestration
- `ci_cd_automation/` – CI/CD pipeline management
- `code_execution_sandbox/` – Safe execution environments
- `code_review/` – Automated code review
- `config_management/` – Configuration management
- `containerization/` – Container lifecycle management
- `data_visualization/` – Data visualization automation
- `database_management/` – Database operations
- `git_operations/` – Git workflow automation
- `language_models/` – Language model management
- `logging_monitoring/` – Logging system configuration
- `maintenance/` – System maintenance utilities
- `model_context_protocol/` – MCP tool management
- `modeling_3d/` – 3D modeling utilities
- `module_template/` – Module creation templates
- `ollama_integration/` – Local LLM integration
- `pattern_matching/` – Pattern analysis tools
- `performance/` – Performance monitoring
- `physical_management/` – Hardware management
- `project_orchestration/` – Project workflow orchestration
- `security_audit/` – Security scanning tools
- `static_analysis/` – Code analysis utilities
- `system_discovery/` – System exploration tools
- `terminal_interface/` – Terminal interface components
- `fabric_integration/` – Fabric AI framework integration

## Navigation

### Getting Started
- **Environment Setup**: [development/setup.sh](development/setup.sh) - Complete development environment
- **Quick Examples**: [examples/](examples/) - Usage examples and demonstrations

### Advanced Usage
- **Script Development**: [module_template/](module_template/) - Creating new scripts
- **Maintenance**: [maintenance/](maintenance/) - System maintenance utilities

### Related Documentation
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Development Guide**: [docs/development/environment-setup.md](../../../docs/development/environment-setup.md)
- **Contributing**: [docs/project/contributing.md](../../../docs/project/contributing.md)

## Contributing

When adding new scripts:

1. **Follow Standards** - Adhere to established patterns and conventions
2. **Add Documentation** - Include usage examples and help text
3. **Write Tests** - Create comprehensive test coverage
4. **Update This README** - Document the new script in this file

### Script Template

Use the module template for new scripts:

```bash
# Copy template
cp scripts/module_template/script_template.py scripts/new_feature/new_script.py

# Customize for your needs
# Add comprehensive documentation
# Include error handling
# Add logging integration
```
