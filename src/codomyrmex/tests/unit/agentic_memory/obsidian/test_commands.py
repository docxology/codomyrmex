"""Tests for miscellaneous CLI commands."""

import pytest

from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable
from codomyrmex.agentic_memory.obsidian.commands import (
    DiffResult,
    HistoryEntry,
    OutlineItem,
    WordCount,
    generate_unique_id,
    get_backlinks_cli,
    get_deadends,
    get_diff,
    get_history,
    get_hotkey,
    get_links,
    get_orphans,
    get_outline,
    get_unresolved,
    get_version,
    get_wordcount,
    list_commands,
    list_history,
    list_hotkeys,
    open_history,
    open_random,
    open_web,
    read_history,
    read_random,
    reload_vault,
    restart_app,
    restore_history,
    run_command,
)


class TestCommandModels:
    def test_diff_result(self):
        d = DiffResult(file="note.md", diff_text="+ added", has_changes=True)
        assert d.has_changes is True

    def test_diff_result_no_changes(self):
        d = DiffResult(file="note.md")
        assert d.has_changes is False

    def test_history_entry(self):
        h = HistoryEntry(version="v1", timestamp="2024-01-01")
        assert h.version == "v1"

    def test_outline_item(self):
        o = OutlineItem(level=2, text="Section")
        assert o.level == 2

    def test_word_count(self):
        wc = WordCount(words=500, characters=3000, sentences=25)
        assert wc.words == 500

    def test_word_count_defaults(self):
        wc = WordCount()
        assert wc.words == 0


class TestWordCountParsing:
    def test_parse_output(self):
        lines = ["Words: 500", "Characters: 3,000", "Sentences: 25", "Paragraphs: 10"]
        wc = WordCount()
        for line in lines:
            parts = line.split(":")
            if len(parts) == 2:
                label = parts[0].strip().lower()
                try:
                    val = int(parts[1].strip().replace(",", ""))
                except ValueError:
                    continue
                if "word" in label:
                    wc.words = val
                elif "character" in label:
                    wc.characters = val
                elif "sentence" in label:
                    wc.sentences = val
                elif "paragraph" in label:
                    wc.paragraphs = val
        assert wc.words == 500
        assert wc.characters == 3000


class TestOutlineParsing:
    def test_parse_hash_headings(self):
        lines = ["# Title", "## Section", "### Subsection"]
        items = []
        for line in lines:
            stripped = line.strip()
            level = 0
            text = stripped
            if stripped.startswith("#"):
                hashes = stripped.split(" ", 1)[0]
                level = len(hashes)
                text = stripped[level:].strip()
            items.append(OutlineItem(level=level, text=text, raw=line))
        assert items[0].level == 1
        assert items[0].text == "Title"
        assert items[2].level == 3


class TestCommandsUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_list_commands(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_commands(self._cli())

    def test_list_commands_with_filter(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_commands(self._cli(), filter="editor")

    def test_run_command(self):
        with pytest.raises(ObsidianCLINotAvailable):
            run_command(self._cli(), "editor:toggle-bold")

    def test_list_hotkeys(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_hotkeys(self._cli())

    def test_get_hotkey(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_hotkey(self._cli(), "editor:toggle-bold")

    def test_get_diff(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_diff(self._cli(), file="note.md")

    def test_get_diff_with_versions(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_diff(self._cli(), file="note", from_version=1, to_version=3, filter="local")

    def test_get_history(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_history(self._cli(), file="note")

    def test_list_history(self):
        with pytest.raises(ObsidianCLINotAvailable):
            list_history(self._cli(), file="note")

    def test_read_history(self):
        with pytest.raises(ObsidianCLINotAvailable):
            read_history(self._cli(), file="note", version="v1")

    def test_restore_history(self):
        with pytest.raises(ObsidianCLINotAvailable):
            restore_history(self._cli(), file="note", version="v1")

    def test_open_history(self):
        with pytest.raises(ObsidianCLINotAvailable):
            open_history(self._cli(), file="note")


class TestLinksUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_get_backlinks_cli(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_backlinks_cli(self._cli(), file="note")

    def test_get_links(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_links(self._cli(), file="note")

    def test_get_unresolved(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_unresolved(self._cli())

    def test_get_orphans(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_orphans(self._cli())

    def test_get_deadends(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_deadends(self._cli())


class TestMiscUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_get_outline(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_outline(self._cli(), file="note")

    def test_get_wordcount(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_wordcount(self._cli(), file="note")

    def test_open_random(self):
        with pytest.raises(ObsidianCLINotAvailable):
            open_random(self._cli())

    def test_read_random(self):
        with pytest.raises(ObsidianCLINotAvailable):
            read_random(self._cli())

    def test_generate_unique_id(self):
        with pytest.raises(ObsidianCLINotAvailable):
            generate_unique_id(self._cli())

    def test_open_web(self):
        with pytest.raises(ObsidianCLINotAvailable):
            open_web(self._cli(), "https://example.com")

    def test_get_version(self):
        with pytest.raises(ObsidianCLINotAvailable):
            get_version(self._cli())

    def test_reload_vault(self):
        with pytest.raises(ObsidianCLINotAvailable):
            reload_vault(self._cli())

    def test_restart_app(self):
        with pytest.raises(ObsidianCLINotAvailable):
            restart_app(self._cli())
