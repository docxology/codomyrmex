"""Zero-mock unit tests for reporting functionality."""

from codomyrmex.reporting.reporting import Reporting, create_reporting


def test_reporting_initialization() -> None:
    """Test that Reporting is properly initialized."""
    config = {"key": "value"}
    reporter = Reporting(config=config)
    assert reporter.config == config

    reporter_default = Reporting()
    assert reporter_default.config == {}


def test_reporting_process() -> None:
    """Test data processing functionality."""
    reporter = Reporting()
    result = reporter.process("my report data")

    assert result["status"] == "success"
    assert result["report"] == "my report data"


def test_create_reporting() -> None:
    """Test the factory method."""
    reporter = create_reporting({"test": True})
    assert isinstance(reporter, Reporting)
    assert reporter.config == {"test": True}
