"""Template manager — registry, loading, rendering, and inheritance.

Manages multiple named templates with:
- Template registration and retrieval
- File-system template loading from directories
- Template inheritance (child extends parent via blocks)
- Batch rendering
- Template validation
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

from ..engines.template_engine import Template, TemplateEngine

logger = get_logger(__name__)


class TemplateManager:
    """Manager for template operations with directory loading and inheritance.

    Example::

        mgr = TemplateManager()
        mgr.register("greeting", "Hello {{ name }}!")
        result = mgr.render("greeting", {"name": "World"})
        assert result == "Hello World!"
    """

    def __init__(self, engine: str = "jinja2") -> None:
        self.engine = TemplateEngine(engine=engine)
        self._templates: dict[str, str] = {}  # name -> template source string
        self._parents: dict[str, str] = {}  # child_name -> parent_name

    # ── Registration ────────────────────────────────────────────────

    def register(self, name: str, template_source: str, parent: str | None = None) -> None:
        """Register a template by name.

        Args:
            name: Template name (unique key).
            template_source: Template source string.
            parent: Optional parent template name for inheritance.
        """
        self._templates[name] = template_source
        if parent:
            self._parents[name] = parent
        logger.info("Registered template: %s", name)

    # Alias for backward compatibility
    def add_template(self, name: str, template: str | Template) -> None:
        """Add a template (backward-compatible)."""
        if isinstance(template, Template):
            self._templates[name] = template.source if hasattr(template, "source") else str(template)
        else:
            self._templates[name] = template
        logger.info("Added template: %s", name)

    def remove_template(self, name: str) -> bool:
        """Remove a template by name."""
        if name in self._templates:
            del self._templates[name]
            self._parents.pop(name, None)
            return True
        return False

    def has_template(self, name: str) -> bool:
        """Check if a template is registered."""
        return name in self._templates

    def list_templates(self) -> list[str]:
        """List all registered template names."""
        return sorted(self._templates.keys())

    # ── Retrieval ───────────────────────────────────────────────────

    def get_template(self, name: str) -> str | None:
        """Get template source by name. Returns None if not found."""
        return self._templates.get(name)

    def get_parent(self, name: str) -> str | None:
        """Get the parent template name, if any."""
        return self._parents.get(name)

    # ── Rendering ───────────────────────────────────────────────────

    def render(self, name: str, context: dict[str, Any] | None = None) -> str:
        """Render a template by name with context.

        If the template has a parent, the parent is rendered first and
        the child's output replaces the ``{{ content }}`` block in the parent.

        Args:
            name: Template name.
            context: Context variables for rendering.

        Returns:
            Rendered string.

        Raises:
            ValueError: If template not found.
        """
        source = self._templates.get(name)
        if source is None:
            raise ValueError(f"Template not found: {name}")

        ctx = context or {}
        rendered = self.engine.render(source, ctx)

        # Handle inheritance: inject into parent's {{ content }} block
        parent_name = self._parents.get(name)
        if parent_name and parent_name in self._templates:
            parent_source = self._templates[parent_name]
            parent_ctx = {**ctx, "content": rendered}
            rendered = self.engine.render(parent_source, parent_ctx)

        return rendered

    def render_string(self, template_source: str, context: dict[str, Any] | None = None) -> str:
        """Render an ad-hoc template string without registration.

        Args:
            template_source: Raw template source string.
            context: Variables for rendering.
        """
        return self.engine.render(template_source, context or {})

    def render_batch(self, name: str, contexts: list[dict[str, Any]]) -> list[str]:
        """Render the same template with multiple contexts.

        Args:
            name: Template name.
            contexts: List of context dicts.

        Returns:
            List of rendered strings.
        """
        return [self.render(name, ctx) for ctx in contexts]

    # ── File System Loading ─────────────────────────────────────────

    def load_directory(self, directory: str | Path, extension: str = ".html") -> int:
        """Load all templates from a directory.

        Template names are derived from filenames (without extension).

        Args:
            directory: Path to template directory.
            extension: File extension to match.

        Returns:
            Number of templates loaded.
        """
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise FileNotFoundError(f"Template directory not found: {directory}")

        count = 0
        for entry in sorted(dir_path.iterdir()):
            if entry.is_file() and entry.name.endswith(extension):
                name = entry.stem
                source = entry.read_text(encoding="utf-8")
                self.register(name, source)
                count += 1

        logger.info("Loaded %d templates from %s", count, directory)
        return count

    # ── Validation ──────────────────────────────────────────────────

    def validate(self, name: str) -> tuple[bool, str]:
        """Validate a template can be rendered.

        Attempts to render with empty context. Returns (True, "") on success
        or (False, error_message) on failure.
        """
        source = self._templates.get(name)
        if source is None:
            return False, f"Template not found: {name}"
        try:
            self.engine.render(source, {})
            return True, ""
        except Exception as e:
            return False, str(e)

    def validate_all(self) -> dict[str, tuple[bool, str]]:
        """Validate all registered templates.

        Returns:
            Dict mapping template name to (valid, error_message).
        """
        return {name: self.validate(name) for name in self._templates}

    # ── Summary ─────────────────────────────────────────────────────

    @property
    def template_count(self) -> int:
        return len(self._templates)

    def summary(self) -> dict[str, Any]:
        """Return summary of registered templates."""
        return {
            "total": len(self._templates),
            "with_parent": len(self._parents),
            "names": sorted(self._templates.keys()),
        }
