# Codomyrmex Agents — src/codomyrmex/project_orchestration

## Purpose
Agents coordinating multi-step project workflows and dependencies.

## Active Components
- `templates/` – Agent surface for `templates` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Workflow execution maintains dependency order and handles failures gracefully.
- Performance monitoring provides real-time metrics without impacting workflow execution.
- Multi-module coordination maintains data consistency across all participating modules.

## Related Modules
- **All Modules** - Project orchestration coordinates workflows across all Codomyrmex modules
- **Logging Monitoring** (`logging_monitoring/`) - Provides telemetry for orchestration
- **Performance** (`performance/`) - Monitors orchestration performance

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔌 API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Complete API reference
- **🔧 MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md) - MCP tool specifications
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation
