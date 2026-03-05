"""Zero-mock tests for coding.generator module.

Covers: CodeBundle dataclass, CodeGenerator.generate with various specs.

No mocks. No MagicMock. No monkeypatch.
"""

from __future__ import annotations

import pytest

from codomyrmex.coding.generator import CodeBundle, CodeGenerator


@pytest.mark.unit
class TestCodeBundle:
    """Tests for CodeBundle dataclass and its properties."""

    def test_default_filename(self):
        """CodeBundle default filename is 'generated.py'."""
        bundle = CodeBundle()
        assert bundle.filename == "generated.py"

    def test_default_language(self):
        """CodeBundle default language is 'python'."""
        bundle = CodeBundle()
        assert bundle.language == "python"

    def test_default_source_is_empty(self):
        """CodeBundle default source is empty string."""
        bundle = CodeBundle()
        assert bundle.source == ""

    def test_default_imports_empty_list(self):
        """CodeBundle default imports is empty list."""
        bundle = CodeBundle()
        assert bundle.imports == []

    def test_default_functions_empty_list(self):
        """CodeBundle default functions is empty list."""
        bundle = CodeBundle()
        assert bundle.functions == []

    def test_default_classes_empty_list(self):
        """CodeBundle default classes is empty list."""
        bundle = CodeBundle()
        assert bundle.classes == []

    def test_line_count_empty_source(self):
        """line_count returns 0 for empty source."""
        bundle = CodeBundle(source="")
        assert bundle.line_count == 0

    def test_line_count_single_line(self):
        """line_count returns 1 for a single non-empty line."""
        bundle = CodeBundle(source="x = 1")
        assert bundle.line_count == 1

    def test_line_count_multiple_lines(self):
        """line_count counts non-empty lines correctly."""
        source = "def foo():\n    return 42\n"
        bundle = CodeBundle(source=source)
        assert bundle.line_count == 2

    def test_line_count_only_whitespace_lines(self):
        """line_count ignores leading/trailing whitespace when using strip()."""
        bundle = CodeBundle(source="\n\n\n")
        assert bundle.line_count == 0

    def test_to_dict_returns_dict(self):
        """to_dict returns a dictionary."""
        bundle = CodeBundle(filename="my_module.py", language="python")
        result = bundle.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_contains_filename(self):
        """to_dict result includes filename."""
        bundle = CodeBundle(filename="foo.py")
        result = bundle.to_dict()
        assert result["filename"] == "foo.py"

    def test_to_dict_contains_language(self):
        """to_dict result includes language."""
        bundle = CodeBundle(language="javascript")
        result = bundle.to_dict()
        assert result["language"] == "javascript"

    def test_to_dict_contains_lines_count(self):
        """to_dict result includes lines count matching line_count property."""
        bundle = CodeBundle(source="x = 1\ny = 2\n")
        result = bundle.to_dict()
        assert result["lines"] == bundle.line_count

    def test_to_dict_contains_functions(self):
        """to_dict result includes functions list."""
        bundle = CodeBundle(functions=["add", "subtract"])
        result = bundle.to_dict()
        assert result["functions"] == ["add", "subtract"]

    def test_to_dict_contains_classes(self):
        """to_dict result includes classes list."""
        bundle = CodeBundle(classes=["Calculator"])
        result = bundle.to_dict()
        assert result["classes"] == ["Calculator"]

    def test_custom_values_stored_correctly(self):
        """Custom values passed at construction are retained."""
        bundle = CodeBundle(
            filename="calc.py",
            source="class Calc:\n    pass\n",
            language="python",
            imports=["math"],
            functions=["add"],
            classes=["Calc"],
        )
        assert bundle.filename == "calc.py"
        assert bundle.language == "python"
        assert "math" in bundle.imports
        assert "add" in bundle.functions
        assert "Calc" in bundle.classes


@pytest.mark.unit
class TestCodeGeneratorFunctionGeneration:
    """Tests for CodeGenerator.generate producing function-based code."""

    def setup_method(self):
        self.gen = CodeGenerator()

    def test_returns_code_bundle(self):
        """generate() always returns a CodeBundle instance."""
        result = self.gen.generate("Create a utility with add and subtract")
        assert isinstance(result, CodeBundle)

    def test_default_language_is_python(self):
        """Generated bundle uses Python language."""
        result = self.gen.generate("Build a calculator with add")
        assert result.language == "python"

    def test_custom_filename_preserved(self):
        """Custom filename is stored in the bundle."""
        result = self.gen.generate("Build something", filename="mymodule.py")
        assert result.filename == "mymodule.py"

    def test_default_filename_is_generated_py(self):
        """Default filename is 'generated.py'."""
        result = self.gen.generate("Do something")
        assert result.filename == "generated.py"

    def test_no_ops_spec_generates_main_function(self):
        """Spec with no extractable ops generates a 'main' function."""
        result = self.gen.generate("Just a simple script")
        assert "main" in result.functions

    def test_source_is_non_empty_string(self):
        """Generated source is always a non-empty string."""
        result = self.gen.generate("Build a parser with parse and tokenize")
        assert isinstance(result.source, str)
        assert len(result.source) > 0

    def test_source_contains_def_keyword(self):
        """Generated source contains function definitions."""
        result = self.gen.generate("Create utilities with add and multiply")
        assert "def " in result.source

    def test_functions_with_operations_extracted(self):
        """Operations listed in spec appear in functions list."""
        result = self.gen.generate("Create a utility with add and subtract")
        assert len(result.functions) >= 1

    def test_source_contains_not_implemented_error(self):
        """Generated stubs raise NotImplementedError, not pass."""
        result = self.gen.generate("Create a utility with add and multiply")
        assert "NotImplementedError" in result.source

    def test_source_starts_with_docstring(self):
        """Generated source begins with a module docstring."""
        result = self.gen.generate("Create a calculator")
        assert result.source.startswith('"""')

    def test_line_count_positive(self):
        """Generated bundles have a positive line count."""
        result = self.gen.generate("Create utilities with parse")
        assert result.line_count > 0


@pytest.mark.unit
class TestCodeGeneratorClassGeneration:
    """Tests for CodeGenerator.generate producing class-based code."""

    def setup_method(self):
        self.gen = CodeGenerator()

    def test_class_keyword_triggers_class_generation(self):
        """Specs with 'class' keyword produce class-based code."""
        result = self.gen.generate("Create a class with add and remove")
        assert len(result.classes) >= 1

    def test_service_keyword_triggers_class_generation(self):
        """Specs with 'service' keyword produce class-based code."""
        result = self.gen.generate("Build a service with process and handle")
        assert len(result.classes) >= 1

    def test_class_name_capitalized(self):
        """Generated class names start with an uppercase letter."""
        result = self.gen.generate("Create a class with run")
        for cls_name in result.classes:
            assert cls_name[0].isupper(), f"Class name {cls_name!r} not capitalized"

    def test_class_source_contains_class_keyword(self):
        """Generated source for class specs contains 'class' keyword."""
        result = self.gen.generate("Build a service with process")
        assert "class " in result.source

    def test_class_methods_have_self(self):
        """Methods in generated classes take self as first parameter."""
        result = self.gen.generate("Create a class with add and remove")
        assert "def " in result.source
        assert "self" in result.source

    def test_class_methods_in_functions_list(self):
        """Methods generated inside a class are tracked in functions list."""
        result = self.gen.generate("Create a service with process and validate")
        assert len(result.functions) >= 1


@pytest.mark.unit
class TestCodeGeneratorHelpers:
    """Tests for CodeGenerator static helper methods."""

    def test_to_snake_case_single_word(self):
        """Single word is lowercased as-is."""
        result = CodeGenerator._to_snake_case("Add")
        assert result == "add"

    def test_to_snake_case_two_words(self):
        """Two words are joined with underscore."""
        result = CodeGenerator._to_snake_case("add items")
        assert result == "add_items"

    def test_to_snake_case_removes_special_chars(self):
        """Special characters are stripped."""
        result = CodeGenerator._to_snake_case("add-items!")
        assert "_" not in result or result == "add_items"
        assert "!" not in result

    def test_extract_operations_returns_list(self):
        """_extract_operations returns a list."""
        ops = CodeGenerator._extract_operations("Create a tool with add and remove")
        assert isinstance(ops, list)

    def test_extract_operations_finds_items_after_with(self):
        """Operations after 'with' keyword are extracted."""
        ops = CodeGenerator._extract_operations(
            "Create a utility with add and multiply"
        )
        assert len(ops) >= 1

    def test_extract_class_name_returns_string(self):
        """_extract_class_name returns a string."""
        name = CodeGenerator._extract_class_name("Create a calculator")
        assert isinstance(name, str)

    def test_extract_class_name_capitalized(self):
        """Extracted class names are capitalized."""
        name = CodeGenerator._extract_class_name("Create a calculator")
        assert name[0].isupper()

    def test_extract_class_name_fallback(self):
        """Without a matching verb, returns 'Generated' as fallback."""
        name = CodeGenerator._extract_class_name("A simple thing")
        assert name == "Generated"
