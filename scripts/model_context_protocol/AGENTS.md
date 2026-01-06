# Codomyrmex Agents — scripts/model_context_protocol

## Signposting
- **Parent**: [Parent](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Model Context Protocol automation scripts providing command-line interfaces for MCP tool management, specification handling, and protocol validation. This script module enables automated MCP workflows for the Codomyrmex platform.

The model_context_protocol scripts serve as the primary interface for MCP tool management and protocol coordination.

## Module Overview

### Key Capabilities
- **Tool Information**: Display and manage MCP tool specifications
- **Tool Listing**: Comprehensive listing of available MCP tools
- **Protocol Validation**: Validation of MCP protocol compliance
- **Tool Discovery**: Automated discovery and registration of MCP tools
- **Specification Management**: Management of tool specifications and metadata

### Key Features
- Command-line interface with argument parsing
- Integration with core MCP implementation
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for MCP operations tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the MCP orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `info` - Display MCP information and status
- `list-tools` - List available MCP tools

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--format, -f` - Output format (json, text, table)

```python
def handle_info(args) -> None
```

Handle information display commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `show_config` (bool, optional): Show MCP configuration. Defaults to False
  - `show_stats` (bool, optional): Show MCP statistics. Defaults to False
  - `detailed` (bool, optional): Show detailed information. Defaults to False

**Returns:** None (displays MCP information)

```python
def handle_list_tools(args) -> None
```

Handle tool listing commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `category` (str, optional): Filter tools by category
  - `provider` (str, optional): Filter tools by provider
  - `status` (str, optional): Filter tools by status ("active", "inactive", "all"). Defaults to "active"
  - `output_file` (str, optional): Output file for tool list

**Returns:** None (lists MCP tools and outputs results)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### MCP Assets
- `tool_specs/` – MCP tool specifications
- `protocol_configs/` – Protocol configuration files
- `validation_rules/` – Protocol validation rules

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Protocol Compliance**: Ensure MCP protocol compliance
4. **Tool Validation**: Validate tool specifications and functionality
5. **Security**: Handle sensitive MCP configuration securely

### Module-Specific Guidelines

#### Tool Management
- Support comprehensive tool discovery and registration
- Provide detailed tool information and capabilities
- Validate tool specifications against MCP standards
- Support tool categorization and filtering

#### Protocol Validation
- Implement MCP protocol compliance checking
- Validate tool specifications and schemas
- Provide detailed validation reports and recommendations
- Support automated protocol updates

#### Information Display
- Provide clear, structured information about MCP tools
- Support different output formats for different use cases
- Include tool capabilities, parameters, and usage examples
- Support filtering and searching of tool information

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Tool Integration**: Coordinate with AI modules for tool usage
3. **Protocol Standards**: Maintain consistency with MCP implementations
4. **Validation Coordination**: Share validation results with other assessment tools

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **MCP Testing**: Scripts work with MCP protocol correctly
3. **Tool Testing**: Tool listing and information display work accurately
4. **Validation Testing**: Protocol validation works correctly
5. **Integration Testing**: Scripts work with core MCP implementation

## Version History

- **v0.1.0** (December 2025) - Initial MCP automation scripts with tool management and protocol validation capabilities