"""
Template engine implementations.

Provides different template rendering engines.
"""

import html
import logging
import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TemplateContext:
    """Context for template rendering."""
    data: dict[str, Any] = field(default_factory=dict)
    parent: Optional['TemplateContext'] = None

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from context, checking parent if not found."""
        if key in self.data:
            return self.data[key]
        if self.parent:
            return self.parent.get(key, default)
        return default

    def set(self, key: str, value: Any) -> None:
        """Set a value in the context."""
        self.data[key] = value

    def child(self, **kwargs) -> 'TemplateContext':
        """Create a child context."""
        return TemplateContext(data=kwargs, parent=self)

    def __getitem__(self, key: str) -> Any:
        """getitem ."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """setitem ."""
        self.set(key, value)


class TemplateEngine(ABC):
    """Abstract base class for template engines."""

    @abstractmethod
    def render(self, template: str, context: dict[str, Any]) -> str:
        """Render a template with the given context."""
        pass

    @abstractmethod
    def render_file(self, path: str, context: dict[str, Any]) -> str:
        """Render a template file."""
        pass


class SimpleTemplateEngine(TemplateEngine):
    """Simple string interpolation template engine."""

    def __init__(
        self,
        delimiters: tuple = ("{{", "}}"),
        escape_html: bool = False,
    ):
        """Initialize this instance."""
        self.left_delim = delimiters[0]
        self.right_delim = delimiters[1]
        self.escape_html = escape_html
        self._pattern = re.compile(
            re.escape(self.left_delim) + r'\s*(.+?)\s*' + re.escape(self.right_delim)
        )

    def _resolve_path(self, path: str, context: dict[str, Any]) -> Any:
        """Resolve a dotted path in the context."""
        parts = path.split('.')
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
        """render ."""
        def replace(match):
            """replace ."""
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
        """render File ."""
        with open(path) as f:
            template = f.read()
        return self.render(template, context)


class Jinja2LikeEngine(TemplateEngine):
    """Enhanced template engine with control structures."""

    def __init__(
        self,
        filters: dict[str, Callable] | None = None,
        autoescape: bool = True,
    ):
        """Initialize this instance."""
        self.filters = filters or {}
        self.autoescape = autoescape

        # Default filters
        self._default_filters = {
            'upper': str.upper,
            'lower': str.lower,
            'title': str.title,
            'strip': str.strip,
            'length': len,
            'default': lambda x, d='': x if x else d,
            'safe': lambda x: x,
            'escape': html.escape,
            'join': lambda lst, sep=', ': sep.join(str(x) for x in lst),
            'first': lambda lst: lst[0] if lst else None,
            'last': lambda lst: lst[-1] if lst else None,
            'reverse': lambda x: list(reversed(x)),
            'sort': sorted,
        }
        self._default_filters.update(self.filters)

    def _parse_expression(self, expr: str, context: dict[str, Any]) -> Any:
        """Parse and evaluate an expression."""
        expr = expr.strip()

        # Handle filters
        if '|' in expr:
            parts = expr.split('|')
            value = self._parse_expression(parts[0], context)

            for filter_expr in parts[1:]:
                filter_expr = filter_expr.strip()

                # Parse filter with arguments
                if '(' in filter_expr:
                    fname = filter_expr[:filter_expr.index('(')]
                    args_str = filter_expr[filter_expr.index('(')+1:filter_expr.rindex(')')]
                    args = [a.strip().strip('"\'') for a in args_str.split(',') if a.strip()]
                else:
                    fname = filter_expr
                    args = []

                if fname in self._default_filters:
                    if args:
                        value = self._default_filters[fname](value, *args)
                    else:
                        value = self._default_filters[fname](value)

            return value

        # Handle simple variable lookup
        return self._resolve_path(expr, context)

    def _resolve_path(self, path: str, context: dict[str, Any]) -> Any:
        """Resolve a dotted path or subscript in the context."""
        path = path.strip()

        # Handle string literals
        if (path.startswith('"') and path.endswith('"')) or \
           (path.startswith("'") and path.endswith("'")):
            return path[1:-1]

        # Handle numeric literals
        if path.isdigit():
            return int(path)
        if path.replace('.', '', 1).isdigit():
            return float(path)

        # Handle boolean
        if path.lower() == 'true':
            return True
        if path.lower() == 'false':
            return False

        parts = re.split(r'\.|\[|\]', path)
        parts = [p for p in parts if p]

        value = context
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif isinstance(value, (list, tuple)):
                try:
                    value = value[int(part)]
                except (ValueError, IndexError) as e:
                    logger.warning("Failed to resolve path segment '%s': %s", part, e)
                    return None
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None

        return value

    def render(self, template: str, context: dict[str, Any]) -> str:
        """render ."""
        # Process control structures
        template = self._process_for_loops(template, context)
        template = self._process_if_blocks(template, context)

        # Process variable interpolation
        template = self._process_variables(template, context)

        return template

    def _process_variables(self, template: str, context: dict[str, Any]) -> str:
        """Process {{ variable }} expressions."""
        pattern = re.compile(r'\{\{\s*(.+?)\s*\}\}')

        def replace(match):
            """replace ."""
            expr = match.group(1)
            value = self._parse_expression(expr, context)

            if value is None:
                return ''

            result = str(value)
            if self.autoescape:
                result = html.escape(result)

            return result

        return pattern.sub(replace, template)

    def _process_for_loops(self, template: str, context: dict[str, Any]) -> str:
        """Process {% for item in items %} blocks."""
        pattern = re.compile(
            r'\{%\s*for\s+(\w+)\s+in\s+(.+?)\s*%\}(.+?)\{%\s*endfor\s*%\}',
            re.DOTALL
        )

        def replace(match):
            """replace ."""
            var_name = match.group(1)
            iterable_expr = match.group(2)
            body = match.group(3)

            iterable = self._parse_expression(iterable_expr, context)
            if not iterable:
                return ''

            result = []
            for i, item in enumerate(iterable):
                loop_context = dict(context)
                loop_context[var_name] = item
                loop_context['loop'] = {
                    'index': i + 1,
                    'index0': i,
                    'first': i == 0,
                    'last': i == len(iterable) - 1,
                    'length': len(iterable),
                }

                rendered = self.render(body, loop_context)
                result.append(rendered)

            return ''.join(result)

        # Process nested loops from inside out
        while pattern.search(template):
            template = pattern.sub(replace, template)

        return template

    def _process_if_blocks(self, template: str, context: dict[str, Any]) -> str:
        """Process {% if condition %} blocks."""
        # Simple if/endif pattern
        pattern = re.compile(
            r'\{%\s*if\s+(.+?)\s*%\}(.+?)(?:\{%\s*else\s*%\}(.+?))?\{%\s*endif\s*%\}',
            re.DOTALL
        )

        def replace(match):
            """replace ."""
            condition = match.group(1)
            true_block = match.group(2)
            false_block = match.group(3) or ''

            value = self._evaluate_condition(condition, context)

            if value:
                return self.render(true_block, context)
            else:
                return self.render(false_block, context)

        while pattern.search(template):
            template = pattern.sub(replace, template)

        return template

    def _evaluate_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        condition = condition.strip()

        # Handle comparison operators
        for op, func in [
            (' == ', lambda a, b: a == b),
            (' != ', lambda a, b: a != b),
            (' >= ', lambda a, b: a >= b),
            (' <= ', lambda a, b: a <= b),
            (' > ', lambda a, b: a > b),
            (' < ', lambda a, b: a < b),
            (' in ', lambda a, b: a in b),
        ]:
            if op in condition:
                left, right = condition.split(op, 1)
                left_val = self._parse_expression(left, context)
                right_val = self._parse_expression(right, context)
                return func(left_val, right_val)

        # Handle 'not' prefix
        if condition.startswith('not '):
            return not self._evaluate_condition(condition[4:], context)

        # Handle 'and' / 'or'
        if ' and ' in condition:
            parts = condition.split(' and ')
            return all(self._evaluate_condition(p, context) for p in parts)

        if ' or ' in condition:
            parts = condition.split(' or ')
            return any(self._evaluate_condition(p, context) for p in parts)

        # Simple truthiness check
        value = self._parse_expression(condition, context)
        return bool(value)

    def render_file(self, path: str, context: dict[str, Any]) -> str:
        """render File ."""
        with open(path) as f:
            template = f.read()
        return self.render(template, context)


class MustacheEngine(TemplateEngine):
    """Mustache-style logic-less templates."""

    def __init__(self):
        """Initialize this instance."""
        self._var_pattern = re.compile(r'\{\{([#^/]?)(.+?)\}\}')

    def render(self, template: str, context: dict[str, Any]) -> str:
        """render ."""
        return self._render_internal(template, context)

    def _render_internal(self, template: str, context: dict[str, Any]) -> str:
        """render Internal ."""
        # Process sections
        template = self._process_sections(template, context)

        # Process variables
        template = self._process_variables(template, context)

        return template

    def _process_sections(self, template: str, context: dict[str, Any]) -> str:
        """Process {{#section}} and {{^section}} blocks."""
        section_pattern = re.compile(
            r'\{\{([#^])(.+?)\}\}(.*?)\{\{/\2\}\}',
            re.DOTALL
        )

        def replace(match):
            """replace ."""
            section_type = match.group(1)
            name = match.group(2).strip()
            content = match.group(3)

            value = self._resolve_path(name, context)

            if section_type == '#':
                # Truthy section
                if not value:
                    return ''

                if isinstance(value, list):
                    result = []
                    for item in value:
                        if isinstance(item, dict):
                            new_context = {**context, **item}
                        else:
                            new_context = {**context, '.': item}
                        result.append(self._render_internal(content, new_context))
                    return ''.join(result)
                elif isinstance(value, dict):
                    new_context = {**context, **value}
                    return self._render_internal(content, new_context)
                else:
                    return self._render_internal(content, context)

            else:  # Inverted section
                if value:
                    return ''
                return self._render_internal(content, context)

        while section_pattern.search(template):
            template = section_pattern.sub(replace, template)

        return template

    def _process_variables(self, template: str, context: dict[str, Any]) -> str:
        """Process {{variable}} expressions."""
        pattern = re.compile(r'\{\{([^#^/].+?)\}\}')

        def replace(match):
            """replace ."""
            name = match.group(1).strip()

            # Triple mustache for unescaped
            if name.startswith('{') and name.endswith('}'):
                name = name[1:-1]
                value = self._resolve_path(name, context)
                return str(value) if value is not None else ''

            # Ampersand for unescaped
            if name.startswith('&'):
                name = name[1:].strip()
                value = self._resolve_path(name, context)
                return str(value) if value is not None else ''

            value = self._resolve_path(name, context)
            if value is None:
                return ''
            return html.escape(str(value))

        return pattern.sub(replace, template)

    def _resolve_path(self, path: str, context: dict[str, Any]) -> Any:
        """Resolve a dotted path."""
        if path == '.':
            return context.get('.')

        parts = path.split('.')
        value = context

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None

        return value

    def render_file(self, path: str, context: dict[str, Any]) -> str:
        """render File ."""
        with open(path) as f:
            template = f.read()
        return self.render(template, context)


def create_engine(
    engine_type: str = "simple",
    **kwargs
) -> TemplateEngine:
    """Factory function to create template engines."""
    engines = {
        "simple": SimpleTemplateEngine,
        "jinja2": Jinja2LikeEngine,
        "mustache": MustacheEngine,
    }

    engine_class = engines.get(engine_type)
    if not engine_class:
        raise ValueError(f"Unknown engine type: {engine_type}")

    return engine_class(**kwargs)


__all__ = [
    "TemplateContext",
    "TemplateEngine",
    "SimpleTemplateEngine",
    "Jinja2LikeEngine",
    "MustacheEngine",
    "create_engine",
]
