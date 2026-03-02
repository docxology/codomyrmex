"""Unit tests for DocumentationGenerator.

Tests cover initialization, template loading, variable substitution,
directory purpose mapping, and all generate_* methods using real
filesystem operations via tmp_path.
"""

from pathlib import Path

import pytest

from codomyrmex.logistics.orchestration.project.documentation_generator import (
    DocumentationGenerator,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def gen(tmp_path: Path) -> DocumentationGenerator:
    """DocumentationGenerator with a tmp_path-based templates directory."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    return DocumentationGenerator(templates_dir=templates_dir)


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    """Create a minimal project directory layout."""
    project = tmp_path / "my_project"
    project.mkdir()
    for sub in ("src", "tests", "docs", "config"):
        (project / sub).mkdir()
    return project


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDocumentationGeneratorInit:
    """Initialization and constructor behaviour."""

    def test_init_with_custom_templates_dir(self, tmp_path: Path):
        """Constructor stores the supplied templates_dir."""
        tdir = tmp_path / "custom_templates"
        gen = DocumentationGenerator(templates_dir=tdir)
        assert gen.templates_dir == tdir
        assert tdir.exists()  # mkdir(parents=True, exist_ok=True)

    def test_init_creates_templates_dir_if_missing(self, tmp_path: Path):
        """Constructor creates templates directory when it does not exist."""
        tdir = tmp_path / "deep" / "nested" / "templates"
        assert not tdir.exists()
        gen = DocumentationGenerator(templates_dir=tdir)
        assert gen.templates_dir == tdir
        assert tdir.exists()

    def test_init_default_templates_dir_when_none(self):
        """Constructor falls back to module-relative templates directory."""
        gen = DocumentationGenerator(templates_dir=None)
        assert gen.templates_dir.name == "doc_templates"
        assert gen.templates_dir.exists()


@pytest.mark.unit
class TestLoadTemplate:
    """Template file loading via _load_template."""

    def test_load_existing_template(self, gen: DocumentationGenerator):
        """Returns content when the template file exists."""
        (gen.templates_dir / "hello.md").write_text("Hello {{name}}", encoding="utf-8")
        result = gen._load_template("hello.md")
        assert result == "Hello {{name}}"

    def test_load_nonexistent_template_returns_none(self, gen: DocumentationGenerator):
        """Returns None when the template file does not exist."""
        result = gen._load_template("does_not_exist.md")
        assert result is None

    def test_load_template_utf8_content(self, gen: DocumentationGenerator):
        """Loads UTF-8 content (accents, symbols) without error."""
        (gen.templates_dir / "utf8.md").write_text(
            "Caf\u00e9 \u2014 \u2603", encoding="utf-8"
        )
        result = gen._load_template("utf8.md")
        assert "\u00e9" in result
        assert "\u2603" in result


@pytest.mark.unit
class TestSubstituteVariables:
    """Variable substitution with {{variable}} syntax."""

    def test_basic_substitution(self, gen: DocumentationGenerator):
        """Replaces {{key}} with corresponding value."""
        result = gen._substitute_variables("Hello {{name}}!", {"name": "World"})
        assert result == "Hello World!"

    def test_substitution_with_spaces(self, gen: DocumentationGenerator):
        """Replaces {{ key }} (with spaces) with value."""
        result = gen._substitute_variables("Hello {{ name }}!", {"name": "World"})
        assert result == "Hello World!"

    def test_multiple_variables(self, gen: DocumentationGenerator):
        """Replaces multiple distinct variables."""
        template = "{{greeting}}, {{name}}! Version {{ver}}"
        result = gen._substitute_variables(
            template, {"greeting": "Hi", "name": "Bob", "ver": "1.0"}
        )
        assert result == "Hi, Bob! Version 1.0"

    def test_no_variables_returns_unchanged(self, gen: DocumentationGenerator):
        """Content with no placeholders is returned unchanged."""
        content = "No variables here."
        result = gen._substitute_variables(content, {"unused": "val"})
        assert result == content

    def test_empty_variables_dict(self, gen: DocumentationGenerator):
        """Empty dict leaves template unchanged."""
        content = "Hello {{name}}"
        result = gen._substitute_variables(content, {})
        assert result == content


@pytest.mark.unit
class TestGetDirectoryPurpose:
    """Directory purpose resolution."""

    def test_known_directory_names(self, gen: DocumentationGenerator):
        """Known directory names return their exact purpose."""
        assert "Source code" in gen._get_directory_purpose("src", "python")
        assert "Test" in gen._get_directory_purpose("tests", "python")
        assert "Configuration" in gen._get_directory_purpose("config", "python")
        assert "Documentation" in gen._get_directory_purpose("docs", "python")

    def test_partial_match(self, gen: DocumentationGenerator):
        """Directory names containing a known key get a partial match."""
        result = gen._get_directory_purpose("my_tests_dir", "python")
        assert "Test" in result

    def test_unknown_directory_fallback(self, gen: DocumentationGenerator):
        """Unknown directories get a generic fallback description."""
        result = gen._get_directory_purpose("random_stuff", "python")
        assert "random_stuff" in result


@pytest.mark.unit
class TestGetDirectoryAgentPurpose:
    """Directory agent purpose descriptions."""

    def test_basic_agent_purpose(self, gen: DocumentationGenerator):
        """Returns agent surface string with directory and project name."""
        result = gen._get_directory_agent_purpose("my_module", "MyProject")
        assert "my module" in result
        assert "MyProject" in result

    def test_underscores_replaced(self, gen: DocumentationGenerator):
        """Underscores in dir_name are replaced with spaces."""
        result = gen._get_directory_agent_purpose("some_deep_module", "Proj")
        assert "some deep module" in result


@pytest.mark.unit
class TestGenerateRootReadme:
    """Root README.md generation."""

    def test_generates_readme_file(self, gen: DocumentationGenerator, project_dir: Path):
        """Creates a README.md at project root."""
        result = gen.generate_root_readme(
            project_dir, "TestProject", "python", "A test project",
            "1.0.0", "Author", "2026-01-01",
        )
        assert result is True
        readme = project_dir / "README.md"
        assert readme.exists()
        content = readme.read_text(encoding="utf-8")
        assert "TestProject" in content
        assert "1.0.0" in content
        assert "2026-01-01" in content

    def test_uses_custom_template_when_available(
        self, gen: DocumentationGenerator, project_dir: Path
    ):
        """Loads <template>_README.template.md when template arg is given."""
        (gen.templates_dir / "special_README.template.md").write_text(
            "# CUSTOM {{project_name}} v{{version}}", encoding="utf-8"
        )
        result = gen.generate_root_readme(
            project_dir, "Proj", "python", "desc", "2.0", "Auth", "2026",
            template="special",
        )
        assert result is True
        content = (project_dir / "README.md").read_text(encoding="utf-8")
        assert "CUSTOM Proj v2.0" in content

    def test_falls_back_to_default_template(
        self, gen: DocumentationGenerator, project_dir: Path
    ):
        """When no template file exists, the built-in default template is used."""
        result = gen.generate_root_readme(
            project_dir, "FallbackProj", "python", "desc",
            "0.1", "Auth", "2026",
        )
        assert result is True
        content = (project_dir / "README.md").read_text(encoding="utf-8")
        assert "FallbackProj" in content
        # Default template has '## Overview' heading
        assert "## Overview" in content

    def test_empty_description_uses_project_type(
        self, gen: DocumentationGenerator, project_dir: Path
    ):
        """Empty description is replaced with a project-type-derived string."""
        gen.generate_root_readme(
            project_dir, "P", "data_science", "", "1.0", "", "2026",
        )
        content = (project_dir / "README.md").read_text(encoding="utf-8")
        assert "Data Science" in content


@pytest.mark.unit
class TestGenerateRootAgents:
    """Root AGENTS.md generation."""

    def test_generates_agents_file(self, gen: DocumentationGenerator, project_dir: Path):
        """Creates an AGENTS.md at project root."""
        result = gen.generate_root_agents(
            project_dir, "TestProject", "python", "A test project",
            ["src", "tests"],
        )
        assert result is True
        agents = project_dir / "AGENTS.md"
        assert agents.exists()
        content = agents.read_text(encoding="utf-8")
        assert "TestProject" in content
        assert "`src/`" in content
        assert "`tests/`" in content

    def test_empty_nested_dirs_shows_no_components(
        self, gen: DocumentationGenerator, project_dir: Path
    ):
        """When nested_dirs is empty, active_components says 'No active components'."""
        gen.generate_root_agents(
            project_dir, "P", "python", "desc", [],
        )
        content = (project_dir / "AGENTS.md").read_text(encoding="utf-8")
        assert "No active components" in content


@pytest.mark.unit
class TestGenerateNestedReadme:
    """Nested directory README.md generation."""

    def test_generates_nested_readme(self, gen: DocumentationGenerator, project_dir: Path):
        """Creates README.md inside a nested directory."""
        nested = project_dir / "src"
        result = gen.generate_nested_readme(
            nested, "src", "MyProject", "python", parent_path=project_dir,
        )
        assert result is True
        readme = nested / "README.md"
        assert readme.exists()
        content = readme.read_text(encoding="utf-8")
        assert "src" in content
        assert "MyProject" in content

    def test_parent_link_present(self, gen: DocumentationGenerator, project_dir: Path):
        """Parent link is rendered when parent_path is provided."""
        nested = project_dir / "docs"
        gen.generate_nested_readme(
            nested, "docs", "P", "python", parent_path=project_dir,
        )
        content = (nested / "README.md").read_text(encoding="utf-8")
        assert "Parent Directory" in content
        assert "../README.md" in content

    def test_no_parent_link_when_none(self, gen: DocumentationGenerator, project_dir: Path):
        """No parent link when parent_path is None."""
        nested = project_dir / "config"
        gen.generate_nested_readme(nested, "config", "P", "python", parent_path=None)
        content = (nested / "README.md").read_text(encoding="utf-8")
        assert "Parent Directory" not in content


@pytest.mark.unit
class TestGenerateNestedAgents:
    """Nested directory AGENTS.md generation."""

    def test_generates_nested_agents(self, gen: DocumentationGenerator, project_dir: Path):
        """Creates AGENTS.md inside a nested directory."""
        nested = project_dir / "tests"
        result = gen.generate_nested_agents(
            nested, "tests", "MyProject", "python", parent_path=project_dir,
        )
        assert result is True
        agents = nested / "AGENTS.md"
        assert agents.exists()
        content = agents.read_text(encoding="utf-8")
        assert "tests" in content
        assert "MyProject" in content

    def test_parent_agents_link_present(
        self, gen: DocumentationGenerator, project_dir: Path
    ):
        """Parent agents link is rendered when parent_path is provided."""
        nested = project_dir / "src"
        gen.generate_nested_agents(
            nested, "src", "P", "python", parent_path=project_dir,
        )
        content = (nested / "AGENTS.md").read_text(encoding="utf-8")
        assert "Parent Agents" in content
        assert "../AGENTS.md" in content


@pytest.mark.unit
class TestGenerateAllDocumentation:
    """Full documentation generation orchestration."""

    def test_generates_root_and_nested_docs(
        self, gen: DocumentationGenerator, project_dir: Path
    ):
        """Generates README.md + AGENTS.md at root and in each nested dir."""
        result = gen.generate_all_documentation(
            project_path=project_dir,
            project_name="FullProject",
            project_type="python",
            description="A complete project",
            version="3.0",
            author="Team",
            created_at="2026-02-26",
            nested_dirs=["src", "tests", "docs"],
        )
        assert result is True

        # Root files
        assert (project_dir / "README.md").exists()
        assert (project_dir / "AGENTS.md").exists()

        # Nested files
        for sub in ("src", "tests", "docs"):
            assert (project_dir / sub / "README.md").exists()
            assert (project_dir / sub / "AGENTS.md").exists()

    def test_skips_nonexistent_nested_dirs(
        self, gen: DocumentationGenerator, project_dir: Path
    ):
        """Nested dirs that do not exist on disk are silently skipped."""
        result = gen.generate_all_documentation(
            project_path=project_dir,
            project_name="P",
            project_type="python",
            description="desc",
            version="1.0",
            author="A",
            created_at="2026",
            nested_dirs=["nonexistent_dir"],
        )
        # Root docs still generated successfully
        assert result is True
        assert (project_dir / "README.md").exists()
        assert not (project_dir / "nonexistent_dir").exists()

    def test_doc_links_disabled_skips_nested(
        self, gen: DocumentationGenerator, project_dir: Path
    ):
        """When doc_links['enabled'] is False, nested docs are not generated."""
        gen.generate_all_documentation(
            project_path=project_dir,
            project_name="P",
            project_type="python",
            description="desc",
            version="1.0",
            author="A",
            created_at="2026",
            nested_dirs=["src"],
            doc_links={"enabled": False},
        )
        # Root exists
        assert (project_dir / "README.md").exists()
        # Nested NOT generated
        assert not (project_dir / "src" / "README.md").exists()

    def test_default_doc_links_when_none(
        self, gen: DocumentationGenerator, project_dir: Path
    ):
        """When doc_links is None, defaults enable nested doc generation."""
        gen.generate_all_documentation(
            project_path=project_dir,
            project_name="P",
            project_type="python",
            description="desc",
            version="1.0",
            author="A",
            created_at="2026",
            nested_dirs=["src"],
            doc_links=None,
        )
        assert (project_dir / "src" / "README.md").exists()

    def test_trailing_slash_in_nested_dirs_handled(
        self, gen: DocumentationGenerator, project_dir: Path
    ):
        """Trailing slashes on nested dir names are stripped correctly."""
        gen.generate_all_documentation(
            project_path=project_dir,
            project_name="P",
            project_type="python",
            description="desc",
            version="1.0",
            author="A",
            created_at="2026",
            nested_dirs=["src/"],
        )
        assert (project_dir / "src" / "README.md").exists()
        assert (project_dir / "src" / "AGENTS.md").exists()
