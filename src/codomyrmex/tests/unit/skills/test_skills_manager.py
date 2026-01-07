"""Tests for SkillsManager."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from codomyrmex.skills.skills_manager import SkillsManager


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@patch("codomyrmex.skills.skills_manager.SkillSync.clone_upstream")
def test_initialize_clone(mock_clone, temp_dir):
    """Test initialization with clone."""
    mock_clone.return_value = True

    manager = SkillsManager(
        temp_dir / "skills",
        "https://github.com/test/repo",
        "main",
        auto_sync=False,
    )

    result = manager.initialize()
    assert result is True
    mock_clone.assert_called_once()


@patch("codomyrmex.skills.skills_manager.SkillSync.pull_upstream")
@patch("codomyrmex.skills.skills_manager.SkillSync.check_upstream_status")
def test_initialize_auto_sync(mock_status, mock_pull, temp_dir):
    """Test initialization with auto-sync."""
    mock_status.return_value = {"exists": True}
    mock_pull.return_value = True

    skills_dir = temp_dir / "skills"
    upstream_dir = skills_dir / "upstream"
    upstream_dir.mkdir(parents=True)

    manager = SkillsManager(
        skills_dir,
        "https://github.com/test/repo",
        "main",
        auto_sync=True,
    )

    result = manager.initialize()
    assert result is True
    mock_pull.assert_called_once()


@patch("codomyrmex.skills.skills_manager.SkillSync.pull_upstream")
def test_sync_upstream(mock_pull, temp_dir):
    """Test syncing upstream."""
    mock_pull.return_value = True

    skills_dir = temp_dir / "skills"
    upstream_dir = skills_dir / "upstream"
    upstream_dir.mkdir(parents=True)

    manager = SkillsManager(skills_dir, "https://github.com/test/repo", "main")
    manager.registry.build_index = MagicMock()  # Mock build_index

    result = manager.sync_upstream()
    assert result is True
    mock_pull.assert_called_once()


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

