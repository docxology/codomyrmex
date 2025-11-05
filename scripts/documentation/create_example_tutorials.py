#!/usr/bin/env python3
"""
Create placeholder example_tutorial.md files for modules that reference them.

Creates a standard template that modules can customize with their own examples.
"""

import json
from pathlib import Path
import sys


EXAMPLE_TUTORIAL_TEMPLATE = """# Example Tutorial

This is a placeholder tutorial file for the {module_name} module.

## Overview

This tutorial demonstrates how to use the {module_name} module with practical examples.

## Prerequisites

- Basic understanding of Python
- Codomyrmex installed and configured
- Appropriate API keys/credentials (if required)

## Basic Usage

```python
from codomyrmex.{module_name} import main_function

# Example usage
result = main_function("example_input")
print(result)
```

## Advanced Examples

### Example 1: Basic Operation

```python
# Add module-specific examples here
```

### Example 2: Advanced Configuration

```python
# Add advanced usage examples here
```

## Integration with Other Modules

```python
# Show how this module integrates with others
```

## Next Steps

- Review the [API Specification](../API_SPECIFICATION.md) for complete API documentation
- Explore [Usage Examples](../USAGE_EXAMPLES.md) for more examples
- Check the [Technical Overview](../technical_overview.md) for architecture details

## Related Documentation

- [Module README](../README.md)
- [API Specification](../API_SPECIFICATION.md)
- [Usage Examples](../USAGE_EXAMPLES.md)
- [Technical Overview](../technical_overview.md)

---

**Note**: This is a template file. Please customize it with module-specific examples and use cases.
"""


def create_example_tutorials():
    """Create placeholder example_tutorial.md files."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    # Load audit data
    audit_data_path = script_dir / 'module_audit_data.json'
    if not audit_data_path.exists():
        print("Error: module_audit_data.json not found. Run module_docs_auditor.py first.")
        return 1
    
    with open(audit_data_path, 'r') as f:
        audit_data = json.load(f)
    
    example_tutorial_refs = audit_data['example_tutorial_refs']
    
    print(f"Creating {len(example_tutorial_refs)} example_tutorial.md files...\n")
    
    created_count = 0
    skipped_count = 0
    
    for ref in example_tutorial_refs:
        tutorial_path = Path(ref['resolved'])
        module_name = ref['module']
        
        # Check if file already exists
        if tutorial_path.exists():
            print(f"⏭️  Already exists: {tutorial_path.relative_to(repo_root)}")
            skipped_count += 1
            continue
        
        # Ensure tutorials directory exists
        tutorial_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create the template
        content = EXAMPLE_TUTORIAL_TEMPLATE.format(module_name=module_name)
        tutorial_path.write_text(content, encoding='utf-8')
        
        print(f"✅ Created: {tutorial_path.relative_to(repo_root)}")
        created_count += 1
    
    print(f"\n✅ Created {created_count} files, skipped {skipped_count} existing files")
    return 0


if __name__ == '__main__':
    sys.exit(create_example_tutorials())

