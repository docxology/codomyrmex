# Codomyrmex Agents — docs

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [deployment](deployment/AGENTS.md)
    - [development](development/AGENTS.md)
    - [examples](examples/AGENTS.md)
    - [getting-started](getting-started/AGENTS.md)
    - [integration](integration/AGENTS.md)
    - [modules](modules/AGENTS.md)
    - [project](project/AGENTS.md)
    - [project_orchestration](project_orchestration/AGENTS.md)
    - [reference](reference/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This is the documentation coordination document for all guides, references, and user-facing content in the Codomyrmex repository. It defines the documentation system that serves users, contributors, and agents working with the Codomyrmex platform.

**Important**: Documentation in this directory is about Codomyrmex itself (the platform), not tools that Codomyrmex provides to users.

## Documentation Structure

### Primary Documentation Areas

The documentation is organized by audience and purpose:

| Area | Purpose | Key Content |
|------|---------|-------------|
| **getting-started/** | Onboarding and setup | Installation, quickstart, tutorials |
| **project/** | Architecture and process | Design principles, contributing, architecture |
| **modules/** | Module system | Module relationships, API specifications |
| **development/** | Development workflow | Environment setup, testing, documentation |
| **reference/** | Technical reference | API docs, CLI reference, troubleshooting |
| **deployment/** | Production deployment | Production setup, scaling, monitoring |
| **integration/** | External integrations | Third-party tools, API integrations |
| **examples/** | Usage examples | Code samples, integration patterns |

## Documentation Principles

### Content Guidelines

All documentation must follow these principles:

1. **"Show, Don't Tell"**: Demonstrate concepts through examples rather than abstract descriptions
2. **Audience-Aware**: Content tailored to specific audiences (users, contributors, agents)
3. **Actionable**: Every document should enable specific actions or understanding
4. **Current**: Documentation must reflect current codebase and practices
5. **Navigable**: Clear cross-references and navigation between related documents

### Quality Standards

- **Completeness**: Every feature and module must be documented
- **Accuracy**: Technical details must match implementation
- **Clarity**: Use clear, understated language without unnecessary adjectives
- **Consistency**: Follow established patterns and terminology
- **Accessibility**: Content should be accessible to various experience levels

## Active Components

### Core Documentation Structure
- `README.md` – Documentation hub and navigation

### User-Facing Documentation
- `getting-started/` – Installation, setup, and basic usage
- `examples/` – Code examples and integration patterns
- `reference/` – Technical reference and troubleshooting

### Contributor Documentation
- `project/` – Architecture, contributing guidelines, project management
- `development/` – Development environment, testing, documentation workflow
- `modules/` – Module system architecture and relationships

### Advanced Documentation
- `deployment/` – Production deployment and operations
- `integration/` – External system integrations
- `project_orchestration/` – Workflow orchestration and project management

## Operating Contracts

### Universal Documentation Protocols

All documentation in this directory must:

1. **Reflect Reality**: Documentation must accurately represent the current codebase
2. **Stay Current**: Update documentation alongside code changes
3. **Clear Navigation**: Maintain consistent cross-references and navigation
4. **Quality First**: Follow established writing and structure standards
5. **Agent Coordination**: Support both human and AI agent navigation

### Documentation-Specific Guidelines

#### User Documentation
- Focus on practical usage and real-world scenarios
- Include working examples
- Provide troubleshooting guidance
- Assume minimal prior knowledge

#### Technical Documentation
- Provide API specifications
- Include implementation details and design rationale
- Document constraints and limitations
- Support advanced use cases

#### Process Documentation
- Document workflows and decision processes
- Include contribution guidelines and standards
- Provide clear escalation paths
- Support collaborative development

## Documentation Maintenance

### Update Triggers

Documentation must be updated when:
- Code interfaces change (API modifications)
- New features are added
- Workflows or processes change
- User experience improvements are made
- Security considerations evolve

### Review Process

- **Code Reviews**: Include documentation impact assessment
- **Automated Checks**: Link validation and audits
- **Regular Audits**: Periodic review of documentation currency
- **User Feedback**: Incorporate user-reported documentation issues

## Navigation
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### For Users
- **Getting Started**: [getting-started/quickstart.md](getting-started/quickstart.md) - Quick introduction
- **Installation**: [getting-started/installation.md](getting-started/installation.md) - Setup instructions
- **Examples**: [examples/README.md](../scripts/examples/README.md) - Usage examples
- **Troubleshooting**: [reference/troubleshooting.md](reference/troubleshooting.md) - Common issues

### For Contributors
- **Contributing**: [project/contributing.md](project/contributing.md) - Development guidelines
- **Architecture**: [project/architecture.md](project/architecture.md) - System design
- **Testing**: [development/testing-strategy.md](development/testing-strategy.md) - Testing approach
- **Documentation**: [development/documentation.md](development/documentation.md) - Documentation workflow

### For Agents
- **Module System**: [modules/overview.md](modules/overview.md) - Module architecture
- **API Reference**: [reference/api.md](reference/api.md) - API documentation
- **Coding Standards**: [cursorrules/general.cursorrules](../cursorrules/general.cursorrules)

## Agent Coordination

### Documentation Synchronization

When documentation changes impact multiple areas:

1. **Cross-Reference Updates**: Ensure all related documents reflect changes
2. **Navigation Consistency**: Maintain consistent linking patterns
3. **Version Alignment**: Keep documentation versions synchronized with code
4. **Agent Communication**: Update agent coordination documents as needed

### Quality Gates

Before publishing documentation changes:

1. **Link Validation**: All internal and external links functional
2. **Completeness Check**: Required sections present
3. **Accuracy Review**: Technical details verified against codebase
4. **Navigation Audit**: Cross-references and navigation paths validated
5. **Style Consistency**: Follows established documentation standards

## Documentation Metrics

### Quality Metrics
- **Link Health**: 100% valid internal links
- **Completeness**: All modules and features documented
- **Freshness**: Documentation updated within 30 days of code changes
- **Accessibility**: Content accessible to target audiences

### Coverage Areas
- **User Documentation**: Installation through advanced usage
- **API Documentation**: OpenAPI/Swagger specifications
- **Integration Guides**: Third-party tool integration patterns
- **Troubleshooting**: Common issues and resolution steps

## Version History

- **v0.1.0** (December 2025) - Initial documentation system with audience-specific organization

## Related Documentation

- **[Documentation Guide](development/documentation.md)** - Documentation workflow and standards
- **[Contributing Guide](project/contributing.md)** - Contribution guidelines and process
- **[Module Overview](modules/overview.md)** - Module system documentation