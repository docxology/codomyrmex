"""Documentation site generator.

Orchestrates API extraction, search indexing, and static
site configuration generation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.docs_gen.api_doc_extractor import APIDocExtractor, ModuleDoc
from codomyrmex.docs_gen.search_index import SearchIndex


@dataclass
class SiteConfig:
    """Documentation site configuration.

    Attributes:
        title: Site title.
        theme: Theme name.
        nav: Navigation structure.
        plugins: Enabled plugins.
        base_url: Base URL.
        extra_css: List of extra CSS files.
        extra_javascript: List of extra JS files.
    """

    title: str = "Codomyrmex Documentation"
    theme: str = "material"
    nav: list[dict[str, Any]] = field(default_factory=list)
    plugins: list[str] = field(default_factory=lambda: ["search", "mkdocstrings"])
    base_url: str = "/"
    extra_css: list[str] = field(default_factory=list)
    extra_javascript: list[str] = field(default_factory=list)


class SiteGenerator:
    """Generate documentation site configuration and content.

    Example::

        gen = SiteGenerator(title="My Docs")
        gen.add_module_source(source, "mymodule")
        config = gen.generate_config()
        pages = gen.generate_pages()
    """

    def __init__(self, title: str = "Codomyrmex Documentation") -> None:
        self._title = title
        self._extractor = APIDocExtractor()
        self._index = SearchIndex()
        self._modules: list[ModuleDoc] = []
        self._pages: dict[str, str] = {}
        self._extra_css: list[str] = []
        self._extra_js: list[str] = []

    @property
    def module_count(self) -> int:
        return len(self._modules)

    @property
    def page_count(self) -> int:
        return len(self._pages)

    @property
    def search_index(self) -> SearchIndex:
        return self._index

    def add_module_source(self, source: str, module_name: str) -> ModuleDoc:
        """Extract and index a module's documentation.

        Args:
            source: Python source code.
            module_name: Module name.

        Returns:
            Extracted ModuleDoc.
        """
        doc = self._extractor.extract_from_source(source, module_name)
        self._modules.append(doc)

        # Generate page
        md_content = self._extractor.to_markdown(doc)
        page_path = f"api/{module_name}.md"
        self._pages[page_path] = md_content

        # Index for search
        self._index.add(
            doc_id=module_name,
            title=module_name,
            content=md_content,
            path=page_path,
        )

        return doc

    def add_page(self, path: str, content: str, title: str = "") -> None:
        """Add a custom page.

        Args:
            path: Page path.
            content: Markdown content.
            title: Page title for search.
        """
        self._pages[path] = content
        self._index.add(
            doc_id=path,
            title=title or path,
            content=content,
            path=path,
        )

    def add_extra_css(self, path: str) -> None:
        """Add extra CSS file."""
        self._extra_css.append(path)

    def add_extra_javascript(self, path: str) -> None:
        """Add extra JavaScript file."""
        self._extra_js.append(path)

    def generate_config(self) -> SiteConfig:
        """Generate site configuration."""
        nav: list[dict[str, Any]] = [{"Home": "index.md"}]

        # API reference nav
        api_nav = []
        for module in sorted(self._modules, key=lambda x: x.name):
            api_nav.append({module.name: f"api/{module.name}.md"})
        if api_nav:
            nav.append({"API Reference": api_nav})

        # Add other pages to nav if not already there
        other_pages = []
        nav_paths = set()

        def collect_paths(item):
            if isinstance(item, str):
                nav_paths.add(item)
            elif isinstance(item, dict):
                for v in item.values():
                    collect_paths(v)
            elif isinstance(item, list):
                for i in item:
                    collect_paths(i)

        collect_paths(nav)

        for path in sorted(self._pages.keys()):
            if path not in nav_paths and not path.startswith("api/"):
                name = path.split("/")[-1].replace(".md", "").title()
                other_pages.append({name: path})

        if other_pages:
            nav.append({"More": other_pages})

        return SiteConfig(
            title=self._title,
            nav=nav,
            extra_css=list(self._extra_css),
            extra_javascript=list(self._extra_js),
        )

    def generate_pages(self) -> dict[str, str]:
        """Get all generated pages."""
        return dict(self._pages)

    def to_mkdocs_yaml(self) -> str:
        """Generate mkdocs.yml content."""
        config = self.generate_config()
        lines = [
            f"site_name: {config.title}",
            "theme:",
            f"  name: {config.theme}",
            "  palette:",
            "    scheme: slate",
            "    primary: indigo",
            "    accent: indigo",
            "  features:",
            "    - navigation.tabs",
            "    - navigation.sections",
            "    - navigation.top",
            "    - search.suggest",
            "    - search.highlight",
            "    - content.code.copy",
            "plugins:",
        ]
        for plugin in config.plugins:
            lines.append(f"  - {plugin}")

        if config.extra_css:
            lines.append("extra_css:")
            for css in config.extra_css:
                lines.append(f"  - {css}")

        if config.extra_javascript:
            lines.append("extra_javascript:")
            for js in config.extra_javascript:
                lines.append(f"  - {js}")

        lines.append("nav:")
        for item in config.nav:
            self._render_nav_item(lines, item, indent=2)

        return "\n".join(lines)

    def _render_nav_item(self, lines: list[str], item: Any, indent: int) -> None:
        if isinstance(item, dict):
            for key, val in item.items():
                if isinstance(val, list):
                    lines.append(f"{' ' * indent}- {key}:")
                    for sub in val:
                        self._render_nav_item(lines, sub, indent + 2)
                else:
                    lines.append(f"{' ' * indent}- {key}: {val}")
        elif isinstance(item, str):
            lines.append(f"{' ' * indent}- {item}")


__all__ = ["SiteConfig", "SiteGenerator"]
