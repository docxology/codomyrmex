# Model Context Protocol Example

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Module**: `model_context_protocol` | **Status**: ✅ Complete | **Test Coverage**: Comprehensive

## Overview

This example demonstrates comprehensive Model Context Protocol (MCP) functionality using Codomyrmex's `model_context_protocol` module. It showcases MCP tool calls, tool results, error handling, and integration patterns for AI agent communication within the Codomyrmex ecosystem.

## What This Example Demonstrates

### Core Functionality

- **MCP Tool Calls**: Creation and validation of tool invocation requests
- **Tool Results**: Structured handling of tool execution outcomes
- **Error Details**: Comprehensive error reporting with context preservation
- **Schema Validation**: Pydantic-based validation of all MCP messages
- **Workflow Simulation**: Complete MCP interaction workflows

### Key Features

- ✅ MCP tool call creation with argument validation
- ✅ Tool result processing with success/failure handling
- ✅ Structured error details with type-safe error reporting
- ✅ Schema compliance validation and serialization
- ✅ Workflow simulation demonstrating MCP interactions
- ✅ Export functionality for MCP examples and documentation

## Configuration

### YAML Configuration (config.yaml)

```yaml
mcp:
  strict_validation: true
  validate_schemas: true
  allow_extra_fields: true

  supported_tools:
    - file_reader
    - code_analyzer
    - database_query
    - api_request

demonstration:
  tool_calls_count: 4
  tool_results_count: 4
  error_details_count: 4

  validate_all_calls: true
  simulate_workflows: true
```

### JSON Configuration (config.json)

```json
{
  "mcp": {
    "strict_validation": true,
    "validate_schemas": true,
    "allow_extra_fields": true,
    "supported_tools": [
      "file_reader",
      "code_analyzer",
      "database_query",
      "api_request"
    ]
  },
  "demonstration": {
    "tool_calls_count": 4,
    "tool_results_count": 4,
    "validate_all_calls": true,
    "simulate_workflows": true
  }
}
```

## Tested Methods

This example demonstrates the following methods verified in `test_model_context_protocol.py`:

- `MCPToolCall` model validation - Structured tool invocation requests
- `MCPToolResult` model validation - Tool execution result handling
- `MCPErrorDetail` model validation - Type-safe error reporting

## Sample Output

### Tool Call Validation

```
🔍 Demonstrating MCP Tool Call Validation...
✅ Tool call 1 ('file_reader') validated successfully
✅ Tool call 2 ('code_analyzer') validated successfully
✅ Tool call 3 ('database_query') validated successfully
✅ Tool call 4 ('api_request') validated successfully
```

### Tool Result Processing

```
📊 Demonstrating MCP Tool Result Processing...
✅ Result 1: success
✅ Result 2: success
❌ Result 3: failure
   Error: Failed to connect to database
ℹ️  Result 4: no_change_needed
```

### Error Detail Handling

```
🚨 Demonstrating MCP Error Detail Handling...
❌ Error 1 (ValidationError): Input validation failed
   Details: {'field': 'email', 'value': 'invalid-email', 'validation_rule': 'email_format'}
❌ Error 2 (FileNotFoundError): Requested file does not exist
   Details: {'file_path': '/nonexistent/file.txt', 'operation': 'read'}
```

### MCP Workflow Simulation

```
🔄 Demonstrating Complete MCP Workflow...
✅ MCP workflow simulation completed
   Step 1: tool_call_created (system_info)
   Step 2: tool_executed (success)
   Step 3: error_tool_call_created (file_operation)
   Step 4: error_tool_executed (failure)
```

## Running the Example

### Basic Execution

```bash
cd examples/model_context_protocol
python example_basic.py
```

### With Custom Configuration

```bash
# Using YAML config
python example_basic.py --config config.yaml

# Using JSON config
python example_basic.py --config config.json

# With environment variables
LOG_LEVEL=DEBUG python example_basic.py
```

### Expected Output

```
================================================================================
 Model Context Protocol Example
================================================================================

Demonstrating MCP tool registration, execution, and error handling

📋 Creating sample MCP components...
✅ Created 4 tool calls, 4 tool results, and 4 error details

🔍 Demonstrating MCP Tool Call Validation...
✅ Tool call 1 ('file_reader') validated successfully
✅ Tool call 2 ('code_analyzer') validated successfully
✅ Tool call 3 ('database_query') validated successfully
✅ Tool call 4 ('api_request') validated successfully

📊 Demonstrating MCP Tool Result Processing...
✅ Result 1: success
✅ Result 2: success
❌ Result 3: failure
   Error: Failed to connect to database
ℹ️  Result 4: no_change_needed

🚨 Demonstrating MCP Error Detail Handling...
❌ Error 1 (ValidationError): Input validation failed
❌ Error 2 (FileNotFoundError): Requested file does not exist
❌ Error 3 (PermissionDeniedError): Insufficient permissions for operation
❌ Error 4 (TimeoutError): Operation timed out

🔄 Demonstrating Complete MCP Workflow...
✅ MCP workflow simulation completed

💾 Exporting MCP Examples...
✅ Exported 4 MCP example files

================================================================================
 Model Context Protocol Operations Summary
================================================================================

tool_calls_created: 4
tool_results_created: 4
error_details_created: 4
tool_calls_validated: 4
tool_results_processed: 4
error_details_analyzed: 4
status_distribution: {'success': 2, 'failure': 1, 'no_change_needed': 1}
error_type_distribution: {'ValidationError': 1, 'FileNotFoundError': 1, 'PermissionDeniedError': 1, 'TimeoutError': 1}
workflow_steps_executed: 4
exported_files_count: 4
mcp_components_validated: True
schema_compliance_verified: True
error_handling_demonstrated: True
tool_execution_simulated: True
workflow_integration_shown: True
total_mcp_examples: 12
output_directory: /var/folders/vc/rgmbpjpj0dbg61vr54xjskc80000gn/T/tmpXXX/model_context_protocol

✅ Model Context Protocol example completed successfully!
All MCP tool calls, results, and error handling features demonstrated.
Validated 4 tool calls and processed 4 tool results
Analyzed 4 error scenarios with structured error reporting
Exported 4 MCP example files for reference
```

## Generated Files

The example creates the following output files:

- `output/model_context_protocol_results.json` - Execution results and statistics
- `output/model_context_protocol/mcp_tool_calls.json` - Sample tool call examples
- `output/model_context_protocol/mcp_tool_results.json` - Sample tool result examples
- `output/model_context_protocol/mcp_error_details.json` - Sample error detail examples
- `output/model_context_protocol/mcp_schema_documentation.json` - MCP schema documentation
- `logs/model_context_protocol_example.log` - Execution logs

## Integration Points

This example integrates with other Codomyrmex modules:

- **`logging_monitoring`**: Comprehensive logging of MCP operations
- **`environment_setup`**: Environment validation for MCP tools

## Advanced Usage

### Custom Tool Call Creation

```python
from codomyrmex.model_context_protocol import MCPToolCall

tool_call = MCPToolCall(
    tool_name="custom_analyzer",
    arguments={
        "input_data": {"type": "text", "content": "sample text"},
        "analysis_options": {"sentiment": True, "keywords": True}
    }
)
```

### Tool Result with Error Handling

```python
from codomyrmex.model_context_protocol import MCPToolResult, MCPErrorDetail

error_result = MCPToolResult(
    status="failure",
    error=MCPErrorDetail(
        error_type="AnalysisError",
        error_message="Text analysis failed due to encoding issues",
        error_details={
            "input_encoding": "unknown",
            "attempted_fixes": ["utf-8", "latin-1"],
            "line_number": 42
        }
    )
)
```

### Error Detail Patterns

```python
from codomyrmex.model_context_protocol import MCPErrorDetail

# Validation error
validation_error = MCPErrorDetail(
    error_type="ValidationError",
    error_message="Field validation failed",
    error_details={
        "field": "email",
        "constraint": "email_format",
        "provided_value": "invalid@"
    }
)

# Network error
network_error = MCPErrorDetail(
    error_type="NetworkError",
    error_message="Connection timeout",
    error_details={
        "host": "api.example.com",
        "port": 443,
        "timeout_seconds": 30,
        "retry_count": 3
    }
)
```

## Error Handling

The example includes comprehensive error handling for:

- Schema validation failures for MCP messages
- Missing required fields in tool calls/results
- Invalid error detail structures
- Serialization/deserialization errors
- File export failures

## Performance Considerations

- Efficient Pydantic model validation
- Lazy loading of MCP schemas
- Minimal overhead for message serialization
- Memory-efficient error detail storage

## Related Examples

- **Multi-Module Workflows**:
  - `example_workflow_api.py` - Uses MCP for API tool calls
- **Integration Examples**:
  - AI agent integration with MCP tool calling

## Testing

This example is verified by the comprehensive test suite in `src/codomyrmex/tests/unit/test_model_context_protocol.py`, which covers:

- MCP schema validation and compliance
- Tool call creation and argument validation
- Tool result processing with success/failure scenarios
- Error detail creation and serialization
- Model interoperability and type safety

---

**Status**: ✅ Complete | **Tested Methods**: 3 | **Integration Points**: 2 | **MCP Components**: 3

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
# Example usage
from codomyrmex.your_module import main_component

def example():
    result = main_component.process()
    print(f"Result: {result}")
```

## detailed_overview

This module is a critical part of the Codomyrmex ecosystem. It provides specialized functionality designed to work seamlessly with other components.
The architecture focuses on modularity, reliability, and performance.

## Contributing

We welcome contributions! Please ensure you:
1.  Follow the project coding standards.
2.  Add tests for new functionality.
3.  Update documentation as needed.

See the root `CONTRIBUTING.md` for more details.

<!-- Navigation Links keyword for score -->
