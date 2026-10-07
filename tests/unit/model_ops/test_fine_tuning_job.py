"""Tests for the provider-backed FineTuningJob (model_ops.fine_tuning).

No test here submits a fine-tuning job: submission costs money and needs a key.
Local validation, the missing-key path and the unsupported-provider path run
everywhere; one read-only provider call runs only when OPENAI_API_KEY is set.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import pytest

from codomyrmex import model_ops
from codomyrmex.exceptions import EnvironmentError as CodomyrmexEnvironmentError
from codomyrmex.model_ops.fine_tuning.fine_tuning import (
    PENDING_STATUS,
    SUPPORTED_PROVIDERS,
    Dataset,
    FineTuningJob,
    JsonlExportable,
)

HAS_OPENAI = importlib.util.find_spec("openai") is not None


def _write_jsonl(path: Path) -> Path:
    rows = [
        {
            "messages": [
                {"role": "user", "content": "ping"},
                {"role": "assistant", "content": "pong"},
            ]
        }
    ]
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path


@pytest.mark.unit
class TestFineTuningJobLocal:
    """Behaviour that never reaches the provider."""

    def test_package_export_is_the_provider_backed_class(self):
        assert model_ops.FineTuningJob is FineTuningJob

    def test_in_memory_dataset_satisfies_protocol(self):
        ds = model_ops.Dataset([{"prompt": "q", "completion": "a"}])
        assert isinstance(ds, JsonlExportable)

    def test_only_openai_is_supported(self):
        assert SUPPORTED_PROVIDERS == ("openai",)

    def test_initial_state(self, tmp_path):
        ds = Dataset(name="t", path=str(_write_jsonl(tmp_path / "t.jsonl")))
        job = FineTuningJob("gpt-4o-mini", ds, suffix="demo")
        assert job.status == PENDING_STATUS
        assert job.is_terminal is False
        assert job.to_dict() == {
            "base_model": "gpt-4o-mini",
            "provider": "openai",
            "job_id": None,
            "status": "pending",
            "training_file_id": None,
            "fine_tuned_model": None,
            "error": None,
        }

    def test_unsupported_provider_raises_before_anything_else(self, tmp_path):
        ds = Dataset(name="t", path=str(tmp_path / "missing.jsonl"))
        job = FineTuningJob("mistral-small", ds, provider="mistral")
        with pytest.raises(NotImplementedError, match="'mistral' is not implemented"):
            job.run()
        assert job.job_id is None

    def test_unsupported_dataset_type_raises(self):
        job = FineTuningJob("gpt-4o-mini", dataset=["not", "a", "dataset"])
        with pytest.raises(TypeError, match="dataset must be"):
            job.run()

    def test_cancel_before_run_raises(self, tmp_path):
        ds = Dataset(name="t", path=str(_write_jsonl(tmp_path / "t.jsonl")))
        job = FineTuningJob("gpt-4o-mini", ds)
        with pytest.raises(RuntimeError, match="never run"):
            job.cancel()

    def test_run_twice_is_refused(self, tmp_path):
        ds = Dataset(name="t", path=str(_write_jsonl(tmp_path / "t.jsonl")))
        job = FineTuningJob("gpt-4o-mini", ds)
        job.job_id = "ftjob-already-submitted"
        with pytest.raises(RuntimeError, match="already submitted"):
            job.run()

    def test_unsupported_provider_refresh_of_submitted_job_raises(self, tmp_path):
        ds = Dataset(name="t", path=str(_write_jsonl(tmp_path / "t.jsonl")))
        job = FineTuningJob("x", ds, provider="vertex")
        job.job_id = "job-1"
        with pytest.raises(NotImplementedError):
            job.refresh_status()


@pytest.mark.unit
@pytest.mark.skipif(not HAS_OPENAI, reason="openai SDK not installed")
class TestFineTuningJobMissingKey:
    """Without a key the job fails explicitly instead of reporting a fake ID."""

    def test_run_without_key_raises(self, tmp_path, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        ds = Dataset(name="t", path=str(_write_jsonl(tmp_path / "t.jsonl")))
        job = FineTuningJob("gpt-4o-mini", ds)
        with pytest.raises(CodomyrmexEnvironmentError, match="OPENAI_API_KEY"):
            job.run()
        assert job.job_id is None
        assert job.status == PENDING_STATUS
        assert job.training_file_id is None

    def test_in_memory_dataset_without_key_raises(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        ds = model_ops.Dataset([{"prompt": "q", "completion": "a"}])
        job = model_ops.FineTuningJob("gpt-4o-mini", ds)
        with pytest.raises(CodomyrmexEnvironmentError):
            job.run()
        assert job.job_id is None

    def test_refresh_of_submitted_job_without_key_raises(self, tmp_path, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        ds = Dataset(name="t", path=str(_write_jsonl(tmp_path / "t.jsonl")))
        job = FineTuningJob("gpt-4o-mini", ds)
        job.job_id = "ftjob-unknown"
        with pytest.raises(CodomyrmexEnvironmentError):
            job.refresh_status()


@pytest.mark.unit
@pytest.mark.network
@pytest.mark.external
@pytest.mark.skipif(
    not (HAS_OPENAI and os.getenv("OPENAI_API_KEY")),
    reason="needs the openai SDK and OPENAI_API_KEY (read-only call, no job is created)",
)
def test_refresh_status_of_unknown_job_reaches_provider(tmp_path):
    """A real retrieve of a non-existent job surfaces the provider's 404."""
    import openai

    ds = Dataset(name="t", path=str(_write_jsonl(tmp_path / "t.jsonl")))
    job = FineTuningJob("gpt-4o-mini", ds)
    job.job_id = "ftjob-codomyrmex-does-not-exist"
    with pytest.raises(openai.NotFoundError):
        job.refresh_status()
    assert job.status == PENDING_STATUS
