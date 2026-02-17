"""Tests for SkillsManager — Zero-Mock implementation.

Uses real git operations and temporary directories. Tests that depend
on network connectivity or git are skipped when unavailable.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

from codomyrmex.skills.skills_manager import SkillsManager

_GIT_AVAILABLE = shutil.which("git") is not None


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


def _init_repo_with_skills(path: Path, skills: dict[str, dict]) -> None:
    """Create a git repo at *path* containing skill YAML files.

    Args:
        path: Root of the repo.
        skills: Mapping of ``category/skill_name`` → skill data dict.
    """
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(path), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(path), capture_output=True, check=True,
    )
    for rel, data in skills.items():
        skill_dir = path / rel
        skill_dir.mkdir(parents=True, exist_ok=True)
        with open(skill_dir / "skill.yaml", "w", encoding="utf-8") as f:
            yaml.dump(data, f)
    subprocess.run(["git", "add", "."], cwd=str(path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(path), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "branch", "-M", "main"],
        cwd=str(path), capture_output=True, check=True,
    )


# ---- Tests ----


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not installed")
def test_initialize_clone(temp_dir):
    """Test initialization clones a real repo."""
    origin = temp_dir / "origin"
    _init_repo_with_skills(origin, {
        "cat1/skill1": {"description": "s1"}
    })

    skills_dir = temp_dir / "skills"
    manager = SkillsManager(
        skills_dir,
        str(origin),
        "main",
        auto_sync=False,
    )

    result = manager.initialize()
    assert result is True
    assert (skills_dir / "upstream").exists()


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not installed")
def test_initialize_auto_sync(temp_dir):
    """Test initialization with auto-sync pulls updates."""
    origin = temp_dir / "origin"
    _init_repo_with_skills(origin, {
        "cat1/skill1": {"description": "s1"}
    })

    skills_dir = temp_dir / "skills"
    manager = SkillsManager(skills_dir, str(origin), "main", auto_sync=True)

    # First init clones
    result = manager.initialize()
    assert result is True

    # Second init should pull (auto_sync=True)
    manager2 = SkillsManager(skills_dir, str(origin), "main", auto_sync=True)
    result2 = manager2.initialize()
    assert result2 is True


@pytest.mark.skipif(not _GIT_AVAILABLE, reason="git not installed")
def test_sync_upstream(temp_dir):
    """Test syncing upstream pulls from remote."""
    origin = temp_dir / "origin"
    _init_repo_with_skills(origin, {
        "cat1/skill1": {"description": "s1"}
    })

    skills_dir = temp_dir / "skills"
    manager = SkillsManager(skills_dir, str(origin), "main")
    manager.initialize()


    # Configure pull strategy and identity to allow merging
    for args in [
        ["git", "config", "pull.rebase", "false"],
        ["git", "config", "user.email", "test@example.com"],
        ["git", "config", "user.name", "Test User"],
    ]:
        subprocess.run(
            args, cwd=str(skills_dir / "upstream"), capture_output=True, check=True
        )

    result = manager.sync_upstream()
    assert result is True


@pytest.mark.unit
def test_get_skill(temp_dir):
    """Test getting a skill."""
    skills_dir = temp_dir / "skills"
    upstream_dir = skills_dir / "upstream" / "test-category" / "test-skill"
    upstream_dir.mkdir(parents=True)

    skill_data = {"description": "Test skill"}
    skill_file = upstream_dir / "skill.yaml"
    with open(skill_file, "w", encoding="utf-8") as f:
        yaml.dump(skill_data, f)

    manager = SkillsManager(skills_dir, "https://github.com/test/repo", "main")
    manager.initialize()

    skill = manager.get_skill("test-category", "test-skill")
    assert skill is not None
    assert skill["description"] == "Test skill"


@pytest.mark.unit
def test_list_skills(temp_dir):
    """Test listing skills."""
    skills_dir = temp_dir / "skills"
    upstream_dir = skills_dir / "upstream"

    # Create multiple skills
    for i in range(3):
        skill_dir = upstream_dir / "category1" / f"skill{i}"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "skill.yaml"
        with open(skill_file, "w", encoding="utf-8") as f:
            yaml.dump({"description": f"Skill {i}"}, f)

    manager = SkillsManager(skills_dir, "https://github.com/test/repo", "main")
    manager.initialize()

    skills = manager.list_skills()
    assert len(skills) == 3

    # Filter by category
    skills = manager.list_skills(category="category1")
    assert len(skills) == 3


@pytest.mark.unit
def test_search_skills(temp_dir):
    """Test searching skills."""
    skills_dir = temp_dir / "skills"
    upstream_dir = skills_dir / "upstream"

    skill_dir = upstream_dir / "category1" / "test-skill"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "skill.yaml"
    skill_data = {
        "description": "Authentication skill",
        "patterns": [{"name": "Auth Pattern"}],
    }
    with open(skill_file, "w", encoding="utf-8") as f:
        yaml.dump(skill_data, f)

    manager = SkillsManager(skills_dir, "https://github.com/test/repo", "main")
    manager.initialize()

    results = manager.search_skills("authentication")
    assert len(results) > 0


@pytest.mark.unit
def test_add_custom_skill(temp_dir):
    """Test adding a custom skill."""
    skills_dir = temp_dir / "skills"

    manager = SkillsManager(skills_dir, "https://github.com/test/repo", "main")
    manager.initialize()

    skill_data = {
        "description": "Custom skill",
        "patterns": [],
    }

    result = manager.add_custom_skill("my-category", "my-skill", skill_data)
    assert result is True

    # Verify skill was created
    custom_file = skills_dir / "custom" / "my-category" / "my-skill" / "skill.yaml"
    assert custom_file.exists()

    # Verify it can be retrieved
    skill = manager.get_skill("my-category", "my-skill")
    assert skill is not None
    assert skill["description"] == "Custom skill"


@pytest.mark.unit
def test_get_categories(temp_dir):
    """Test getting categories."""
    skills_dir = temp_dir / "skills"
    upstream_dir = skills_dir / "upstream"

    # Create skills in multiple categories
    for cat in ["category1", "category2"]:
        skill_dir = upstream_dir / cat / "skill1"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "skill.yaml"
        with open(skill_file, "w", encoding="utf-8") as f:
            yaml.dump({"description": "Test"}, f)

    manager = SkillsManager(skills_dir, "https://github.com/test/repo", "main")
    manager.initialize()

    categories = manager.get_categories()
    assert "category1" in categories
    assert "category2" in categories
