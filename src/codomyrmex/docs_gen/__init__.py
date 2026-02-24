"""Documentation generation module for Codomyrmex.

Provides tools for extracting API documentation from Python source,
building searchable in-memory indices, and generating static documentation
site configuration.

Components:
    - APIDocExtractor: Extract docstrings, signatures, and metadata from Python modules
    - SearchIndex: In-memory inverted index for fast full-text doc search
    - SiteGenerator: Orchestrate extraction, indexing, and site config generation
"""

from codomyrmex.docs_gen.api_doc_extractor import (
    APIDocExtractor,
    ClassDoc,
    FunctionDoc,
    ModuleDoc,
)
from codomyrmex.docs_gen.search_index import (
    IndexEntry,
    SearchIndex,
    SearchResult,
)
from codomyrmex.docs_gen.site_generator import (
    SiteConfig,
    SiteGenerator,
)

__all__ = [
    "APIDocExtractor",
    "ClassDoc",
    "FunctionDoc",
    "ModuleDoc",
    "IndexEntry",
    "SearchIndex",
    "SearchResult",
    "SiteConfig",
    "SiteGenerator",
]
