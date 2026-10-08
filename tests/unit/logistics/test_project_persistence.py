"""Tests for ProjectManager persistence to ``<project>/project.json``.

Projects are saved on creation and after every status, metrics or milestone
update; a new ProjectManager registers ``<projects_root>/*/project.json``.
``Project.from_dict`` round-trips ``Project.to_dict`` (Path, enums, aware
datetimes). Invalid files are logged and skipped.

Zero-mock policy: real directories under ``tmp_path``.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

import pytest

from codomyrmex.logistics.orchestration.project import PROJECT_FILE_NAME
from codomyrmex.logistics.orchestration.project.project_manager import (
    Project,
    ProjectManager,
    ProjectStatus,
    ProjectType,
)

pytestmark = pytest.mark.unit


def read_file(project: Project) -> dict:
    return json.loads(project.metadata_file.read_text(encoding="utf-8"))


@pytest.fixture
def root(tmp_path) -> Path:
    return tmp_path / "projects"


@pytest.fixture
def manager(root) -> ProjectManager:
    root.mkdir()
    return ProjectManager(projects_root=root)


class TestProjectDict:
    def make_project(self) -> Project:
        return Project(
            name="demo",
            path=Path("/srv/demo"),
            type=ProjectType.DATA_PIPELINE,
            description="desc",
            status=ProjectStatus.PAUSED,
            config={"a": [1, 2]},
            created_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC),
            updated_at=datetime(
                2026, 2, 3, 4, 5, 6, 789, tzinfo=timezone(timedelta(hours=2))
            ),
            owner="ops",
            version="1.2.3",
            metrics={"runs": 3, "ok": True},
            milestones={"m1": {"recorded_at": "2026-02-03T00:00:00+00:00"}},
        )

    def test_round_trip_restores_types(self):
        project = self.make_project()
        restored = Project.from_dict(json.loads(json.dumps(project.to_dict())))

        assert restored == project
        assert isinstance(restored.path, Path)
        assert restored.type is ProjectType.DATA_PIPELINE
        assert restored.status is ProjectStatus.PAUSED
        assert restored.updated_at.utcoffset() == timedelta(hours=2)

    def test_optional_fields_default(self):
        restored = Project.from_dict(
            {
                "name": "minimal",
                "path": "p",
                "type": "custom",
                "status": "active",
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:00+00:00",
            }
        )
        assert restored.description == ""
        assert restored.config == {}
        assert restored.owner is None
        assert restored.version == "0.1.0"
        assert restored.metrics == {}
        assert restored.milestones == {}

    @pytest.mark.parametrize(
        ("change", "match"),
        [
            ({"name": None}, "'name' must be str"),
            ({"name": ""}, "'name' must not be empty"),
            ({"type": "spaceship"}, "is not a valid ProjectType"),
            ({"status": "dreaming"}, "is not a valid ProjectStatus"),
            ({"created_at": "yesterday"}, "Invalid isoformat"),
            ({"updated_at": "2026-01-01T00:00:00"}, "must include a UTC offset"),
            ({"metrics": []}, "'metrics' must be dict"),
            ({"owner": 7}, "'owner' must be str or null"),
            ({"path": 1}, "'path' must be str"),
        ],
    )
    def test_invalid_values_raise(self, change, match):
        data = {**self.make_project().to_dict(), **change}
        with pytest.raises(ValueError, match=match):
            Project.from_dict(data)

    @pytest.mark.parametrize(
        "missing", ["name", "path", "type", "status", "created_at", "updated_at"]
    )
    def test_missing_required_field_raises(self, missing):
        data = self.make_project().to_dict()
        del data[missing]
        with pytest.raises(ValueError, match=f"'{missing}' is missing"):
            Project.from_dict(data)

    def test_non_mapping_raises(self):
        with pytest.raises(ValueError, match="must be a JSON object"):
            Project.from_dict(["not", "a", "mapping"])


class TestSaveAndLoad:
    def test_create_writes_project_json(self, manager, root):
        project = manager.create_project("alpha", ProjectType.RESEARCH, "notes")

        assert project is not None
        assert project.metadata_file == root / "alpha" / PROJECT_FILE_NAME
        assert read_file(project) == project.to_dict()

    def test_new_manager_lists_created_projects(self, manager, root):
        alpha = manager.create_project("alpha", ProjectType.RESEARCH, "notes")
        beta = manager.create_project("beta", ProjectType.ML_MODEL)

        reloaded = ProjectManager(projects_root=root)

        assert sorted(p.name for p in reloaded.list_projects()) == ["alpha", "beta"]
        assert reloaded.get_project("alpha") == alpha
        assert reloaded.get_project("beta") == beta

    def test_updates_are_persisted(self, manager, root):
        manager.create_project("alpha", ProjectType.RESEARCH)

        assert manager.update_project_status("alpha", ProjectStatus.COMPLETED)
        assert manager.update_project_metrics("alpha", {"runs": 2})
        assert manager.add_project_milestone("alpha", "v1", {"tag": "v1.0"})

        reloaded = ProjectManager(projects_root=root).get_project("alpha")
        assert reloaded == manager.get_project("alpha")
        assert reloaded.status is ProjectStatus.COMPLETED
        assert reloaded.metrics == {"runs": 2}
        assert reloaded.milestones["v1"]["tag"] == "v1.0"
        assert reloaded.updated_at == datetime.fromisoformat(
            reloaded.milestones["v1"]["recorded_at"]
        )

    def test_updates_on_unknown_project_return_false(self, manager, root):
        assert not manager.update_project_status("ghost", ProjectStatus.ACTIVE)
        assert not manager.update_project_metrics("ghost", {"a": 1})
        assert not manager.add_project_milestone("ghost", "m")
        assert list(root.iterdir()) == []

    def test_unserialisable_update_leaves_project_unchanged(self, manager):
        project = manager.create_project("alpha", ProjectType.RESEARCH)
        manager.update_project_metrics("alpha", {"runs": 1})
        before_file = project.metadata_file.read_text(encoding="utf-8")
        before = project.to_dict()

        with pytest.raises(TypeError, match="not JSON serializable"):
            manager.update_project_metrics("alpha", {"when": datetime.now(UTC)})
        with pytest.raises(ValueError, match="not JSON compliant"):
            manager.add_project_milestone("alpha", "m", {"score": float("inf")})

        assert project.to_dict() == before
        assert project.metadata_file.read_text(encoding="utf-8") == before_file
        assert sorted(p.name for p in project.path.iterdir() if p.is_file()) == [
            "AGENTS.md",
            "README.md",
            PROJECT_FILE_NAME,
        ]

    def test_write_failure_raises_and_leaves_project_unchanged(self, manager):
        project = manager.create_project("alpha", ProjectType.RESEARCH)
        before = json.loads(json.dumps(project.to_dict()))
        shutil.rmtree(project.path)

        with pytest.raises(OSError):
            manager.update_project_status("alpha", ProjectStatus.ARCHIVED)

        assert project.to_dict() == before
        assert not project.path.exists()

    def test_save_project_after_direct_change(self, manager, root):
        project = manager.create_project("alpha", ProjectType.RESEARCH)
        project.config["setting"] = "on"

        assert manager.save_project("alpha") == project.metadata_file
        assert ProjectManager(projects_root=root).get_project("alpha").config == {
            "setting": "on"
        }

    def test_save_unknown_project_raises(self, manager):
        with pytest.raises(KeyError, match="not registered"):
            manager.save_project("ghost")

    def test_registered_project_cannot_be_recreated(self, manager, root):
        manager.create_project("alpha", ProjectType.RESEARCH)
        reloaded = ProjectManager(projects_root=root)
        assert reloaded.create_project("alpha", ProjectType.CUSTOM) is None
        assert reloaded.get_project("alpha").type is ProjectType.RESEARCH

    def test_custom_path_outside_root(self, manager, root, tmp_path):
        outside = tmp_path / "elsewhere" / "gamma"
        project = manager.create_project("gamma", ProjectType.CUSTOM, path=outside)

        assert project is not None
        assert (outside / PROJECT_FILE_NAME).is_file()
        assert ProjectManager(projects_root=root).get_project("gamma") is None
        assert (
            ProjectManager(projects_root=outside.parent).get_project("gamma") == project
        )

    def test_missing_root_loads_nothing(self, tmp_path):
        manager = ProjectManager(projects_root=tmp_path / "does-not-exist")
        assert manager.list_projects() == []
        assert not (tmp_path / "does-not-exist").exists()

    def test_moved_project_uses_its_directory(self, manager, root, caplog):
        manager.create_project("alpha", ProjectType.RESEARCH)
        (root / "alpha").rename(root / "renamed")

        with caplog.at_level(logging.WARNING):
            project = ProjectManager(projects_root=root).get_project("alpha")

        assert project.path == root / "renamed"
        assert any("records path" in r.getMessage() for r in caplog.records)


class TestInvalidFilesAreSkipped:
    @pytest.mark.parametrize(
        ("content", "reason"),
        [
            ("{broken", "Expecting property name"),
            ("[1, 2]", "must be a JSON object"),
            ('{"name": "x"}', "'path' is missing"),
            (b"\xff\xfe\x00", "codec can't decode"),
        ],
    )
    def test_logged_and_skipped(self, manager, root, caplog, content, reason):
        manager.create_project("good", ProjectType.CUSTOM)
        bad = root / "bad"
        bad.mkdir()
        if isinstance(content, bytes):
            (bad / PROJECT_FILE_NAME).write_bytes(content)
        else:
            (bad / PROJECT_FILE_NAME).write_text(content, encoding="utf-8")

        with caplog.at_level(logging.WARNING):
            reloaded = ProjectManager(projects_root=root)

        assert [p.name for p in reloaded.list_projects()] == ["good"]
        messages = [
            r.getMessage()
            for r in caplog.records
            if "Skipping project" in r.getMessage()
        ]
        assert len(messages) == 1
        assert str(bad / PROJECT_FILE_NAME) in messages[0]
        assert reason in messages[0]

    def test_duplicate_name_is_skipped(self, manager, root, caplog):
        project = manager.create_project("alpha", ProjectType.RESEARCH)
        copy_dir = root / "zz-copy"
        copy_dir.mkdir()
        data = project.to_dict()
        data["path"] = str(copy_dir)
        (copy_dir / PROJECT_FILE_NAME).write_text(json.dumps(data), encoding="utf-8")

        with caplog.at_level(logging.WARNING):
            reloaded = ProjectManager(projects_root=root)

        assert reloaded.get_project("alpha").path == root / "alpha"
        assert any("already loaded" in r.getMessage() for r in caplog.records)
