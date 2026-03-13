"""MLX Model Manager — download, list, inspect, and delete MLX models.

Manages the local model cache, leveraging ``huggingface_hub`` for
downloads and ``mlx-lm`` for conversion / quantization.  All operations
are filesystem-based; no server process is required.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .config import MLXConfig, get_mlx_config

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class MLXModelInfo:
    """Metadata for a locally-cached MLX model."""

    repo_id: str
    local_path: str
    size_bytes: int = 0
    quantization: str | None = None
    model_type: str | None = None
    vocab_size: int | None = None
    hidden_size: int | None = None
    num_layers: int | None = None
    max_position_embeddings: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _repo_to_dirname(repo_id: str) -> str:
    """Convert a HuggingFace repo id to a filesystem-safe directory name.

    ``mlx-community/Llama-3.2-3B-Instruct-4bit``
    → ``mlx-community--Llama-3.2-3B-Instruct-4bit``
    """
    return repo_id.replace("/", "--")


def _dirname_to_repo(dirname: str) -> str:
    """Inverse of :func:`_repo_to_dirname`."""
    return dirname.replace("--", "/", 1)


def _dir_size_bytes(path: Path) -> int:
    """Recursively compute the total size (bytes) of all files under *path*."""
    total = 0
    try:
        for child in path.rglob("*"):
            if child.is_file():
                total += child.stat().st_size
    except OSError as exc:
        logger.warning("Error computing directory size for %s: %s", path, exc)
    return total


def _read_config_json(model_dir: Path) -> dict[str, Any]:
    """Read and return ``config.json`` from a model directory, or ``{}``."""
    config_path = model_dir / "config.json"
    if not config_path.is_file():
        return {}
    try:
        with config_path.open() as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read %s: %s", config_path, exc)
        return {}


# ---------------------------------------------------------------------------
# MLXModelManager
# ---------------------------------------------------------------------------


class MLXModelManager:
    """Manages local MLX model lifecycle: download, list, inspect, delete.

    Args:
        config: Optional :class:`MLXConfig`.  Falls back to the global
            singleton when omitted.
    """

    def __init__(self, config: MLXConfig | None = None) -> None:
        self._config = config or get_mlx_config()
        self._cache_dir = Path(self._config.cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def cache_dir(self) -> Path:
        """Return the root cache directory."""
        return self._cache_dir

    # ------------------------------------------------------------------
    # Download
    # ------------------------------------------------------------------

    def download_model(self, repo_id: str | None = None) -> Path:
        """Download a model from the HuggingFace Hub into the local cache.

        Uses ``huggingface_hub.snapshot_download`` which is the same
        mechanism ``mlx-lm`` calls internally.

        Args:
            repo_id: HuggingFace model repository id.  Defaults to the
                configured model (``MLXConfig.model``).

        Returns:
            Path to the downloaded model directory.

        Raises:
            ImportError: If ``huggingface_hub`` is not installed.
            RuntimeError: On download failure.
        """
        repo_id = repo_id or self._config.model

        try:
            from huggingface_hub import snapshot_download
        except ImportError as exc:
            raise ImportError(
                "huggingface_hub is required for model downloads. "
                "Install it with: pip install huggingface-hub"
            ) from exc

        dest = self._cache_dir / _repo_to_dirname(repo_id)
        logger.info("Downloading model %s → %s", repo_id, dest)

        try:
            snapshot_download(
                repo_id=repo_id,
                local_dir=str(dest),
                local_dir_use_symlinks=False,
            )
            logger.info("Download complete: %s", dest)
            return dest
        except Exception as exc:
            raise RuntimeError(
                f"Failed to download model {repo_id}: {exc}"
            ) from exc

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list_cached_models(self) -> list[MLXModelInfo]:
        """Return metadata for every model in the local cache.

        Returns:
            List of :class:`MLXModelInfo` objects, one per cached model.
        """
        models: list[MLXModelInfo] = []
        if not self._cache_dir.is_dir():
            return models

        for child in sorted(self._cache_dir.iterdir()):
            if not child.is_dir():
                continue
            # Skip hidden / metadata directories
            if child.name.startswith("."):
                continue
            info = self._build_model_info(child)
            if info is not None:
                models.append(info)
        return models

    # ------------------------------------------------------------------
    # Inspect
    # ------------------------------------------------------------------

    def get_model_info(self, repo_id: str) -> MLXModelInfo | None:
        """Return info for a specific cached model, or ``None``."""
        model_dir = self._cache_dir / _repo_to_dirname(repo_id)
        if not model_dir.is_dir():
            return None
        return self._build_model_info(model_dir)

    def is_model_cached(self, repo_id: str) -> bool:
        """Check whether *repo_id* is present in the local cache."""
        model_dir = self._cache_dir / _repo_to_dirname(repo_id)
        return model_dir.is_dir()

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_model(self, repo_id: str) -> bool:
        """Remove a model from the local cache.

        Args:
            repo_id: HuggingFace model repository id.

        Returns:
            ``True`` if the directory was removed, ``False`` if it did
            not exist.
        """
        model_dir = self._cache_dir / _repo_to_dirname(repo_id)
        if not model_dir.is_dir():
            logger.warning("Model %s not found in cache", repo_id)
            return False

        logger.info("Deleting cached model %s (%s)", repo_id, model_dir)
        shutil.rmtree(model_dir)
        return True

    # ------------------------------------------------------------------
    # Memory estimation
    # ------------------------------------------------------------------

    @staticmethod
    def estimate_memory_gb(
        total_params_billions: float,
        bits: int = 4,
        overhead_gb: float = 1.0,
    ) -> float:
        """Estimate the RAM needed to load a model.

        Formula:
            ``(params × bytes_per_param) + overhead``

        Args:
            total_params_billions: Model parameter count in billions.
            bits: Quantization bit-width (2, 3, 4, 6, 8, 16).
            overhead_gb: Fixed overhead for MLX graph, KV cache, etc.

        Returns:
            Estimated RAM in gigabytes.
        """
        bytes_per_param = bits / 8
        weight_gb = (total_params_billions * 1e9 * bytes_per_param) / (1024**3)
        return round(weight_gb + overhead_gb, 2)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _build_model_info(self, model_dir: Path) -> MLXModelInfo | None:
        """Build an :class:`MLXModelInfo` from an on-disk directory."""
        config = _read_config_json(model_dir)
        repo_id = _dirname_to_repo(model_dir.name)

        # Detect quantization from config
        quantization = config.get("quantization")
        if quantization is None and "quantization_config" in config:
            qcfg = config["quantization_config"]
            bits = qcfg.get("bits")
            if bits:
                quantization = f"{bits}-bit"

        return MLXModelInfo(
            repo_id=repo_id,
            local_path=str(model_dir),
            size_bytes=_dir_size_bytes(model_dir),
            quantization=quantization,
            model_type=config.get("model_type"),
            vocab_size=config.get("vocab_size"),
            hidden_size=config.get("hidden_size"),
            num_layers=config.get("num_hidden_layers"),
            max_position_embeddings=config.get("max_position_embeddings"),
            extra={
                k: v
                for k, v in config.items()
                if k
                not in {
                    "model_type",
                    "vocab_size",
                    "hidden_size",
                    "num_hidden_layers",
                    "max_position_embeddings",
                    "quantization",
                    "quantization_config",
                }
            },
        )
