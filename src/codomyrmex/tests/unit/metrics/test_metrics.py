
import pytest
from codomyrmex import metrics

def test_metrics_module_import():
    """Verify that the metrics module can be imported successfully."""
    assert metrics is not None
    assert hasattr(metrics, "__path__")

def test_metrics_module_structure():
    """Verify basic structure of metrics module."""
    assert hasattr(metrics, "__file__")
