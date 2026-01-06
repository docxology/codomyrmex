# Codomyrmex Agents — src/codomyrmex/documentation

## Signposting
- **Parent**: [codomyrmex](../AGENTS.md)
- **Self**: [Documentation Agents](AGENTS.md)
- **Children**:
    - [docs](docs/AGENTS.md)
    - [scripts](scripts/AGENTS.md)
    - [src](src/AGENTS.md)
    - [static](static/AGENTS.md)
    - [tests](tests/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core Service Layer module providing documentation management, website generation, and quality assessment capabilities for the Codomyrmex platform. This module manages the project's documentation ecosystem, including Docusaurus-based website generation, documentation aggregation, and quality validation.

The documentation module serves as the knowledge management layer, ensuring consistent, accessible, and high-quality documentation across all platform components.

## Module Overview

### Key Capabilities
- **Documentation Website Generation**: Automated website building with Docusaurus
- **Documentation Aggregation**: Unified documentation collection from all modules
- **Quality Assessment**: Automated documentation quality validation
- **Consistency Checking**: Cross-documentation consistency validation
- **Version Validation**: Documentation version synchronization

### Key Features
- Docusaurus-based documentation website
- Multi-module documentation aggregation
- Documentation quality metrics and reporting
- Consistency validation across modules
- Automated documentation deployment

## Function Signatures

### Environment and Setup Functions

```python
def check_doc_environment() -> bool
```

Check if the documentation environment is properly configured.

**Returns:** `bool` - True if environment is ready for documentation work

```python
def install_dependencies(package_manager: str = "npm") -> bool
```

Install documentation website dependencies.

**Parameters:**
- `package_manager` (str): Package manager to use ("npm" or "yarn"). Defaults to "npm"

**Returns:** `bool` - True if dependencies installed successfully

### Development Server Functions

```python
def start_dev_server(package_manager: str = "npm") -> None
```

Start the documentation development server.

**Parameters:**
- `package_manager` (str): Package manager to use ("npm" or "yarn"). Defaults to "npm"

**Returns:** None - Starts development server (blocks until interrupted)

### Build and Deployment Functions

```python
def build_static_site(package_manager: str = "npm") -> bool
```

Build the documentation website for production.

**Parameters:**
- `package_manager` (str): Package manager to use ("npm" or "yarn"). Defaults to "npm"

**Returns:** `bool` - True if build completed successfully

```python
def serve_static_site(package_manager: str = "npm") -> None
```

Serve the built documentation website locally.

**Parameters:**
- `package_manager` (str): Package manager to use ("npm" or "yarn"). Defaults to "npm"

**Returns:** None - Starts local server (blocks until interrupted)

### Documentation Management Functions

```python
def aggregate_docs(source_root: str = None, dest_root: str = None) -> None
```

Aggregate module documentation into the Docusaurus docs/modules folder.

**Parameters:**
- `source_root` (str): Root directory to scan for documentation. If None, uses default
- `dest_root` (str): Destination directory for aggregated docs. If None, uses default

**Returns:** None - Copies documentation files to Docusaurus structure

```python
def validate_doc_versions() -> bool
```

Validate that documentation versions are consistent across modules.

**Returns:** `bool` - True if all documentation versions are consistent

### Assessment and Quality Functions

```python
def assess_site() -> dict[str, Any]
```

Assess the documentation website for completeness and quality.

**Returns:** `dict[str, Any]` - Assessment results including coverage, quality metrics, and issues

```python
def print_assessment_checklist() -> None
```

Print a checklist of documentation quality assessment items.

**Returns:** None - Prints checklist to console

```python
def generate_quality_report(project_path: Path) -> str
```

Generate a documentation quality report.

**Parameters:**
- `project_path` (Path): Path to the project root directory

**Returns:** `str` - Markdown-formatted quality report

## Data Structures

### DocumentationConsistencyChecker
```python
class DocumentationConsistencyChecker:
    def __init__(self, project_root: str = None)

    def check_file_exists(self, file_path: str) -> bool
    def check_required_files(self) -> list[str]
    def check_navigation_links(self) -> list[str]
    def check_cross_references(self) -> list[str]
    def generate_report(self) -> str
    def validate_all(self) -> bool
```

Documentation consistency validation and checking.

## Utility Functions

```python
def run_command_stream_output(command_parts: list[str], cwd: str = None) -> tuple[bool, str]
```

Run a command and stream its output in real-time.

**Parameters:**
- `command_parts` (list[str]): Command and arguments as list
- `cwd` (str): Working directory for command execution

**Returns:** `tuple[bool, str]` - (success: bool, combined_output: str)

```python
def command_exists(command: str) -> bool
```

Check if a command exists on the system PATH.

**Parameters:**
- `command` (str): Command name to check

**Returns:** `bool` - True if command is available

## Quality Assessment Functions

```python
def generate_quality_tests() -> str
```

Generate tests for documentation quality validation.

**Returns:** `str` - Generated test code for quality assessment

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `documentation_website.py` – Docusaurus website management and build functions
- `consistency_checker.py` – Documentation consistency validation
- `quality_assessment.py` – Documentation quality metrics and reporting

### Documentation Structure
- `docs/` – Docusaurus documentation content organized by module
- `src/` – Docusaurus website source code and components
- `static/` – Static assets for the documentation website

### Configuration Files
- `docusaurus.config.js` – Docusaurus site configuration
- `sidebars.js` – Documentation sidebar navigation structure
- `package.json` – Node.js dependencies and scripts

### Assessment and Validation
- `coverage_assessment.md` – Documentation coverage evaluation
- `bug_taxonomy.md` – Classification of documentation issues
- `scripts/` – Maintenance and validation scripts

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for documentation
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Python dependencies
- `package-lock.json` – Node.js dependency lock file
- `tests/` – Documentation validation tests

## Operating Contracts

### Universal Documentation Protocols

All documentation within the Codomyrmex platform must:

1. **Consistency** - Documentation remains synchronized with code changes
2. **Accessibility** - Documentation is findable and readable by intended audiences
3. **Accuracy** - Documentation reflects actual system behavior and capabilities
4. **Completeness** - All significant functionality is documented
5. **Maintainability** - Documentation structure supports ongoing updates

### Module-Specific Guidelines

#### Documentation Website
- Maintain consistent navigation structure across versions
- Ensure responsive design for different screen sizes
- Provide clear search functionality
- Include version selection for multi-version documentation

#### Documentation Aggregation
- Automatically collect documentation from all modules
- Maintain consistent file naming conventions
- Preserve module-specific documentation structure
- Handle documentation conflicts and overrides

#### Quality Assessment
- Define clear quality metrics and thresholds
- Provide actionable feedback for improvement
- Automate quality checks in CI/CD pipelines
- Track quality trends over time

#### Consistency Validation
- Check for broken internal links and references
- Validate consistent terminology usage
- Ensure consistent formatting across documents
- Verify version consistency across modules

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification (if applicable)
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations (if applicable)

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation
- **Source Root**: [src](../../README.md) - Source code documentation