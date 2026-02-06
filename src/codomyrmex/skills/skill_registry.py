"""Skill Registry Module

Handles indexing, categorizing, and searching skills.
"""

import logging
import re
from typing import Any

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SkillRegistry:
    """Indexes and categorizes skills for search and discovery."""

    def __init__(self, skill_loader: "SkillLoader"):
        """
        Initialize SkillRegistry.

        Args:
            skill_loader: SkillLoader instance to use for loading skills
        """
        self.skill_loader = skill_loader
        self._index: dict[str, dict[str, dict[str, Any]]] = {}
        self._metadata: dict[str, dict[str, dict[str, Any]]] = {}
        logger.info("SkillRegistry initialized")

    def build_index(self) -> dict[str, dict[str, dict[str, Any]]]:
        """
        Build the skill index from all available skills.

        Returns:
            Index dictionary mapping category -> name -> skill_data
        """
        logger.info("Building skill index...")
        self._index = self.skill_loader.load_all_skills()

        # Build metadata for each skill
        self._metadata = {}
        for category, skills in self._index.items():
            self._metadata[category] = {}
            for name, skill_data in skills.items():
                self._metadata[category][name] = self._extract_metadata(category, name, skill_data)

        logger.info(f"Index built: {len(self._index)} categories, {sum(len(s) for s in self._index.values())} skills")
        return self._index

    def _extract_metadata(
        self, category: str, name: str, skill_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Extract metadata from a skill.

        Args:
            category: Skill category
            name: Skill name
            skill_data: Skill data dictionary

        Returns:
            Metadata dictionary
        """
        metadata = {
            "category": category,
            "name": name,
            "source": skill_data.get("_source", "unknown"),
            "has_patterns": "patterns" in skill_data,
            "has_anti_patterns": "anti_patterns" in skill_data,
            "has_validations": "validations" in skill_data,
            "has_sharp_edges": "sharp_edges" in skill_data,
        }

        # Extract text content for search
        search_text = []
        if "description" in skill_data:
            search_text.append(str(skill_data["description"]))
        if "patterns" in skill_data:
            for pattern in skill_data["patterns"]:
                if isinstance(pattern, dict):
                    search_text.append(str(pattern.get("name", "")))
                    search_text.append(str(pattern.get("description", "")))
        if "anti_patterns" in skill_data:
            for anti_pattern in skill_data["anti_patterns"]:
                if isinstance(anti_pattern, dict):
                    search_text.append(str(anti_pattern.get("name", "")))
                    search_text.append(str(anti_pattern.get("why_bad", "")))

        metadata["search_text"] = " ".join(search_text).lower()
        return metadata

    def get_categories(self) -> list[str]:
        """
        Get all available skill categories.

        Returns:
            List of category names
        """
        if not self._index:
            self.build_index()
        return sorted(self._index.keys())

    def get_skill_metadata(self, category: str, name: str) -> dict[str, Any] | None:
        """
        Get metadata for a specific skill.

        Args:
            category: Skill category
            name: Skill name

        Returns:
            Metadata dictionary or None if skill not found
        """
        if not self._metadata:
            self.build_index()

        return self._metadata.get(category, {}).get(name)

    def search_by_pattern(self, pattern: str, case_sensitive: bool = False) -> list[dict[str, Any]]:
        """
        Search skills by pattern (regex or text).

        Args:
            pattern: Search pattern (regex supported)
            case_sensitive: Whether search is case sensitive

        Returns:
            List of matching skill metadata
        """
        if not self._metadata:
            self.build_index()

        results = []
        flags = 0 if case_sensitive else re.IGNORECASE

        try:
            regex = re.compile(pattern, flags)
        except re.error:
            # If pattern is not valid regex, treat as literal text
            regex = re.compile(re.escape(pattern), flags)

        for category, skills in self._metadata.items():
            for name, metadata in skills.items():
                # Search in category, name, and search_text
                searchable = f"{category} {name} {metadata.get('search_text', '')}"
                if regex.search(searchable):
                    results.append(
                        {
                            "category": category,
                            "name": name,
                            "metadata": metadata,
                        }
                    )

        return results

    def search_skills(self, query: str) -> list[dict[str, Any]]:
        """
        Search skills by query string.

        Args:
            query: Search query

        Returns:
            List of matching skills with full data
        """
        matches = self.search_by_pattern(query, case_sensitive=False)
        results = []

        for match in matches:
            category = match["category"]
            name = match["name"]
            skill_data = self.skill_loader.get_merged_skill(category, name)
            if skill_data:
                results.append(
                    {
                        "category": category,
                        "name": name,
                        "data": skill_data,
                        "metadata": match["metadata"],
                    }
                )

        return results

    def get_index(self) -> dict[str, dict[str, dict[str, Any]]]:
        """
        Get the current skill index.

        Returns:
            Index dictionary
        """
        if not self._index:
            self.build_index()
        return self._index

    def refresh_index(self) -> None:
        """Refresh the skill index by rebuilding it."""
        logger.info("Refreshing skill index...")
        self.skill_loader.clear_cache()
        self.build_index()
