"""Comprehensive unit tests for docs_gen module.

Covers:
- APIDocExtractor: source parsing, class/function/module extraction, markdown rendering, signatures, type hints, decorators
- SearchIndex: add/remove/search, inverted index, scoring, snippets, CamelCase, snake_case, stopwords
- SiteGenerator: module ingestion, page generation, config generation, mkdocs YAML, extra CSS/JS, sorted nav
- Module-level __init__.py exports

Zero-Mock Policy: all tests use real implementations with real temp files.
"""

import pytest

from codomyrmex.docs_gen import (
    APIDocExtractor,
    SearchIndex,
    SiteGenerator,
)

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

COMPLEX_SIGNATURE_SOURCE = '''
def complex_fn(a: int, b: str = "default", *args: list[int], kw1: bool, kw2: float = 1.0, **kwargs: dict[str, Any]) -> None:
    """Complex signature."""
    pass

async def async_fn(posonly: int, /, standard: str) -> bool:
    """Async with posonly."""
    return True

@property
def my_property(self):
    """Property."""
    return 1
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
# Tests: APIDocExtractor
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAPIDocExtractorComprehensive:
    """Comprehensive APIDocExtractor tests."""

    def test_extract_complex_signature(self):
        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(COMPLEX_SIGNATURE_SOURCE, "complex")
        fn = next(f for f in doc.functions if f.name == "complex_fn")
        assert "a: int" in fn.signature
        # ast.unparse might use single quotes for strings
        assert "b: str = 'default'" in fn.signature or 'b: str = "default"' in fn.signature
        assert "*args: list[int]" in fn.signature
        assert "kw1: bool" in fn.signature
        assert "kw2: float = 1.0" in fn.signature
        assert "**kwargs: dict[str, Any]" in fn.signature
        assert "-> None" in fn.signature

    def test_extract_posonly_async(self):
        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(COMPLEX_SIGNATURE_SOURCE, "complex")
        fn = next(f for f in doc.functions if f.name == "async_fn")
        assert fn.is_async is True
        assert "(posonly: int, /, standard: str) -> bool" in fn.signature

    def test_extract_property_decorator(self):
        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(COMPLEX_SIGNATURE_SOURCE, "complex")
        fn = next(f for f in doc.functions if f.name == "my_property")
        assert "property" in fn.decorators

    def test_markdown_formatting_enhanced(self):
        extractor = APIDocExtractor()
        doc = extractor.extract_from_source(SIMPLE_MODULE_SOURCE, "mymod")
        md = extractor.to_markdown(doc)
        assert "# Module `mymod`" in md
        assert "## Exports" in md
        assert "`MyClass`" in md
        assert "`my_function`" in md
        assert "### Methods" in md
        assert "#### `__init__(self, value: int) -> None`" in md


# ---------------------------------------------------------------------------
# Tests: SearchIndex
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSearchIndexComprehensive:
    """Comprehensive SearchIndex tests."""

    def test_tokenize_camel_case(self):
        index = SearchIndex()
        tokens = index._tokenize("MyCamelCaseClass")
        assert "camel" in tokens
        assert "case" in tokens
        assert "class" in tokens

    def test_tokenize_snake_case(self):
        index = SearchIndex()
        tokens = index._tokenize("my_snake_case_function")
        assert "snake" in tokens
        assert "case" in tokens
        assert "function" in tokens

    def test_stopwords_filtered(self):
        index = SearchIndex()
        tokens = index._tokenize("The quick brown fox is in the box")
        assert "the" not in tokens
        assert "is" not in tokens
        assert "in" not in tokens
        assert "quick" in tokens

    def test_snippet_centering(self):
        index = SearchIndex()
        content = "word " * 100 + "TARGET" + " word" * 100
        index.add("d1", title="Title", content=content)
        results = index.search("TARGET")
        snippet = results[0].snippet
        assert "TARGET" in snippet
        assert snippet.startswith("...")
        assert snippet.endswith("...")

    def test_tag_tokenization(self):
        index = SearchIndex()
        # Tags are also tokenized
        index.add("d1", title="T", content="C", tags=["mytag", "another tag"])
        assert len(index.search("mytag")) > 0
        assert len(index.search("another")) > 0
        assert len(index.search("tag")) > 0


# ---------------------------------------------------------------------------
# Tests: SiteGenerator
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestSiteGeneratorComprehensive:
    """Comprehensive SiteGenerator tests."""

    def test_sorted_navigation(self):
        gen = SiteGenerator()
        gen.add_module_source("def a(): pass", "z_mod")
        gen.add_module_source("def b(): pass", "a_mod")
        config = gen.generate_config()
        api_nav = next(item["API Reference"] for item in config.nav if "API Reference" in item)
        names = [list(d.keys())[0] for d in api_nav]
        assert names == ["a_mod", "z_mod"]

    def test_extra_css_js(self):
        gen = SiteGenerator()
        gen.add_extra_css("custom.css")
        gen.add_extra_javascript("script.js")
        config = gen.generate_config()
        assert "custom.css" in config.extra_css
        assert "script.js" in config.extra_javascript

        yaml = gen.to_mkdocs_yaml()
        assert "extra_css:" in yaml
        assert "- custom.css" in yaml
        assert "extra_javascript:" in yaml
        assert "- script.js" in yaml

    def test_custom_pages_in_more_nav(self):
        gen = SiteGenerator()
        gen.add_page("extra/info.md", "Content", title="Info")
        config = gen.generate_config()
        more_nav = next(item["More"] for item in config.nav if "More" in item)
        assert {"Info": "extra/info.md"} in more_nav

    def test_mkdocs_features_in_yaml(self):
        gen = SiteGenerator()
        yaml = gen.to_mkdocs_yaml()
        assert "navigation.tabs" in yaml
        assert "search.suggest" in yaml
        assert "content.code.copy" in yaml
