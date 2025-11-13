# Codomyrmex Agents — src/codomyrmex/physical_management

## Purpose
Physical system management agents controlling hardware interfaces, sensor integration, and robotic systems with real-time monitoring and control capabilities.

## Active Components
- `docs/` – Agent surface for `docs` components.
- `examples/` – Agent surface for `examples` components.
- `tests/` – Agent surface for `tests` components.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Hardware interfaces maintain safety boundaries and error handling.
- Real-time monitoring provides accurate system state without performance degradation.

## Related Modules
- **Modeling 3D** (`modeling_3d/`) - Provides 3D visualization for physical systems
- **Performance** (`performance/`) - Monitors physical system performance
- **System Discovery** (`system_discovery/`) - Discovers physical hardware capabilities

## Navigation Links
- **📚 Module Overview**: [README.md](README.md) - Module documentation and usage
- **🔌 API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Complete API reference
- **🏠 Package Root**: [../../README.md](../../README.md) - Package overview
- **📖 Documentation Hub**: [../../../docs/README.md](../../../docs/README.md) - Complete documentation
