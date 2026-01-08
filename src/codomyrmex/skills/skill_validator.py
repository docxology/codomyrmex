from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

import yaml

from codomyrmex.logging_monitoring.logger_config import get_logger











































"""Skill Validator Module

Validates YAML skill files against schema.
"""

try:
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    yaml = None

try:
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SkillValidator:
    """Validates skill YAML files against expected schema."""

    def __init__(self):
        """Initialize SkillValidator."""
        self.required_fields = []  # Skills are flexible, no strict requirements
        self.optional_fields = [
            "patterns",
            "anti_patterns",
            "validations",
            "sharp_edges",
            "collaboration",
            "description",
            "handoffs",
        ]
        logger.info("SkillValidator initialized")

    def validate_skill(self, skill_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate a skill data dictionary.

        Args:
            skill_data: Skill data dictionary

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not isinstance(skill_data, dict):
            errors.append("Skill data must be a dictionary")
            return False, errors

        # Check for at least some content
        if not skill_data:
            errors.append("Skill data is empty")
            return False, errors

        # Validate patterns if present
        if "patterns" in skill_data:
            if not isinstance(skill_data["patterns"], list):
                errors.append("'patterns' must be a list")
            else:
                for i, pattern in enumerate(skill_data["patterns"]):
                    if not isinstance(pattern, dict):
                        errors.append(f"Pattern {i} must be a dictionary")

        # Validate anti_patterns if present
        if "anti_patterns" in skill_data:
            if not isinstance(skill_data["anti_patterns"], list):
                errors.append("'anti_patterns' must be a list")
            else:
                for i, anti_pattern in enumerate(skill_data["anti_patterns"]):
                    if not isinstance(anti_pattern, dict):
                        errors.append(f"Anti-pattern {i} must be a dictionary")

        # Validate validations if present
        if "validations" in skill_data:
            if not isinstance(skill_data["validations"], list):
                errors.append("'validations' must be a list")

        # Validate sharp_edges if present
        if "sharp_edges" in skill_data:
            if not isinstance(skill_data["sharp_edges"], list):
                errors.append("'sharp_edges' must be a list")

        is_valid = len(errors) == 0
        return is_valid, errors

    def validate_file(self, file_path: Path) -> tuple[bool, List[str]]:
        """
        Validate a skill file.

        Args:
            file_path: Path to skill YAML file

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not file_path.exists():
            return False, [f"File does not exist: {file_path}"]

        if not HAS_YAML:
            return False, ["PyYAML not installed. Install with: pip install pyyaml"]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                skill_data = yaml.safe_load(f)

            return self.validate_skill(skill_data)

        except Exception as e:
            return False, [f"Error reading file: {e}"]

    def validate_directory(self, directory: Path) -> Dict[str, tuple[bool, List[str]]]:
        """
        Validate all skill files in a directory.

        Args:
            directory: Directory containing skill files

        Returns:
            Dictionary mapping file_path -> (is_valid, errors)
        """
        results = {}

        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return results

        for category_dir in directory.iterdir():
            if not category_dir.is_dir():
                continue

            for skill_item in category_dir.iterdir():
                if skill_item.is_dir():
                    skill_file = skill_item / "skill.yaml"
                    if skill_file.exists():
                        results[str(skill_file)] = self.validate_file(skill_file)
                elif skill_item.suffix == ".yaml":
                    results[str(skill_item)] = self.validate_file(skill_item)

        return results

