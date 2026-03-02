"""Artifact manager for CI/CD pipelines."""

import shutil
from pathlib import Path

class ArtifactManager:
    """
    Manager for build artifacts in CI/CD pipelines.
    """

    def __init__(self, storage_dir: str | None = None):
        self.storage_dir = Path(storage_dir) if storage_dir else Path(".artifacts")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, pattern: str, version: str):
        """
        'Upload' artifacts matching a pattern to the storage directory.
        Actually just copies them to the storage directory in this implementation.
        """
        import glob
        files = glob.glob(pattern)
        version_dir = self.storage_dir / version
        version_dir.mkdir(parents=True, exist_ok=True)
        
        for f in files:
            shutil.copy2(f, version_dir)
            
    def download(self, name: str, version: str, target_dir: str):
        """Download an artifact from storage."""
        source = self.storage_dir / version / name
        if not source.exists():
            raise FileNotFoundError(f"Artifact {name} v{version} not found")
            
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target_dir)
