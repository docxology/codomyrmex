"""Skills Module for Codomyrmex

This module provides integration with the vibeship-spawner-skills repository,
enabling skill management, syncing with upstream, and support for custom skills.
"""

from pathlib import Path
from typing import Optional

from .skills_manager import SkillsManager
from .skill_loader import SkillLoader
from .skill_sync import SkillSync
from .skill_registry import SkillRegistry

__all__ = [
    "SkillsManager",
    "SkillLoader",
    "SkillSync",
    "SkillRegistry",
]

# Default configuration
DEFAULT_UPSTREAM_REPO = "https://github.com/vibeforge1111/vibeship-spawner-skills"
DEFAULT_UPSTREAM_BRANCH = "main"
DEFAULT_SKILLS_DIR = Path(__file__).parent / "skills"


def get_skills_manager(
    skills_dir: Optional[Path] = None,
    upstream_repo: Optional[str] = None,
    upstream_branch: Optional[str] = None,
    auto_sync: bool = False,
) -> SkillsManager:
    """
    Get a configured SkillsManager instance.

    Args:
        skills_dir: Directory for skills storage (default: module skills/ dir)
        upstream_repo: Upstream repository URL
        upstream_branch: Upstream branch to track
        auto_sync: Whether to auto-sync on initialization

    Returns:
        Configured SkillsManager instance
    """
    if skills_dir is None:
        skills_dir = DEFAULT_SKILLS_DIR
    if upstream_repo is None:
        upstream_repo = DEFAULT_UPSTREAM_REPO
    if upstream_branch is None:
        upstream_branch = DEFAULT_UPSTREAM_BRANCH

    return SkillsManager(
        skills_dir=skills_dir,
        upstream_repo=upstream_repo,
        upstream_branch=upstream_branch,
        auto_sync=auto_sync,
    )

