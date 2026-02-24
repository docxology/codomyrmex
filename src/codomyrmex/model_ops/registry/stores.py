"""
Model Storage Backends

Storage backends for model artifacts.
"""

import threading
from abc import ABC, abstractmethod
from pathlib import Path


class ModelStore(ABC):
    """Base class for model storage backends."""

    @abstractmethod
    def save_artifact(self, model_name: str, version: str, artifact: bytes) -> str:
        """Save model artifact and return path."""
        pass

    @abstractmethod
    def load_artifact(self, path: str) -> bytes:
        """Load model artifact from path."""
        pass

    @abstractmethod
    def delete_artifact(self, path: str) -> bool:
        """Delete model artifact."""
        pass


class FileModelStore(ModelStore):
    """File-based model storage."""

    def __init__(self, base_path: str = "./models"):
        """Execute   Init   operations natively."""
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_path(self, model_name: str, version: str) -> Path:
        """Get path for a model version."""
        return self.base_path / model_name / version / "model.bin"

    def save_artifact(self, model_name: str, version: str, artifact: bytes) -> str:
        """Save model artifact."""
        path = self._get_path(model_name, version)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(artifact)
        return str(path)

    def load_artifact(self, path: str) -> bytes:
        """Load model artifact."""
        return Path(path).read_bytes()

    def delete_artifact(self, path: str) -> bool:
        """Delete model artifact."""
        try:
            Path(path).unlink()
            return True
        except FileNotFoundError:
            return False


class InMemoryModelStore(ModelStore):
    """In-memory model storage for testing."""

    def __init__(self):
        """Execute   Init   operations natively."""
        self._artifacts: dict[str, bytes] = {}
        self._lock = threading.Lock()

    def save_artifact(self, model_name: str, version: str, artifact: bytes) -> str:
        """Save model artifact."""
        path = f"{model_name}/{version}/model.bin"
        with self._lock:
            self._artifacts[path] = artifact
        return path

    def load_artifact(self, path: str) -> bytes:
        """Load model artifact."""
        artifact = self._artifacts.get(path)
        if artifact is None:
            raise FileNotFoundError(f"Artifact not found: {path}")
        return artifact

    def delete_artifact(self, path: str) -> bool:
        """Delete model artifact."""
        with self._lock:
            if path in self._artifacts:
                del self._artifacts[path]
                return True
        return False
