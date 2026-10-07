"""Fine-tuning orchestration.

Submits and tracks supervised fine-tuning jobs on a remote provider.

The only implemented provider is OpenAI, reached through the official
``openai`` SDK (``uv sync --extra llm_providers``) and authenticated with the
``OPENAI_API_KEY`` environment variable (or an explicit ``api_key``). Any other
provider raises :class:`NotImplementedError`; nothing in this module invents
job identifiers or statuses.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from codomyrmex.exceptions import DependencyError
from codomyrmex.exceptions import EnvironmentError as CodomyrmexEnvironmentError
from codomyrmex.logging_monitoring import get_logger

if TYPE_CHECKING:
    from openai import OpenAI
    from openai.types.fine_tuning import FineTuningJob as OpenAIFineTuningJob

logger = get_logger(__name__)

#: Providers with a real submission path.
SUPPORTED_PROVIDERS: tuple[str, ...] = ("openai",)

#: Status of a job that has not been submitted yet. Once submitted, ``status``
#: holds the provider's own status string (for OpenAI: ``validating_files``,
#: ``queued``, ``running``, ``succeeded``, ``failed`` or ``cancelled``).
PENDING_STATUS = "pending"

#: Provider statuses after which the job will not change any more.
TERMINAL_STATUSES: frozenset[str] = frozenset({"succeeded", "failed", "cancelled"})


@dataclass
class Dataset:
    """Represents a fine-tuning dataset stored in a file."""

    name: str
    path: str
    format: str = "jsonl"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this dataset."""
        return {
            "name": self.name,
            "path": self.path,
            "format": self.format,
            "metadata": self.metadata,
        }


@runtime_checkable
class JsonlExportable(Protocol):
    """An in-memory dataset that can write itself as JSONL.

    ``codomyrmex.model_ops.Dataset`` satisfies this protocol.
    """

    data: list[dict[str, Any]]

    def to_jsonl(self, path: str) -> None:
        """Write the examples to ``path`` as JSON Lines."""


class FineTuningJob:
    """A supervised fine-tuning job on a remote provider.

    The job starts in the ``"pending"`` state. :meth:`run` uploads the training
    data and creates the job on the provider; :meth:`refresh_status` and
    :meth:`cancel` talk to the provider about the submitted job.

    Args:
        base_model: Provider model identifier to fine-tune.
        dataset: Training data, either a file-backed :class:`Dataset` (JSONL)
            or an in-memory dataset implementing :class:`JsonlExportable`.
        provider: Provider name. Only ``"openai"`` is implemented.
        hyperparameters: Optional provider hyperparameters
            (e.g. ``{"n_epochs": 3}``).
        suffix: Optional suffix for the fine-tuned model name.
        api_key: API key; defaults to the ``OPENAI_API_KEY`` environment
            variable, read when the provider is first contacted.
    """

    def __init__(
        self,
        base_model: str,
        dataset: Dataset | JsonlExportable,
        provider: str = "openai",
        *,
        hyperparameters: dict[str, Any] | None = None,
        suffix: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.base_model = base_model
        self.dataset = dataset
        self.provider = provider
        self.hyperparameters = dict(hyperparameters) if hyperparameters else None
        self.suffix = suffix
        self._api_key = api_key
        self._client: OpenAI | None = None

        self.job_id: str | None = None
        self.status: str = PENDING_STATUS
        self.training_file_id: str | None = None
        self.fine_tuned_model: str | None = None
        self.error: str | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def is_terminal(self) -> bool:
        """Whether the provider reported a final status for this job."""
        return self.status in TERMINAL_STATUSES

    def run(self) -> str:
        """Upload the training data and create the job on the provider.

        Returns:
            The provider-assigned job ID.

        Raises:
            RuntimeError: If this job was already submitted.
            NotImplementedError: If ``provider`` has no implementation.
            FileNotFoundError: If a file-backed dataset does not exist.
            ValueError: If the dataset is empty or not JSONL.
            TypeError: If the dataset is of an unsupported type.
            DependencyError: If the ``openai`` SDK is not installed.
            codomyrmex.exceptions.EnvironmentError: If no API key is available.
        """
        if self.job_id is not None:
            raise RuntimeError(
                f"Fine-tuning job already submitted as {self.job_id}; "
                "create a new FineTuningJob to submit again."
            )
        self._require_supported_provider()
        self._check_dataset()

        client = self._get_client()
        logger.info(
            "Starting fine-tuning for %s via %s", self.base_model, self.provider
        )

        with self._training_file() as training_path, training_path.open("rb") as fh:
            uploaded = client.files.create(file=fh, purpose="fine-tune")
        self.training_file_id = uploaded.id

        create_kwargs: dict[str, Any] = {}
        if self.hyperparameters:
            create_kwargs["hyperparameters"] = self.hyperparameters
        if self.suffix:
            create_kwargs["suffix"] = self.suffix

        job = client.fine_tuning.jobs.create(
            model=self.base_model,
            training_file=uploaded.id,
            **create_kwargs,
        )
        self._apply(job)
        logger.info("Fine-tuning job %s created (status=%s)", job.id, self.status)
        return job.id

    def refresh_status(self) -> str:
        """Fetch the job's current status from the provider.

        A job that has not been submitted is not sent to the provider; its
        status stays ``"pending"``.

        Returns:
            The current status string.
        """
        if self.job_id is None:
            return self.status
        self._require_supported_provider()
        job = self._get_client().fine_tuning.jobs.retrieve(self.job_id)
        self._apply(job)
        return self.status

    def cancel(self) -> str:
        """Ask the provider to cancel the submitted job.

        Returns:
            The status reported by the provider after the cancel request.

        Raises:
            RuntimeError: If the job has not been submitted.
        """
        if self.job_id is None:
            raise RuntimeError("Cannot cancel a fine-tuning job that was never run.")
        self._require_supported_provider()
        job = self._get_client().fine_tuning.jobs.cancel(self.job_id)
        self._apply(job)
        return self.status

    def to_dict(self) -> dict[str, Any]:
        """Return the job's current, provider-reported state."""
        return {
            "base_model": self.base_model,
            "provider": self.provider,
            "job_id": self.job_id,
            "status": self.status,
            "training_file_id": self.training_file_id,
            "fine_tuned_model": self.fine_tuned_model,
            "error": self.error,
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _require_supported_provider(self) -> None:
        if self.provider not in SUPPORTED_PROVIDERS:
            raise NotImplementedError(
                f"Fine-tuning provider {self.provider!r} is not implemented; "
                f"supported providers: {', '.join(SUPPORTED_PROVIDERS)}."
            )

    def _check_dataset(self) -> None:
        dataset = self.dataset
        if isinstance(dataset, Dataset):
            if dataset.format.lower() != "jsonl":
                raise ValueError(
                    f"Dataset {dataset.name!r} has format {dataset.format!r}; "
                    "fine-tuning requires JSONL."
                )
            path = Path(dataset.path)
            if not path.is_file():
                raise FileNotFoundError(f"Training file not found: {path}")
            if path.stat().st_size == 0:
                raise ValueError(f"Training file is empty: {path}")
            return
        if isinstance(dataset, JsonlExportable):
            if not dataset.data:
                raise ValueError("Training dataset has no examples.")
            return
        raise TypeError(
            "dataset must be a fine_tuning.Dataset or provide data and "
            f"to_jsonl(); got {type(dataset).__name__}."
        )

    @contextmanager
    def _training_file(self) -> Iterator[Path]:
        """Yield a JSONL file for upload; in-memory data goes to a temp file."""
        dataset = self.dataset
        if isinstance(dataset, Dataset):
            yield Path(dataset.path)
            return
        fd, name = tempfile.mkstemp(prefix="codomyrmex-ft-", suffix=".jsonl")
        os.close(fd)
        path = Path(name)
        try:
            dataset.to_jsonl(str(path))
            yield path
        finally:
            path.unlink(missing_ok=True)

    def _get_client(self) -> OpenAI:
        if self._client is not None:
            return self._client
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise DependencyError(
                "The openai SDK is required for OpenAI fine-tuning. "
                "Install it with: uv sync --extra llm_providers",
                dependency_name="openai",
            ) from exc
        api_key = self._api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise CodomyrmexEnvironmentError(
                "OPENAI_API_KEY is not set; it is required to submit or query "
                "OpenAI fine-tuning jobs.",
                variable_name="OPENAI_API_KEY",
            )
        self._client = OpenAI(api_key=api_key)
        return self._client

    def _apply(self, job: OpenAIFineTuningJob) -> None:
        self.job_id = job.id
        self.status = job.status
        self.fine_tuned_model = job.fine_tuned_model
        self.error = job.error.message if job.error else None


__all__ = [
    "PENDING_STATUS",
    "SUPPORTED_PROVIDERS",
    "TERMINAL_STATUSES",
    "Dataset",
    "FineTuningJob",
    "JsonlExportable",
]
