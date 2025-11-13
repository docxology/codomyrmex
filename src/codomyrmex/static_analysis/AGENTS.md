# Codomyrmex Agents — src/codomyrmex/static_analysis

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2025

## Purpose
Static analysis agents scanning codebases for quality and compliance.

## Active Components
- `docs/` – Agent surface for `docs` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Static analysis maintains accuracy across all supported programming languages.
- Security scanning identifies vulnerabilities without false positives exceeding threshold.
- Performance analysis provides actionable optimization recommendations.

## Related Modules
- **Code Review** (`code_review/`) - Uses static analysis for code reviews
- **Security Audit** (`security_audit/`) - Integrates security scanning
- **AI Code Editing** (`ai_code_editing/`) - Validates generated code

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔌 API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Complete API reference
- **🔧 MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation
