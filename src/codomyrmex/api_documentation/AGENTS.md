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

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
