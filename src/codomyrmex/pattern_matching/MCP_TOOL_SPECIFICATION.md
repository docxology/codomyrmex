# Pattern Matching - MCP Tool Specification

This document outlines the specification for tools within the Pattern Matching module that are intended to be integrated with the Model Context Protocol (MCP). These tools leverage the `cased/kit` toolkit for various code analysis and search functionalities.

## General Considerations

- **Dependencies**: Tools rely on the `cased/kit` library and potentially pre-built indexes or embeddings for some functionalities (e.g., semantic search).
- **Target Scope**: Searches can often be scoped to specific paths or the entire project.
- **API Keys**: Some advanced features like semantic search might require API keys (e.g., `OPENAI_API_KEY`) configured in the environment for `cased/kit`.

---

## Tool: `search_text_pattern`

### 1. Tool Purpose and Description

Searches for literal text strings or regular expression patterns within the codebase. Returns matching lines with context.

### 2. Invocation Name

`search_text_pattern`

### 3. Input Schema (Parameters)

| Parameter Name    | Type          | Required | Description                                                                                             | Example Value                                     |
| :---------------- | :------------ | :------- | :------------------------------------------------------------------------------------------------------ | :------------------------------------------------ |
| `query`           | `string`      | Yes      | The literal string or regular expression pattern to search for.                                         | `"TODO"` or `"def my_function"`                    |
| `is_regex`        | `boolean`     | No       | Whether the `query` is a regular expression. Default: `false`.                                          | `true`                                            |
| `target_paths`    | `array[string]`| No       | List of file or directory paths to search within. Default: searches entire project.                     | `["src/module_a/", "utils/helpers.py"]`          |
| `case_sensitive`  | `boolean`     | No       | Whether the search should be case-sensitive. Default: `false`.                                          | `true`                                            |
| `context_lines`   | `integer`     | No       | Number of lines of context to show before and after the matching line. Default: `2`. Max: `10`.            | `3`                                               |
| `file_extensions` | `array[string]`| No       | List of file extensions to include in the search (e.g., `[".py", ".js"]`). Default: searches common code file types. | `[".py", ".md"]`                               |

### 4. Output Schema (Return Value)

| Field Name      | Type          | Description                                                              | Example Value                                                                    |
| :-------------- | :------------ | :----------------------------------------------------------------------- | :------------------------------------------------------------------------------- |
| `status`        | `string`      | "success", "no_matches_found", "error".                                  | `"success"`                                                                      |
| `matches`       | `array[object]`| List of found matches. Empty if no matches or on error.                  | `[{"file_path": "src/main.py", "line_number": 42, "matched_line": "...", "context": [...]}]` |
| `match_count`   | `integer`     | Total number of matches found.                                           | `5`                                                                              |
| `error_message` | `string`      | Error description if `status` is "error".                                | `"Invalid regular expression."`                                                    |

**Structure for `matches` objects:**

| Field Name    | Type          | Description                                                        |
| :------------ | :------------ | :----------------------------------------------------------------- |
| `file_path`   | `string`      | Path to the file containing the match.                             |
| `line_number` | `integer`     | Line number of the matched line.                                   |
| `matched_line`| `string`      | The content of the line that matched the query.                    |
| `context`     | `array[string]`| Surrounding lines of context (number based on `context_lines`).    |
| `match_details`| `object`      | For regex, details like captured groups. Optional.                 |

### 5. Error Handling

- Invalid regular expressions or inaccessible paths will result in an "error" status and a message in `error_message`.

### 6. Idempotency

- **Idempotent**: Yes, assuming the codebase state and input parameters do not change.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "search_text_pattern",
  "arguments": {
    "query": "api_key",
    "target_paths": ["src/"],
    "case_sensitive": false,
    "file_extensions": [".py"]
  }
}
```

### 8. Security Considerations

- `target_paths` should be validated to stay within the project scope.
- Complex regular expressions in `query` could lead to performance issues (ReDoS). Input validation or timeout for regex execution might be needed.

---

## Tool: `find_symbol_occurrences`

### 1. Tool Purpose and Description

Finds occurrences (definitions and references) of a specified symbol (e.g., function, class, variable) within the codebase.

### 2. Invocation Name

`find_symbol_occurrences`

### 3. Input Schema (Parameters)

| Parameter Name   | Type          | Required | Description                                                                                   | Example Value                                      |
| :--------------- | :------------ | :------- | :-------------------------------------------------------------------------------------------- | :------------------------------------------------- |
| `symbol_name`    | `string`      | Yes      | The name of the symbol to find (can be fully qualified or partial, depending on implementation). | `"my_module.my_function"` or `"MyClass"`           |
| `target_paths`   | `array[string]`| No       | List of file or directory paths to search within. Default: searches entire project.       | `["src/module_b/"]`                                |
| `find_definitions`| `boolean`     | No       | Whether to find definitions of the symbol. Default: `true`.                                 | `true`                                             |
| `find_references`| `boolean`     | No       | Whether to find references (usages) of the symbol. Default: `true`.                           | `true`                                             |
| `language`       | `string`      | No       | Specify language to improve accuracy (e.g., "python").                                      | `"python"`                                         |

### 4. Output Schema (Return Value)

| Field Name      | Type          | Description                                                                | Example Value                                                                          |
| :-------------- | :------------ | :------------------------------------------------------------------------- | :------------------------------------------------------------------------------------- |
| `status`        | `string`      | "success", "no_occurrences_found", "error", "indexing_required".           | `"success"`                                                                            |
| `occurrences`   | `array[object]`| List of found symbol occurrences.                                          | `[{"file_path": "src/utils.py", "line_number": 10, "type": "definition", "snippet": "..."}]` |
| `occurrence_count`| `integer`     | Total number of occurrences found.                                         | `3`                                                                                    |
| `error_message` | `string`      | Error description if `status` is "error".                                  | `"Symbol parsing failed for some files."`                                                |

**Structure for `occurrences` objects:**

| Field Name    | Type     | Description                                                       |
| :------------ | :------- | :---------------------------------------------------------------- |
| `file_path`   | `string` | Path to the file containing the occurrence.                       |
| `line_number` | `integer`| Line number where the symbol occurs.                                |
| `column_number`| `integer`| Column number where the symbol occurs.                              |
| `type`        | `string` | Type of occurrence (e.g., "definition", "reference", "import").   |
| `symbol_fqn`  | `string` | Fully qualified name of the symbol found, if resolvable.          |
| `snippet`     | `string` | A small snippet of code showing the symbol in context.            |

### 5. Error Handling

- If symbol parsing or indexing is required and not complete, might return "indexing_required".
- Errors during parsing specific files might be logged, and results might be partial.

### 6. Idempotency

- **Idempotent**: Yes, assuming the codebase state and symbol indexes do not change.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "find_symbol_occurrences",
  "arguments": {
    "symbol_name": "get_user_data",
    "target_paths": ["src/api/"],
    "language": "python"
  }
}
```

### 8. Security Considerations

- `target_paths` validation is important.
- Relies on accurate parsing of code; malformed code might cause parser errors.

---

## Tool: `search_semantic_concept`

### 1. Tool Purpose and Description

Searches the codebase for code snippets that are semantically related to a given natural language concept or description. Requires pre-computed embeddings for the codebase.

### 2. Invocation Name

`search_semantic_concept`

### 3. Input Schema (Parameters)

| Parameter Name      | Type          | Required | Description                                                                                             | Example Value                                            |
| :------------------ | :------------ | :------- | :------------------------------------------------------------------------------------------------------ | :------------------------------------------------------- |
| `concept_description`| `string`      | Yes      | A natural language description of the code functionality or concept to search for.                      | `"Find all functions that handle user authentication and password hashing."` |
| `target_paths`      | `array[string]`| No       | List of file or directory paths to search within. Default: searches entire indexed project.             | `["src/auth/"]`                                          |
| `top_n_results`     | `integer`     | No       | The maximum number of most relevant results to return. Default: `5`. Max: `20`.                         | `10`                                                     |
| `language`          | `string`      | No       | Specify language to scope search or use language-specific models (e.g., "python").                    | `"python"`                                               |

### 4. Output Schema (Return Value)

| Field Name       | Type          | Description                                                                   | Example Value                                                                         |
| :--------------- | :------------ | :---------------------------------------------------------------------------- | :------------------------------------------------------------------------------------ |
| `status`         | `string`      | "success", "no_results_found", "error", "embeddings_not_ready".             | `"success"`                                                                           |
| `results`        | `array[object]`| List of semantically relevant code snippets.                                  | `[{"file_path": "auth/service.py", "score": 0.85, "snippet_id": "func_xyz", "text": "..."}]` |
| `result_count`   | `integer`     | Number of results returned.                                                   | `5`                                                                                   |
| `error_message`  | `string`      | Error description if `status` is "error" or embeddings are not available.     | `"Code embeddings are not available for this project or specified paths."`            |

**Structure for `results` objects:**

| Field Name    | Type     | Description                                                                        |
| :------------ | :------- | :--------------------------------------------------------------------------------- |
| `file_path`   | `string` | Path to the file containing the relevant snippet.                                  |
| `start_line`  | `integer`| Starting line number of the snippet.                                               |
| `end_line`    | `integer`| Ending line number of the snippet.                                                 |
| `text`        | `string` | The actual code snippet text.                                                      |
| `score`       | `float`  | A relevance score (e.g., cosine similarity) between the query and the snippet.   |
| `snippet_id`  | `string` | An identifier for the snippet, if available from the underlying search mechanism.  |

### 5. Error Handling

- If codebase embeddings are not generated or accessible, an error status like "embeddings_not_ready" will be returned.
- API key errors for embedding models (if used by `cased/kit`) should be handled.

### 6. Idempotency

- **Idempotent**: Yes, if the codebase, its embeddings, and the query `concept_description` remain the same.

### 7. Usage Examples (for MCP context)

```json
{
  "tool_name": "search_semantic_concept",
  "arguments": {
    "concept_description": "Code that reads data from a CSV file and processes it.",
    "top_n_results": 3,
    "language": "python"
  }
}
```

### 8. Security Considerations

- `target_paths` validation.
- The quality and security of the semantic search depend on the `cased/kit` implementation and the underlying embedding models. Ensure API keys are handled securely if `cased/kit` calls external services.

---

## Tool: `[Another Tool Name]`

(Repeat the above structure for each tool provided by this module that interfaces with MCP.) 
## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
