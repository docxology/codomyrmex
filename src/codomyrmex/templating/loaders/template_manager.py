"""
Template manager for managing multiple templates.
"""

from typing import Optional, Union

from codomyrmex.logging_monitoring.logger_config import get_logger

from .template_engine import Template, TemplateEngine

logger = get_logger(__name__)


class TemplateManager:
    """Manager for template operations."""

    def __init__(self, engine: str = "jinja2"):
        """Initialize template manager.

        Args:
            engine: Template engine to use
        """
        self.engine = TemplateEngine(engine=engine)
        self._templates: dict[str, Union[str, Template]] = {}

    def add_template(self, name: str, template: Union[str, Template]) -> None:
        """Add a template to the template manager.

        Args:
            name: Template name
            template: Template string or object
        """
        self._templates[name] = template
        logger.info(f"Added template: {name}")

    def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name.

        Args:
            name: Template name

        Returns:
            Template object if found
        """
        if name not in self._templates:
            return None

        template = self._templates[name]
        if isinstance(template, Template):
            return template
        elif isinstance(template, str):
            # Create template from string
            return Template(self.engine._render_jinja2(template, {}), self.engine.engine)

        return None

    def render(self, name: str, context: dict) -> str:
        """Render a template by name.

        Args:
            name: Template name
            context: Context data

        Returns:
            Rendered template
        """
        template = self.get_template(name)
        if template is None:
            raise ValueError(f"Template not found: {name}")

        return template.render(context)


