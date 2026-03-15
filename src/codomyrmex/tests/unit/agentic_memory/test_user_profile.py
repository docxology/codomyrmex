"""Tests for agentic_memory.user_profile module."""

from pathlib import Path


from codomyrmex.agentic_memory.user_profile import UserProfile


class TestUserProfilePersistence:
    """Tests for save/load round-trip."""

    def test_save_and_load(self, tmp_path: Path) -> None:
        """Profile survives JSON round-trip."""
        profile = UserProfile(
            preferences={"theme": "dark", "lang": "en"},
            history_summary="User likes concise answers.",
        )
        path = tmp_path / "profile.json"
        profile.save(path)

        loaded = UserProfile.load(path)
        assert loaded.preferences == profile.preferences
        assert loaded.history_summary == profile.history_summary

    def test_load_nonexistent_returns_default(self, tmp_path: Path) -> None:
        """Loading a missing file returns a default profile."""
        profile = UserProfile.load(tmp_path / "nope.json")
        assert profile.preferences == {}
        assert profile.history_summary == ""

    def test_load_corrupt_json_returns_default(self, tmp_path: Path) -> None:
        """A corrupt JSON file falls back to defaults instead of crashing."""
        path = tmp_path / "bad.json"
        path.write_text("{not valid json!!!", encoding="utf-8")
        profile = UserProfile.load(path)
        assert profile.preferences == {}

    def test_save_creates_parent_dirs(self, tmp_path: Path) -> None:
        """save() creates intermediate directories."""
        path = tmp_path / "a" / "b" / "c" / "profile.json"
        UserProfile(preferences={"k": "v"}).save(path)
        assert path.exists()


class TestUserProfileHelpers:
    """Tests for set/get preference and context string."""

    def test_set_and_get_preference(self) -> None:
        p = UserProfile()
        p.set_preference("theme", "dark")
        assert p.get_preference("theme") == "dark"

    def test_get_preference_default(self) -> None:
        p = UserProfile()
        assert p.get_preference("missing", 42) == 42

    def test_to_context_string(self) -> None:
        p = UserProfile(preferences={"theme": "dark", "lang": "en"})
        ctx = p.to_context_string()
        assert "theme=dark" in ctx
        assert "lang=en" in ctx

    def test_to_context_string_empty(self) -> None:
        p = UserProfile()
        assert p.to_context_string() == "(no preferences)"

    def test_dataclass_defaults(self) -> None:
        p = UserProfile()
        assert p.preferences == {}
        assert p.history_summary == ""
