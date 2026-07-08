"""Tests for template CLI commands."""

import pytest

from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable
from codomyrmex.agentic_memory.obsidian.templates import (
    TemplateInfo,
    _parse_templates,
    insert_template,
    list_templates,
    read_template,
)


class TestTemplateInfo:
    def test_create(self):
        t = TemplateInfo(name="Daily", path="Templates/Daily.md")
        assert t.name == "Daily"
        assert t.path == "Templates/Daily.md"

    def test_defaults(self):
        t = TemplateInfo(name="Test")
        assert t.path == ""


class TestParseTemplates:
    def test_parse_md_paths(self):
        lines = ["Templates/Daily.md", "Templates/Weekly Review.md"]
        templates = _parse_templates(lines)
        assert len(templates) == 2
        assert templates[0].name == "Daily"
        assert templates[1].name == "Weekly Review"

    def test_parse_nested(self):
        templates = _parse_templates(["Templates/Project/Kickoff.md"])
        assert templates[0].name == "Kickoff"

    def test_parse_non_md(self):
        templates = _parse_templates(["Some Template"])
        assert templates[0].name == "Some Template"

    def test_parse_empty_lines(self):
        templates = _parse_templates(["Template1.md", "", "Template2.md"])
        assert len(templates) == 2


class TestTemplateUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_list_templates(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_templates(self._cli())

    def test_read_template(self):
        with pytest.raises(ObsidianCLINotAvailable):
            read_template(self._cli(), file="Daily")

    def test_read_template_with_resolve(self):
        with pytest.raises(ObsidianCLINotAvailable):
            read_template(self._cli(), file="Daily", resolve=True)

    def test_insert_template(self):
        with pytest.raises(ObsidianCLINotAvailable):
            insert_template(self._cli(), "Daily", file="note")
