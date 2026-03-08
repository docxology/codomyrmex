"""Tests for HandsManager output parsing — zero-mock."""
import pytest

from codomyrmex.agents.openfang.hands import Hand, HandsManager


class TestHandDataclass:
    def test_hand_requires_name(self):
        h = Hand(name="my-hand")
        assert h.name == "my-hand"

    def test_hand_defaults(self):
        h = Hand(name="test")
        assert h.description == ""
        assert h.schedule == ""
        assert h.enabled is True
        assert h.tags == []

    def test_hand_with_all_fields(self):
        h = Hand(
            name="daily-reporter",
            description="Sends daily reports",
            schedule="0 9 * * *",
            enabled=True,
            tags=["reporting", "daily"],
        )
        assert h.name == "daily-reporter"
        assert len(h.tags) == 2

    def test_hand_disabled(self):
        h = Hand(name="old-hand", enabled=False)
        assert h.enabled is False

    def test_hand_repr_contains_name(self):
        h = Hand(name="test-hand")
        assert "test-hand" in repr(h)


class TestHandsManagerParseEmpty:
    def test_empty_string_returns_empty_list(self):
        result = HandsManager.parse_list_output("")
        assert result == []

    def test_whitespace_only_returns_empty_list(self):
        result = HandsManager.parse_list_output("   \n  \n  ")
        assert result == []

    def test_returns_list_type(self):
        result = HandsManager.parse_list_output("")
        assert isinstance(result, list)


class TestHandsManagerParseSingle:
    def test_single_name_only(self):
        raw = "my-hand\n"
        result = HandsManager.parse_list_output(raw)
        assert len(result) == 1
        assert result[0].name == "my-hand"

    def test_single_with_description(self):
        raw = "my-hand\ndescription: Does something useful\n"
        result = HandsManager.parse_list_output(raw)
        assert len(result) == 1
        assert result[0].description == "Does something useful"

    def test_single_with_schedule(self):
        raw = "scheduler-hand\nschedule: 0 * * * *\n"
        result = HandsManager.parse_list_output(raw)
        assert result[0].schedule == "0 * * * *"

    def test_single_enabled_true(self):
        raw = "hand-a\nenabled: true\n"
        result = HandsManager.parse_list_output(raw)
        assert result[0].enabled is True

    def test_single_enabled_false(self):
        raw = "hand-b\nenabled: false\n"
        result = HandsManager.parse_list_output(raw)
        assert result[0].enabled is False

    def test_single_with_tags(self):
        raw = "tagged-hand\ntags: alpha, beta, gamma\n"
        result = HandsManager.parse_list_output(raw)
        assert "alpha" in result[0].tags
        assert "beta" in result[0].tags
        assert "gamma" in result[0].tags


class TestHandsManagerParseMultiple:
    def test_two_hands_separated_by_blank_line(self):
        raw = "hand-one\ndescription: First hand\n\nhand-two\ndescription: Second hand\n"
        result = HandsManager.parse_list_output(raw)
        assert len(result) == 2
        assert result[0].name == "hand-one"
        assert result[1].name == "hand-two"

    def test_multiple_hands_all_parsed(self):
        raw = "a\n\nb\n\nc\n"
        result = HandsManager.parse_list_output(raw)
        assert len(result) == 3

    def test_returns_hand_instances(self):
        raw = "hand-x\n\nhand-y\n"
        result = HandsManager.parse_list_output(raw)
        for h in result:
            assert isinstance(h, Hand)
