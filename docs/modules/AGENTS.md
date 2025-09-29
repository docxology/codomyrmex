# Codomyrmex Agents — docs/modules

## Purpose
Module system architecture and design documentation coordination for Codomyrmex, providing comprehensive understanding of the modular architecture, inter-module dependencies, integration patterns, and system design principles.

## Active Components
- **overview.md** - Module system architecture, design principles, and organizational structure
- **relationships.md** - Inter-module dependencies, data flow patterns, and integration relationships

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Maintain comprehensive cross-linking between module documentation and related sections.
- Ensure module documentation reflects current architecture and real-world module interactions.

## Checkpoints
- [x] Confirm AGENTS.md reflects the current module system documentation purpose and comprehensive coverage.
- [x] Verify logging and telemetry hooks for this directory's agents are properly configured.
- [x] Sync automation scripts and TODO entries after modifications to maintain module documentation consistency.
- [x] Ensure module documentation is properly linked and navigable from main documentation hubs.
- [x] Maintain consistent AGENTS.md structure with parent documentation coordination agents.

## Navigation Links
- **📚 Documentation Hub**: [../../README.md](../../README.md) - Central documentation overview and navigation
- **🏛️ Module Overview**: [overview.md](overview.md) - Module architecture and design principles
- **🔗 Module Relationships**: [relationships.md](relationships.md) - Dependencies and integration patterns
- **🏛️ Architecture**: [../../project/architecture.md](../../project/architecture.md) - System design context
- **🔌 API Reference**: [../../reference/api-complete.md](../../reference/api-complete.md) - Module APIs
- **📦 Module Template**: [../../../src/codomyrmex/module_template/README.md](../../../src/codomyrmex/module_template/README.md) - Template for creating new modules
- **🎓 Module Tutorial**: [../../getting-started/tutorials/creating-a-module.md](../../getting-started/tutorials/creating-a-module.md) - Learn by building modules
