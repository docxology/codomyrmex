from pathlib import Path
from typing import Any, Optional
import logging
import re

from codomyrmex.logging_monitoring import get_logger



"""
Documentation Generator for Codomyrmex Projects

This module generates README.md and AGENTS.md files for projects and their
nested directories based on templates and project metadata.
"""


try:

    logger = get_logger(__name__)
except ImportError:

    logger = logging.getLogger(__name__)


class DocumentationGenerator:
    """Generates documentation files for projects and nested directories."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the documentation generator."""
        self.templates_dir = (
            templates_dir
            if templates_dir
            else Path(__file__).parent / "templates" / "doc_templates"
        )
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    def _load_template(self, template_name: str) -> Optional[str]:
        """Load a template file."""
        template_path = self.templates_dir / template_name
        if template_path.exists():
            try:
                return template_path.read_text(encoding="utf-8")
            except Exception as e:
                logger.error(f"Failed to load template {template_name}: {e}")
                return None
        return None

    def _substitute_variables(self, content: str, variables: dict[str, Any]) -> str:
        """Substitute variables in template content using {{variable}} syntax."""
        result = content
        for key, value in variables.items():
            # Handle both {{variable}} and {{ variable }} patterns
            pattern = r"\{\{\s*" + re.escape(key) + r"\s*\}\}"
            result = re.sub(pattern, str(value), result)
        return result

    def _get_directory_purpose(self, dir_name: str, project_type: str) -> str:
        """Get a description of the directory's purpose based on its name and project type."""
        purpose_map = {
            "src": "Source code and implementation files",
            "config": "Configuration files and settings",
            "data": "Data files and datasets",
            "output": "Generated output files and artifacts",
            "reports": "Analysis reports and documentation",
            "tests": "Test files and test data",
            "docs": "Documentation files",
            "frontend": "Frontend application code",
            "backend": "Backend application code",
            "database": "Database schemas and migrations",
            "deploy": "Deployment configuration and scripts",
            "pipelines": "Data processing pipelines",
            "notebooks": "Jupyter notebooks and analysis scripts",
        }

        if dir_name in purpose_map:
            return purpose_map[dir_name]

        # Try partial match
        for key, value in purpose_map.items():
            if key in dir_name.lower():
                return value

        return f"Files and resources for {dir_name}"

    def _get_directory_agent_purpose(self, dir_name: str, project_name: str) -> str:
        """Get the agent purpose description for a directory."""
        dir_display = dir_name.replace("_", " ").replace("/", " ").strip()
        return f"Agent surface for {dir_display} components in {project_name}"

    def generate_root_readme(
        self,
        project_path: Path,
        project_name: str,
        project_type: str,
        description: str,
        version: str,
        author: str,
        created_at: str,
        template: Optional[str] = None,
    ) -> bool:
        """Generate README.md for the project root."""
        # Try to load custom template, otherwise use default
        template_content = None
        if template:
            template_content = self._load_template(f"{template}_README.template.md")

        if not template_content:
            template_content = self._load_template("README.template.md")

        if not template_content:
            # Generate default template
            template_content = self._get_default_readme_template()

        variables = {
            "project_name": project_name,
            "project_type": project_type,
            "description": description or f"{project_type.replace('_', ' ').title()} project",
            "version": version,
            "author": author or "",
            "created_at": created_at,
        }

        content = self._substitute_variables(template_content, variables)
        readme_path = project_path / "README.md"

        try:
            readme_path.write_text(content, encoding="utf-8")
            logger.info(f"Generated README.md for {project_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate README.md: {e}")
            return False

    def generate_root_agents(
        self,
        project_path: Path,
        project_name: str,
        project_type: str,
        description: str,
        nested_dirs: list[str],
        template: Optional[str] = None,
    ) -> bool:
        """Generate AGENTS.md for the project root."""
        template_content = None
        if template:
            template_content = self._load_template(f"{template}_AGENTS.template.md")

        if not template_content:
            template_content = self._load_template("AGENTS.template.md")

        if not template_content:
            template_content = self._get_default_agents_template()

        # Build active components list
        active_components = []
        for nested_dir in nested_dirs:
            dir_name = nested_dir.rstrip("/")
            active_components.append(f'- `{dir_name}/` – {self._get_directory_purpose(dir_name, project_type)}')

        variables = {
            "project_name": project_name,
            "project_type": project_type,
            "description": description or f"{project_type.replace('_', ' ').title()} project",
            "active_components": "\n".join(active_components) if active_components else "No active components specified",
        }

        content = self._substitute_variables(template_content, variables)
        agents_path = project_path / "AGENTS.md"

        try:
            agents_path.write_text(content, encoding="utf-8")
            logger.info(f"Generated AGENTS.md for {project_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate AGENTS.md: {e}")
            return False

    def generate_nested_readme(
        self,
        dir_path: Path,
        dir_name: str,
        project_name: str,
        project_type: str,
        parent_path: Optional[Path] = None,
        template: Optional[str] = None,
    ) -> bool:
        """Generate README.md for a nested directory."""
        template_content = None
        if template:
            template_content = self._load_template(f"{template}_README.nested.template.md")

        if not template_content:
            template_content = self._load_template("README.nested.template.md")

        if not template_content:
            template_content = self._get_default_nested_readme_template()

        purpose = self._get_directory_purpose(dir_name, project_type)
        purpose_lower = purpose.lower()

        # Calculate relative path to parent
        parent_link = ""
        if parent_path:
            depth_diff = len(dir_path.parts) - len(parent_path.parts)
            if depth_diff > 0:
                rel_path = "../" * depth_diff
            else:
                rel_path = "../"
            parent_link = f"\n- **Parent Directory**: [{parent_path.name}]({rel_path}README.md)"

        variables = {
            "directory_name": dir_name,
            "project_name": project_name,
            "project_type": project_type,
            "purpose": purpose,
            "purpose_lower": purpose_lower,
            "parent_link": parent_link,
        }

        content = self._substitute_variables(template_content, variables)
        readme_path = dir_path / "README.md"

        try:
            readme_path.write_text(content, encoding="utf-8")
            logger.debug(f"Generated README.md for {dir_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate nested README.md for {dir_name}: {e}")
            return False

    def generate_nested_agents(
        self,
        dir_path: Path,
        dir_name: str,
        project_name: str,
        project_type: str,
        parent_path: Optional[Path] = None,
        template: Optional[str] = None,
    ) -> bool:
        """Generate AGENTS.md for a nested directory."""
        template_content = None
        if template:
            template_content = self._load_template(f"{template}_AGENTS.nested.template.md")

        if not template_content:
            template_content = self._load_template("AGENTS.nested.template.md")

        if not template_content:
            template_content = self._get_default_nested_agents_template()

        purpose = self._get_directory_agent_purpose(dir_name, project_name)

        # Calculate relative path to parent
        parent_link = ""
        if parent_path:
            depth_diff = len(dir_path.parts) - len(parent_path.parts)
            if depth_diff > 0:
                rel_path = "../" * depth_diff
            else:
                rel_path = "../"
            parent_link = f"\n- **Parent Agents**: [{parent_path.name} AGENTS.md]({rel_path}AGENTS.md)"

        variables = {
            "directory_name": dir_name,
            "project_name": project_name,
            "project_type": project_type,
            "purpose": purpose,
            "parent_link": parent_link,
        }

        content = self._substitute_variables(template_content, variables)
        agents_path = dir_path / "AGENTS.md"

        try:
            agents_path.write_text(content, encoding="utf-8")
            logger.debug(f"Generated AGENTS.md for {dir_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate nested AGENTS.md for {dir_name}: {e}")
            return False

    def generate_all_documentation(
        self,
        project_path: Path,
        project_name: str,
        project_type: str,
        description: str,
        version: str,
        author: str,
        created_at: str,
        nested_dirs: list[str],
        template: Optional[str] = None,
        doc_links: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Generate all documentation for a project and its nested directories."""
        if doc_links is None:
            doc_links = {"enabled": True, "parent_link": True, "child_links": True}

        success = True

        # Generate root documentation
        success &= self.generate_root_readme(
            project_path, project_name, project_type, description, version, author, created_at, template
        )
        success &= self.generate_root_agents(
            project_path, project_name, project_type, description, nested_dirs, template
        )

        # Generate nested documentation
        if doc_links.get("enabled", True):
            for nested_dir in nested_dirs:
                dir_name = nested_dir.rstrip("/")
                nested_path = project_path / dir_name

                if nested_path.exists() and nested_path.is_dir():
                    success &= self.generate_nested_readme(
                        nested_path, dir_name, project_name, project_type, project_path, template
                    )
                    success &= self.generate_nested_agents(
                        nested_path, dir_name, project_name, project_type, project_path, template
                    )

        return success

    def _get_default_readme_template(self) -> str:
        """Get default README template."""
        return """# {{project_name}}

**Version**: {{version}} | **Type**: {{project_type}} | **Created**: {{created_at}}

## Overview

{{description}}

## Core Capabilities

### Primary Functions
- **Modular Architecture**: Self-contained module with clear boundaries and responsibilities
- **Agent Integration**: Seamlessly integrates with Codomyrmex agent ecosystem
- **Comprehensive Testing**: Full test coverage with unit, integration, and performance tests
- **Documentation**: Complete documentation with examples and API references

## Architecture

```
{{project_name}}/
├── src/           # Source code
├── config/        # Configuration files
├── data/          # Data files
├── output/        # Generated output
└── reports/       # Analysis reports
```

## Key Components

### Active Components
- See AGENTS.md for detailed agent configuration

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Integration Points

### Related Modules
See project configuration for required and optional modules.

## Usage Examples

```python
# Example usage will be documented based on specific project capabilities
```

## Quality Assurance

The project includes comprehensive testing to ensure:
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

When contributing to this project:
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

    def _get_default_agents_template(self) -> str:
        """Get default AGENTS template."""
        return """# Codomyrmex Agents — {{project_name}}

## Purpose
{{description}}

## Active Components
{{active_components}}

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
"""

    def _get_default_nested_readme_template(self) -> str:
        """Get default nested README template."""
        return """# {{directory_name}}

**Component**: {{project_name}} | **Type**: {{project_type}}

## Overview

{{purpose}}.{{parent_link}}

## Purpose

This directory contains {{purpose.lower()}} for the {{project_name}} project.

## Structure

Files and subdirectories in this directory support the project's {{project_type}} functionality.

## Related Documentation

- **AGENTS.md**: Agent configuration for this directory
- **Parent README**: [../README.md](../README.md) - Project overview
- **Parent AGENTS**: [../AGENTS.md](../AGENTS.md) - Project agents
"""

    def _get_default_nested_agents_template(self) -> str:
        """Get default nested AGENTS template."""
        return """# Codomyrmex Agents — {{project_name}}/{{directory_name}}

## Purpose
{{purpose}}.{{parent_link}}

## Active Components
No active components specified at this level.

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Checkpoints
- [ ] Confirm AGENTS.md reflects the current module purpose.
- [ ] Verify logging and telemetry hooks for this directory's agents.
- [ ] Sync automation scripts or TODO entries after modifications.
"""
