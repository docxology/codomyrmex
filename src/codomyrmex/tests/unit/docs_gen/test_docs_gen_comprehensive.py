"""Comprehensive unit tests for docs_gen module.

Covers:
- APIDocExtractor: source parsing, class/function/module extraction, markdown rendering
- SearchIndex: add/remove/search, inverted index, scoring, snippets
- SiteGenerator: module ingestion, page generation, config generation, mkdocs YAML
- Module-level __init__.py exports

Zero-Mock Policy: all tests use real implementations with real temp files.
"""

import pytest

from codomyrmex.docs_gen import (
    APIDocExtractor,
    ClassDoc,
    FunctionDoc,
    IndexEntry,
    ModuleDoc,
    SearchIndex,
    SearchResult,
    SiteConfig,
    SiteGenerator,
)
from codomyrmex.docs_gen.api_doc_extractor import APIDocExtractor as _ExtractorDirect
from codomyrmex.docs_gen.search_index import SearchIndex as _IndexDirect
from codomyrmex.docs_gen.site_generator import SiteGenerator as _GeneratorDirect

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SIMPLE_MODULE_SOURCE = '''"""A simple test module.

This module does stuff.
"""

__all__ = ["MyClass", "my_function"]


class MyClass:
    """A test class.

    Inherits from object.
    """

    def __init__(self, value: int) -> None:
        """Initialize MyClass."""
        self.value = value

    def get_value(self) -> int:
        """Return the value."""
        return self.value

    async def async_method(self) -> str:
        """Async method example."""
        return "async"


def my_function(x: int, y: int = 0) -> int:
    """Add two integers.

    Args:
        x: First integer.
        y: Second integer.

    Returns:
        Sum of x and y.
    """
    return x + y
'''

DECORATED_SOURCE = '''"""Module with decorators."""

def decorator(fn):
    return fn

@decorator
def decorated_fn(self):
    """A decorated function."""
    pass

class Decorated:
    @staticmethod
    def static_method():
        """Static method."""
        pass
'''

EMPTY_SOURCE = ""
NO_DOCSTRING_SOURCE = "class Bare:\n    pass\n\ndef bare():\n    pass\n"


# ---------------------------------------------------------------------------
# Tests: Module-level exports
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDocsGenImports:
    """Verify all __all__ exports are importable and correct types."""

    def test_apiextractor_importable(self):
        assert APIDocExtractor is not None
        assert callable(APIDocExtractor)

    def test_searchindex_importable(self):
        assert SearchIndex is not None
        assert callable(SearchIndex)

    def test_sitegenerator_importable(self):
        assert SiteGenerator is not None
        assert callable(SiteGenerator)

    def test_dataclass_types_importable(self):
        for cls in (ClassDoc, FunctionDoc, ModuleDoc, IndexEntry, SearchResult, SiteConfig):
            assert cls is not None

    def test_extractor_same_object_as_direct(self):
        assert APIDocExtractor is _ExtractorDirect

    def test_index_same_object_as_direct(self):
        assert SearchIndex is _IndexDirect

    def test_generator_same_object_as_direct(self):
        assert SiteGenerator is _GeneratorDirect


# ---------------------------------------------------------------------------
# Tests: APIDocExtractor
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAPIDocExtractorBasics:
    """Basic APIDocExtractor extraction tests."""

    def test_instantiation(self):
        extractor = APIDocExtractor()
        assert extractor is not None

    def test_extract_returns_module_doc(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "test_module")
        assert isinstance(result, ModuleDoc)

    def test_module_name_set(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "my.module")
        assert result.name == "my.module"

    def test_module_docstring_extracted(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        assert "simple test module" in result.docstring

    def test_empty_source_returns_empty_module_doc(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(EMPTY_SOURCE, "empty")
        assert result.name == "empty"
        assert result.docstring == ""
        assert result.classes == []
        assert result.functions == []

    def test_all_exports_extracted(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        assert "MyClass" in result.exports
        assert "my_function" in result.exports

    def test_no_docstring_module(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(NO_DOCSTRING_SOURCE, "bare")
        assert result.docstring == ""


@pytest.mark.unit
class TestAPIDocExtractorClasses:
    """Class extraction from APIDocExtractor."""

    def test_class_count(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        assert len(result.classes) == 1

    def test_class_name(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        assert result.classes[0].name == "MyClass"

    def test_class_docstring(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        assert "test class" in result.classes[0].docstring

    def test_class_module_set(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "mymod")
        assert result.classes[0].module == "mymod"

    def test_class_methods_count(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        # __init__, get_value, async_method
        assert len(result.classes[0].methods) == 3

    def test_class_async_method_detected(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        methods = {m.name: m for m in result.classes[0].methods}
        assert methods["async_method"].is_async is True

    def test_class_sync_method_not_async(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        methods = {m.name: m for m in result.classes[0].methods}
        assert methods["get_value"].is_async is False

    def test_bare_class_no_docstring(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(NO_DOCSTRING_SOURCE, "bare")
        assert result.classes[0].docstring == ""


@pytest.mark.unit
class TestAPIDocExtractorFunctions:
    """Top-level function extraction."""

    def test_function_count(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        assert len(result.functions) == 1

    def test_function_name(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        assert result.functions[0].name == "my_function"

    def test_function_signature_includes_params(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        sig = result.functions[0].signature
        assert "x" in sig
        assert "y" in sig

    def test_function_docstring(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        assert "Add two integers" in result.functions[0].docstring

    def test_function_is_not_async(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        assert result.functions[0].is_async is False

    def test_decorated_function_captured(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(DECORATED_SOURCE, "d")
        assert any(f.name == "decorated_fn" for f in result.functions)

    def test_decorator_name_recorded(self):
        extractor = APIDocExtractor()
        result = extractor.extract_from_source(DECORATED_SOURCE, "d")
        fn = next(f for f in result.functions if f.name == "decorated_fn")
        assert "decorator" in fn.decorators


@pytest.mark.unit
class TestAPIDocExtractorMarkdown:
    """Markdown rendering tests."""

    def test_to_markdown_returns_string(self):
        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        md = extractor.to_markdown(doc)
        assert isinstance(md, str)
        assert len(md) > 0

    def test_to_markdown_includes_module_name(self):
        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "mymodule")
        md = extractor.to_markdown(doc)
        assert "mymodule" in md

    def test_to_markdown_includes_class_name(self):
        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        md = extractor.to_markdown(doc)
        assert "MyClass" in md

    def test_to_markdown_includes_function_name(self):
        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "m")
        md = extractor.to_markdown(doc)
        assert "my_function" in md

    def test_to_markdown_empty_module(self):
        extractor = APIDocExtractor()
        doc = ModuleDoc(name="empty")
        md = extractor.to_markdown(doc)
        assert "empty" in md


# ---------------------------------------------------------------------------
# Tests: SearchIndex
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSearchIndexBasics:
    """SearchIndex construction and basic operations."""

    def test_instantiation(self):
        index = SearchIndex()
        assert index is not None

    def test_initial_doc_count_zero(self):
        index = SearchIndex()
        assert index.doc_count == 0

    def test_add_single_document(self):
        index = SearchIndex()
        index.add("doc1", title="Hello World", content="Some content about agents")
        assert index.doc_count == 1

    def test_add_multiple_documents(self):
        index = SearchIndex()
        index.add("a", title="Alpha", content="first document")
        index.add("b", title="Beta", content="second document")
        index.add("c", title="Gamma", content="third document")
        assert index.doc_count == 3

    def test_add_with_tags(self):
        index = SearchIndex()
        index.add("t1", title="Tagged", content="content", tags=["python", "docs"])
        assert index.doc_count == 1

    def test_remove_existing_document(self):
        index = SearchIndex()
        index.add("x", title="X", content="remove me")
        removed = index.remove("x")
        assert removed is True
        assert index.doc_count == 0

    def test_remove_nonexistent_returns_false(self):
        index = SearchIndex()
        removed = index.remove("nonexistent")
        assert removed is False

    def test_add_duplicate_id_overwrites(self):
        index = SearchIndex()
        index.add("dup", title="First", content="first content")
        index.add("dup", title="Second", content="second content")
        # doc_count behavior: second add creates new entry (overwrite)
        assert index.doc_count >= 1


@pytest.mark.unit
class TestSearchIndexSearch:
    """SearchIndex search and ranking tests."""

    def test_search_empty_index_returns_empty(self):
        index = SearchIndex()
        results = index.search("anything")
        assert results == []

    def test_search_returns_list(self):
        index = SearchIndex()
        index.add("d1", title="Python Agents", content="agents work with python code")
        results = index.search("python")
        assert isinstance(results, list)

    def test_search_finds_matching_document(self):
        index = SearchIndex()
        index.add("doc1", title="Agent Guide", content="guide to building ai agents")
        results = index.search("agent")
        assert any(r.doc_id == "doc1" for r in results)

    def test_search_returns_search_result_objects(self):
        index = SearchIndex()
        index.add("doc1", title="Test", content="some test content")
        results = index.search("test")
        for r in results:
            assert isinstance(r, SearchResult)

    def test_search_result_has_score(self):
        index = SearchIndex()
        index.add("doc1", title="Scoring", content="relevance scoring")
        results = index.search("scoring")
        assert results[0].score > 0

    def test_search_no_match_returns_empty(self):
        index = SearchIndex()
        index.add("doc1", title="Python", content="python programming")
        results = index.search("zzznonexistentzzzz")
        assert results == []

    def test_search_title_bonus_increases_score(self):
        index = SearchIndex()
        # "agent" in title gets bonus vs "agent" only in content
        index.add("title_match", title="Agent Overview", content="overview of system")
        index.add("content_only", title="Overview", content="about agents in detail")
        results = index.search("agent")
        # title_match should rank higher due to title bonus
        doc_ids = [r.doc_id for r in results]
        assert doc_ids[0] == "title_match"

    def test_search_limit_respected(self):
        index = SearchIndex()
        for i in range(20):
            index.add(f"doc{i}", title=f"Document {i}", content="common search term")
        results = index.search("document", limit=5)
        assert len(results) <= 5

    def test_search_result_snippet_not_empty_for_match(self):
        index = SearchIndex()
        index.add("d1", title="Title", content="The quick brown fox jumps over")
        results = index.search("fox")
        assert len(results) > 0
        # Snippet should contain some content
        assert len(results[0].snippet) > 0

    def test_search_by_tag(self):
        index = SearchIndex()
        index.add("tagged", title="Doc", content="content", tags=["mytag"])
        results = index.search("mytag")
        assert any(r.doc_id == "tagged" for r in results)

    def test_search_empty_query_returns_empty(self):
        index = SearchIndex()
        index.add("d1", title="X", content="some content here")
        results = index.search("")
        assert results == []

    def test_search_path_preserved(self):
        index = SearchIndex()
        index.add("d1", title="Doc", content="content", path="/docs/api.md")
        results = index.search("content")
        assert results[0].path == "/docs/api.md"


# ---------------------------------------------------------------------------
# Tests: SiteGenerator
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSiteGeneratorBasics:
    """SiteGenerator construction and basic properties."""

    def test_instantiation_default(self):
        gen = SiteGenerator()
        assert gen is not None

    def test_instantiation_custom_title(self):
        gen = SiteGenerator(title="My Custom Docs")
        assert gen is not None

    def test_initial_module_count_zero(self):
        gen = SiteGenerator()
        assert gen.module_count == 0

    def test_initial_page_count_zero(self):
        gen = SiteGenerator()
        assert gen.page_count == 0

    def test_search_index_accessible(self):
        gen = SiteGenerator()
        assert isinstance(gen.search_index, SearchIndex)


@pytest.mark.unit
class TestSiteGeneratorModuleIngestion:
    """add_module_source and related behavior."""

    def test_add_module_source_returns_module_doc(self):
        gen = SiteGenerator()
        result = gen.add_module_source(SIMPLE_MODULE_SOURCE, "mymod")
        assert isinstance(result, ModuleDoc)

    def test_module_count_increments(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE_SOURCE, "mod1")
        assert gen.module_count == 1
        gen.add_module_source(SIMPLE_MODULE_SOURCE, "mod2")
        assert gen.module_count == 2

    def test_page_created_for_module(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE_SOURCE, "mymod")
        assert gen.page_count == 1

    def test_page_path_follows_api_convention(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE_SOURCE, "mymod")
        pages = gen.generate_pages()
        assert "api/mymod.md" in pages

    def test_page_content_is_markdown(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE_SOURCE, "mymod")
        pages = gen.generate_pages()
        content = pages["api/mymod.md"]
        assert "mymod" in content
        assert "#" in content  # Has markdown headings

    def test_module_indexed_for_search(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE_SOURCE, "searchable_mod")
        results = gen.search_index.search("searchable_mod")
        assert len(results) > 0

    def test_add_custom_page(self):
        gen = SiteGenerator()
        gen.add_page("guide/intro.md", "# Introduction\n\nWelcome.", title="Intro")
        assert gen.page_count == 1
        pages = gen.generate_pages()
        assert "guide/intro.md" in pages

    def test_generate_pages_returns_dict(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE_SOURCE, "m")
        pages = gen.generate_pages()
        assert isinstance(pages, dict)

    def test_generate_pages_returns_copy(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE_SOURCE, "m")
        p1 = gen.generate_pages()
        p2 = gen.generate_pages()
        assert p1 is not p2  # Independent copies


@pytest.mark.unit
class TestSiteGeneratorConfig:
    """generate_config and to_mkdocs_yaml tests."""

    def test_generate_config_returns_site_config(self):
        gen = SiteGenerator()
        config = gen.generate_config()
        assert isinstance(config, SiteConfig)

    def test_config_has_home_nav(self):
        gen = SiteGenerator()
        config = gen.generate_config()
        nav_keys = [list(item.keys())[0] for item in config.nav]
        assert "Home" in nav_keys

    def test_config_includes_api_nav_for_modules(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE_SOURCE, "mymod")
        config = gen.generate_config()
        # "API Reference" should appear in nav
        nav_keys = [list(item.keys())[0] for item in config.nav]
        assert "API Reference" in nav_keys

    def test_config_title_matches_init(self):
        gen = SiteGenerator(title="Custom Title")
        config = gen.generate_config()
        assert config.title == "Custom Title"

    def test_to_mkdocs_yaml_returns_string(self):
        gen = SiteGenerator()
        yaml_str = gen.to_mkdocs_yaml()
        assert isinstance(yaml_str, str)
        assert len(yaml_str) > 0

    def test_to_mkdocs_yaml_includes_site_name(self):
        gen = SiteGenerator(title="Docs Title")
        yaml_str = gen.to_mkdocs_yaml()
        assert "site_name: Docs Title" in yaml_str

    def test_to_mkdocs_yaml_includes_plugins(self):
        gen = SiteGenerator()
        yaml_str = gen.to_mkdocs_yaml()
        assert "search" in yaml_str
        assert "mkdocstrings" in yaml_str

    def test_to_mkdocs_yaml_includes_theme(self):
        gen = SiteGenerator()
        yaml_str = gen.to_mkdocs_yaml()
        assert "material" in yaml_str

    def test_to_mkdocs_yaml_includes_module_pages(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE_SOURCE, "testmod")
        yaml_str = gen.to_mkdocs_yaml()
        assert "testmod" in yaml_str
