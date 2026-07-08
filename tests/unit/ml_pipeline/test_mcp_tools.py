from codomyrmex.ml_pipeline.mcp_tools import ml_pipeline_create, ml_pipeline_execute


def test_ml_pipeline_create():
    """Test creating an ML pipeline."""
    steps = [{"name": "preprocess"}, {"name": "train"}]
    result = ml_pipeline_create("my_pipeline", steps)
    assert result["status"] == "success"
    assert result["pipeline"]["name"] == "my_pipeline"
    assert result["pipeline"]["steps"] == steps


def test_ml_pipeline_execute():
    """Test executing an ML pipeline."""
    inputs = {"data": [1, 2, 3]}
    result = ml_pipeline_execute("my_pipeline", inputs)
    assert result["status"] == "success"
    assert result["result"]["pipeline"] == "my_pipeline"
    assert result["result"]["outputs"] == inputs
