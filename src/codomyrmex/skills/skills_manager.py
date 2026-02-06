"""Skills Manager Module

Main interface for skill operations.
"""

import logging
from pathlib import Path
from typing import Any

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

from .skill_loader import SkillLoader
from .skill_registry import SkillRegistry
from .skill_sync import SkillSync


class SkillsManager:
    """Main interface for skill operations."""

    def __init__(
        self,
        skills_dir: Path,
        upstream_repo: str,
        upstream_branch: str = "main",
        auto_sync: bool = False,
        cache_enabled: bool = True,
    ):
        """
        Initialize SkillsManager.

        Args:
            skills_dir: Base directory for skills storage
            upstream_repo: URL of upstream repository
            upstream_branch: Branch to track
            auto_sync: Whether to auto-sync on initialization
            cache_enabled: Whether to enable skill caching
        """
        self.skills_dir = Path(skills_dir)
        self.upstream_dir = self.skills_dir / "upstream"
        self.custom_dir = self.skills_dir / "custom"
        self.cache_dir = self.skills_dir / ".cache" if cache_enabled else None

        self.upstream_repo = upstream_repo
        self.upstream_branch = upstream_branch
        self.auto_sync = auto_sync

        # Initialize components
        self.sync = SkillSync(self.upstream_dir, upstream_repo, upstream_branch)
        self.loader = SkillLoader(self.upstream_dir, self.custom_dir, self.cache_dir)
        self.registry = SkillRegistry(self.loader)

        logger.info(
            f"SkillsManager initialized: skills_dir={skills_dir}, "
            f"upstream_repo={upstream_repo}, auto_sync={auto_sync}"
        )

    def initialize(self) -> bool:
        """
        Initialize the skills system (setup directories, clone if needed).

        Returns:
            True if successful, False otherwise
        """
        logger.info("Initializing skills system...")

        # Ensure directories exist
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.custom_dir.mkdir(parents=True, exist_ok=True)
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Clone upstream if needed
        if not self.upstream_dir.exists():
            logger.info("Upstream directory does not exist, cloning...")
            if not self.sync.clone_upstream():
                logger.error("Failed to clone upstream repository")
                return False
        elif self.auto_sync:
            logger.info("Auto-sync enabled, pulling latest changes...")
            self.sync.pull_upstream()

        # Build index
        try:
            self.registry.build_index()
            logger.info("Skills system initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error building skill index: {e}")
            return False

    def sync_upstream(self, force: bool = False) -> bool:
        """
        Sync with upstream repository.

        Args:
            force: If True, force re-clone even if directory exists

        Returns:
            True if successful, False otherwise
        """
        logger.info("Syncing with upstream repository...")

        if not self.upstream_dir.exists() or force:
            success = self.sync.clone_upstream(force=force)
        else:
            success = self.sync.pull_upstream()

        if success:
            # Refresh index after sync
            self.registry.refresh_index()
            logger.info("Upstream sync completed successfully")
        else:
            logger.error("Upstream sync failed")

        return success

    def get_skill(self, category: str, name: str) -> dict[str, Any] | None:
        """
        Get a specific skill.

        Args:
            category: Skill category
            name: Skill name

        Returns:
            Skill data or None if not found
        """
        return self.loader.get_merged_skill(category, name)

    def list_skills(self, category: str | None = None) -> list[dict[str, Any]]:
        """
        List available skills.

        Args:
            category: Optional category filter

        Returns:
            List of skill information dictionaries
        """
        index = self.registry.get_index()

        if category:
            if category not in index:
                return []
            skills = index[category]
            return [
                {
                    "category": category,
                    "name": name,
                    "metadata": self.registry.get_skill_metadata(category, name),
                }
                for name in skills.keys()
            ]

        # Return all skills
        results = []
        for cat, skills in index.items():
            for name in skills.keys():
                results.append(
                    {
                        "category": cat,
                        "name": name,
                        "metadata": self.registry.get_skill_metadata(cat, name),
                    }
                )

        return results

    def search_skills(self, query: str) -> list[dict[str, Any]]:
        """
        Search skills by query.

        Args:
            query: Search query

        Returns:
            List of matching skills
        """
        return self.registry.search_skills(query)

    def add_custom_skill(
        self, category: str, name: str, skill_data: dict[str, Any]
    ) -> bool:
        """
        Add a custom skill (overrides upstream).

        Args:
            category: Skill category
            name: Skill name
            skill_data: Skill data dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            skill_dir = self.custom_dir / category / name
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "skill.yaml"

            try:
                import yaml
            except ImportError:
                logger.error("PyYAML not installed. Install with: pip install pyyaml")
                return False

            with open(skill_file, "w", encoding="utf-8") as f:
                yaml.dump(skill_data, f, default_flow_style=False, sort_keys=False)

            # Clear cache and refresh index
            self.loader.clear_cache()
            self.registry.refresh_index()

            logger.info(f"Custom skill added: {category}/{name}")
            return True

        except Exception as e:
            logger.error(f"Error adding custom skill: {e}")
            return False

    def get_merged_skill(self, category: str, name: str) -> dict[str, Any] | None:
        """
        Get skill with custom overrides applied.

        Args:
            category: Skill category
            name: Skill name

        Returns:
            Merged skill data or None if not found
        """
        return self.loader.get_merged_skill(category, name)

    def get_categories(self) -> list[str]:
        """
        Get all available skill categories.

        Returns:
            List of category names
        """
        return self.registry.get_categories()

    def get_upstream_status(self) -> dict[str, Any]:
        """
        Get status of upstream repository.

        Returns:
            Status dictionary
        """
        return self.sync.check_upstream_status()
