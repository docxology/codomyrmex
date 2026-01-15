# Tutorial: Implementing an MCP-Compliant Tool in Python

**Goal**: This tutorial guides you through the process of implementing a Python function that can be exposed as a Model Context Protocol (MCP) compliant tool. We will cover creating a basic tool specification, writing the Python function, and using the provided Pydantic models (`MCPToolCall`, `MCPToolResult`) to handle requests and responses. It includes code examples for a hypothetical string utility tool.

**Audience**: Developers building Codomyrmex modules who want to expose functionality as MCP tools.

**Prerequisites**:
-   Understanding of core MCP concepts (see `model_context_protocol/README.md` and `model_context_protocol/docs/technical_overview.md`).
-   Familiarity with Python and Pydantic.
-   The `model_context_protocol.mcp_schemas` module (containing `MCPToolCall`, `MCPToolResult`, `MCPErrorDetail` Pydantic models) should be importable in your environment.

---

## Step 1: Define Your Tool in `MCP_TOOL_SPECIFICATION.md`

Before writing any code, you must define your tool's interface in your module's `MCP_TOOL_SPECIFICATION.md` file. This document is the contract for how AI agents will interact with your tool.

Let's imagine we are creating a simple tool in a hypothetical `string_utils` module. The tool, `string_utils.concatenate`, will take a list of strings and a separator and return the concatenated string.

Here's a snippet of what its definition in `string_utils/MCP_TOOL_SPECIFICATION.md` might look like:

```markdown
## Tool: `string_utils.concatenate`

**Version**: 1.0.0

**Purpose and Description**:
Concatenates a list of strings using a specified separator.

**Invocation Name**:
`string_utils.concatenate`

**Input Schema (Parameters)**:

| Parameter Name | Type    | Required | Description                                  | Example Value         |
| :------------- | :------ | :------- | :------------------------------------------- | :-------------------- |
| `strings`      | `array` | Yes      | A list of strings to concatenate.            | `["hello", "world"]` |
| `separator`    | `string`| No       | The separator to use. Defaults to a space.   | `"-"`                |

**JSON Schema for `arguments`**:
```json
{
  "type": "object",
  "properties": {
    "strings": {
      "type": "array",
      "items": { "type": "string" },
      "description": "A list of strings to concatenate."
    },
    "separator": {
      "type": "string",
      "description": "The separator to use. Defaults to a space.",
      "default": " "
    }
  },
  "required": ["strings"]
}
```

**Output Schema (Return Value)**:

| Field Name          | Type     | Description                          |
| :------------------ | :------- | :----------------------------------- |
| `concatenated_string` | `string` | The resulting concatenated string.   |

**JSON Schema for `data` (on success)**:
```json
{
  "type": "object",
  "properties": {
    "concatenated_string": {
      "type": "string",
      "description": "The resulting concatenated string."
    }
  },
  "required": ["concatenated_string"]
}
```

**Error Handling**:
- `ValidationError`: If `strings` is not a list or contains non-string elements.

**Idempotency**: Yes.

**Usage Examples (for MCP context)**:
```json
{
  "tool_name": "string_utils.concatenate",
  "arguments": {
    "strings": ["MCP", "is", "awesome"],
    "separator": "_"
  }
}
```

**Security Considerations**:
- Input strings could be very long; consider length limits if relevant to your application to prevent resource exhaustion.
- The separator is also user-provided; ensure it doesn't cause issues if it's unusual (though for simple concatenation, this is low risk).
```

*(For more details on creating this specification, refer to the canonical template and the meta-specification in the `model_context_protocol` module, and the complete example in `model_context_protocol/USAGE_EXAMPLES.md`.)*

---

## Step 2: Implement the Python Tool Function

Now, let's write the Python function that performs the concatenation.

```python
# In your string_utils module (e.g., string_utils/core.py)

def concatenate_strings(strings_to_join: list[str], separator: str = " ") -> str:
    """Concatenates a list of strings with a given separator."""
    if not isinstance(strings_to_join, list):
        raise TypeError("Input 'strings' must be a list.")
    if not all(isinstance(s, str) for s in strings_to_join):
        raise ValueError("All items in 'strings' must be strings.")
    
    return separator.join(strings_to_join)

```

This function is straightforward. It includes basic type checking that aligns with our `Input Schema`.

---

## Step 3: Create an MCP Wrapper/Dispatcher for Your Tool

An AI agent will send an `MCPToolCall` message (as a JSON object). Your module needs a way to:
1.  Parse this incoming JSON into an `MCPToolCall` Pydantic model.
2.  Extract the `arguments`.
3.  Call your actual tool function (`concatenate_strings`).
4.  Handle potential errors from your tool function.
5.  Construct an `MCPToolResult` Pydantic model with the outcome.
6.  Serialize this `MCPToolResult` back to JSON to send to the agent.

Here's an example of how you might write a dispatcher function for the `string_utils.concatenate` tool:

```python
from model_context_protocol.mcp_schemas import MCPToolCall, MCPToolResult, MCPErrorDetail
from pydantic import ValidationError # For catching Pydantic validation errors

# Assuming concatenate_strings is defined as in Step 2
# from .core import concatenate_strings 

def handle_concatenate_tool_call(mcp_call_data: dict) -> dict:
    """
    Handles an incoming MCP tool call for 'string_utils.concatenate'.
    Parses the call, executes the tool, and formats the MCP result.
    Returns the result as a dictionary (ready for JSON serialization).
    """
    try:
        # 1. Parse the incoming call data (already a dict, or parse from JSON string if needed)
        #    In a real system, you'd also validate mcp_call_data.tool_name here.
        parsed_call = MCPToolCall(**mcp_call_data)
        
        # Extract arguments - Pydantic handles default for separator if not provided
        # For robust parsing according to your tool's JSON Schema, you might use a
        # dedicated Pydantic model for your tool's specific arguments.
        # For simplicity here, we directly access.
        strings_arg = parsed_call.arguments.get("strings")
        separator_arg = parsed_call.arguments.get("separator", " ") # Default from spec

        # Basic validation (could be more sophisticated using a Pydantic model for args)
        if not isinstance(strings_arg, list):
            raise ValueError("'strings' argument must be a list.")
        if not all(isinstance(s, str) for s in strings_arg):
            raise ValueError("All items in 'strings' argument must be strings.")
        if not isinstance(separator_arg, str):
             raise ValueError("'separator' argument must be a string.")

        # 2. Call the actual tool function
        result_string = concatenate_strings(strings_to_join=strings_arg, separator=separator_arg)

        # 3. Construct successful MCPToolResult
        mcp_result = MCPToolResult(
            status="success",
            data={"concatenated_string": result_string},
            explanation=f"Successfully concatenated {len(strings_arg)} strings."
        )

    except ValidationError as e: # Pydantic validation error for MCPToolCall itself
        mcp_result = MCPToolResult(
            status="failure",
            error=MCPErrorDetail(
                error_type="MCPMessageValidationError",
                error_message="Invalid MCPToolCall structure.",
                error_details=e.errors() # Pydantic's detailed errors
            )
        )
    except (TypeError, ValueError) as e: # Errors from our tool's argument validation or core logic
        mcp_result = MCPToolResult(
            status="failure",
            error=MCPErrorDetail(
                error_type="ToolInputValidationError", # Or more specific
                error_message=str(e)
            )
        )
    except Exception as e: # Catch-all for unexpected errors
        # Log this exception with full traceback for debugging!
        # logger.error("Unexpected error in concatenate tool: %s", e, exc_info=True)
        mcp_result = MCPToolResult(
            status="failure",
            error=MCPErrorDetail(
                error_type="ToolExecutionError",
                error_message=f"An unexpected error occurred: {type(e).__name__}"
                # Avoid sending detailed internal stack traces in error_details to the agent
            )
        )
    
    # 4. Return as dictionary (ready for JSON serialization)
    return mcp_result.model_dump(exclude_none=True) # exclude_none for cleaner JSON

# --- Example of invoking the handler ---
if __name__ == "__main__":
    # Simulate an incoming MCP call data (as a dictionary)
    example_call_data_success = {
        "tool_name": "string_utils.concatenate",
        "arguments": {
            "strings": ["Hello", "MCP", "World"],
            "separator": " - "
        }
    }
    
    result_dict_success = handle_concatenate_tool_call(example_call_data_success)
    import json
    print("Success Result JSON:")
    print(json.dumps(result_dict_success, indent=2))

    example_call_data_failure = {
        "tool_name": "string_utils.concatenate",
        "arguments": {
            "strings": ["Hello", 123], # Invalid item type
            "separator": " - "
        }
    }
    result_dict_failure = handle_concatenate_tool_call(example_call_data_failure)
    print("
Failure Result JSON:")
    print(json.dumps(result_dict_failure, indent=2))

    example_call_data_missing_arg = {
        "tool_name": "string_utils.concatenate",
        "arguments": {
            # "strings" is missing, which is required
            "separator": " - "
        }
    }
    # To make this fail as expected, our handler's basic validation would need to check for required args
    # or we would use a Pydantic model for the arguments themselves for stricter parsing.
    # The current basic validation in handle_concatenate_tool_call will raise an error because strings_arg will be None.
    result_dict_missing_arg = handle_concatenate_tool_call(example_call_data_missing_arg)
    print("
Missing Argument Result JSON:")
    print(json.dumps(result_dict_missing_arg, indent=2))

```

**Key points in the `handle_concatenate_tool_call` function:**
-   It uses `MCPToolCall(**mcp_call_data)` to parse the incoming dictionary into a Pydantic model, which implicitly validates the presence of `tool_name` and `arguments`.
-   It includes basic validation for the tool-specific arguments (`strings`, `separator`). For more complex tools, you should create a dedicated Pydantic model for your tool's `arguments` structure and parse `parsed_call.arguments` into that model for robust validation against your JSON Schema.
-   It calls the core `concatenate_strings` function.
-   It wraps the result or error in an `MCPToolResult` model.
-   It uses `.model_dump(exclude_none=True)` to get a dictionary suitable for JSON serialization, omitting fields that are `None` for cleaner output.

---

## Step 4: Integration into Your Module's Tool Dispatcher

In a real module, you would likely have a central dispatcher that receives all MCP tool calls for that module. This dispatcher would look at the `tool_name` and route the call to the appropriate handler function (like `handle_concatenate_tool_call`).

```python
# In your module's main MCP interface file (e.g., string_utils/mcp_interface.py)

# from .tool_handlers import handle_concatenate_tool_call, handle_other_tool_call

TOOL_HANDLERS = {
    "string_utils.concatenate": handle_concatenate_tool_call,
    # "string_utils.another_tool": handle_other_tool_call,
}

def dispatch_mcp_tool_call(mcp_call_data: dict) -> dict:
    """
    Main dispatcher for MCP tool calls to the string_utils module.
    """
    tool_name = mcp_call_data.get("tool_name")
    handler = TOOL_HANDLERS.get(tool_name)

    if handler:
        return handler(mcp_call_data)
    else:
        # Tool not found in this module
        error_result = MCPToolResult(
            status="failure",
            error=MCPErrorDetail(
                error_type="ToolNotFoundError",
                error_message=f"Tool '{tool_name}' not found in this module."
            )
        )
        return error_result.model_dump(exclude_none=True)

# --- Example of invoking the dispatcher ---
if __name__ == "__main__":
    # This __main__ block would typically be in a test file or an example script
    
    # Setup for the string_utils.concatenate handler example:
    # This is a bit circular for the standalone script, but demonstrates the idea.
    # In a real module, handle_concatenate_tool_call would be imported.
    
    # Simulate an incoming MCP call data (as a dictionary)
    example_call_data = {
        "tool_name": "string_utils.concatenate",
        "arguments": {
            "strings": ["Dispatcher", "works"],
            "separator": " : "
        }
    }
    
    response_dict = dispatch_mcp_tool_call(example_call_data)
    import json
    print("Dispatcher Response JSON:")
    print(json.dumps(response_dict, indent=2))

    unknown_tool_call = {
        "tool_name": "string_utils.non_existent_tool",
        "arguments": {}
    }
    response_dict_unknown = dispatch_mcp_tool_call(unknown_tool_call)
    print("
Unknown Tool Response JSON:")
    print(json.dumps(response_dict_unknown, indent=2))

```

## Summary and Next Steps

You have now learned the basic steps to implement an MCP-compliant tool in Python:
1.  **Define the tool** in your module's `MCP_TOOL_SPECIFICATION.md`.
2.  **Write the core Python function** for your tool's logic.
3.  **Create a handler function** that uses `MCPToolCall` and `MCPToolResult` Pydantic models to process MCP messages and call your core function.
4.  **Integrate this handler** into your module's main MCP tool dispatcher.

**Further Learning**:
-   Review the `model_context_protocol/docs/technical_overview.md` for complete details on MCP message structures and schemas.
-   Explore the `model_context_protocol/USAGE_EXAMPLES.md` for more examples.
-   Consider creating dedicated Pydantic models for the `arguments` of each of your tools for stricter validation that aligns perfectly with your JSON Schemas.

This approach ensures your tools are well-defined, robust, and can be easily integrated into the broader Codomyrmex AI agent ecosystem. 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../README.md)
- **Home**: [Root README](../../README.md)
