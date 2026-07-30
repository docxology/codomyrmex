from codomyrmex.ml_pipeline import ml_pipeline_create, ml_pipeline_execute


def test_package_exports_are_explicit() -> None:
    from codomyrmex import ml_pipeline

    assert ml_pipeline.__all__ == ["ml_pipeline_create", "ml_pipeline_execute"]


def test_ml_pipeline_create() -> None:
    """Test creating an ML pipeline."""
    steps = [{"name": "preprocess"}, {"name": "train"}]
    result = ml_pipeline_create("my_pipeline", steps)
    assert result["status"] == "success"
    assert result["pipeline"]["name"] == "my_pipeline"
    assert result["pipeline"]["steps"] == steps


def test_ml_pipeline_execute() -> None:
    """Test executing an ML pipeline."""
    inputs = {"data": [1, 2, 3]}
    result = ml_pipeline_execute("my_pipeline", inputs)
    assert result["status"] == "success"
    assert result["result"]["pipeline"] == "my_pipeline"
    assert result["result"]["outputs"] == inputs
