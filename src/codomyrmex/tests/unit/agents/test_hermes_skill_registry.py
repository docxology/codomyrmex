"""Tests for unified Hermes skill registry, profiles, and merge layers."""

from __future__ import annotations

from pathlib import Path

import pytest

from codomyrmex.agents.hermes import skill_registry
from codomyrmex.agents.hermes.skill_names import normalize_hermes_skill_names


@pytest.mark.unit
class TestSkillRegistryCore:
    def test_merge_ordered_unique(self) -> None:
        assert skill_registry.merge_ordered_unique(
            ["a", "b"],
            ["b", "c"],
            None,
        ) == ["a", "b", "c"]

    def test_resolve_skill_ids_known(self) -> None:
        idx = skill_registry.load_skill_index()
        r = skill_registry.resolve_skill_ids(["codomyrmex-fabric"], index=idx)
        assert r["hermes_preload"] == ["fabric"]
        assert not r["unknown_skill_ids"]

    def test_resolve_skill_ids_unknown(self) -> None:
        r = skill_registry.resolve_skill_ids(["no-such-id-xyz"])
        assert "no-such-id-xyz" in r["unknown_skill_ids"]
        assert r["hermes_preload"] == []

    def test_project_profile_hermes_names(self, tmp_path: Path, monkeypatch) -> None:
        d = tmp_path / ".codomyrmex"
        d.mkdir()
        (d / skill_registry.PROFILE_FILENAME).write_text(
            "version: 1\n"
            "skill_ids:\n  - codomyrmex-fabric\n"
            "hermes_preload:\n  - extra_pack\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)
        names, p = skill_registry.project_profile_hermes_names(tmp_path)
        assert p is not None
        assert "fabric" in names
        assert "extra_pack" in names

    def test_merged_layers_order(self, tmp_path: Path, monkeypatch) -> None:
        prof = tmp_path / ".codomyrmex"
        prof.mkdir()
        (prof / skill_registry.PROFILE_FILENAME).write_text(
            "version: 1\nhermes_preload:\n  - from_profile\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)
        merged = skill_registry.merged_hermes_skill_list_for_client(
            cwd=tmp_path,
            client_config={"hermes_default_hermes_skills": ["from_config"]},
            profile_disabled=False,
            session_skills=["from_session"],
            context={"hermes_skills": ["from_context"]},
        )
        assert merged == [
            "from_profile",
            "from_config",
            "from_session",
            "from_context",
        ]

    def test_parse_cli_skills_output(self) -> None:
        text = "- fabric\n* code_review\n"
        tokens = skill_registry.parse_cli_skills_output(text)
        assert "fabric" in tokens
        assert "code_review" in tokens

    def test_validate_registry_cli_subset(self) -> None:
        idx = skill_registry.load_skill_index()
        cli_text = "\n".join(hp for rec in idx.values() for hp in rec.hermes_preload)
        v = skill_registry.validate_registry_against_cli_lines(cli_text, index=idx)
        assert v["status"] == "ok"


@pytest.mark.unit
class TestNormalizeReexport:
    def test_normalize_from_skill_names(self) -> None:
        assert normalize_hermes_skill_names("a", "b") == ["a", "b"]


@pytest.mark.unit
class TestHermesSkillsResolveMCP:
    def test_hermes_skills_resolve_mcp_success(self) -> None:
        from codomyrmex.agents.hermes.mcp_tools import hermes_skills_resolve

        out = hermes_skills_resolve(["codomyrmex-fabric"])
        assert out["status"] == "success"
        assert "fabric" in out.get("hermes_preload", [])


@pytest.mark.unit
class TestProfileDisabled:
    def test_profile_disable_skips_file(self, tmp_path: Path, monkeypatch) -> None:
        d = tmp_path / ".codomyrmex"
        d.mkdir()
        (d / skill_registry.PROFILE_FILENAME).write_text(
            "version: 1\nhermes_preload:\n  - only_in_profile\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)
        merged = skill_registry.merged_hermes_skill_list_for_client(
            cwd=tmp_path,
            client_config={},
            profile_disabled=True,
            session_skills=None,
            context={},
        )
        assert merged == []
