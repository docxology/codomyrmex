# Codomyrmex Agents — src/codomyrmex/documentation

## Purpose
Documentation agents generating and reviewing written artifacts.

## Active Components
- `docs/` – Agent surface for `docs` components.
- `scripts/` – Agent surface for `scripts` components.
- `src/` – Agent surface for `src` components.
- `static/` – Agent surface for `static` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Documentation generation maintains accuracy and stays synchronized with code.
- Website generation produces accessible and navigable documentation.

## Related Modules
- **API Documentation** (`api_documentation/`) - Generates API documentation
- **Build Synthesis** (`build_synthesis/`) - Integrates documentation into builds
- **Project Orchestration** (`project_orchestration/`) - Coordinates documentation workflows

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation
