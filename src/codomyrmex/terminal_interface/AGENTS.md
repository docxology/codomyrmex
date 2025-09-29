# Codomyrmex Agents — src/codomyrmex/terminal_interface

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2025

## Purpose
Advanced terminal interface agents providing rich CLI experiences, interactive shells, command routing, and developer productivity tools with intelligent command completion and workflow integration.

## Active Components
- `interactive_shell.py` – Rich terminal interface with command history, auto-completion, and workflow integration
- `terminal_utils.py` – Terminal utility functions for formatting, colors, and system interaction
- `__init__.py` – Package initialization and terminal interface exports
- `README.md` – Terminal interface usage guides and customization documentation

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Terminal interfaces maintain responsive performance and handle user input gracefully.
- Command routing provides accurate module discovery and execution.
- Interactive features enhance developer productivity without overwhelming system resources.

## Related Modules
- **Project Orchestration** (`project_orchestration/`) - Integrates terminal workflows with project management
- **AI Code Editing** (`ai_code_editing/`) - Provides terminal access to AI-powered development tools
- **Documentation** (`documentation/`) - Offers terminal-based documentation browsing

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
