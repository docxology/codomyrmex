"""Fetcher for FPF specification from GitHub.

This module provides functionality to fetch the latest FPF specification
from GitHub and manage local caching.
"""

import hashlib
from pathlib import Path
from typing import Dict, Optional

import requests

from .models import FPFSpec


class FPFFetcher:
    """Fetcher for FPF specification from GitHub."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the fetcher.

        Args:
            cache_dir: Optional directory for caching fetched files
        """
        self.cache_dir = cache_dir or Path.home() / ".codomyrmex" / "fpf_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_latest(
        self, repo: str = "ailev/FPF", branch: str = "main", file_path: str = "FPF-Spec.md"
    ) -> str:
        """Fetch the latest FPF specification from GitHub.

        Args:
            repo: GitHub repository in format "owner/repo"
            branch: Branch name (default: "main")
            file_path: Path to the file in the repository

        Returns:
            Content of the FPF specification file

        Raises:
            requests.RequestException: If the fetch fails
        """
        # Construct raw GitHub URL
        url = f"https://raw.githubusercontent.com/{repo}/{branch}/{file_path}"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to fetch FPF specification from {url}: {e}"
            ) from e

    def check_for_updates(self, local_path: Path) -> bool:
        """Check if there are updates available on GitHub.

        Args:
            local_path: Path to local FPF-Spec.md file

        Returns:
            True if updates are available, False otherwise
        """
        if not local_path.exists():
            return True

        try:
            # Get local file hash
            local_content = local_path.read_text(encoding="utf-8")
            local_hash = hashlib.sha256(local_content.encode()).hexdigest()

            # Get remote file hash
            remote_content = self.fetch_latest()
            remote_hash = hashlib.sha256(remote_content.encode()).hexdigest()

            return local_hash != remote_hash
        except Exception:
            # If check fails, assume updates are available
            return True

    def get_version_info(self, repo: str = "ailev/FPF") -> Dict[str, any]:
        """Get version information from GitHub.

        Args:
            repo: GitHub repository in format "owner/repo"

        Returns:
            Dictionary with version information
        """
        try:
            # Try to get commit info from GitHub API
            api_url = f"https://api.github.com/repos/{repo}/commits/main"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            commit_data = response.json()

            return {
                "sha": commit_data.get("sha", ""),
                "date": commit_data.get("commit", {}).get("author", {}).get("date", ""),
                "message": commit_data.get("commit", {}).get("message", ""),
            }
        except Exception:
            return {
                "sha": "unknown",
                "date": "unknown",
                "message": "unknown",
            }

    def cache_spec(self, content: str, version: Optional[str] = None) -> Path:
        """Cache the specification content locally.

        Args:
            content: The specification content
            version: Optional version identifier

        Returns:
            Path to the cached file
        """
        # Generate filename
        if version:
            filename = f"FPF-Spec-{version}.md"
        else:
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
            filename = f"FPF-Spec-{content_hash}.md"

        cache_path = self.cache_dir / filename
        cache_path.write_text(content, encoding="utf-8")

        return cache_path


