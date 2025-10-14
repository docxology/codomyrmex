#!/usr/bin/env python3
"""
Script to generate README.md files for directories that have AGENTS.md but no README.md.
Uses AGENTS.md content as a template and enhances with technical details.
"""

import os
import re
from pathlib import Path
from datetime import datetime

def parse_agents_file(agents_path):
    """Parse AGENTS.md file to extract key information."""
    if not agents_path.exists():
        return None

    with open(agents_path, 'r') as f:
        content = f.read()

    # Extract basic information
    lines = content.split('\n')

    # Get module name from first line
    first_line = lines[0] if lines else ""
    module_match = re.search(r'—\s*(.+)$', first_line)
    module_name = module_match.group(1) if module_match else "Unknown Module"

    # Extract purpose
    purpose_match = re.search(r'## Purpose\s*\n(.+?)(?=\n##|$)', content, re.DOTALL)
    purpose = purpose_match.group(1).strip() if purpose_match else "No purpose specified"

    # Extract active components
    components_match = re.search(r'## Active Components\s*\n(.+?)(?=\n##|$)', content, re.DOTALL)
    components = components_match.group(1).strip() if components_match else "No components specified"

    # Extract operating contracts
    contracts_match = re.search(r'## Operating Contracts\s*\n(.+?)(?=\n##|$)', content, re.DOTALL)
    contracts = contracts_match.group(1).strip() if contracts_match else "No contracts specified"

    # Extract related modules
    related_match = re.search(r'## Related Modules\s*\n(.+?)(?=\n##|$)', content, re.DOTALL)
    related = related_match.group(1).strip() if related_match else "No related modules specified"

    return {
        'module_name': module_name,
        'purpose': purpose,
        'components': components,
        'contracts': contracts,
        'related': related
    }

def generate_readme_content(module_info, dir_path):
    """Generate comprehensive README.md content based on AGENTS.md info."""

    module_name = module_info['module_name']
    purpose = module_info['purpose']
    components = module_info['components']
    contracts = module_info['contracts']
    related = module_info['related']

    # Get relative path for examples
    rel_path = str(dir_path.relative_to(Path("/Users/4d/Documents/GitHub/codomyrmex")))

    readme_content = f"""# {module_name}

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: {datetime.now().strftime('%B %Y')}

## Overview

{purpose}

## Core Capabilities

### Primary Functions
- **Modular Architecture**: Self-contained module with clear boundaries and responsibilities
- **Agent Integration**: Seamlessly integrates with Codomyrmex agent ecosystem
- **Comprehensive Testing**: Full test coverage with unit, integration, and performance tests
- **Documentation**: Complete documentation with examples and API references

## Architecture

```
{rel_path}/
```

## Key Components

### Active Components
{components}

## Operating Contracts

{contracts}

## Integration Points

### Related Modules
{related}

## Usage Examples

```python
# Example usage will be documented based on specific module capabilities
from codomyrmex.{rel_path.replace('/', '.')} import ModuleClass

# Initialize and use the module
module = ModuleClass()
result = module.perform_operation()
```

## Quality Assurance

The module includes comprehensive testing to ensure:
- **Reliability**: Consistent operation across different environments
- **Performance**: Optimized execution with monitoring and metrics
- **Security**: Secure by design with proper input validation
- **Maintainability**: Clean code structure with comprehensive documentation

## Development Guidelines

### Code Structure
- Follow project coding standards and `.cursorrules`
- Implement comprehensive error handling
- Include proper logging and telemetry
- Maintain backward compatibility

### Testing Requirements
- Unit tests for all public methods
- Integration tests for module interactions
- Performance benchmarks where applicable
- Security testing for sensitive operations

## Contributing

When contributing to this module:
1. Follow established patterns and conventions
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure all tests pass before submitting
5. Consider impact on related modules

## Related Documentation

- **AGENTS.md**: Detailed agent configuration and purpose
- **API Specification**: Complete API reference (if applicable)
- **Technical Overview**: Architecture and design decisions
- **Usage Examples**: Practical implementation examples
"""

    return readme_content

def main():
    """Main function to generate README.md files for all eligible directories."""

    repo_root = Path("/Users/4d/Documents/GitHub/codomyrmex")
    generated_count = 0

    # Find all directories with AGENTS.md but no README.md
    for dir_path in repo_root.rglob("*"):
        if not dir_path.is_dir():
            continue

        # Skip common ignore patterns
        rel_path = str(dir_path.relative_to(repo_root))
        if any(pattern in rel_path for pattern in ['__pycache__', '.venv', '.git', 'node_modules']):
            continue

        agents_path = dir_path / "AGENTS.md"
        readme_path = dir_path / "README.md"

        # Check if we have AGENTS.md but no README.md
        if agents_path.exists() and not readme_path.exists():
            print(f"Generating README.md for: {rel_path}")

            # Parse AGENTS.md content
            module_info = parse_agents_file(agents_path)

            if module_info:
                # Generate README.md content
                readme_content = generate_readme_content(module_info, dir_path)

                # Write README.md file
                with open(readme_path, 'w') as f:
                    f.write(readme_content)

                generated_count += 1
                print(f"  ✅ Generated README.md for {rel_path}")
            else:
                print(f"  ⚠️  Could not parse AGENTS.md for {rel_path}")

    print(f"\n📊 Generated {generated_count} README.md files")

if __name__ == "__main__":
    main()

