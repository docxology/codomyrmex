# Codomyrmex Agents — scripts/api_documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

API documentation automation scripts providing command-line interfaces for generating, extracting, and validating API documentation. This script module enables automated API specification generation, OpenAPI validation, and documentation management for Codomyrmex projects.

The api_documentation scripts serve as the primary interface for developers and automated systems to manage API documentation workflows.

## Module Overview

### Key Capabilities
- **Documentation Generation**: Generate API documentation from code
- **Specification Extraction**: Extract API specifications from source code
- **OpenAPI Generation**: Create OpenAPI/Swagger specifications
- **Validation**: Validate API specifications and documentation
- **Multi-Format Support**: Support for various documentation formats

### Key Features
- Command-line interface with argument parsing
- Integration with core API documentation modules
- Structured output formatting (JSON, YAML, HTML)
- Error handling and validation
- Logging integration for operation tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the API documentation orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `generate-docs` - Generate API documentation from source code
- `extract-specs` - Extract API specifications from code
- `generate-openapi` - Generate OpenAPI specifications
- `validate-openapi` - Validate OpenAPI specifications

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--output, -o` - Output file path

```python
def handle_generate_docs(args) -> None
```

Handle API documentation generation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `source_path` (str): Path to source code directory
  - `output_path` (str, optional): Output path for documentation
  - `format` (str, optional): Output format ("html", "markdown", "json"). Defaults to "html"
  - `include_private` (bool, optional): Include private APIs. Defaults to False

**Returns:** None (outputs documentation to specified location)

```python
def handle_extract_specs(args) -> None
```

Handle API specification extraction commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `source_path` (str): Path to source code directory
  - `output_path` (str, optional): Output path for specifications
  - `format` (str, optional): Output format ("json", "yaml"). Defaults to "json"

**Returns:** None (outputs specifications to specified location)

```python
def handle_generate_openapi(args) -> None
```

Handle OpenAPI specification generation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `title` (str): API title
  - `version` (str): API version
  - `source_path` (str, optional): Path to source code for analysis
  - `output_path` (str, optional): Output path for OpenAPI spec
  - `servers` (list, optional): List of server URLs

**Returns:** None (outputs OpenAPI specification to specified location)

```python
def handle_validate_openapi(args) -> None
```

Handle OpenAPI specification validation commands from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `spec_path` (str): Path to OpenAPI specification file
  - `strict` (bool, optional): Enable strict validation. Defaults to False

**Returns:** None (outputs validation results to stdout)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

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
3. **Logging Integration**: Use centralized logging for all operations
4. **Output Formatting**: Provide structured output options (JSON, YAML)
5. **Validation**: Validate inputs and outputs before processing

### Module-Specific Guidelines

#### Documentation Generation
- Support multiple output formats for different consumers
- Include comprehensive API information (parameters, responses, examples)
- Generate navigation and cross-references in documentation
- Handle large codebases efficiently

#### Specification Extraction
- Extract accurate API signatures and metadata
- Support multiple API frameworks and patterns
- Validate extracted specifications
- Handle complex type definitions and relationships

#### OpenAPI Generation
- Generate valid OpenAPI 3.0 specifications
- Include all required fields and proper schema definitions
- Support advanced OpenAPI features (security, examples, links)
- Validate generated specifications

#### Validation
- Perform comprehensive validation of API specifications
- Report specific validation errors with context
- Support different validation strictness levels
- Provide actionable error messages

## Navigation Links

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Configuration Sharing**: Coordinate API settings and documentation paths
3. **Output Consistency**: Maintain consistent output formats across scripts
4. **Validation Coordination**: Share validation rules and error handling

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Validation Testing**: API specifications validate correctly
3. **Output Verification**: Generated documentation and specs are accurate
4. **Integration Testing**: Scripts work with core API documentation modules

## Version History

- **v0.1.0** (December 2025) - Initial API documentation automation scripts with CLI interface
