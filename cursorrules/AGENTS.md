# Codomyrmex Agents — cursorrules

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the coding standards coordination document for all Cursor rules, coding conventions, and automation guidelines in the Codomyrmex repository. It defines the rule system that ensures consistent code quality, style, and development practices across the entire platform.

The cursorrules directory contains hierarchical coding standards that guide both human developers and AI agents in maintaining high-quality, consistent code.

## Rule Hierarchy

### Rule Organization

Rules are organized by scope and specificity:

| Level | Scope | Purpose | Location |
|-------|-------|---------|----------|
| **General** | Repository-wide | Universal coding standards | `general.cursorrules` |
| **Cross-Module** | Multi-module coordination | Inter-module consistency | `cross-module/` |
| **Module-Specific** | Individual modules | Module-specific standards | `modules/` |
| **File-Specific** | Individual files | File-type specific rules | `file-specific/` |

### Rule Priority

When rules conflict, more specific rules take precedence over more general rules in this hierarchy (from most specific to most general):
1. File-specific rules (highest priority - apply to specific file types)
2. Module-specific rules (apply to specific modules)
3. Cross-module rules (apply across multiple modules)
4. General rules (lowest priority - apply repository-wide)

## Rule Categories

### General Rules (`general.cursorrules`)

Universal standards applicable across all code:
- Python best practices (PEP 8 compliance)
- Import organization and dependency management
- Error handling and logging standards
- Documentation requirements
- Testing standards

### Cross-Module Rules (`cross-module/`)

Standards for inter-module coordination:
- API design consistency
- Data structure standardization
- Communication protocol adherence
- Shared utility usage patterns

### Module-Specific Rules (`modules/`)

Module-tailored standards:
- Module-specific naming conventions
- Module architecture patterns
- Module-specific testing requirements
- Module documentation standards

### File-Specific Rules (`file-specific/`)

File-type specific guidance:
- Python file structure and imports
- Markdown documentation formatting
- Configuration file standards
- Script file conventions

## Active Components

### Core Rule Files
- `README.md` – Coding standards documentation
- `general.cursorrules` – Repository-wide coding standards

### Specialized Rule Sets
- `cross-module/` – Rules for cross-module interactions
- `modules/` – Module-specific coding standards
- `file-specific/` – File-type specific conventions

### Rule Files by Category

**Cross-Module Rules:**
- `build_synthesis.cursorrules` - Build orchestration standards
- `code_execution_sandbox.cursorrules` - Safe execution guidelines
- `data_visualization.cursorrules` - Visualization consistency
- `logging_monitoring.cursorrules` - Logging standards
- `model_context_protocol.cursorrules` - MCP compliance
- `output_module.cursorrules` - Output directory management standards
- `pattern_matching.cursorrules` - Pattern matching coordination standards
- `static_analysis.cursorrules` - Static analysis coordination standards
- `template_module.cursorrules` - Template usage coordination standards

**Module-Specific Rules:**
- `ai_code_editing.cursorrules` - AI-assisted coding standards
- `api_documentation.cursorrules` - API documentation guidelines
- `build_synthesis.cursorrules` - Build automation standards
- `ci_cd_automation.cursorrules` - CI/CD automation standards
- `code_execution_sandbox.cursorrules` - Code execution sandbox standards
- `code_review.cursorrules` - Code review standards
- `config_management.cursorrules` - Configuration management standards
- `containerization.cursorrules` - Containerization standards
- `data_visualization.cursorrules` - Data visualization standards
- `database_management.cursorrules` - Database management standards
- `documentation.cursorrules` - Documentation generation standards
- `environment_setup.cursorrules` - Environment setup standards
- `git_operations.cursorrules` - Git operations standards
- `language_models.cursorrules` - Language model integration standards
- `logging_monitoring.cursorrules` - Logging and monitoring standards
- `model_context_protocol.cursorrules` - Model context protocol standards
- `modeling_3d.cursorrules` - 3D modeling standards
- `module_template.cursorrules` - Module template standards
- `ollama_integration.cursorrules` - Ollama integration standards
- `pattern_matching.cursorrules` - Pattern matching standards
- `performance.cursorrules` - Performance optimization standards
- `physical_management.cursorrules` - Physical system management standards
- `project_orchestration.cursorrules` - Project orchestration standards
- `security_audit.cursorrules` - Security audit standards
- `static_analysis.cursorrules` - Static analysis standards
- `system_discovery.cursorrules` - System discovery standards
- `terminal_interface.cursorrules` - Terminal interface standards

**File-Specific Rules:**
- `README.md.cursorrules` - README file standards

## Operating Contracts

### Universal Rule Protocols

All coding standards in this directory must:

1. **Technology Agnostic** - Rules work across different technologies
2. **Clearly Justified** - Each rule includes rationale for its existence
3. **Regularly Reviewed** - Standards evolve with project needs
4. **Well Documented** - Rules include examples and explanations
5. **Enforceable** - Rules can be automatically validated

### Rule-Specific Guidelines

#### General Rules
- Focus on universal best practices
- Minimize technology-specific requirements
- Provide clear examples and counter-examples
- Include enforcement mechanisms

#### Module Rules
- Address module-specific challenges
- Consider module architecture and purpose
- Include module-specific tooling requirements
- Support module evolution and refactoring

#### File Rules
- Address file-type specific concerns
- Include formatting and structure requirements
- Define file organization standards
- Support automated formatting and validation

## Rule Enforcement

### Automated Validation

Rules are enforced through:
- **Pre-commit hooks** - Automatic validation before commits
- **CI/CD checks** - Automated validation in pipelines
- **IDE integration** - Real-time validation in development environments
- **Manual reviews** - Peer review validation

### Validation Tools

Rule compliance verified using:
- **Linters** - Code style and quality checking
- **Formatters** - Automated code formatting
- **Custom validators** - Project-specific rule checking
- **Documentation auditors** - Documentation standard validation

## Rule Development

### Adding New Rules

Process for introducing new coding standards:

1. **Identify Need** - Document the problem the rule addresses
2. **Research Solutions** - Review industry best practices
3. **Draft Rule** - Write clear, actionable rule with examples
4. **Validate Impact** - Test rule against existing codebase
5. **Document Rationale** - Explain why the rule is necessary
6. **Implement Enforcement** - Add automated validation where possible

### Rule Modification

Changing existing rules requires:
- Impact assessment across the codebase
- Migration plan for existing code
- Clear communication to all contributors
- Gradual rollout with deprecation warnings

## Navigation

### For Users
- **Quick Reference**: [general.cursorrules](general.cursorrules) - Core coding standards
- **Getting Started**: [README.md](README.md) - Coding standards overview

### For Agents
- **General Standards**: [general.cursorrules](general.cursorrules) - Repository-wide rules
- **Module Standards**: [modules/](modules/) - Module-specific guidelines
- **Cross-Module**: [cross-module/](cross-module/) - Inter-module coordination

### For Contributors
- **Contributing**: [docs/project/contributing.md](../docs/project/contributing.md)
- **Rule Development**: Guidelines for creating new standards
- **Enforcement**: [scripts/static_analysis/](../../scripts/static_analysis/) - Rule validation tools

## Agent Coordination

### Rule Consistency

When rules affect multiple areas:

1. **Cross-Reference Updates** - Ensure related rules remain consistent
2. **Impact Assessment** - Evaluate effects on existing code and processes
3. **Documentation Updates** - Update rule documentation and examples
4. **Enforcement Updates** - Modify validation tools and processes

### Quality Gates

Before rule changes are accepted:

1. **Consistency Check** - Rules don't conflict with existing standards
2. **Enforcement Ready** - Automated validation available or planned
3. **Documentation Complete** - Rules fully documented with examples
4. **Impact Assessed** - Effects on codebase evaluated
5. **Migration Planned** - Plan for existing code compliance

## Rule Metrics

### Compliance Metrics
- **Rule Coverage** - Percentage of rules with automated validation
- **Compliance Rate** - Percentage of code meeting standards
- **Violation Trends** - Tracking of rule violations over time
- **Review Efficiency** - Time spent on style-related reviews

### Maintenance Metrics
- **Rule Updates** - Frequency of rule updates and improvements
- **Documentation Freshness** - How current rule documentation remains
- **Adoption Rate** - How quickly new rules are adopted

## Version History

- **v0.1.0** (December 2025) - Initial coding standards system with hierarchical rule organization

## Related Documentation

- **[Contributing Guide](../docs/project/contributing.md)** - Development standards and workflow
- **[Testing Strategy](../docs/development/testing-strategy.md)** - Testing standards and practices
- **[Architecture](../docs/project/architecture.md)** - System design principles
