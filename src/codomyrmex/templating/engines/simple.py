"""SimpleTemplateEngine: basic {{ var }} string interpolation."""

import html
import re
from typing import Any

from .base import TemplateEngine


class SimpleTemplateEngine(TemplateEngine):
    """Simple string interpolation template engine."""

    def __init__(
        self,
        delimiters: tuple = ("{{", "}}"),
        escape_html: bool = False,
    ):
        self.left_delim = delimiters[0]
        self.right_delim = delimiters[1]
        self.escape_html = escape_html
        self._pattern = re.compile(
            re.escape(self.left_delim) + r"\s*(.+?)\s*" + re.escape(self.right_delim)
        )

    def _resolve_path(self, path: str, context: dict[str, Any]) -> Any:
        """Resolve a dotted path in the context."""
        parts = path.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None

            if value is None:
                return None

        return value

    def render(self, template: str, context: dict[str, Any]) -> str:
        """Render template substituting {{ var }} expressions."""

        def replace(match):
            path = match.group(1).strip()
            value = self._resolve_path(path, context)

            if value is None:
                return match.group(0)

            result = str(value)
            if self.escape_html:
                result = html.escape(result)

            return result

        return self._pattern.sub(replace, template)

    def render_file(self, path: str, context: dict[str, Any]) -> str:
        """Render a template file."""
        with open(path) as f:
            template = f.read()
        return self.render(template, context)
