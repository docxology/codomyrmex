"""Tests for droid doc_generators — zero-mock.

Covers: generate_physical_readme_content, generate_physical_api_spec,
generate_physical_examples, generate_physical_tests,
generate_physical_requirements, generate_physical_docs_content.
All functions return large documentation/code strings.
"""


from codomyrmex.agents.droid.generators.physical_generators.doc_generators import (
    generate_physical_api_spec,
    generate_physical_docs_content,
    generate_physical_examples,
    generate_physical_readme_content,
    generate_physical_requirements,
    generate_physical_tests,
)


class TestGeneratePhysicalReadmeContent:
    def test_returns_string(self):
        result = generate_physical_readme_content()
        assert isinstance(result, str)
        assert len(result) > 50

    def test_contains_markdown(self):
        result = generate_physical_readme_content()
        assert "#" in result  # Should have markdown headings


class TestGeneratePhysicalApiSpec:
    def test_returns_string(self):
        result = generate_physical_api_spec()
        assert isinstance(result, str)
        assert len(result) > 50

    def test_contains_api_keywords(self):
        result = generate_physical_api_spec()
        lower = result.lower()
        assert "api" in lower or "endpoint" in lower or "class" in lower


class TestGeneratePhysicalExamples:
    def test_returns_string(self):
        result = generate_physical_examples()
        assert isinstance(result, str)
        assert len(result) > 50

    def test_contains_code(self):
        result = generate_physical_examples()
        assert "import" in result or "def " in result or "class " in result


class TestGeneratePhysicalTests:
    def test_returns_string(self):
        result = generate_physical_tests()
        assert isinstance(result, str)
        assert len(result) > 50

    def test_contains_test_patterns(self):
        result = generate_physical_tests()
        assert "test" in result.lower() or "assert" in result.lower()


class TestGeneratePhysicalRequirements:
    def test_returns_string(self):
        result = generate_physical_requirements()
        assert isinstance(result, str)
        assert len(result) > 0


class TestGeneratePhysicalDocsContent:
    def test_returns_string(self):
        result = generate_physical_docs_content()
        assert isinstance(result, str)
        assert len(result) > 50

    def test_contains_documentation(self):
        result = generate_physical_docs_content()
        assert "#" in result or "Architecture" in result or "module" in result.lower()
