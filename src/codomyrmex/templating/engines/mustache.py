"""MustacheEngine: logic-less {{#section}} / {{^inverted}} templates."""

import html
import re
from typing import Any

from .base import TemplateEngine


class MustacheEngine(TemplateEngine):
    """Mustache-style logic-less templates."""

    def __init__(self):
        self._var_pattern = re.compile(r"\{\{([#^/]?)(.+?)\}\}")

    def render(self, template: str, context: dict[str, Any]) -> str:
        """Render a Mustache template."""
        return self._render_internal(template, context)

    def _render_internal(self, template: str, context: dict[str, Any]) -> str:
        """Process sections then variables."""
        template = self._process_sections(template, context)
        template = self._process_variables(template, context)
        return template

    def _resolve_path(self, path: str, context: dict[str, Any]) -> Any:
        """Resolve a dotted path in the context."""
        if path == ".":
            return context.get(".")

        parts = path.split(".")
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None

        return value

    def _expand_section(self, value: Any, content: str, context: dict[str, Any]) -> str:
        """Expand a truthy section value (list, dict, or scalar)."""
        if isinstance(value, list):
            parts = []
            for item in value:
                new_ctx = (
                    {**context, **item}
                    if isinstance(item, dict)
                    else {**context, ".": item}
                )
                parts.append(self._render_internal(content, new_ctx))
            return "".join(parts)
        if isinstance(value, dict):
            return self._render_internal(content, {**context, **value})
        return self._render_internal(content, context)

    def _process_sections(self, template: str, context: dict[str, Any]) -> str:
        """Process {{#section}} and {{^section}} blocks."""
        section_pattern = re.compile(r"\{\{([#^])(.+?)\}\}(.*?)\{\{/\2\}\}", re.DOTALL)

        def replace(match):
            section_type = match.group(1)
            name = match.group(2).strip()
            content = match.group(3)
            value = self._resolve_path(name, context)

            if section_type == "#":
                if not value:
                    return ""
                return self._expand_section(value, content, context)

            # Inverted section
            return "" if value else self._render_internal(content, context)

        while section_pattern.search(template):
            template = section_pattern.sub(replace, template)

        return template

    def _process_variables(self, template: str, context: dict[str, Any]) -> str:
        """Process {{variable}} expressions with optional triple-mustache or & unescaped."""
        pattern = re.compile(r"\{\{([^#^/].+?)\}\}")

        def replace(match):
            name = match.group(1).strip()

            if name.startswith("{") and name.endswith("}"):
                value = self._resolve_path(name[1:-1], context)
                return str(value) if value is not None else ""

            if name.startswith("&"):
                value = self._resolve_path(name[1:].strip(), context)
                return str(value) if value is not None else ""

            value = self._resolve_path(name, context)
            if value is None:
                return ""
            return html.escape(str(value))

        return pattern.sub(replace, template)

    def render_file(self, path: str, context: dict[str, Any]) -> str:
        """Render a template file."""
        with open(path) as f:
            template = f.read()
        return self.render(template, context)
