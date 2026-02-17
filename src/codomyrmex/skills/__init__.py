"""Skills Module for Codomyrmex

This module provides integration with the vibeship-spawner-skills repository,
enabling skill management, syncing with upstream, and support for custom skills.
"""

from pathlib import Path
from typing import Optional

# Shared schemas for cross-module interop
try:
    from codomyrmex.validation.schemas import Result, ResultStatus
except ImportError:
    Result = None
    ResultStatus = None

# New submodule exports
from . import (
    composition,
    discovery,
    execution,
    marketplace,
    permissions,
    testing,
    versioning,
)
from .skill_loader import SkillLoader
from .skill_registry import SkillRegistry
from .skill_sync import SkillSync
from .skills_manager import SkillsManager


def cli_commands():
    """Return CLI commands for the skills module."""
    def _list_skills():
        """List available skills."""
        try:
            registry = SkillRegistry()
            skills = registry.list_skills()
            for skill in skills:
                print(f"  {skill}")
        except Exception:
            print("Skills: use SkillRegistry to discover available skills")

    def _info_skill():
        """Show skill info."""
        try:
            registry = SkillRegistry()
            print(f"Skills registry: {registry}")
            print(f"Upstream: {DEFAULT_UPSTREAM_REPO}")
            print(f"Branch: {DEFAULT_UPSTREAM_BRANCH}")
        except Exception:
            print(f"Skills upstream: {DEFAULT_UPSTREAM_REPO} ({DEFAULT_UPSTREAM_BRANCH})")

    return {
        "list": _list_skills,
        "info": _info_skill,
    }


__all__ = [
    'permissions',
    'versioning',
    'marketplace',
    "SkillsManager",
    "SkillLoader",
    "SkillSync",
    "SkillRegistry",
    # Submodules
    "discovery",
    "execution",
    "composition",
    "testing",
    "cli_commands",
]

# Default configuration
DEFAULT_UPSTREAM_REPO = "https://github.com/vibeforge1111/vibeship-spawner-skills"
DEFAULT_UPSTREAM_BRANCH = "main"
DEFAULT_SKILLS_DIR = Path(__file__).parent / "skills"


def get_skills_manager(
    skills_dir: Path | None = None,
    upstream_repo: str | None = None,
    upstream_branch: str | None = None,
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
