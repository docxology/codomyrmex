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
    """

    title: str = "Codomyrmex Documentation"
    theme: str = "material"
    nav: list[dict[str, Any]] = field(default_factory=list)
    plugins: list[str] = field(default_factory=lambda: ["search", "mkdocstrings"])
    base_url: str = "/"


class SiteGenerator:
    """Generate documentation site configuration and content.

    Example::

        gen = SiteGenerator(title="My Docs")
        gen.add_module_source(source, "mymodule")
        config = gen.generate_config()
        pages = gen.generate_pages()
    """

    def __init__(self, title: str = "Codomyrmex Documentation") -> None:
        """Initialize this instance."""
        self._title = title
        self._extractor = APIDocExtractor()
        self._index = SearchIndex()
        self._modules: list[ModuleDoc] = []
        self._pages: dict[str, str] = {}

    @property
    def module_count(self) -> int:
        """module Count ."""
        return len(self._modules)

    @property
    def page_count(self) -> int:
        """page Count ."""
        return len(self._pages)

    @property
    def search_index(self) -> SearchIndex:
        """search Index ."""
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

    def generate_config(self) -> SiteConfig:
        """Generate site configuration."""
        nav: list[dict[str, Any]] = [{"Home": "index.md"}]

        # API reference nav
        api_nav = []
        for module in self._modules:
            api_nav.append({module.name: f"api/{module.name}.md"})
        if api_nav:
            nav.append({"API Reference": api_nav})

        return SiteConfig(
            title=self._title,
            nav=nav,
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
            "plugins:",
        ]
        for plugin in config.plugins:
            lines.append(f"  - {plugin}")
        lines.append("nav:")
        for item in config.nav:
            for key, val in item.items():
                if isinstance(val, list):
                    lines.append(f"  - {key}:")
                    for sub in val:
                        for sk, sv in sub.items():
                            lines.append(f"    - {sk}: {sv}")
                else:
                    lines.append(f"  - {key}: {val}")
        return "\n".join(lines)


__all__ = ["SiteConfig", "SiteGenerator"]
