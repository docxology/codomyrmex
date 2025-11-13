# Codomyrmex Agents — src/codomyrmex/code_review

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2025

## Purpose
Comprehensive code review agents providing advanced static analysis capabilities for code quality, security, and maintainability assessment.

## Active Components
- `docs/` – Agent surface for `docs` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Code review agents provide accurate analysis across all supported programming languages.
- Pyscn integration maintains high-performance analysis with LSH acceleration.
- Security scanning identifies vulnerabilities without false positives exceeding threshold.
- Performance analysis provides actionable optimization recommendations.

## Core Features
- **Pyscn Integration**: Advanced static analysis using CFG-based dead code detection, APTED clone detection, and cyclomatic complexity analysis.
- **Multi-language Support**: Python, JavaScript, TypeScript, Java, Go, Rust, and more.
- **Performance Optimization**: 100,000+ lines/sec analysis with parallel processing.
- **CI/CD Integration**: GitHub Actions, pre-commit hooks, and automated quality gates.
- **Rich Reporting**: HTML reports, JSON/CSV exports, and detailed analysis summaries.

## Related Modules
- **Static Analysis** (`static_analysis/`) - Provides foundational analysis capabilities
- **Security Audit** (`security_audit/`) - Integrates security scanning into reviews
- **AI Code Editing** (`ai_code_editing/`) - Uses reviews to validate generated code

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔌 API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Complete API reference
- **🔧 MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
- **🔒 Security**: [SECURITY.md](SECURITY.md) - Security considerations
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation

