#!/usr/bin/env python3
"""
Create missing documentation files that are referenced but don't exist.

Creates placeholder API_SPECIFICATION.md and MCP_TOOL_SPECIFICATION.md files
for modules that reference them but don't have them.
"""

import json
from pathlib import Path
import sys


API_SPEC_TEMPLATE = """# {module_name} - API Specification

## Introduction

This document provides the complete API specification for the `{module_name}` module.

## Module Overview

The `{module_name}` module provides [brief description of module purpose].

## Public API

### Main Functions

#### `function_name()`

**Description**: [Function description]

**Parameters**:
- `param1` (type): Description
- `param2` (type, optional): Description

**Returns**: Return type and description

**Example**:
```python
from codomyrmex.{module_name} import function_name

result = function_name(param1="value")
```

## Classes

### `ClassName`

**Description**: [Class description]

**Methods**:
- `method1()`: Description
- `method2(param)`: Description

## Constants

- `CONSTANT_NAME`: Description

## Exceptions

- `ModuleException`: Description

## Related Documentation

- [Module README](./README.md)
- [Usage Examples](./USAGE_EXAMPLES.md)
- [MCP Tool Specification](./MCP_TOOL_SPECIFICATION.md) (if applicable)

---

**Note**: This is a placeholder file. Please update it with the actual API specification for this module.
"""


MCP_TOOL_SPEC_TEMPLATE = """# {module_name} - MCP Tool Specification

## Overview

This document specifies the Model Context Protocol (MCP) tools provided by the `{module_name}` module.

## Available Tools

### `tool_name`

**Description**: [Tool description]

**Parameters**:
```json
{{
  "param1": {{
    "type": "string",
    "description": "Parameter description",
    "required": true
  }},
  "param2": {{
    "type": "integer",
    "description": "Parameter description",
    "required": false,
    "default": 0
  }}
}}
```

**Returns**: Return value description

**Example**:
```json
{{
  "tool": "tool_name",
  "parameters": {{
    "param1": "value",
    "param2": 42
  }}
}}
```

## Tool Registration

Tools are automatically registered when the module is imported:

```python
from codomyrmex.{module_name} import register_tools

register_tools()
```

## Related Documentation

- [Module README](./README.md)
- [API Specification](./API_SPECIFICATION.md)
- [Usage Examples](./USAGE_EXAMPLES.md)

---

**Note**: This is a placeholder file. Please update it with the actual MCP tool specifications for this module.
"""


def create_missing_doc_files():
    """Create missing documentation files."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    # Load audit data
    audit_data_path = script_dir / 'module_audit_data.json'
    if not audit_data_path.exists():
        print("Error: module_audit_data.json not found. Run module_docs_auditor.py first.")
        return 1
    
    with open(audit_data_path, 'r') as f:
        audit_data = json.load(f)
    
    missing_doc_files = audit_data['missing_doc_files']
    
    print(f"Creating missing documentation files...\n")
    
    created_count = 0
    
    for module_name, missing_files in missing_doc_files.items():
        module_path = repo_root / 'src' / 'codomyrmex' / module_name
        
        if not module_path.exists():
            print(f"⚠️  Module not found: {module_name}")
            continue
        
        for filename in missing_files:
            file_path = module_path / filename
            
            # Check if file already exists
            if file_path.exists():
                print(f"⏭️  Already exists: {file_path.relative_to(repo_root)}")
                continue
            
            # Choose template based on filename
            if filename == 'API_SPECIFICATION.md':
                content = API_SPEC_TEMPLATE.format(module_name=module_name)
            elif filename == 'MCP_TOOL_SPECIFICATION.md':
                content = MCP_TOOL_SPEC_TEMPLATE.format(module_name=module_name)
            else:
                print(f"⚠️  Unknown template for: {filename}")
                continue
            
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Created: {file_path.relative_to(repo_root)}")
            created_count += 1
    
    print(f"\n✅ Created {created_count} missing documentation files")
    return 0


if __name__ == '__main__':
    sys.exit(create_missing_doc_files())

