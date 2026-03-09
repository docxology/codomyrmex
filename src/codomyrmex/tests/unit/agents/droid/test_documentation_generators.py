"""Tests for droid documentation generators — zero-mock.

Covers: assess_readme_quality, assess_agents_quality, assess_technical_accuracy,
generate_quality_tests, generate_documentation_quality_module,
generate_consistency_checker_module.
"""

from pathlib import Path


from codomyrmex.agents.droid.generators.documentation import (
    assess_agents_quality,
    assess_readme_quality,
    assess_technical_accuracy,
    generate_consistency_checker_module,
    generate_documentation_quality_module,
    generate_quality_tests,
)


class TestAssessReadmeQuality:
    def test_good_readme(self):
        content = (
            "# My Project\n\n"
            "## Installation\nRun `pip install myproject`.\n\n"
            "## Usage\nImport and use:\n```python\nimport myproject\n```\n\n"
            "## Contributing\nSee CONTRIBUTING.md\n\n"
            "## License\nMIT\n"
        )
        score = assess_readme_quality(content, Path("README.md"))
        assert isinstance(score, int)
        assert score >= 0

    def test_empty_readme(self):
        score = assess_readme_quality("", Path("README.md"))
        assert isinstance(score, int)

    def test_minimal_readme(self):
        score = assess_readme_quality("# Title\nSome text.", Path("README.md"))
        assert isinstance(score, int)


class TestAssessAgentsQuality:
    def test_good_agents(self):
        content = (
            "# AGENTS.md\n\n"
            "## Agent: Architect\nRole: System design\n\n"
            "## Agent: Coder\nRole: Implementation\n"
        )
        score = assess_agents_quality(content, Path("AGENTS.md"))
        assert isinstance(score, int)

    def test_empty(self):
        score = assess_agents_quality("", Path("AGENTS.md"))
        assert isinstance(score, int)


class TestAssessTechnicalAccuracy:
    def test_accurate_doc(self):
        content = (
            "# API Reference\n\n"
            "## Functions\n"
            "### `process_data(input: dict) -> dict`\n"
            "Processes the input data and returns results.\n"
        )
        score = assess_technical_accuracy(content, Path("api.md"))
        assert isinstance(score, int)

    def test_empty(self):
        score = assess_technical_accuracy("", Path("doc.md"))
        assert isinstance(score, int)


class TestGenerateQualityTests:
    def test_returns_code(self):
        result = generate_quality_tests()
        assert isinstance(result, str)
        assert "test" in result.lower()


class TestGenerateDocQualityModule:
    def test_returns_code(self):
        result = generate_documentation_quality_module()
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_python(self):
        result = generate_documentation_quality_module()
        assert "class " in result or "def " in result


class TestGenerateConsistencyChecker:
    def test_returns_code(self):
        result = generate_consistency_checker_module()
        assert isinstance(result, str)
        assert len(result) > 100
