"""Tests for property CLI commands."""

import shutil

import pytest

from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable
from codomyrmex.agentic_memory.obsidian.properties import (
    PropertyValue,
    get_aliases,
    get_properties,
    get_tags,
    read_property,
    remove_property,
    set_property,
)

_CLI_AVAILABLE = shutil.which("obsidian") is not None
skip_no_cli = pytest.mark.skipif(
    not _CLI_AVAILABLE,
    reason="Obsidian CLI not available on PATH",
)


class TestPropertyValue:
    def test_create(self):
        pv = PropertyValue(key="title", value="My Note")
        assert pv.key == "title"
        assert pv.value == "My Note"
        assert pv.type == ""
        assert pv.raw == ""

    def test_with_type(self):
        pv = PropertyValue(key="tags", value="[a, b]", type="list")
        assert pv.type == "list"


class TestPropertyParsing:
    def test_parse_colon_format(self):
        lines = ["title: My Note", "tags: [a, b]", "created: 2024-01-01"]
        props = []
        for line in lines:
            if ":" in line:
                key, _, value = line.partition(":")
                props.append(PropertyValue(
                    key=key.strip(), value=value.strip(), raw=line
                ))
        assert len(props) == 3
        assert props[0].key == "title"
        assert props[2].key == "created"

    def test_parse_single_column(self):
        pv = PropertyValue(key="orphan-key", value="", raw="orphan-key")
        assert pv.value == ""


class TestPropertyUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_get_aliases(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_aliases(self._cli(), file="note")

    def test_get_aliases_flags(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_aliases(self._cli(), total=True, verbose=True, active=True)

    def test_get_properties(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_properties(self._cli(), file="note")

    def test_get_properties_all_params(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_properties(
                self._cli(), file="note",
                name="title", sort="count", format="json",
                total=True, counts=True, active=True,
            )

    def test_read_property(self):
        with pytest.raises(ObsidianCLINotAvailable):
            read_property(self._cli(), "title", file="note")

    def test_set_property(self):
        with pytest.raises(ObsidianCLINotAvailable):
            set_property(self._cli(), "title", "New Title", file="note")

    def test_set_property_with_type(self):
        with pytest.raises(ObsidianCLINotAvailable):
            set_property(
                self._cli(), "tags", "a,b",
                type="list", file="note",
            )

    def test_remove_property(self):
        with pytest.raises(ObsidianCLINotAvailable):
            remove_property(self._cli(), "title", file="note")

    def test_get_tags(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_tags(self._cli())

    def test_get_tags_with_counts(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_tags(self._cli(), counts=True)
