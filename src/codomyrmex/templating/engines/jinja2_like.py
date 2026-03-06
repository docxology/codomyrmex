"""Jinja2LikeEngine: control structures (for/if) + filters."""

import html
import re
from collections.abc import Callable
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .base import TemplateEngine

logger = get_logger(__name__)


class Jinja2LikeEngine(TemplateEngine):
    """Enhanced template engine with control structures."""

    def __init__(
        self,
        filters: dict[str, Callable] | None = None,
        autoescape: bool = True,
    ):
        self.filters = filters or {}
        self.autoescape = autoescape

        self._default_filters: dict[str, Callable] = {
            "upper": str.upper,
            "lower": str.lower,
            "title": str.title,
            "strip": str.strip,
            "length": len,
            "default": lambda x, d="": x or d,
            "safe": lambda x: x,
            "escape": html.escape,
            "join": lambda lst, sep=", ": sep.join(str(x) for x in lst),
            "first": lambda lst: lst[0] if lst else None,
            "last": lambda lst: lst[-1] if lst else None,
            "reverse": lambda x: list(reversed(x)),
            "sort": sorted,
        }
        self._default_filters.update(self.filters)

    def _resolve_path(self, path: str, context: dict[str, Any]) -> Any:
        """Resolve a dotted path or subscript in the context."""
        path = path.strip()

        if (path.startswith('"') and path.endswith('"')) or (
            path.startswith("'") and path.endswith("'")
        ):
            return path[1:-1]

        if path.isdigit():
            return int(path)
        if path.replace(".", "", 1).isdigit():
            return float(path)

        if path.lower() == "true":
            return True
        if path.lower() == "false":
            return False

        parts = re.split(r"\.|\[|\]", path)
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

    def _apply_filter(self, fname: str, value: Any, args: list) -> Any:
        """Apply a named filter with optional args to value."""
        if fname not in self._default_filters:
            return value
        if args:
            return self._default_filters[fname](value, *args)
        return self._default_filters[fname](value)

    def _parse_expression(self, expr: str, context: dict[str, Any]) -> Any:
        """Parse and evaluate an expression, including pipe filters."""
        expr = expr.strip()

        if "|" not in expr:
            return self._resolve_path(expr, context)

        parts = expr.split("|")
        value = self._parse_expression(parts[0], context)

        for filter_expr in parts[1:]:
            filter_expr = filter_expr.strip()
            if "(" in filter_expr:
                fname = filter_expr[: filter_expr.index("(")]
                args_str = filter_expr[filter_expr.index("(") + 1 : filter_expr.rindex(")")]
                args = [a.strip().strip("\"'") for a in args_str.split(",") if a.strip()]
            else:
                fname = filter_expr
                args = []
            value = self._apply_filter(fname, value, args)

        return value

    def render(self, template: str, context: dict[str, Any]) -> str:
        """Render template processing for/if blocks then variable substitution."""
        template = self._process_for_loops(template, context)
        template = self._process_if_blocks(template, context)
        template = self._process_variables(template, context)
        return template

    def _process_variables(self, template: str, context: dict[str, Any]) -> str:
        """Process {{ variable }} expressions."""
        pattern = re.compile(r"\{\{\s*(.+?)\s*\}\}")

        def replace(match):
            value = self._parse_expression(match.group(1), context)
            if value is None:
                return ""
            result = str(value)
            if self.autoescape:
                result = html.escape(result)
            return result

        return pattern.sub(replace, template)

    def _process_for_loops(self, template: str, context: dict[str, Any]) -> str:
        """Process {% for item in items %} blocks."""
        pattern = re.compile(
            r"\{%\s*for\s+(\w+)\s+in\s+(.+?)\s*%\}(.+?)\{%\s*endfor\s*%\}", re.DOTALL
        )

        def replace(match):
            var_name = match.group(1)
            iterable = self._parse_expression(match.group(2), context)
            body = match.group(3)

            if not iterable:
                return ""

            result = []
            for i, item in enumerate(iterable):
                loop_context = dict(context)
                loop_context[var_name] = item
                loop_context["loop"] = {
                    "index": i + 1,
                    "index0": i,
                    "first": i == 0,
                    "last": i == len(iterable) - 1,
                    "length": len(iterable),
                }
                result.append(self.render(body, loop_context))

            return "".join(result)

        while pattern.search(template):
            template = pattern.sub(replace, template)

        return template

    def _evaluate_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """Evaluate a condition expression supporting comparisons, and/or/not."""
        condition = condition.strip()

        for op, func in [
            (" == ", lambda a, b: a == b),
            (" != ", lambda a, b: a != b),
            (" >= ", lambda a, b: a >= b),
            (" <= ", lambda a, b: a <= b),
            (" > ", lambda a, b: a > b),
            (" < ", lambda a, b: a < b),
            (" in ", lambda a, b: a in b),
        ]:
            if op in condition:
                left, right = condition.split(op, 1)
                return func(
                    self._parse_expression(left, context),
                    self._parse_expression(right, context),
                )

        if condition.startswith("not "):
            return not self._evaluate_condition(condition[4:], context)

        if " and " in condition:
            return all(self._evaluate_condition(p, context) for p in condition.split(" and "))

        if " or " in condition:
            return any(self._evaluate_condition(p, context) for p in condition.split(" or "))

        return bool(self._parse_expression(condition, context))

    def _process_if_blocks(self, template: str, context: dict[str, Any]) -> str:
        """Process {% if condition %} / {% else %} / {% endif %} blocks."""
        pattern = re.compile(
            r"\{%\s*if\s+(.+?)\s*%\}(.+?)(?:\{%\s*else\s*%\}(.+?))?\{%\s*endif\s*%\}",
            re.DOTALL,
        )

        def replace(match):
            condition = match.group(1)
            true_block = match.group(2)
            false_block = match.group(3) or ""

            if self._evaluate_condition(condition, context):
                return self.render(true_block, context)
            return self.render(false_block, context)

        while pattern.search(template):
            template = pattern.sub(replace, template)

        return template

    def render_file(self, path: str, context: dict[str, Any]) -> str:
        """Render a template file."""
        with open(path) as f:
            template = f.read()
        return self.render(template, context)
