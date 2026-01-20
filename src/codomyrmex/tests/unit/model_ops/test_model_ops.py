"""Unit tests for model_ops module."""

import pytest
from codomyrmex.model_ops import Dataset, FineTuningJob, DatasetSanitizer, Evaluator

def test_dataset_validation():
    """Test dataset validation logic."""
    valid_data = [
        {"messages": [{"role": "user", "content": "hi"}]},
        {"prompt": "Hello", "completion": "Hi there"}
    ]
    ds = Dataset(valid_data)
    assert ds.validate() is True
    
    invalid_data = [{"wrong": "format"}]
    ds_invalid = Dataset(invalid_data)
    assert ds_invalid.validate() is False

def test_fine_tuning_flow():
    """Test the orchestration flow of a fine-tuning job."""
    ds = Dataset([{"prompt": "A", "completion": "B"}])
    job = FineTuningJob(base_model="gpt-4o", dataset=ds)
    
    assert job.status == "pending"
    job_id = job.run()
    assert job_id is not None
    assert job.status == "running"
    
    status = job.refresh_status()
    assert status == "completed"
    assert job.status == "completed"

def test_dataset_sanitizer():
    """Test sanitization logic."""
    data = [{"prompt": "hi", "pii": "secret"}, {"prompt": "hello"}]
    ds = Dataset(data)
    sanitized = DatasetSanitizer.strip_keys(ds, ["pii"])
    assert "pii" not in sanitized.data[0]
    assert len(sanitized.data) == 2

def test_evaluator():
    """Test evaluation logic."""
    from codomyrmex.model_ops.evaluators import exact_match_metric
    evaluator = Evaluator(metrics={"EM": exact_match_metric})
    
    preds = ["hello ", "world"]
    refs = ["hello", "world"]
    # Both match after stripping
    results = evaluator.evaluate(preds, refs)
    assert results["EM"] == 1.0 
    
    # Truly different
    results_diff = evaluator.evaluate(["a"], ["b"])
    assert results_diff["EM"] == 0.0
