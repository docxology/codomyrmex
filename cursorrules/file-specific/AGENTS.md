# Codomyrmex Agents — cursorrules/file-specific

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

This directory contains file-type specific coding conventions and standards for the Codomyrmex repository. These rules address formatting, structure, and content requirements for specific file types to ensure consistency across the codebase.

## File-Specific Rule Categories

### README.md Rules (`README.md.cursorrules`)
**Purpose**: Standards for README.md file formatting and content
**Key Functions**:
- `validate_readme_structure(content: str) -> ValidationResult`
- `check_readme_links(content: str) -> LinkValidation`
- `standardize_readme_sections(content: str) -> StandardizedContent`

**Standards**:
- Consistent section ordering and naming
- Required sections for each documentation level
- Proper link formatting and validation
- Clear content organization and hierarchy

**Required Sections**:
```markdown
# Title

**Version**: X.X.X | **Status**: Active | **Last Updated**: Month YYYY

## Overview
Brief description of the component/folder purpose.

## [Content Sections]
Component-specific content with Mermaid diagrams where applicable.

## Navigation
Links to related documentation and parent/child directories.
```

**Content Guidelines**:
- Use Mermaid diagrams for architecture visualization
- Include version and status information
- Provide clear navigation links
- Maintain consistent formatting across all README files

## Active Components
- `README.md` – Directory documentation
- `README.md.cursorrules` – README file formatting standards (function: validate_readme_format(filepath: str) -> ValidationResult)

## File Type Coverage

### Python Files (`.py`)
**Standards Applied**:
- PEP 8 compliance (enforced by general.cursorrules)
- Type hints for function parameters and return values
- Docstring format: Google/NumPy style
- Import organization: standard library, third-party, local

**Validation Functions**:
```python
def validate_python_file(filepath: str) -> ValidationResult:
    """Validate Python file against coding standards."""
    pass

def check_imports_organization(content: str) -> bool:
    """Check that imports are properly organized."""
    pass
```

### Markdown Files (`.md`)
**Standards Applied**:
- Consistent header hierarchy
- Proper link formatting
- Table alignment and formatting
- Code block language specification

**Validation Functions**:
```python
def validate_markdown_file(filepath: str) -> ValidationResult:
    """Validate Markdown file formatting."""
    pass

def check_table_formatting(content: str) -> bool:
    """Check table formatting consistency."""
    pass
```

### Configuration Files (`.json`, `.yaml`, `.env`)
**Standards Applied**:
- Consistent key naming conventions
- Proper commenting where supported
- Validation against schemas
- Environment variable naming (UPPER_CASE)

**Validation Functions**:
```python
def validate_config_file(filepath: str) -> ValidationResult:
    """Validate configuration file format and content."""
    pass

def check_environment_variables(content: str) -> bool:
    """Check environment variable naming conventions."""
    pass
```

### Shell Scripts (`.sh`)
**Standards Applied**:
- Bash strict mode (`set -euo pipefail`)
- Proper error handling
- Input validation
- Logging integration

**Validation Functions**:
```bash
validate_shell_script() {
    # Validate shell script standards
    local filepath="$1"
    # Implementation
}
```

## Operating Contracts

### File Type Standards
1. **Format Consistency** - Maintain consistent formatting within each file type
2. **Tool Integration** - Ensure standards work with automated tools (linters, formatters)
3. **Documentation Updates** - Update file-specific rules when new file types are introduced
4. **Validation Coverage** - Provide automated validation for all defined standards

### Rule Application
- File-specific rules override general rules for formatting and structure
- Module-specific rules may further customize file-type standards
- Rules must be enforceable through automated tools where possible
- Include clear examples and counter-examples for each standard

## Navigation Links
- **Parent Directory**: [cursorrules](../README.md) - Coding standards documentation
- **General Rules**: [general.cursorrules](../general.cursorrules) - Repository-wide standards
