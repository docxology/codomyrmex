"""Module Scaffolding for Codomyrmex.

Provides utilities to programmatically create new modules from the template.
"""

import re
import shutil
from pathlib import Path

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

# Files to copy from template
TEMPLATE_FILES = [
    "AGENTS.md",
    "API_SPECIFICATION.md",
    "CHANGELOG.md",
    "MCP_TOOL_SPECIFICATION.md",
    "README.md",
    "SECURITY.md",
    "SPEC.md",
    "USAGE_EXAMPLES.md",
    "__init__.py",
    ".gitignore",
]


def scaffold_new_module(
    module_name: str,
    target_path: Path | None = None,
    description: str = "",
    author: str = "",
) -> Path:
    """
    Create a new Codomyrmex module from the template.

    Args:
        module_name: Name of the new module (snake_case preferred)
        target_path: Path where the module should be created.
                     Defaults to src/codomyrmex/{module_name}
        description: Short description of the module
        author: Author name for documentation

    Returns:
        Path to the created module directory

    Raises:
        FileExistsError: If the target directory already exists
        ValueError: If module_name is invalid
    """
    # Validate module name
    if not re.match(r'^[a-z][a-z0-9_]*$', module_name):
        raise ValueError(
            f"Invalid module name '{module_name}'. "
            "Use lowercase letters, numbers, and underscores. Must start with a letter."
        )

    # Determine paths
    template_dir = Path(__file__).parent
    if target_path is None:
        target_path = template_dir.parent / module_name
    else:
        target_path = Path(target_path) / module_name

    # Check if target exists
    if target_path.exists():
        raise FileExistsError(f"Directory already exists: {target_path}")

    # Create directory
    target_path.mkdir(parents=True, exist_ok=False)
    logger.info(f"Created module directory: {target_path}")

    # Copy and customize template files
    replacements = {
        "module_template": module_name,
        "Module Template": module_name.replace("_", " ").title(),
        "MODULE_TEMPLATE": module_name.upper(),
    }

    for filename in TEMPLATE_FILES:
        src_file = template_dir / filename
        dst_file = target_path / filename

        if src_file.exists():
            _copy_and_customize(src_file, dst_file, replacements, description, author)
            logger.debug(f"Created: {dst_file}")
        else:
            logger.warning(f"Template file not found: {src_file}")

    # Create core module file
    core_file = target_path / f"{module_name}.py"
    _create_core_module(core_file, module_name, description)

    logger.info(f"Successfully scaffolded module '{module_name}' at {target_path}")
    return target_path


def _copy_and_customize(
    src: Path,
    dst: Path,
    replacements: dict,
    description: str,
    author: str
) -> None:
    """Copy a file and perform text replacements."""
    try:
        content = src.read_text(encoding='utf-8')

        # Perform replacements
        for old, new in replacements.items():
            content = content.replace(old, new)

        # Add description if provided
        if description and "# Description" not in content:
            # For README.md, add description after first heading
            if dst.name == "README.md":
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('# '):
                        lines.insert(i + 1, f"\n{description}\n")
                        break
                content = '\n'.join(lines)

        dst.write_text(content, encoding='utf-8')
    except Exception as e:
        logger.error(f"Error customizing {src}: {e}")
        # Fall back to simple copy
        shutil.copy2(src, dst)


def _create_core_module(path: Path, module_name: str, description: str) -> None:
    """Create the main Python file for the new module."""
    class_name = ''.join(word.title() for word in module_name.split('_'))

    content = f'''"""
{module_name.replace("_", " ").title()} Module

{description or "Core implementation for this module."}
"""

from typing import Any, Dict, Optional

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


class {class_name}:
    """Main class for {module_name.replace("_", " ")} functionality."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize {class_name}.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {{}}
        logger.info(f"{class_name} initialized")

    def process(self, data: Any) -> Any:
        """
        Process input data.

        Args:
            data: Input data to process

        Returns:
            Processed data
        """
        logger.debug(f"Processing data: {{type(data).__name__}}")
        raise NotImplementedError("scaffold.process() requires implementation by consuming module")  # ABC: intentional


# Convenience function
def create_{module_name}(config: Optional[Dict[str, Any]] = None) -> {class_name}:
    """
    Create a new {class_name} instance.

    Args:
        config: Optional configuration

    Returns:
        {class_name} instance
    """
    return {class_name}(config)
'''
    path.write_text(content, encoding='utf-8')
    logger.debug(f"Created core module: {path}")


def list_template_files() -> list[str]:
    """
    List all files available in the module template.

    Returns:
        List of template file names
    """
    template_dir = Path(__file__).parent
    return [f.name for f in template_dir.iterdir() if f.is_file() and not f.name.startswith('.')]
