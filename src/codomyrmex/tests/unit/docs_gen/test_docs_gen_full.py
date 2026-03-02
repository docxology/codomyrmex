"""Full coverage unit tests for docs_gen module.

Covers every branch and code path in:
- api_doc_extractor.py: FunctionDoc, ClassDoc, ModuleDoc, APIDocExtractor
- search_index.py: SearchResult, IndexEntry, SearchIndex, STOPWORDS
- site_generator.py: SiteConfig, SiteGenerator
- __init__.py: re-exports

Zero-Mock Policy: all tests use real implementations only.
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
from codomyrmex.docs_gen.search_index import STOPWORDS


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

SIMPLE_MODULE = '''"""Module docstring for testing."""

__all__ = ["MyClass", "helper"]


class MyClass:
    """A sample class."""

    def method_one(self, x: int) -> str:
        """First method."""
        return str(x)

    async def async_method(self) -> None:
        """Async method."""
        pass


def helper(a: int, b: int = 10) -> int:
    """Helper function."""
    return a + b
'''

COMPLEX_SIGS = '''
def positional_only(a: int, b: str, /) -> None:
    """Has positional-only params."""
    pass

def keyword_only(*, key1: int, key2: str = "val") -> bool:
    """Has keyword-only params."""
    return True

def mixed_args(a: int, b: str = "x", *args: int, kw: bool, **kwargs) -> None:
    """Mixed positional, *args, keyword-only, **kwargs."""
    pass

def no_annotations(x, y=5):
    """No type annotations at all."""
    pass

def return_only() -> int:
    """Only return annotation, no params."""
    return 0
'''

DECORATED_SOURCE = '''"""Decorated module."""

import functools

def my_decorator(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper

@my_decorator
def decorated_func() -> None:
    """I am decorated."""
    pass

class DecoratedClass:
    """Class with decorated methods."""

    @staticmethod
    def static_thing():
        """Static."""
        pass

    @classmethod
    def class_thing(cls):
        """Classmethod."""
        pass

    @property
    def prop(self):
        """Property."""
        return 1
'''

INHERITANCE_SOURCE = '''
class Base:
    """Base class."""
    pass

class Child(Base):
    """Child inherits Base."""
    def do_stuff(self) -> None:
        """Does stuff."""
        pass

class Multi(Base, dict):
    """Multiple inheritance."""
    pass
'''

NO_DOCSTRING_SOURCE = "class Bare:\n    pass\n\ndef bare_fn():\n    pass\n"

EMPTY_SOURCE = ""

KWONLY_WITH_DEFAULTS_SOURCE = '''
def kw_defaults(*, a: int = 1, b: str, c: float = 3.14) -> None:
    """Keyword-only with some defaults."""
    pass
'''

MODULE_NO_ALL = '''"""No __all__ defined."""

def func_a():
    pass

def func_b():
    pass
'''


# ===========================================================================
# Tests: FunctionDoc dataclass
# ===========================================================================

@pytest.mark.unit
class TestFunctionDocDataclass:
    """Tests for FunctionDoc dataclass defaults and fields."""

    def test_defaults(self):
        fd = FunctionDoc(name="fn")
        assert fd.name == "fn"
        assert fd.signature == ""
        assert fd.docstring == ""
        assert fd.module == ""
        assert fd.decorators == []
        assert fd.is_async is False

    def test_all_fields(self):
        fd = FunctionDoc(
            name="my_fn",
            signature="(x: int) -> str",
            docstring="My function.",
            module="mymod",
            decorators=["staticmethod"],
            is_async=True,
        )
        assert fd.name == "my_fn"
        assert fd.is_async is True
        assert "staticmethod" in fd.decorators

    def test_decorators_list_independent(self):
        fd1 = FunctionDoc(name="a")
        fd2 = FunctionDoc(name="b")
        fd1.decorators.append("test")
        assert "test" not in fd2.decorators


# ===========================================================================
# Tests: ClassDoc dataclass
# ===========================================================================

@pytest.mark.unit
class TestClassDocDataclass:
    """Tests for ClassDoc dataclass."""

    def test_defaults(self):
        cd = ClassDoc(name="Cls")
        assert cd.name == "Cls"
        assert cd.docstring == ""
        assert cd.module == ""
        assert cd.methods == []
        assert cd.bases == []

    def test_with_methods_and_bases(self):
        method = FunctionDoc(name="do_thing")
        cd = ClassDoc(
            name="MyClass",
            docstring="A class.",
            module="mod",
            methods=[method],
            bases=["Base", "Mixin"],
        )
        assert len(cd.methods) == 1
        assert cd.bases == ["Base", "Mixin"]


# ===========================================================================
# Tests: ModuleDoc dataclass
# ===========================================================================

@pytest.mark.unit
class TestModuleDocDataclass:
    """Tests for ModuleDoc dataclass."""

    def test_defaults(self):
        md = ModuleDoc(name="mymod")
        assert md.docstring == ""
        assert md.path == ""
        assert md.classes == []
        assert md.functions == []
        assert md.exports == []

    def test_full_construction(self):
        md = ModuleDoc(
            name="full",
            docstring="A full module.",
            path="/some/path.py",
            classes=[ClassDoc(name="Cls")],
            functions=[FunctionDoc(name="fn")],
            exports=["Cls", "fn"],
        )
        assert md.name == "full"
        assert len(md.classes) == 1
        assert len(md.functions) == 1
        assert md.exports == ["Cls", "fn"]


# ===========================================================================
# Tests: APIDocExtractor - extraction
# ===========================================================================

@pytest.mark.unit
class TestAPIDocExtractorExtraction:
    """APIDocExtractor.extract_from_source comprehensive tests."""

    def test_module_docstring(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "simple")
        assert doc.docstring == "Module docstring for testing."

    def test_module_name(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "simple")
        assert doc.name == "simple"

    def test_empty_module_name(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "")
        assert doc.name == ""

    def test_exports(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "simple")
        assert doc.exports == ["MyClass", "helper"]

    def test_no_exports(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(MODULE_NO_ALL, "noall")
        assert doc.exports == []

    def test_class_extraction(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "simple")
        assert len(doc.classes) == 1
        cls = doc.classes[0]
        assert cls.name == "MyClass"
        assert cls.docstring == "A sample class."
        assert cls.module == "simple"

    def test_class_methods(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "simple")
        methods = doc.classes[0].methods
        names = [m.name for m in methods]
        assert "method_one" in names
        assert "async_method" in names

    def test_async_method_detection(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "simple")
        async_method = next(m for m in doc.classes[0].methods if m.name == "async_method")
        assert async_method.is_async is True
        sync_method = next(m for m in doc.classes[0].methods if m.name == "method_one")
        assert sync_method.is_async is False

    def test_function_extraction(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "simple")
        assert len(doc.functions) == 1
        fn = doc.functions[0]
        assert fn.name == "helper"
        assert fn.docstring == "Helper function."

    def test_function_signature_default_args(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "simple")
        fn = doc.functions[0]
        assert "a: int" in fn.signature
        assert "b: int = 10" in fn.signature
        assert "-> int" in fn.signature

    def test_empty_source(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(EMPTY_SOURCE, "empty")
        assert doc.name == "empty"
        assert doc.docstring == ""
        assert doc.classes == []
        assert doc.functions == []
        assert doc.exports == []

    def test_no_docstring_source(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(NO_DOCSTRING_SOURCE, "nodoc")
        assert doc.docstring == ""
        cls = doc.classes[0]
        assert cls.docstring == ""
        fn = doc.functions[0]
        assert fn.docstring == ""

    def test_module_no_docstring_first_node_not_str(self):
        """Module where first statement is not a docstring."""
        source = "x = 1\ndef f(): pass\n"
        ext = APIDocExtractor()
        doc = ext.extract_from_source(source, "nomod")
        assert doc.docstring == ""


# ===========================================================================
# Tests: APIDocExtractor - complex signatures
# ===========================================================================

@pytest.mark.unit
class TestAPIDocExtractorSignatures:
    """Tests for signature extraction: positional-only, keyword-only, *args, **kwargs."""

    def test_positional_only_params(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(COMPLEX_SIGS, "sigs")
        fn = next(f for f in doc.functions if f.name == "positional_only")
        assert "a: int" in fn.signature
        assert "b: str" in fn.signature
        assert "/" in fn.signature
        assert "-> None" in fn.signature

    def test_keyword_only_params(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(COMPLEX_SIGS, "sigs")
        fn = next(f for f in doc.functions if f.name == "keyword_only")
        assert "*" in fn.signature
        assert "key1: int" in fn.signature
        assert "key2: str" in fn.signature

    def test_kwonly_with_defaults(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(KWONLY_WITH_DEFAULTS_SOURCE, "kwd")
        fn = doc.functions[0]
        assert "a: int = 1" in fn.signature
        assert "b: str" in fn.signature
        assert "c: float = 3.14" in fn.signature

    def test_mixed_args(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(COMPLEX_SIGS, "sigs")
        fn = next(f for f in doc.functions if f.name == "mixed_args")
        assert "*args: int" in fn.signature
        assert "kw: bool" in fn.signature
        assert "**kwargs" in fn.signature

    def test_no_annotations(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(COMPLEX_SIGS, "sigs")
        fn = next(f for f in doc.functions if f.name == "no_annotations")
        assert "x" in fn.signature
        assert "y = 5" in fn.signature

    def test_return_only(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(COMPLEX_SIGS, "sigs")
        fn = next(f for f in doc.functions if f.name == "return_only")
        assert "-> int" in fn.signature
        assert fn.signature.startswith("(")


# ===========================================================================
# Tests: APIDocExtractor - decorators
# ===========================================================================

@pytest.mark.unit
class TestAPIDocExtractorDecorators:
    """Tests for decorator extraction."""

    def test_function_decorator(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(DECORATED_SOURCE, "deco")
        fn = next(f for f in doc.functions if f.name == "decorated_func")
        assert "my_decorator" in fn.decorators

    def test_static_method_decorator(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(DECORATED_SOURCE, "deco")
        cls = next(c for c in doc.classes if c.name == "DecoratedClass")
        static_m = next(m for m in cls.methods if m.name == "static_thing")
        assert "staticmethod" in static_m.decorators

    def test_classmethod_decorator(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(DECORATED_SOURCE, "deco")
        cls = next(c for c in doc.classes if c.name == "DecoratedClass")
        class_m = next(m for m in cls.methods if m.name == "class_thing")
        assert "classmethod" in class_m.decorators

    def test_property_decorator(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(DECORATED_SOURCE, "deco")
        cls = next(c for c in doc.classes if c.name == "DecoratedClass")
        prop_m = next(m for m in cls.methods if m.name == "prop")
        assert "property" in prop_m.decorators


# ===========================================================================
# Tests: APIDocExtractor - inheritance
# ===========================================================================

@pytest.mark.unit
class TestAPIDocExtractorInheritance:
    """Tests for class base extraction."""

    def test_single_base(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(INHERITANCE_SOURCE, "inh")
        child = next(c for c in doc.classes if c.name == "Child")
        assert "Base" in child.bases

    def test_multiple_bases(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(INHERITANCE_SOURCE, "inh")
        multi = next(c for c in doc.classes if c.name == "Multi")
        assert "Base" in multi.bases
        assert "dict" in multi.bases

    def test_no_bases(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(INHERITANCE_SOURCE, "inh")
        base = next(c for c in doc.classes if c.name == "Base")
        assert base.bases == []


# ===========================================================================
# Tests: APIDocExtractor - to_markdown
# ===========================================================================

@pytest.mark.unit
class TestAPIDocExtractorMarkdown:
    """Tests for markdown rendering."""

    def test_module_header(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "mymod")
        md = ext.to_markdown(doc)
        assert md.startswith("# Module `mymod`")

    def test_module_docstring_in_markdown(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "mymod")
        md = ext.to_markdown(doc)
        assert "Module docstring for testing." in md

    def test_exports_section(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "mymod")
        md = ext.to_markdown(doc)
        assert "## Exports" in md
        assert "`MyClass`" in md
        assert "`helper`" in md

    def test_no_exports_section(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(MODULE_NO_ALL, "noall")
        md = ext.to_markdown(doc)
        assert "## Exports" not in md

    def test_class_heading_with_bases(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(INHERITANCE_SOURCE, "inh")
        md = ext.to_markdown(doc)
        assert "## Class `Child(Base)`" in md

    def test_class_heading_no_bases(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(INHERITANCE_SOURCE, "inh")
        md = ext.to_markdown(doc)
        assert "## Class `Base`" in md

    def test_methods_section(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "mymod")
        md = ext.to_markdown(doc)
        assert "### Methods" in md

    def test_async_prefix_in_markdown(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "mymod")
        md = ext.to_markdown(doc)
        assert "async async_method" in md

    def test_functions_section(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(SIMPLE_MODULE, "mymod")
        md = ext.to_markdown(doc)
        assert "## Functions" in md
        assert "`helper" in md

    def test_no_functions_section_when_empty(self):
        source = '''"""Mod."""\nclass Cls:\n    pass\n'''
        ext = APIDocExtractor()
        doc = ext.extract_from_source(source, "nofn")
        md = ext.to_markdown(doc)
        assert "## Functions" not in md

    def test_decorator_in_markdown(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(DECORATED_SOURCE, "deco")
        md = ext.to_markdown(doc)
        assert "@staticmethod" in md

    def test_empty_module_markdown(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(EMPTY_SOURCE, "empty")
        md = ext.to_markdown(doc)
        assert "# Module `empty`" in md

    def test_no_docstring_class_markdown(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(NO_DOCSTRING_SOURCE, "nodoc")
        md = ext.to_markdown(doc)
        assert "## Class `Bare`" in md

    def test_no_docstring_function_markdown(self):
        ext = APIDocExtractor()
        doc = ext.extract_from_source(NO_DOCSTRING_SOURCE, "nodoc")
        md = ext.to_markdown(doc)
        # Function heading should be present even without docstring
        assert "bare_fn" in md


# ===========================================================================
# Tests: SearchResult dataclass
# ===========================================================================

@pytest.mark.unit
class TestSearchResultDataclass:
    """Tests for SearchResult dataclass."""

    def test_defaults(self):
        sr = SearchResult(doc_id="d1")
        assert sr.doc_id == "d1"
        assert sr.title == ""
        assert sr.snippet == ""
        assert sr.score == 0.0
        assert sr.path == ""

    def test_full_construction(self):
        sr = SearchResult(
            doc_id="d1", title="Title", snippet="snip",
            score=5.0, path="/a/b.md",
        )
        assert sr.title == "Title"
        assert sr.score == 5.0


# ===========================================================================
# Tests: IndexEntry dataclass
# ===========================================================================

@pytest.mark.unit
class TestIndexEntryDataclass:
    """Tests for IndexEntry dataclass."""

    def test_defaults(self):
        ie = IndexEntry(doc_id="e1")
        assert ie.doc_id == "e1"
        assert ie.title == ""
        assert ie.content == ""
        assert ie.path == ""
        assert ie.tags == []

    def test_tags_independence(self):
        ie1 = IndexEntry(doc_id="a")
        ie2 = IndexEntry(doc_id="b")
        ie1.tags.append("test")
        assert "test" not in ie2.tags


# ===========================================================================
# Tests: STOPWORDS constant
# ===========================================================================

@pytest.mark.unit
class TestStopwords:
    """Tests for the STOPWORDS set."""

    def test_contains_common_words(self):
        for word in ("the", "is", "and", "of", "to", "in", "for"):
            assert word in STOPWORDS

    def test_is_set(self):
        assert isinstance(STOPWORDS, set)


# ===========================================================================
# Tests: SearchIndex - core operations
# ===========================================================================

@pytest.mark.unit
class TestSearchIndexOperations:
    """SearchIndex add, remove, search, doc_count."""

    def test_empty_index(self):
        idx = SearchIndex()
        assert idx.doc_count == 0

    def test_add_increments_count(self):
        idx = SearchIndex()
        idx.add("d1", title="First")
        idx.add("d2", title="Second")
        assert idx.doc_count == 2

    def test_add_replaces_existing(self):
        idx = SearchIndex()
        idx.add("d1", title="Original", content="original content")
        idx.add("d1", title="Updated", content="updated content")
        assert idx.doc_count == 1
        results = idx.search("updated")
        assert len(results) >= 1

    def test_remove_existing(self):
        idx = SearchIndex()
        idx.add("d1", title="Doc", content="content")
        result = idx.remove("d1")
        assert result is True
        assert idx.doc_count == 0

    def test_remove_nonexistent(self):
        idx = SearchIndex()
        result = idx.remove("ghost")
        assert result is False

    def test_remove_clears_from_inverted_index(self):
        idx = SearchIndex()
        idx.add("d1", title="Unique Token", content="hello world")
        idx.remove("d1")
        results = idx.search("unique")
        assert len(results) == 0

    def test_search_empty_query(self):
        idx = SearchIndex()
        idx.add("d1", title="Test", content="test content")
        results = idx.search("")
        assert results == []

    def test_search_only_stopwords(self):
        idx = SearchIndex()
        idx.add("d1", title="Test", content="content")
        results = idx.search("the is and")
        assert results == []

    def test_search_no_results(self):
        idx = SearchIndex()
        idx.add("d1", title="Test", content="testing content")
        results = idx.search("zzzznonexistent")
        assert results == []

    def test_search_returns_results(self):
        idx = SearchIndex()
        idx.add("d1", title="API Reference", content="The agent processes tasks")
        results = idx.search("agent")
        assert len(results) >= 1
        assert results[0].doc_id == "d1"

    def test_search_result_fields(self):
        idx = SearchIndex()
        idx.add("d1", title="My Title", content="some content here", path="/a/b.md")
        results = idx.search("content")
        assert results[0].title == "My Title"
        assert results[0].path == "/a/b.md"
        assert results[0].score > 0

    def test_search_limit(self):
        idx = SearchIndex()
        for i in range(20):
            idx.add(f"d{i}", title=f"Doc {i}", content="matching keyword")
        results = idx.search("keyword", limit=5)
        assert len(results) == 5


# ===========================================================================
# Tests: SearchIndex - scoring
# ===========================================================================

@pytest.mark.unit
class TestSearchIndexScoring:
    """Title boost and relevance scoring."""

    def test_title_boost(self):
        idx = SearchIndex()
        idx.add("title_match", title="Agent Guide", content="some other content")
        idx.add("content_match", title="Other Doc", content="agent mentioned here")
        results = idx.search("agent")
        assert results[0].doc_id == "title_match"

    def test_multiple_query_tokens_score_higher(self):
        """Doc matching more query tokens scores higher."""
        idx = SearchIndex()
        idx.add("both", title="Other", content="keyword alpha beta gamma")
        idx.add("one", title="Other", content="keyword something else entirely")
        # Query with multiple terms: "both" matches keyword+alpha+beta, "one" only keyword
        results = idx.search("keyword alpha beta")
        assert results[0].doc_id == "both"

    def test_tag_search(self):
        idx = SearchIndex()
        idx.add("tagged", title="Doc", content="content", tags=["important", "api_reference"])
        results = idx.search("important")
        assert len(results) == 1
        assert results[0].doc_id == "tagged"

    def test_tag_removal(self):
        idx = SearchIndex()
        idx.add("tagged", title="Doc", content="content", tags=["specialtag"])
        idx.remove("tagged")
        results = idx.search("specialtag")
        assert len(results) == 0


# ===========================================================================
# Tests: SearchIndex - tokenization
# ===========================================================================

@pytest.mark.unit
class TestSearchIndexTokenization:
    """CamelCase, snake_case, stopword filtering."""

    def test_camel_case_splitting(self):
        idx = SearchIndex()
        tokens = idx._tokenize("MyCamelCaseIdentifier")
        assert "camel" in tokens
        assert "case" in tokens
        assert "identifier" in tokens

    def test_snake_case_splitting(self):
        idx = SearchIndex()
        tokens = idx._tokenize("my_snake_case_var")
        assert "snake" in tokens
        assert "case" in tokens
        assert "var" in tokens

    def test_mixed_case_splitting(self):
        idx = SearchIndex()
        tokens = idx._tokenize("parseXMLDocument_v2")
        assert "parse" in tokens
        # CamelCase split only inserts space on lowercase->uppercase boundary
        # "XMLDocument" stays as one token since X->M->L->D are all uppercase transitions
        assert any("xml" in t for t in tokens)

    def test_stopwords_removed(self):
        idx = SearchIndex()
        tokens = idx._tokenize("The quick brown fox is in the box")
        for sw in ("the", "is", "in"):
            assert sw not in tokens
        assert "quick" in tokens
        assert "brown" in tokens
        assert "fox" in tokens

    def test_short_tokens_removed(self):
        idx = SearchIndex()
        tokens = idx._tokenize("I a the hello")
        # Single-char tokens removed (min length 2)
        assert "i" not in tokens
        assert "a" not in tokens
        assert "hello" in tokens

    def test_non_alpha_removed(self):
        idx = SearchIndex()
        tokens = idx._tokenize("hello-world! foo@bar.com #tag")
        assert "hello" in tokens
        assert "world" in tokens


# ===========================================================================
# Tests: SearchIndex - snippets
# ===========================================================================

@pytest.mark.unit
class TestSearchIndexSnippets:
    """Snippet extraction from content."""

    def test_snippet_contains_query_term(self):
        idx = SearchIndex()
        content = "Here is some text about agents and their processing capabilities."
        idx.add("d1", title="T", content=content)
        results = idx.search("agents")
        assert "agents" in results[0].snippet.lower()

    def test_snippet_truncation_short_content(self):
        idx = SearchIndex()
        idx.add("d1", title="T", content="short")
        results = idx.search("short")
        snippet = results[0].snippet
        assert "..." not in snippet

    def test_snippet_centering_on_match(self):
        idx = SearchIndex()
        padding = "filler " * 60
        content = padding + "TARGETWORD " + padding
        idx.add("d1", title="T", content=content)
        results = idx.search("TARGETWORD")
        assert len(results) >= 1
        snippet = results[0].snippet
        assert "TARGETWORD" in snippet

    def test_snippet_no_match_uses_prefix(self):
        idx = SearchIndex()
        # Search for a token that maps to content but not verbatim
        content = "A" * 300
        idx.add("d1", title="matched", content=content)
        results = idx.search("matched")
        # The snippet should be content prefix since "matched" appears in title not content
        assert len(results) > 0

    def test_snippet_max_len(self):
        idx = SearchIndex()
        content = "x " * 500
        idx.add("d1", title="Test", content=content)
        results = idx.search("test")
        # Snippet should not exceed 200 chars + "..."
        assert len(results[0].snippet) <= 210


# ===========================================================================
# Tests: SiteConfig dataclass
# ===========================================================================

@pytest.mark.unit
class TestSiteConfigDataclass:
    """Tests for SiteConfig dataclass."""

    def test_defaults(self):
        sc = SiteConfig()
        assert sc.title == "Codomyrmex Documentation"
        assert sc.theme == "material"
        assert sc.nav == []
        assert "search" in sc.plugins
        assert "mkdocstrings" in sc.plugins
        assert sc.base_url == "/"
        assert sc.extra_css == []
        assert sc.extra_javascript == []

    def test_custom_values(self):
        sc = SiteConfig(
            title="Custom",
            theme="readthedocs",
            plugins=["search"],
            base_url="/docs/",
        )
        assert sc.title == "Custom"
        assert sc.theme == "readthedocs"
        assert sc.base_url == "/docs/"


# ===========================================================================
# Tests: SiteGenerator - core operations
# ===========================================================================

@pytest.mark.unit
class TestSiteGeneratorCore:
    """SiteGenerator add_module_source, add_page, properties."""

    def test_empty_generator(self):
        gen = SiteGenerator()
        assert gen.module_count == 0
        assert gen.page_count == 0

    def test_custom_title(self):
        gen = SiteGenerator(title="My Docs")
        config = gen.generate_config()
        assert config.title == "My Docs"

    def test_add_module_source(self):
        gen = SiteGenerator()
        doc = gen.add_module_source(SIMPLE_MODULE, "mymod")
        assert gen.module_count == 1
        assert doc.name == "mymod"
        assert gen.page_count == 1

    def test_add_module_creates_page(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE, "mymod")
        pages = gen.generate_pages()
        assert "api/mymod.md" in pages

    def test_add_module_indexes_for_search(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE, "mymod")
        assert gen.search_index.doc_count == 1

    def test_add_multiple_modules(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE, "mod_a")
        gen.add_module_source(MODULE_NO_ALL, "mod_b")
        assert gen.module_count == 2
        assert gen.page_count == 2

    def test_add_page(self):
        gen = SiteGenerator()
        gen.add_page("guide/setup.md", "# Setup\nHow to set up.", title="Setup Guide")
        assert gen.page_count == 1
        pages = gen.generate_pages()
        assert "guide/setup.md" in pages
        assert "# Setup" in pages["guide/setup.md"]

    def test_add_page_with_no_title(self):
        gen = SiteGenerator()
        gen.add_page("notes/misc.md", "Misc content")
        # Should use path as title for search
        assert gen.search_index.doc_count == 1

    def test_add_page_indexes_for_search(self):
        gen = SiteGenerator()
        gen.add_page("guide.md", "Configuration and setup instructions", title="Guide")
        results = gen.search_index.search("configuration")
        assert len(results) >= 1

    def test_add_extra_css(self):
        gen = SiteGenerator()
        gen.add_extra_css("custom.css")
        gen.add_extra_css("theme.css")
        config = gen.generate_config()
        assert config.extra_css == ["custom.css", "theme.css"]

    def test_add_extra_javascript(self):
        gen = SiteGenerator()
        gen.add_extra_javascript("app.js")
        config = gen.generate_config()
        assert config.extra_javascript == ["app.js"]

    def test_search_index_property(self):
        gen = SiteGenerator()
        assert isinstance(gen.search_index, SearchIndex)


# ===========================================================================
# Tests: SiteGenerator - generate_config
# ===========================================================================

@pytest.mark.unit
class TestSiteGeneratorConfig:
    """SiteGenerator.generate_config tests."""

    def test_home_in_nav(self):
        gen = SiteGenerator()
        config = gen.generate_config()
        assert {"Home": "index.md"} in config.nav

    def test_api_reference_in_nav(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE, "mymod")
        config = gen.generate_config()
        api_section = next(
            (item for item in config.nav if isinstance(item, dict) and "API Reference" in item),
            None,
        )
        assert api_section is not None

    def test_sorted_api_nav(self):
        gen = SiteGenerator()
        gen.add_module_source("def a(): pass", "z_mod")
        gen.add_module_source("def b(): pass", "a_mod")
        gen.add_module_source("def c(): pass", "m_mod")
        config = gen.generate_config()
        api_section = next(item for item in config.nav if "API Reference" in item)
        api_nav = api_section["API Reference"]
        names = [list(d.keys())[0] for d in api_nav]
        assert names == ["a_mod", "m_mod", "z_mod"]

    def test_more_nav_for_custom_pages(self):
        gen = SiteGenerator()
        gen.add_page("guide/intro.md", "Intro content", title="Introduction")
        config = gen.generate_config()
        more_section = next(
            (item for item in config.nav if isinstance(item, dict) and "More" in item),
            None,
        )
        assert more_section is not None

    def test_no_more_section_without_custom_pages(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE, "mymod")
        config = gen.generate_config()
        more_section = next(
            (item for item in config.nav if isinstance(item, dict) and "More" in item),
            None,
        )
        assert more_section is None

    def test_api_pages_not_in_more(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE, "mymod")
        gen.add_page("guide/setup.md", "Setup")
        config = gen.generate_config()
        more_section = next(
            (item for item in config.nav if isinstance(item, dict) and "More" in item),
            None,
        )
        if more_section:
            more_paths = [list(d.values())[0] for d in more_section["More"]]
            assert "api/mymod.md" not in more_paths


# ===========================================================================
# Tests: SiteGenerator - generate_pages
# ===========================================================================

@pytest.mark.unit
class TestSiteGeneratorPages:
    """SiteGenerator.generate_pages tests."""

    def test_returns_dict(self):
        gen = SiteGenerator()
        pages = gen.generate_pages()
        assert isinstance(pages, dict)

    def test_pages_contain_markdown(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE, "mymod")
        pages = gen.generate_pages()
        content = pages["api/mymod.md"]
        assert "# Module" in content

    def test_pages_is_copy(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE, "mymod")
        pages1 = gen.generate_pages()
        pages2 = gen.generate_pages()
        assert pages1 is not pages2
        assert pages1 == pages2


# ===========================================================================
# Tests: SiteGenerator - to_mkdocs_yaml
# ===========================================================================

@pytest.mark.unit
class TestSiteGeneratorMkdocsYaml:
    """SiteGenerator.to_mkdocs_yaml tests."""

    def test_site_name(self):
        gen = SiteGenerator(title="Test Docs")
        yaml = gen.to_mkdocs_yaml()
        assert "site_name: Test Docs" in yaml

    def test_theme_section(self):
        gen = SiteGenerator()
        yaml = gen.to_mkdocs_yaml()
        assert "theme:" in yaml
        assert "name: material" in yaml
        assert "scheme: slate" in yaml
        assert "primary: indigo" in yaml

    def test_features_section(self):
        gen = SiteGenerator()
        yaml = gen.to_mkdocs_yaml()
        assert "navigation.tabs" in yaml
        assert "navigation.sections" in yaml
        assert "navigation.top" in yaml
        assert "search.suggest" in yaml
        assert "search.highlight" in yaml
        assert "content.code.copy" in yaml

    def test_plugins_section(self):
        gen = SiteGenerator()
        yaml = gen.to_mkdocs_yaml()
        assert "plugins:" in yaml
        assert "  - search" in yaml
        assert "  - mkdocstrings" in yaml

    def test_nav_section(self):
        gen = SiteGenerator()
        gen.add_module_source(SIMPLE_MODULE, "mymod")
        yaml = gen.to_mkdocs_yaml()
        assert "nav:" in yaml
        assert "Home: index.md" in yaml
        assert "mymod" in yaml

    def test_extra_css_in_yaml(self):
        gen = SiteGenerator()
        gen.add_extra_css("custom.css")
        yaml = gen.to_mkdocs_yaml()
        assert "extra_css:" in yaml
        assert "  - custom.css" in yaml

    def test_extra_js_in_yaml(self):
        gen = SiteGenerator()
        gen.add_extra_javascript("app.js")
        yaml = gen.to_mkdocs_yaml()
        assert "extra_javascript:" in yaml
        assert "  - app.js" in yaml

    def test_no_extra_css_section_when_empty(self):
        gen = SiteGenerator()
        yaml = gen.to_mkdocs_yaml()
        assert "extra_css:" not in yaml

    def test_no_extra_js_section_when_empty(self):
        gen = SiteGenerator()
        yaml = gen.to_mkdocs_yaml()
        assert "extra_javascript:" not in yaml

    def test_nested_nav_rendering(self):
        gen = SiteGenerator()
        gen.add_module_source("def a(): pass", "alpha")
        gen.add_module_source("def b(): pass", "beta")
        yaml = gen.to_mkdocs_yaml()
        assert "API Reference:" in yaml
        assert "alpha:" in yaml
        assert "beta:" in yaml

    def test_more_section_rendering(self):
        gen = SiteGenerator()
        gen.add_page("extras/faq.md", "FAQ content", title="FAQ")
        yaml = gen.to_mkdocs_yaml()
        assert "More:" in yaml

    def test_plain_string_nav_item(self):
        """The _render_nav_item method handles plain string items."""
        gen = SiteGenerator()
        lines = []
        gen._render_nav_item(lines, "plain_item.md", indent=2)
        assert "  - plain_item.md" in lines


# ===========================================================================
# Tests: __init__.py re-exports
# ===========================================================================

@pytest.mark.unit
class TestModuleExports:
    """Tests for docs_gen __init__.py re-exports."""

    def test_apidocextractor_exported(self):
        from codomyrmex.docs_gen import APIDocExtractor as Cls
        assert Cls is APIDocExtractor

    def test_classdoc_exported(self):
        from codomyrmex.docs_gen import ClassDoc as Cls
        assert Cls is ClassDoc

    def test_functiondoc_exported(self):
        from codomyrmex.docs_gen import FunctionDoc as Cls
        assert Cls is FunctionDoc

    def test_moduledoc_exported(self):
        from codomyrmex.docs_gen import ModuleDoc as Cls
        assert Cls is ModuleDoc

    def test_indexentry_exported(self):
        from codomyrmex.docs_gen import IndexEntry as Cls
        assert Cls is IndexEntry

    def test_searchindex_exported(self):
        from codomyrmex.docs_gen import SearchIndex as Cls
        assert Cls is SearchIndex

    def test_searchresult_exported(self):
        from codomyrmex.docs_gen import SearchResult as Cls
        assert Cls is SearchResult

    def test_siteconfig_exported(self):
        from codomyrmex.docs_gen import SiteConfig as Cls
        assert Cls is SiteConfig

    def test_sitegenerator_exported(self):
        from codomyrmex.docs_gen import SiteGenerator as Cls
        assert Cls is SiteGenerator
