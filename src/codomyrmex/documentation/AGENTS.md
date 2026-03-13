# Codomyrmex Agents — src/codomyrmex/documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Documentation files and guides.

## Active Components
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `CHANGELOG.md` – Version history and release notes
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SECURITY.md` – Security considerations and vulnerability reporting
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `USAGE_EXAMPLES.md` – Usage Examples implementation
- `__init__.py` – Python package entry point — exports and initialization
- `bug_taxonomy.md` – Bug Taxonomy implementation
- `coverage_assessment.md` – Coverage Assessment implementation
- `docs/` – Documentation files
- `documentation_website.py` – Internal implementation module
- `docusaurus.config.js` – Docusaurus.Config implementation
- `education/` – education module implementation
- `maintenance.py` – Maintenance implementation
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `package-lock.json` – Package Lock implementation
- `package.json` – Package implementation
- `pai.py` – Pai implementation
- `py.typed` – PEP 561 marker for typed package
- `quality/` – quality module implementation
- `scripts/` – Automation and utility scripts
- `sidebars.js` – Sidebars implementation
- `src/` – src module implementation
- `static/` – static module implementation
- `yarn.lock` – Yarn implementation

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `CHANGELOG.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SECURITY.md`
- `SPEC.md`
- `USAGE_EXAMPLES.md`
- `__init__.py`
- `bug_taxonomy.md`
- `coverage_assessment.md`
- `documentation_website.py`
- `docusaurus.config.js`
- `maintenance.py`
- `mcp_tools.py`
- `package-lock.json`
- `package.json`
- `pai.py`
- `py.typed`
- `sidebars.js`
- `yarn.lock`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
