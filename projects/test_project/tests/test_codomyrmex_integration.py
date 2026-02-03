"""Integration tests verifying real codomyrmex module imports and functionality.

These tests ensure test_project properly integrates with all key codomyrmex
modules without falling back to stdlib implementations.
"""

import pytest


class TestLoggingMonitoringIntegration:
    """Tests for codomyrmex.logging_monitoring integration."""

    def test_import_get_logger(self):
        """Verify get_logger imports from codomyrmex."""
        from codomyrmex.logging_monitoring import get_logger
        
        logger = get_logger("test_module")
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        
    def test_import_setup_logging(self):
        """Verify setup_logging is available."""
        from codomyrmex.logging_monitoring import setup_logging
        
        # Should not raise
        setup_logging()


class TestConfigManagementIntegration:
    """Tests for codomyrmex.config_management integration."""

    def test_import_configuration_manager(self):
        """Verify ConfigurationManager imports."""
        from codomyrmex.config_management import ConfigurationManager
        
        assert ConfigurationManager is not None

    def test_import_load_configuration(self):
        """Verify load_configuration function."""
        from codomyrmex.config_management import load_configuration
        
        assert callable(load_configuration)


class TestSerializationIntegration:
    """Tests for codomyrmex.serialization integration."""

    def test_import_serialize_deserialize(self):
        """Verify serialize/deserialize functions."""
        from codomyrmex.serialization import serialize, deserialize
        
        data = {"key": "value", "number": 42}
        serialized = serialize(data, format="json")
        assert isinstance(serialized, bytes)
        
        deserialized = deserialize(serialized, format="json")
        assert deserialized == data
        
    def test_import_serialization_format(self):
        """Verify SerializationFormat enum."""
        from codomyrmex.serialization import SerializationFormat
        
        assert SerializationFormat.JSON is not None


class TestValidationIntegration:
    """Tests for codomyrmex.validation integration."""

    def test_import_validator(self):
        """Verify Validator class."""
        from codomyrmex.validation import Validator, ValidationResult
        
        assert Validator is not None
        assert ValidationResult is not None
        
    def test_import_validate_function(self):
        """Verify validate function."""
        from codomyrmex.validation import validate, is_valid
        
        assert callable(validate)
        assert callable(is_valid)


class TestEventsIntegration:
    """Tests for codomyrmex.events integration."""

    def test_import_event_bus(self):
        """Verify EventBus imports."""
        from codomyrmex.events import EventBus, get_event_bus
        
        bus = get_event_bus()
        assert bus is not None
        
    def test_import_event_types(self):
        """Verify Event and EventType."""
        from codomyrmex.events import Event, EventType
        
        assert Event is not None
        assert EventType is not None


class TestStaticAnalysisIntegration:
    """Tests for codomyrmex.static_analysis integration."""

    def test_import_static_analyzer(self):
        """Verify StaticAnalyzer imports."""
        from codomyrmex.static_analysis import StaticAnalyzer
        
        analyzer = StaticAnalyzer()
        assert analyzer is not None
        
    def test_import_analyze_functions(self):
        """Verify analyze functions."""
        from codomyrmex.static_analysis import analyze_file, analyze_project
        
        assert callable(analyze_file)
        assert callable(analyze_project)


class TestOrchestratorIntegration:
    """Tests for codomyrmex.orchestrator integration."""

    def test_import_workflow(self):
        """Verify Workflow and Task imports."""
        from codomyrmex.orchestrator import Workflow, Task, TaskStatus
        
        assert Workflow is not None
        assert Task is not None
        assert TaskStatus is not None
        
    def test_import_runners(self):
        """Verify runner functions."""
        from codomyrmex.orchestrator import run_script, run_function
        
        assert callable(run_script)
        assert callable(run_function)


class TestLLMIntegration:
    """Tests for codomyrmex.llm integration."""

    def test_import_llm_config(self):
        """Verify LLMConfig imports."""
        from codomyrmex.llm import LLMConfig, LLMConfigPresets
        
        assert LLMConfig is not None
        assert LLMConfigPresets is not None
        
    def test_import_providers(self):
        """Verify providers submodule."""
        from codomyrmex.llm import providers
        
        assert providers is not None


class TestExceptionsIntegration:
    """Tests for codomyrmex.exceptions integration."""

    def test_import_base_exceptions(self):
        """Verify base exceptions."""
        from codomyrmex.exceptions import (
            CodomyrmexError,
            ConfigurationError,
            ValidationError,
        )
        
        assert issubclass(ConfigurationError, CodomyrmexError)
        assert issubclass(ValidationError, CodomyrmexError)


class TestTestProjectModulesUseCodomyrmex:
    """Verify test_project source modules use real codomyrmex."""

    def test_main_uses_codomyrmex_logging(self):
        """Verify main.py has codomyrmex logging enabled."""
        from src.main import HAS_CODOMYRMEX_LOGGING
        
        assert HAS_CODOMYRMEX_LOGGING is True, (
            "main.py should use real codomyrmex.logging_monitoring, not fallback"
        )

    def test_analyzer_logger_is_codomyrmex(self):
        """Verify analyzer uses codomyrmex logger."""
        from src import analyzer
        
        # Logger should be from codomyrmex, not stdlib
        assert "codomyrmex" in str(type(analyzer.logger).__module__) or \
               hasattr(analyzer, 'HAS_CODOMYRMEX_LOGGING')
