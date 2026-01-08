from pathlib import Path
from typing import Any, Dict, Optional
import logging

import yaml

from codomyrmex.logging_monitoring.logger_config import get_logger




























"""Skill Loader Module

Handles loading and parsing YAML skill files with merge logic.
"""


try:
except ImportError:
    yaml = None  # type: ignore

try:
except ImportError:

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

logger = get_logger(__name__)


class SkillLoader:
    """Loads and parses YAML skill files with merge logic."""

    def __init__(self, upstream_dir: Path, custom_dir: Path, cache_dir: Optional[Path] = None):
        """
        Initialize SkillLoader.

        Args:
            upstream_dir: Directory containing upstream skills
            custom_dir: Directory containing custom skills
            cache_dir: Directory for caching merged skills (optional)
        """
        self.upstream_dir = Path(upstream_dir)
        self.custom_dir = Path(custom_dir)
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self._cache: Dict[str, Dict[str, Any]] = {}

        # Ensure directories exist
        self.custom_dir.mkdir(parents=True, exist_ok=True)
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"SkillLoader initialized: upstream={upstream_dir}, custom={custom_dir}, cache={cache_dir}"
        )

    def load_skill_file(self, path: Path) -> Optional[Dict[str, Any]]:
        """
        Load a skill file from disk.

        Args:
            path: Path to the skill YAML file

        Returns:
            Parsed skill data or None if file doesn't exist or is invalid
        """
        if not path.exists():
            logger.debug(f"Skill file does not exist: {path}")
            return None

        if yaml is None:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    logger.warning(f"Skill file does not contain a dictionary: {path}")
                    return None
                return data
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading skill file {path}: {e}")
            return None

    def get_skill_paths(self, category: str, name: str) -> tuple[Optional[Path], Optional[Path]]:
        """
        Get paths for upstream and custom skill files.

        Args:
            category: Skill category
            name: Skill name

        Returns:
            Tuple of (upstream_path, custom_path)
        """
        # Try skill.yaml first, then just the directory name
        upstream_path = self.upstream_dir / category / name / "skill.yaml"
        if not upstream_path.exists():
            upstream_path = self.upstream_dir / category / f"{name}.yaml"
        if not upstream_path.exists():
            upstream_path = None

        custom_path = self.custom_dir / category / name / "skill.yaml"
        if not custom_path.exists():
            custom_path = self.custom_dir / category / f"{name}.yaml"
        if not custom_path.exists():
            custom_path = None

        return upstream_path, custom_path

    def get_merged_skill(self, category: str, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a skill with custom overrides applied.

        Args:
            category: Skill category
            name: Skill name

        Returns:
            Merged skill data or None if skill doesn't exist
        """
        cache_key = f"{category}/{name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        upstream_path, custom_path = self.get_skill_paths(category, name)

        upstream_skill = None
        if upstream_path:
            upstream_skill = self.load_skill_file(upstream_path)

        custom_skill = None
        if custom_path:
            custom_skill = self.load_skill_file(custom_path)

        # If custom exists, it overrides upstream completely
        if custom_skill:
            merged = custom_skill.copy()
            # Optionally merge nested structures if needed
            if upstream_skill:
                merged.setdefault("_source", "custom")
                merged.setdefault("_upstream_available", True)
            else:
                merged.setdefault("_source", "custom")
            logger.debug(f"Loaded custom skill: {category}/{name}")
        elif upstream_skill:
            merged = upstream_skill.copy()
            merged.setdefault("_source", "upstream")
            logger.debug(f"Loaded upstream skill: {category}/{name}")
        else:
            logger.debug(f"Skill not found: {category}/{name}")
            return None

        # Cache the result
        self._cache[cache_key] = merged

        # Optionally save to cache directory
        if self.cache_dir and yaml is not None:
            cache_file = self.cache_dir / f"{category}_{name}.yaml"
            try:
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                with open(cache_file, "w", encoding="utf-8") as f:
                    yaml.dump(merged, f, default_flow_style=False)
            except Exception as e:
                logger.warning(f"Failed to cache skill: {e}")

        return merged

    def load_all_skills(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Load all available skills from both upstream and custom directories.

        Returns:
            Dictionary mapping category -> name -> skill_data
        """
        all_skills: Dict[str, Dict[str, Dict[str, Any]]] = {}

        # Load from upstream
        if self.upstream_dir.exists():
            for category_dir in self.upstream_dir.iterdir():
                if not category_dir.is_dir():
                    continue
                category = category_dir.name
                if category not in all_skills:
                    all_skills[category] = {}

                # Look for skill.yaml files or .yaml files
                for skill_item in category_dir.iterdir():
                    if skill_item.is_dir():
                        skill_file = skill_item / "skill.yaml"
                        if skill_file.exists():
                            skill_name = skill_item.name
                            skill_data = self.load_skill_file(skill_file)
                            if skill_data:
                                all_skills[category][skill_name] = skill_data
                    elif skill_item.suffix == ".yaml":
                        skill_name = skill_item.stem
                        skill_data = self.load_skill_file(skill_item)
                        if skill_data:
                            all_skills[category][skill_name] = skill_data

        # Load from custom (will override upstream)
        if self.custom_dir.exists():
            for category_dir in self.custom_dir.iterdir():
                if not category_dir.is_dir():
                    continue
                category = category_dir.name
                if category not in all_skills:
                    all_skills[category] = {}

                for skill_item in category_dir.iterdir():
                    if skill_item.is_dir():
                        skill_file = skill_item / "skill.yaml"
                        if skill_file.exists():
                            skill_name = skill_item.name
                            skill_data = self.load_skill_file(skill_file)
                            if skill_data:
                                all_skills[category][skill_name] = skill_data
                    elif skill_item.suffix == ".yaml":
                        skill_name = skill_item.stem
                        skill_data = self.load_skill_file(skill_item)
                        if skill_data:
                            all_skills[category][skill_name] = skill_data

        return all_skills

    def merge_skills(self, upstream: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge upstream and custom skills (custom overrides upstream).

        Args:
            upstream: Upstream skill data
            custom: Custom skill data

        Returns:
            Merged skill data
        """
        merged = upstream.copy()
        merged.update(custom)
        merged["_source"] = "merged"
        merged["_upstream_available"] = True
        merged["_custom_available"] = True
        return merged

    def clear_cache(self) -> None:
        """Clear the skill cache."""
        self._cache.clear()
        logger.debug("Skill cache cleared")

