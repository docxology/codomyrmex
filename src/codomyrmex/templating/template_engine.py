from pathlib import Path
from typing import Any, Callable, Optional

from jinja2 import Environment, FileSystemLoader
from jinja2 import Environment, Template as Jinja2Template
from mako.template import Template as MakoTemplate
from mako.template import Template as MakoTemplate

from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger







"""Template engine implementations.
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL: """

logger = get_logger(__name__)

class TemplatingError(CodomyrmexError):
    """Raised when templating operations fail."""

    pass

class Template:
    """Template object."""

    def __init__(self, template_obj: Any, engine: str):
        """Initialize template.

        Args:
            template_obj: Template object from engine
            engine: Engine name
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        self.template_obj = template_obj
        self.engine = engine

    def render(self, context: dict) -> str:
        """Render template with context."""
        if self.engine == "jinja2":
            return self.template_obj.render(**context)
        elif self.engine == "mako":
            return self.template_obj.render(**context)
        else:
            raise TemplatingError(f"Unknown engine: {self.engine}")

class TemplateEngine:
    """Template engine interface."""

    def __init__(self, engine: str = "jinja2"):
        """Initialize template engine.

        Args:
            engine: Template engine (jinja2, mako)
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        self.engine = engine
        self._filters: dict[str, Callable] = {}
        self._cache: dict[str, Template] = {}

    def render(self, template: str, context: dict) -> str:
        """Render a template string with context data.

        Args:
            template: Template string
            context: Context data for template

        Returns:
            Rendered template

        Raises:
            TemplatingError: If rendering fails
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        try:
            if self.engine == "jinja2":
                return self._render_jinja2(template, context)
            elif self.engine == "mako":
                return self._render_mako(template, context)
            else:
                raise ValueError(f"Unknown engine: {self.engine}")
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            raise TemplatingError(f"Failed to render template: {str(e)}") from e

    def load_template(self, path: str) -> Template:
        """Load a template from a file.

        Args:
            path: Template file path

        Returns:
            Template object

        Raises:
            TemplatingError: If template loading fails
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        path_str = str(path)
        if path_str in self._cache:
            return self._cache[path_str]

        try:
            if self.engine == "jinja2":
                template_obj = self._load_jinja2(path)
            elif self.engine == "mako":
                template_obj = self._load_mako(path)
            else:
                raise ValueError(f"Unknown engine: {self.engine}")

            template = Template(template_obj, self.engine)
            self._cache[path_str] = template
            return template
        except Exception as e:
            logger.error(f"Template loading error: {e}")
            raise TemplatingError(f"Failed to load template: {str(e)}") from e

    def register_filter(self, name: str, func: Callable) -> None:
        """Register a custom template filter.

        Args:
            name: Filter name
            func: Filter function
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        self._filters[name] = func

    def get_filter(self, name: str) -> Optional[Callable]:
        """Get a registered filter.

        Args:
            name: Filter name

        Returns:
            Filter function if found
# AGGRESSIVE_REMOVAL_GARBAGE_DOC: # AGGRESSIVE_REMOVAL:         """
        return self._filters.get(name)

    def _render_jinja2(self, template: str, context: dict) -> str:
        """Render using Jinja2."""
        try:

            env = Environment()
            # Register custom filters
            for name, func in self._filters.items():
                env.filters[name] = func

            template_obj = Jinja2Template(template, environment=env)
            return template_obj.render(**context)
        except ImportError:
            raise TemplatingError("jinja2 package not available. Install with: pip install jinja2")

    def _load_jinja2(self, path: str) -> Any:
        """Load template using Jinja2."""
        try:

            path_obj = Path(path)
            env = Environment(loader=FileSystemLoader(str(path_obj.parent)))
            # Register custom filters
            for name, func in self._filters.items():
                env.filters[name] = func

            return env.get_template(path_obj.name)
        except ImportError:
            raise TemplatingError("jinja2 package not available. Install with: pip install jinja2")

    def _render_mako(self, template: str, context: dict) -> str:
        """Render using Mako."""
        try:

            template_obj = MakoTemplate(template)
            return template_obj.render(**context)
        except ImportError:
            raise TemplatingError("mako package not available. Install with: pip install mako")

    def _load_mako(self, path: str) -> Any:
        """Load template using Mako."""
        try:

            return MakoTemplate(filename=path)
        except ImportError:
            raise TemplatingError("mako package not available. Install with: pip install mako")

