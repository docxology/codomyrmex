"""Tests for sync & publish CLI commands."""

import pytest

from codomyrmex.agentic_memory.obsidian.cli import ObsidianCLI, ObsidianCLINotAvailable
from codomyrmex.agentic_memory.obsidian.sync import (
    PublishStatus, SyncHistoryEntry, SyncStatus,
    publish_add, publish_list, publish_open, publish_remove,
    publish_site, publish_status,
    sync_deleted, sync_history, sync_open, sync_read,
    sync_restore, sync_status, sync_toggle,
)


class TestSyncModels:
    def test_sync_status_defaults(self):
        s = SyncStatus()
        assert s.connected is False
        assert s.vault_name == ""
        assert s.pending_changes == 0

    def test_sync_history_entry(self):
        e = SyncHistoryEntry(file="note.md", action="upload")
        assert e.file == "note.md"

    def test_publish_status_defaults(self):
        p = PublishStatus()
        assert p.site_url == ""
        assert p.published_count == 0


class TestSyncUnavailable:
    def _cli(self):
        return ObsidianCLI(binary="__nonexistent__")

    def test_sync_toggle(self):
        with pytest.raises(ObsidianCLINotAvailable):
            sync_toggle(self._cli(), "on")

    def test_sync_status(self):
        with pytest.raises(ObsidianCLINotAvailable):
            sync_status(self._cli())

    def test_sync_history(self):
        with pytest.raises(ObsidianCLINotAvailable):
            sync_history(self._cli())

    def test_sync_read(self):
        with pytest.raises(ObsidianCLINotAvailable):
            sync_read(self._cli(), file="note")

    def test_sync_restore(self):
        with pytest.raises(ObsidianCLINotAvailable):
            sync_restore(self._cli(), file="note", version="v1")

    def test_sync_open(self):
        with pytest.raises(ObsidianCLINotAvailable):
            sync_open(self._cli(), file="note")

    def test_sync_deleted(self):
        with pytest.raises(ObsidianCLINotAvailable):
            sync_deleted(self._cli())

    def test_publish_site(self):
        with pytest.raises(ObsidianCLINotAvailable):
            publish_site(self._cli())

    def test_publish_list(self):
        with pytest.raises(ObsidianCLINotAvailable):
            publish_list(self._cli())

    def test_publish_status(self):
        with pytest.raises(ObsidianCLINotAvailable):
            publish_status(self._cli())

    def test_publish_add(self):
        with pytest.raises(ObsidianCLINotAvailable):
            publish_add(self._cli(), file="note")

    def test_publish_remove(self):
        with pytest.raises(ObsidianCLINotAvailable):
            publish_remove(self._cli(), file="note")

    def test_publish_open(self):
        with pytest.raises(ObsidianCLINotAvailable):
            publish_open(self._cli(), file="note")
