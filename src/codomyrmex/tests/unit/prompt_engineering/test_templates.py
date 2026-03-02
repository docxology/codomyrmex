"""Zero-Mock tests for prompt template system.

Tests for PromptTemplate variable extraction, rendering, validation,
serialization, TemplateRegistry CRUD, search, import/export, and
the module-level default registry.
"""

import pytest

try:
    from codomyrmex.prompt_engineering.templates import (
        PromptTemplate,
        TemplateRegistry,
        get_default_registry,
    )

    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("prompt_engineering.templates not available", allow_module_level=True)


@pytest.mark.unit
class TestPromptTemplateVariableExtraction:
    """Tests for automatic variable detection from template strings."""

    def test_single_variable(self):
        """Template with one variable should detect it."""
        t = PromptTemplate(name="t", template_str="Hello, {name}!")
        assert t.variables == ["name"]

    def test_multiple_variables_sorted(self):
        """Multiple variables should be returned sorted and deduplicated."""
        t = PromptTemplate(name="t", template_str="{z} meets {a} then {z}")
        assert t.variables == ["a", "z"]

    def test_no_variables(self):
        """Template with no placeholders should have empty variables list."""
        t = PromptTemplate(name="t", template_str="No variables here.")
        assert t.variables == []

    def test_explicit_variables_override(self):
        """Explicitly provided variables should be used as-is."""
        t = PromptTemplate(
            name="t",
            template_str="{x} {y}",
            variables=["x", "y", "z"],
        )
        assert "z" in t.variables
        assert len(t.variables) == 3

    def test_variables_with_underscores(self):
        """Variable names with underscores should be detected."""
        t = PromptTemplate(name="t", template_str="Use {my_var} and {other_thing}")
        assert "my_var" in t.variables
        assert "other_thing" in t.variables


@pytest.mark.unit
class TestPromptTemplateRendering:
    """Tests for template rendering with variable substitution."""

    def test_basic_render(self):
        """render() should substitute variables correctly."""
        t = PromptTemplate(name="t", template_str="Say {word} to {person}")
        rendered = t.render(word="hello", person="Alice")
        assert rendered == "Say hello to Alice"

    def test_render_missing_variable_raises(self):
        """render() should raise KeyError when required variable is missing."""
        t = PromptTemplate(name="t", template_str="Hello {name}")
        with pytest.raises(KeyError, match="Missing required"):
            t.render()

    def test_render_with_extra_variables(self):
        """render() should ignore extra variables not in template."""
        t = PromptTemplate(name="t", template_str="Hello {name}")
        rendered = t.render(name="World", extra="ignored")
        assert rendered == "Hello World"

    def test_render_special_characters_in_value(self):
        """render() should handle special characters in variable values."""
        t = PromptTemplate(name="t", template_str="Code: {code}")
        rendered = t.render(code="if x > 0 && y < 10: pass")
        assert "if x > 0 && y < 10: pass" in rendered

    def test_render_numeric_values(self):
        """render() should convert non-string values via str()."""
        t = PromptTemplate(name="t", template_str="Count: {n}")
        rendered = t.render(n=42)
        assert rendered == "Count: 42"

    def test_render_empty_string_value(self):
        """render() should allow empty string as variable value."""
        t = PromptTemplate(name="t", template_str="Value: {val}")
        rendered = t.render(val="")
        assert rendered == "Value: "


@pytest.mark.unit
class TestPromptTemplateValidation:
    """Tests for template variable validation."""

    def test_validate_all_present(self):
        """validate() should return empty list when all variables provided."""
        t = PromptTemplate(name="t", template_str="{a} {b}")
        assert t.validate(a="x", b="y") == []

    def test_validate_missing_one(self):
        """validate() should return the missing variable name."""
        t = PromptTemplate(name="t", template_str="{a} {b}")
        missing = t.validate(a="x")
        assert missing == ["b"]

    def test_validate_all_missing(self):
        """validate() should return all variables when none provided."""
        t = PromptTemplate(name="t", template_str="{a} {b}")
        missing = t.validate()
        assert sorted(missing) == ["a", "b"]

    def test_validate_no_variables_template(self):
        """validate() should return empty for template with no variables."""
        t = PromptTemplate(name="t", template_str="No vars here")
        assert t.validate() == []

    def test_validate_does_not_modify_template(self):
        """validate() should be pure -- not modify the template."""
        t = PromptTemplate(name="t", template_str="{x}")
        original_str = t.template_str
        t.validate()
        assert t.template_str == original_str


@pytest.mark.unit
class TestPromptTemplateSerialization:
    """Tests for to_dict/from_dict serialization."""

    def test_round_trip(self):
        """to_dict then from_dict should produce equivalent template."""
        t = PromptTemplate(
            name="test",
            template_str="Do {action}",
            version="2.0.0",
            metadata={"author": "tester"},
        )
        d = t.to_dict()
        restored = PromptTemplate.from_dict(d)
        assert restored.name == t.name
        assert restored.template_str == t.template_str
        assert restored.version == t.version
        assert restored.metadata == t.metadata

    def test_to_dict_has_expected_keys(self):
        """to_dict should include all expected keys."""
        t = PromptTemplate(name="t", template_str="{x}")
        d = t.to_dict()
        for key in ("name", "template_str", "variables", "version", "metadata"):
            assert key in d

    def test_from_dict_defaults(self):
        """from_dict should handle missing optional keys with defaults."""
        d = {"name": "t", "template_str": "Hello"}
        t = PromptTemplate.from_dict(d)
        assert t.version == "1.0.0"
        assert t.metadata == {}

    def test_variables_in_dict(self):
        """to_dict should include the detected variables."""
        t = PromptTemplate(name="t", template_str="{a} and {b}")
        d = t.to_dict()
        assert sorted(d["variables"]) == ["a", "b"]

    def test_metadata_preserved(self):
        """Metadata should survive serialization round trip."""
        t = PromptTemplate(
            name="t",
            template_str="Hi",
            metadata={"tags": ["greeting"], "priority": 1},
        )
        restored = PromptTemplate.from_dict(t.to_dict())
        assert restored.metadata["tags"] == ["greeting"]
        assert restored.metadata["priority"] == 1


@pytest.mark.unit
class TestTemplateRegistryCRUD:
    """Tests for TemplateRegistry add/get/update/remove operations."""

    def _make(self, name="t1"):
        return PromptTemplate(name=name, template_str=f"Template {name}: {{var}}")

    def test_add_and_get(self):
        """add() then get() should return the same template."""
        reg = TemplateRegistry()
        t = self._make("greet")
        reg.add(t)
        assert reg.get("greet") is t

    def test_add_duplicate_raises(self):
        """add() should raise ValueError for duplicate name."""
        reg = TemplateRegistry()
        reg.add(self._make("dup"))
        with pytest.raises(ValueError, match="already exists"):
            reg.add(self._make("dup"))

    def test_update_replaces(self):
        """update() should replace an existing template."""
        reg = TemplateRegistry()
        reg.add(self._make("t"))
        new_t = PromptTemplate(name="t", template_str="Updated: {var}")
        reg.update(new_t)
        assert "Updated" in reg.get("t").template_str

    def test_remove_deletes(self):
        """remove() should delete and return the template."""
        reg = TemplateRegistry()
        reg.add(self._make("rm"))
        removed = reg.remove("rm")
        assert removed.name == "rm"
        with pytest.raises(KeyError):
            reg.get("rm")

    def test_remove_nonexistent_raises(self):
        """remove() should raise KeyError for missing template."""
        reg = TemplateRegistry()
        with pytest.raises(KeyError):
            reg.remove("ghost")

    def test_get_nonexistent_raises(self):
        """get() should raise KeyError for missing template."""
        reg = TemplateRegistry()
        with pytest.raises(KeyError, match="not found"):
            reg.get("nonexistent")

    def test_list_returns_sorted_names(self):
        """list() should return template names sorted alphabetically."""
        reg = TemplateRegistry()
        reg.add(self._make("c"))
        reg.add(self._make("a"))
        reg.add(self._make("b"))
        assert reg.list() == ["a", "b", "c"]

    def test_size_property(self):
        """size should reflect number of registered templates."""
        reg = TemplateRegistry()
        assert reg.size == 0
        reg.add(self._make("a"))
        assert reg.size == 1
        reg.add(self._make("b"))
        assert reg.size == 2


@pytest.mark.unit
class TestTemplateRegistryAdvanced:
    """Tests for registry render, search, export/import operations."""

    def test_render_via_registry(self):
        """render() should render template by name with variables."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="greet", template_str="Hi {name}"))
        result = reg.render("greet", name="World")
        assert result == "Hi World"

    def test_search_by_name(self):
        """search() should find templates by name substring."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="code_review", template_str="Review {code}"))
        reg.add(PromptTemplate(name="code_fix", template_str="Fix {code}"))
        reg.add(PromptTemplate(name="summarize", template_str="Sum {text}"))
        results = reg.search("code")
        assert len(results) == 2

    def test_search_by_metadata(self):
        """search() should find templates by metadata value."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="t1", template_str="A", metadata={"tag": "python"}))
        reg.add(PromptTemplate(name="t2", template_str="B", metadata={"tag": "rust"}))
        results = reg.search("python")
        assert len(results) == 1
        assert results[0].name == "t1"

    def test_search_no_results(self):
        """search() should return empty list when nothing matches."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="hello", template_str="Hi"))
        assert reg.search("zzz_no_match") == []

    def test_export_all(self):
        """export_all() should return list of dicts for all templates."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="a", template_str="A: {x}"))
        reg.add(PromptTemplate(name="b", template_str="B: {y}"))
        exported = reg.export_all()
        assert len(exported) == 2
        assert all(isinstance(d, dict) for d in exported)

    def test_import_all_new(self):
        """import_all() should import new templates."""
        reg = TemplateRegistry()
        data = [
            {"name": "a", "template_str": "A: {x}"},
            {"name": "b", "template_str": "B: {y}"},
        ]
        count = reg.import_all(data)
        assert count == 2
        assert reg.size == 2

    def test_import_all_skip_existing(self):
        """import_all() without overwrite should skip existing names."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="a", template_str="Original"))
        data = [{"name": "a", "template_str": "New"}]
        count = reg.import_all(data, overwrite=False)
        assert count == 0
        assert "Original" in reg.get("a").template_str

    def test_import_all_overwrite(self):
        """import_all() with overwrite=True should replace existing."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="a", template_str="Original"))
        data = [{"name": "a", "template_str": "Replaced"}]
        count = reg.import_all(data, overwrite=True)
        assert count == 1
        assert "Replaced" in reg.get("a").template_str

    def test_list_templates_returns_objects(self):
        """list_templates() should return PromptTemplate objects sorted by name."""
        reg = TemplateRegistry()
        reg.add(PromptTemplate(name="b", template_str="B"))
        reg.add(PromptTemplate(name="a", template_str="A"))
        templates = reg.list_templates()
        assert len(templates) == 2
        assert templates[0].name == "a"
        assert templates[1].name == "b"


@pytest.mark.unit
class TestDefaultRegistry:
    """Tests for the module-level default template registry."""

    def test_get_default_registry_returns_registry(self):
        """get_default_registry() should return a TemplateRegistry instance."""
        reg = get_default_registry()
        assert isinstance(reg, TemplateRegistry)

    def test_default_registry_is_singleton(self):
        """get_default_registry() should return the same instance each time."""
        reg1 = get_default_registry()
        reg2 = get_default_registry()
        assert reg1 is reg2

    def test_default_registry_is_usable(self):
        """Default registry should support add/get/remove operations."""
        reg = get_default_registry()
        test_name = "_test_default_registry_template"
        try:
            t = PromptTemplate(name=test_name, template_str="test {x}")
            reg.add(t)
            assert reg.get(test_name) is t
        finally:
            # Clean up so other tests aren't affected
            try:
                reg.remove(test_name)
            except KeyError:
                pass

    def test_default_registry_size_is_int(self):
        """Default registry size should be an integer."""
        reg = get_default_registry()
        assert isinstance(reg.size, int)

    def test_default_registry_list_is_list(self):
        """Default registry list() should return a list."""
        reg = get_default_registry()
        assert isinstance(reg.list(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
