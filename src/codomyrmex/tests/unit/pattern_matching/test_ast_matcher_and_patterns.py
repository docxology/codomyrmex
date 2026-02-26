"""Unit tests for ast_matcher, code_patterns, and similarity modules.

Covers:
- ASTMatcher: parse_code, find_pattern (singleton/factory/decorator/context_manager),
  find_antipatterns (bare_except, mutable_default_arg, star_import, deep_nesting),
  match_structure, unknown pattern handling, unsupported language
- PatternDetector: detect_patterns (singleton, factory, observer, strategy,
  template_method), register_pattern, custom catalogue, empty code, syntax errors
- PatternDefinition / PATTERNS catalogue
- CodeSimilarity: compute_similarity, structural_hash, find_duplicates,
  edge cases (empty strings, identical code, large code)
- DuplicateResult dataclass
"""

import pytest

from codomyrmex.coding.pattern_matching.ast_matcher import ASTMatcher, ASTMatchResult
from codomyrmex.coding.pattern_matching.code_patterns import (
    PATTERNS,
    PatternDefinition,
    PatternDetector,
    _to_definition,
)
from codomyrmex.coding.pattern_matching.similarity import CodeSimilarity, DuplicateResult


# =====================================================================
# ASTMatcher tests
# =====================================================================


@pytest.mark.unit
class TestASTMatcher:
    """Tests for ASTMatcher class."""

    def test_parse_code_simple_function(self):
        """parse_code returns node count and top-level summary for a function."""
        matcher = ASTMatcher()
        result = matcher.parse_code("def hello():\n    pass\n")
        assert result["language"] == "python"
        assert result["node_count"] > 0
        assert len(result["top_level"]) == 1
        assert result["top_level"][0]["type"] == "FunctionDef"
        assert result["top_level"][0]["name"] == "hello"

    def test_parse_code_class_definition(self):
        """parse_code reports ClassDef with correct name."""
        matcher = ASTMatcher()
        result = matcher.parse_code("class Foo:\n    x = 1\n")
        assert any(n["type"] == "ClassDef" and n["name"] == "Foo" for n in result["top_level"])

    def test_parse_code_empty_string(self):
        """parse_code on empty string returns zero top-level nodes."""
        matcher = ASTMatcher()
        result = matcher.parse_code("")
        assert result["top_level"] == []
        # Module node itself is still counted
        assert result["node_count"] >= 1

    def test_parse_code_unsupported_language_raises(self):
        """parse_code raises ValueError for unsupported language."""
        matcher = ASTMatcher()
        with pytest.raises(ValueError, match="Unsupported language"):
            matcher.parse_code("fn main() {}", language="rust")

    def test_parse_code_syntax_error_raises(self):
        """parse_code raises SyntaxError for invalid Python."""
        matcher = ASTMatcher()
        with pytest.raises(SyntaxError):
            matcher.parse_code("def oops(:\n")

    def test_parse_code_line_numbers_present(self):
        """parse_code includes line numbers in top-level summaries."""
        matcher = ASTMatcher()
        code = "x = 1\ndef foo():\n    pass\nclass Bar:\n    pass\n"
        result = matcher.parse_code(code)
        for entry in result["top_level"]:
            assert "line" in entry

    # ----- find_pattern: singleton -----

    def test_find_singleton_with_new(self):
        """find_pattern detects singleton via __new__ override."""
        code = (
            "class MySingleton:\n"
            "    def __new__(cls):\n"
            "        return super().__new__(cls)\n"
        )
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, "singleton")
        assert len(results) == 1
        assert results[0].pattern_name == "singleton"
        assert results[0].name == "MySingleton"
        assert results[0].line == 1
        assert "Overrides __new__" in results[0].details

    def test_find_singleton_with_instance_attr(self):
        """find_pattern detects singleton via _instance class attribute."""
        code = (
            "class Singleton:\n"
            "    _instance = None\n"
            "    def get(cls):\n"
            "        return cls._instance\n"
        )
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, "singleton")
        assert len(results) == 1
        assert "Has _instance attribute" in results[0].details

    def test_find_singleton_not_triggered_by_plain_class(self):
        """find_pattern returns empty for class without singleton indicators."""
        code = "class RegularClass:\n    def method(self):\n        pass\n"
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, "singleton")
        assert results == []

    # ----- find_pattern: factory -----

    def test_find_factory_create_function(self):
        """find_pattern detects factory by 'create' in function name."""
        code = "def create_widget(kind):\n    return Widget(kind)\n"
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, "factory")
        assert len(results) == 1
        assert results[0].name == "create_widget"
        assert results[0].pattern_name == "factory"

    def test_find_factory_build_and_make(self):
        """find_pattern detects multiple factory functions."""
        code = (
            "def build_thing():\n    pass\n"
            "def make_stuff():\n    pass\n"
            "def unrelated():\n    pass\n"
        )
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, "factory")
        names = {r.name for r in results}
        assert "build_thing" in names
        assert "make_stuff" in names
        assert "unrelated" not in names

    # ----- find_pattern: decorator -----

    def test_find_decorated_function(self):
        """find_pattern detects decorated function."""
        code = "@staticmethod\ndef my_func():\n    pass\n"
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, "decorator")
        assert len(results) >= 1
        assert any(r.name == "my_func" for r in results)

    def test_find_decorated_class(self):
        """find_pattern detects decorated class."""
        code = "@dataclass\nclass Config:\n    name: str = 'x'\n"
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, "decorator")
        assert any(r.name == "Config" for r in results)

    # ----- find_pattern: context_manager -----

    def test_find_context_manager(self):
        """find_pattern detects class with __enter__ and __exit__."""
        code = (
            "class MyCtx:\n"
            "    def __enter__(self):\n"
            "        return self\n"
            "    def __exit__(self, *args):\n"
            "        pass\n"
        )
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, "context_manager")
        assert len(results) == 1
        assert results[0].name == "MyCtx"
        assert "Implements __enter__ and __exit__" in results[0].details

    def test_context_manager_missing_exit(self):
        """Class with only __enter__ is not a context manager."""
        code = "class Partial:\n    def __enter__(self):\n        pass\n"
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, "context_manager")
        assert results == []

    # ----- find_pattern: unknown -----

    def test_find_unknown_pattern_returns_empty(self):
        """find_pattern with unknown name returns empty list."""
        matcher = ASTMatcher()
        results = matcher.find_pattern("x = 1", "nonexistent_pattern")
        assert results == []

    # ----- find_antipatterns -----

    def test_antipattern_bare_except(self):
        """find_antipatterns detects bare except clause."""
        code = "try:\n    pass\nexcept:\n    pass\n"
        matcher = ASTMatcher()
        results = matcher.find_antipatterns(code)
        assert any(r.pattern_name == "bare_except" for r in results)

    def test_antipattern_mutable_default_list(self):
        """find_antipatterns detects mutable default argument (list)."""
        code = "def bad(items=[]):\n    items.append(1)\n"
        matcher = ASTMatcher()
        results = matcher.find_antipatterns(code)
        assert any(r.pattern_name == "mutable_default_arg" for r in results)

    def test_antipattern_mutable_default_dict(self):
        """find_antipatterns detects mutable default argument (dict)."""
        code = "def bad(config={}):\n    pass\n"
        matcher = ASTMatcher()
        results = matcher.find_antipatterns(code)
        assert any(r.pattern_name == "mutable_default_arg" for r in results)

    def test_antipattern_star_import(self):
        """find_antipatterns detects star import."""
        code = "from os import *\n"
        matcher = ASTMatcher()
        results = matcher.find_antipatterns(code)
        assert any(r.pattern_name == "star_import" for r in results)
        star_result = [r for r in results if r.pattern_name == "star_import"][0]
        assert "from os import *" in star_result.details

    def test_antipattern_deep_nesting(self):
        """find_antipatterns detects deeply nested functions."""
        code = (
            "def level0():\n"
            "    def level1():\n"
            "        def level2():\n"
            "            def level3():\n"
            "                pass\n"
        )
        matcher = ASTMatcher()
        results = matcher.find_antipatterns(code)
        deep = [r for r in results if r.pattern_name == "deep_nesting"]
        assert len(deep) >= 1
        assert any("level3" in r.name for r in deep)

    def test_antipattern_clean_code_returns_empty(self):
        """find_antipatterns returns empty for clean code."""
        code = (
            "import os\n"
            "def good_function(x: int) -> int:\n"
            "    try:\n"
            "        return x + 1\n"
            "    except ValueError:\n"
            "        return 0\n"
        )
        matcher = ASTMatcher()
        results = matcher.find_antipatterns(code)
        assert results == []

    def test_antipatterns_multiple_in_one_file(self):
        """find_antipatterns detects multiple different antipatterns."""
        code = (
            "from os import *\n"
            "def func(items=[]):\n"
            "    try:\n"
            "        pass\n"
            "    except:\n"
            "        pass\n"
        )
        matcher = ASTMatcher()
        results = matcher.find_antipatterns(code)
        names = {r.pattern_name for r in results}
        assert "star_import" in names
        assert "mutable_default_arg" in names
        assert "bare_except" in names

    # ----- match_structure -----

    def test_match_structure_identical_shape(self):
        """match_structure returns True when shapes match."""
        code = "class A:\n    pass\ndef foo():\n    pass\n"
        template = "class B:\n    pass\ndef bar():\n    pass\n"
        matcher = ASTMatcher()
        assert matcher.match_structure(code, template) is True

    def test_match_structure_different_shape(self):
        """match_structure returns False when node types differ."""
        code = "class A:\n    pass\n"
        template = "def foo():\n    pass\n"
        matcher = ASTMatcher()
        assert matcher.match_structure(code, template) is False

    def test_match_structure_different_count(self):
        """match_structure returns False when node counts differ."""
        code = "x = 1\ny = 2\n"
        template = "x = 1\n"
        matcher = ASTMatcher()
        assert matcher.match_structure(code, template) is False

    def test_match_structure_syntax_error_returns_false(self):
        """match_structure returns False if either argument has a syntax error."""
        matcher = ASTMatcher()
        assert matcher.match_structure("def oops(:", "def ok():\n    pass") is False

    # ----- ASTMatchResult dataclass -----

    def test_ast_match_result_fields(self):
        """ASTMatchResult stores all fields correctly."""
        r = ASTMatchResult(
            pattern_name="test",
            node_type="ClassDef",
            line=10,
            col=4,
            name="MyClass",
            details="details here",
        )
        assert r.pattern_name == "test"
        assert r.node_type == "ClassDef"
        assert r.line == 10
        assert r.col == 4
        assert r.name == "MyClass"
        assert r.details == "details here"

    def test_ast_match_result_defaults(self):
        """ASTMatchResult has empty string defaults for name and details."""
        r = ASTMatchResult(pattern_name="x", node_type="y", line=1, col=0)
        assert r.name == ""
        assert r.details == ""

    # ----- Large code string -----

    def test_find_pattern_large_code(self):
        """find_pattern works on code with many functions (1000+ chars)."""
        lines = []
        for i in range(50):
            lines.append(f"def create_item_{i}():\n    pass\n")
        code = "\n".join(lines)
        assert len(code) > 1000
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, "factory")
        assert len(results) == 50

    # ----- Parametrized pattern detection -----

    @pytest.mark.parametrize(
        "pattern_name,code,expected_count",
        [
            ("singleton", "class S:\n    def __new__(cls): pass\n", 1),
            ("singleton", "class R:\n    def method(self): pass\n", 0),
            ("factory", "def create_x(): pass\ndef make_y(): pass\n", 2),
            ("factory", "def helper(): pass\n", 0),
            ("decorator", "@property\ndef x(self): pass\n", 1),
            ("context_manager", "class C:\n    def __enter__(self): pass\n    def __exit__(self,*a): pass\n", 1),
            ("context_manager", "class C:\n    def __enter__(self): pass\n", 0),
        ],
        ids=[
            "singleton-with-new",
            "singleton-no-match",
            "factory-two-matches",
            "factory-no-match",
            "decorator-property",
            "ctx-manager-full",
            "ctx-manager-partial",
        ],
    )
    def test_find_pattern_parametrized(self, pattern_name, code, expected_count):
        """Parametrized find_pattern tests across all supported patterns."""
        matcher = ASTMatcher()
        results = matcher.find_pattern(code, pattern_name)
        assert len(results) == expected_count


# =====================================================================
# PatternDetector tests
# =====================================================================


@pytest.mark.unit
class TestPatternDetector:
    """Tests for PatternDetector class."""

    def test_detect_singleton(self):
        """detect_patterns finds singleton with __new__."""
        code = "class Cache:\n    def __new__(cls):\n        pass\n"
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        singletons = [r for r in results if r["pattern"] == "singleton"]
        assert len(singletons) == 1
        assert singletons[0]["confidence"] == 0.85
        assert singletons[0]["category"] == "creational"
        assert singletons[0]["location"]["name"] == "Cache"

    def test_detect_singleton_with_instance_attr(self):
        """detect_patterns finds singleton with _instance attribute."""
        code = "class Registry:\n    _instance = None\n    def get(cls): pass\n"
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        assert any(r["pattern"] == "singleton" for r in results)

    def test_detect_factory(self):
        """detect_patterns finds factory functions."""
        code = "def create_connection(url):\n    pass\n"
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        factories = [r for r in results if r["pattern"] == "factory"]
        assert len(factories) == 1
        assert factories[0]["confidence"] == 0.70

    def test_detect_factory_construct_keyword(self):
        """detect_patterns finds factory with 'construct' in name."""
        code = "def construct_pipeline():\n    pass\n"
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        assert any(r["pattern"] == "factory" for r in results)

    def test_detect_observer(self):
        """detect_patterns finds observer with subscribe and notify methods."""
        code = (
            "class EventBus:\n"
            "    _listeners = []\n"
            "    def subscribe(self, fn): pass\n"
            "    def notify(self): pass\n"
        )
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        observers = [r for r in results if r["pattern"] == "observer"]
        assert len(observers) == 1
        assert observers[0]["confidence"] == 0.80

    def test_detect_observer_with_listener_attr_and_emit(self):
        """detect_patterns finds observer with _listeners attr and emit method."""
        code = (
            "class Notifier:\n"
            "    _listeners = []\n"
            "    def emit(self, event): pass\n"
        )
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        assert any(r["pattern"] == "observer" for r in results)

    def test_detect_strategy(self):
        """detect_patterns finds strategy with ABC base and execute method."""
        code = (
            "class Strategy(ABC):\n"
            "    def execute(self): pass\n"
        )
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        strategies = [r for r in results if r["pattern"] == "strategy"]
        assert len(strategies) == 1
        assert strategies[0]["confidence"] == 0.75

    def test_detect_template_method(self):
        """detect_patterns finds template_method with public + hook methods."""
        code = (
            "class Pipeline:\n"
            "    def run(self): pass\n"
            "    def _validate(self): pass\n"
            "    def _transform(self): pass\n"
        )
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        templates = [r for r in results if r["pattern"] == "template_method"]
        assert len(templates) == 1
        assert templates[0]["confidence"] == 0.55

    def test_detect_no_patterns_in_plain_code(self):
        """detect_patterns returns empty for plain code with no patterns."""
        code = "x = 1\ny = x + 2\nprint(y)\n"
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        assert results == []

    def test_detect_patterns_syntax_error_returns_empty(self):
        """detect_patterns returns empty list for syntax errors."""
        detector = PatternDetector()
        results = detector.detect_patterns("def broken(:\n")
        assert results == []

    def test_detect_patterns_empty_string(self):
        """detect_patterns on empty code returns empty list."""
        detector = PatternDetector()
        results = detector.detect_patterns("")
        assert results == []

    def test_register_pattern(self):
        """register_pattern adds a new pattern definition."""
        detector = PatternDetector()
        detector.register_pattern("custom", {
            "description": "My custom pattern",
            "indicators": ["custom indicator"],
            "category": "experimental",
        })
        assert "custom" in detector._definitions
        assert detector._definitions["custom"].category == "experimental"

    def test_custom_catalogue_empty(self):
        """PatternDetector with empty catalogue detects nothing."""
        detector = PatternDetector(patterns={})
        code = "class S:\n    def __new__(cls): pass\n"
        results = detector.detect_patterns(code)
        assert results == []

    def test_detect_multiple_patterns_in_one_file(self):
        """detect_patterns finds multiple different patterns in one code block."""
        code = (
            "class MySingleton:\n"
            "    _instance = None\n"
            "    def get(cls): pass\n"
            "\n"
            "def create_widget(kind):\n"
            "    pass\n"
            "\n"
            "class EventBus:\n"
            "    def subscribe(self, fn): pass\n"
            "    def notify(self): pass\n"
        )
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        patterns_found = {r["pattern"] for r in results}
        assert "singleton" in patterns_found
        assert "factory" in patterns_found
        assert "observer" in patterns_found

    def test_location_has_line_number(self):
        """detect_patterns results include line numbers in location."""
        code = "class Cache:\n    def __new__(cls):\n        pass\n"
        detector = PatternDetector()
        results = detector.detect_patterns(code)
        assert len(results) > 0
        for r in results:
            assert "line" in r["location"]
            assert isinstance(r["location"]["line"], int)
            assert r["location"]["line"] >= 1


# =====================================================================
# PatternDefinition and PATTERNS catalogue tests
# =====================================================================


@pytest.mark.unit
class TestPatternDefinitionAndCatalogue:
    """Tests for PatternDefinition dataclass and PATTERNS dict."""

    def test_pattern_definition_fields(self):
        """PatternDefinition stores all fields."""
        pd = PatternDefinition(
            name="test",
            description="A test pattern",
            indicators=["indicator_1"],
            category="creational",
        )
        assert pd.name == "test"
        assert pd.description == "A test pattern"
        assert pd.indicators == ["indicator_1"]
        assert pd.category == "creational"

    def test_pattern_definition_default_category(self):
        """PatternDefinition defaults category to 'general'."""
        pd = PatternDefinition(name="x", description="y", indicators=[])
        assert pd.category == "general"

    def test_patterns_catalogue_has_expected_keys(self):
        """Built-in PATTERNS catalogue has singleton, factory, observer, strategy, etc."""
        expected = {"singleton", "factory", "observer", "strategy", "decorator_pattern", "template_method"}
        assert expected.issubset(set(PATTERNS.keys()))

    def test_patterns_catalogue_all_have_description(self):
        """Every pattern in the catalogue has a non-empty description."""
        for name, info in PATTERNS.items():
            assert "description" in info, f"{name} missing description"
            assert len(info["description"]) > 0

    def test_patterns_catalogue_all_have_indicators(self):
        """Every pattern in the catalogue has at least one indicator."""
        for name, info in PATTERNS.items():
            assert "indicators" in info, f"{name} missing indicators"
            assert len(info["indicators"]) >= 1

    def test_to_definition_converts_dict(self):
        """_to_definition converts a raw dict into a PatternDefinition."""
        info = {"description": "desc", "indicators": ["ind"], "category": "cat"}
        pd = _to_definition("test_name", info)
        assert isinstance(pd, PatternDefinition)
        assert pd.name == "test_name"
        assert pd.category == "cat"

    def test_to_definition_missing_fields_defaults(self):
        """_to_definition handles missing fields gracefully."""
        pd = _to_definition("empty", {})
        assert pd.description == ""
        assert pd.indicators == []
        assert pd.category == "general"


# =====================================================================
# CodeSimilarity tests
# =====================================================================


@pytest.mark.unit
class TestCodeSimilarity:
    """Tests for CodeSimilarity class."""

    def test_identical_code_similarity_is_one(self):
        """compute_similarity returns ~1.0 for identical code."""
        code = "def foo():\n    return 42\n"
        sim = CodeSimilarity()
        score = sim.compute_similarity(code, code)
        assert score >= 0.99

    def test_completely_different_code_low_similarity(self):
        """compute_similarity returns low score for unrelated code."""
        code_a = "import os\nprint(os.getcwd())\n"
        code_b = "class MyWidget:\n    def render(self):\n        return '<div></div>'\n"
        sim = CodeSimilarity()
        score = sim.compute_similarity(code_a, code_b)
        assert score < 0.5

    def test_both_empty_returns_one(self):
        """compute_similarity returns 1.0 when both inputs are empty."""
        sim = CodeSimilarity()
        assert sim.compute_similarity("", "") == 1.0

    def test_one_empty_returns_zero(self):
        """compute_similarity returns 0.0 when one input is empty."""
        sim = CodeSimilarity()
        assert sim.compute_similarity("def f(): pass", "") == 0.0
        assert sim.compute_similarity("", "def f(): pass") == 0.0

    def test_similarity_score_range(self):
        """compute_similarity always returns a value between 0.0 and 1.0."""
        sim = CodeSimilarity()
        code_a = "x = 1\ny = 2\nz = x + y\n"
        code_b = "a = 10\nb = 20\nc = a + b\n"
        score = sim.compute_similarity(code_a, code_b)
        assert 0.0 <= score <= 1.0

    def test_similar_code_renamed_vars_high_similarity(self):
        """Code differing only in variable names has high similarity."""
        code_a = "def calc(x, y):\n    result = x + y\n    return result\n"
        code_b = "def compute(a, b):\n    total = a + b\n    return total\n"
        sim = CodeSimilarity()
        score = sim.compute_similarity(code_a, code_b)
        # Structural hash match gives a boost; token cosine should also be high
        assert score >= 0.5

    def test_structural_hash_deterministic(self):
        """structural_hash returns same hash for same input."""
        sim = CodeSimilarity()
        code = "def foo():\n    return 1\n"
        h1 = sim.structural_hash(code)
        h2 = sim.structural_hash(code)
        assert h1 == h2
        assert isinstance(h1, str)
        assert len(h1) == 64  # sha256 hex digest

    def test_structural_hash_ignores_names(self):
        """structural_hash is the same for code differing only in names."""
        sim = CodeSimilarity()
        code_a = "def alpha():\n    return 1\n"
        code_b = "def beta():\n    return 1\n"
        assert sim.structural_hash(code_a) == sim.structural_hash(code_b)

    def test_structural_hash_different_structure(self):
        """structural_hash differs for structurally different code."""
        sim = CodeSimilarity()
        code_a = "def foo():\n    pass\n"
        code_b = "class Foo:\n    pass\n"
        assert sim.structural_hash(code_a) != sim.structural_hash(code_b)

    def test_structural_hash_syntax_error_falls_back(self):
        """structural_hash falls back to token hash for invalid Python."""
        sim = CodeSimilarity()
        bad_code = "function hello() { return 1; }"
        h = sim.structural_hash(bad_code)
        assert isinstance(h, str)
        assert len(h) == 64

    def test_find_duplicates_above_threshold(self, tmp_path):
        """find_duplicates returns pairs exceeding the threshold."""
        fa = tmp_path / "a.py"
        fb = tmp_path / "b.py"
        fc = tmp_path / "c.py"
        fa.write_text("def foo():\n    return 1\n")
        fb.write_text("def bar():\n    return 1\n")  # structurally identical
        fc.write_text("import os\nprint(os.listdir('.'))\n")  # different
        sim = CodeSimilarity()
        dupes = sim.find_duplicates([str(fa), str(fb), str(fc)], threshold=0.7)
        # a.py and b.py should be similar
        pairs = [(d.file_a, d.file_b) for d in dupes]
        assert any(str(fa) in p and str(fb) in p for p in pairs)

    def test_find_duplicates_sorted_descending(self, tmp_path):
        """find_duplicates returns results sorted by descending similarity."""
        f1 = tmp_path / "f1.py"
        f2 = tmp_path / "f2.py"
        f3 = tmp_path / "f3.py"
        f1.write_text("x = 1\ny = 2\n")
        f2.write_text("x = 1\ny = 2\n")  # identical
        f3.write_text("x = 1\nz = 3\n")  # similar but not identical
        sim = CodeSimilarity()
        dupes = sim.find_duplicates([str(f1), str(f2), str(f3)], threshold=0.3)
        if len(dupes) >= 2:
            for i in range(len(dupes) - 1):
                assert dupes[i].similarity >= dupes[i + 1].similarity

    def test_find_duplicates_invalid_threshold_raises(self):
        """find_duplicates raises ValueError for out-of-range threshold."""
        sim = CodeSimilarity()
        with pytest.raises(ValueError, match="Threshold"):
            sim.find_duplicates([], threshold=1.5)
        with pytest.raises(ValueError, match="Threshold"):
            sim.find_duplicates([], threshold=-0.1)

    def test_find_duplicates_empty_file_list(self):
        """find_duplicates returns empty for no files."""
        sim = CodeSimilarity()
        assert sim.find_duplicates([], threshold=0.5) == []

    def test_find_duplicates_nonexistent_file_handled(self, tmp_path):
        """find_duplicates handles nonexistent files gracefully."""
        real = tmp_path / "real.py"
        real.write_text("x = 1\n")
        sim = CodeSimilarity()
        # Should not raise, just skip the unreadable file
        dupes = sim.find_duplicates([str(real), "/nonexistent/file.py"], threshold=0.5)
        assert isinstance(dupes, list)

    def test_compute_similarity_large_code(self):
        """compute_similarity works on large code blocks (1000+ chars)."""
        lines_a = [f"x_{i} = {i}" for i in range(200)]
        lines_b = [f"y_{i} = {i}" for i in range(200)]
        code_a = "\n".join(lines_a) + "\n"
        code_b = "\n".join(lines_b) + "\n"
        assert len(code_a) > 1000
        sim = CodeSimilarity()
        score = sim.compute_similarity(code_a, code_b)
        assert 0.0 <= score <= 1.0

    # ----- DuplicateResult dataclass -----

    def test_duplicate_result_fields(self):
        """DuplicateResult stores file_a, file_b, similarity."""
        dr = DuplicateResult(file_a="a.py", file_b="b.py", similarity=0.95)
        assert dr.file_a == "a.py"
        assert dr.file_b == "b.py"
        assert dr.similarity == 0.95

    @pytest.mark.parametrize(
        "code_a,code_b,min_score,max_score",
        [
            # Identical
            ("x = 1", "x = 1", 0.9, 1.0),
            # Renamed variable
            ("x = 1", "y = 1", 0.5, 1.0),
            # Totally different
            ("import sys", "class Foo:\n    def bar(self): pass", 0.0, 0.5),
        ],
        ids=["identical", "renamed-var", "different"],
    )
    def test_similarity_parametrized(self, code_a, code_b, min_score, max_score):
        """Parametrized similarity tests covering identical, renamed, and different code."""
        sim = CodeSimilarity()
        score = sim.compute_similarity(code_a, code_b)
        assert min_score <= score <= max_score
