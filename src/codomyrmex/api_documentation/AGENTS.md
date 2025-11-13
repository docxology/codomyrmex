# Codomyrmex Agents — src/codomyrmex/api_documentation

## Purpose
API documentation agents generating comprehensive documentation from codebases, supporting multiple formats including OpenAPI specifications and interactive documentation websites.

## Active Components
- `doc_generator.py` – Core documentation generation engine that analyzes codebases and produces structured documentation
- `openapi_generator.py` – Specialized generator for OpenAPI/Swagger specifications from Python code
- `__init__.py` – Package initialization and public API exports

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- API documentation generation maintains accuracy and stays synchronized with code changes.
- Generated documentation follows industry standards and supports multiple output formats.

## Related Modules
- **Documentation** (`documentation/`) - Uses API documentation for website generation
- **Build Synthesis** (`build_synthesis/`) - Integrates API docs into build artifacts
- **Project Orchestration** (`project_orchestration/`) - Coordinates documentation workflows

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔒 Security**: [SECURITY.md](SECURITY.md) - Security considerations
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation
