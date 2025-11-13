# Codomyrmex Agents — config

## Purpose
Configuration templates, examples, and setup guides for various Codomyrmex deployment scenarios and environments.

## Active Components
- `templates/` – Agent surface for configuration templates (development, production, testing environments).
- `examples/` – Agent surface for example configurations (workflows, project templates, resources).

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- All configuration templates must be tested and validated before inclusion.
- Configuration examples must demonstrate best practices and common use cases.

## Related Modules
- **Project Orchestration** (`../src/codomyrmex/project_orchestration/`) - Uses configuration templates for workflow setup
- **Environment Setup** (`../src/codomyrmex/environment_setup/`) - Uses environment configuration templates
- **Config Management** (`../src/codomyrmex/config_management/`) - Manages and deploys configurations

## Navigation Links
- **📚 Configuration Overview**: [README.md](README.md) - Configuration templates and examples documentation
- **🏠 Project Root**: [../README.md](../README.md) - Main project README
- **📖 Documentation Hub**: [../docs/README.md](../docs/README.md) - Complete documentation structure
- **🎯 Project Orchestration**: [../src/codomyrmex/project_orchestration/README.md](../src/codomyrmex/project_orchestration/README.md) - Project orchestration module
- **⚙️ Config Management**: [../src/codomyrmex/config_management/README.md](../src/codomyrmex/config_management/README.md) - Config management module

