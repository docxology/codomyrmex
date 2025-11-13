# Codomyrmex Agents — src/codomyrmex/containerization

## Purpose
Containerization agents managing Docker container lifecycle, including image building, container orchestration, and deployment automation for development and production environments.

## Active Components
- `docker_manager.py` – Docker container management system handling image building, container lifecycle, networking, and volume management
- `__init__.py` – Package initialization and Docker utilities exports

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Container operations maintain security boundaries and resource limits.
- Image building optimizes for size and security while maintaining functionality.

## Related Modules
- **CI/CD Automation** (`ci_cd_automation/`) - Uses containers for deployment pipelines
- **Build Synthesis** (`build_synthesis/`) - Integrates container builds into build workflows
- **Code Execution Sandbox** (`code_execution_sandbox/`) - Uses containerization for secure execution

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔒 Security**: [SECURITY.md](SECURITY.md) - Security considerations
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation
