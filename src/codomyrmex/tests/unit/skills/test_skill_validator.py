"""Tests for SkillValidator."""

import tempfile
from pathlib import Path

import pytest
import yaml

from codomyrmex.skills.skill_validator import SkillValidator


@pytest.fixture
def validator():
    """Create a SkillValidator instance."""
    return SkillValidator()


@pytest.fixture
def valid_skill_data():
    """Valid skill data for testing."""
    return {
        "description": "A test skill",
        "patterns": [
            {"name": "Pattern 1", "description": "First pattern"},
            {"name": "Pattern 2", "description": "Second pattern"},
        ],
        "anti_patterns": [
            {"name": "Anti 1", "why_bad": "Because"},
        ],
    }


@pytest.mark.unit
def test_validate_valid_skill(validator, valid_skill_data):
    """Test that valid skill data passes validation."""
    is_valid, errors = validator.validate_skill(valid_skill_data)
    assert is_valid is True
    assert errors == []


@pytest.mark.unit
def test_validate_empty_skill(validator):
    """Test that empty dict fails validation."""
    is_valid, errors = validator.validate_skill({})
    assert is_valid is False
    assert "Skill data is empty" in errors


@pytest.mark.unit
def test_validate_non_dict(validator):
    """Test that non-dict fails validation."""
    is_valid, errors = validator.validate_skill("not a dict")
    assert is_valid is False
    assert "Skill data must be a dictionary" in errors


@pytest.mark.unit
def test_validate_invalid_patterns(validator):
    """Test that non-list patterns fails validation."""
    is_valid, errors = validator.validate_skill({"patterns": "not a list"})
    assert is_valid is False
    assert "'patterns' must be a list" in errors


@pytest.mark.unit
def test_validate_invalid_pattern_item(validator):
    """Test that non-dict pattern item fails validation."""
    is_valid, errors = validator.validate_skill({"patterns": ["not a dict"]})
    assert is_valid is False
    assert "Pattern 0 must be a dictionary" in errors


@pytest.mark.unit
def test_validate_invalid_anti_patterns(validator):
    """Test that non-list anti_patterns fails validation."""
    is_valid, errors = validator.validate_skill(
        {"description": "test", "anti_patterns": "not a list"}
    )
    assert is_valid is False
    assert "'anti_patterns' must be a list" in errors


@pytest.mark.unit
def test_validate_file_exists(validator, valid_skill_data):
    """Test that a valid YAML file passes validation."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w", delete=False) as f:
        yaml.dump(valid_skill_data, f)
        f.flush()
        path = Path(f.name)

    try:
        is_valid, errors = validator.validate_file(path)
        assert is_valid is True
        assert errors == []
    finally:
        path.unlink()


@pytest.mark.unit
def test_validate_file_not_exists(validator):
    """Test that a missing file fails validation."""
    is_valid, errors = validator.validate_file(Path("/nonexistent/file.yaml"))
    assert is_valid is False
    assert any("does not exist" in e for e in errors)


@pytest.mark.unit
def test_validate_directory(validator, valid_skill_data):
    """Test directory validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a category/skill structure
        category_dir = Path(tmpdir) / "category1"
        skill_dir = category_dir / "skill1"
        skill_dir.mkdir(parents=True)
        skill_file = skill_dir / "skill.yaml"
        with open(skill_file, "w") as f:
            yaml.dump(valid_skill_data, f)

        # Also create a flat yaml file
        flat_file = category_dir / "skill2.yaml"
        with open(flat_file, "w") as f:
            yaml.dump(valid_skill_data, f)

        results = validator.validate_directory(Path(tmpdir))
        assert len(results) == 2
        for _path, (is_valid, _errors) in results.items():
            assert is_valid is True
