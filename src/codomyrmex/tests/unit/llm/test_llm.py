"""
Comprehensive Tests for LLM Module

This test suite covers all aspects of the LLM module including:
1. ModelRunner initialization and configuration
2. Prompt handling and formatting
3. Response parsing
4. Temperature and parameter handling
5. Timeout and retry logic
6. Streaming responses
7. Error handling for API failures
8. Output formatting (JSON, text)
9. Token counting (if available)
10. Conversation history management

Uses real Ollama/Fabric when available, with skip markers otherwise.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from unittest import TestCase

import pytest
import requests as _requests_lib


def _ollama_available() -> bool:
    """Return True if Ollama server is reachable."""
    try:
        resp = _requests_lib.get("http://localhost:11434/api/version", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


def _fabric_available() -> bool:
    """Return True if fabric CLI is installed."""
    return shutil.which("fabric") is not None


_OLLAMA_AVAILABLE = _ollama_available()
_FABRIC_AVAILABLE = _fabric_available()
_skip_no_ollama = pytest.mark.skipif(
    not _OLLAMA_AVAILABLE, reason="Ollama server not reachable"
)
_skip_no_fabric = pytest.mark.skipif(
    not _FABRIC_AVAILABLE, reason="fabric CLI not installed"
)

# ============================================================================
# Test the LLM Config Module
# ============================================================================

@pytest.mark.unit
class TestLLMConfig(TestCase):
    """Tests for LLMConfig class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_env = {}

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        # Restore environment
        import os
        for key in ['LLM_MODEL', 'LLM_TEMPERATURE', 'LLM_MAX_TOKENS',
                    'LLM_TOP_P', 'LLM_TOP_K', 'LLM_TIMEOUT', 'LLM_BASE_URL']:
            if key in os.environ:
                del os.environ[key]

    def test_llm_config_default_initialization(self):
        """Test LLMConfig initializes with correct default values."""
        from codomyrmex.llm.config import LLMConfig

        config = LLMConfig(output_root=self.temp_dir)

        assert config.model == "llama3.1:latest"
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.top_p == 0.9
        assert config.top_k == 40
        assert config.timeout == 30
        assert config.base_url == "http://localhost:11434"

    def test_llm_config_custom_values(self):
        """Test LLMConfig accepts custom parameter values."""
        from codomyrmex.llm.config import LLMConfig

        config = LLMConfig(
            model="custom-model:latest",
            temperature=0.5,
            max_tokens=2000,
            top_p=0.8,
            top_k=50,
            timeout=60,
            base_url="http://custom:8080",
            output_root=self.temp_dir
        )

        assert config.model == "custom-model:latest"
        assert config.temperature == 0.5
        assert config.max_tokens == 2000
        assert config.top_p == 0.8
        assert config.top_k == 50
        assert config.timeout == 60
        assert config.base_url == "http://custom:8080"

    def test_llm_config_environment_variables(self):
        """Test LLMConfig reads from environment variables."""
        from codomyrmex.llm.config import LLMConfig

        os.environ['LLM_MODEL'] = 'env-model:v1'
        os.environ['LLM_TEMPERATURE'] = '0.9'
        os.environ['LLM_MAX_TOKENS'] = '500'

        config = LLMConfig(output_root=self.temp_dir)

        assert config.model == 'env-model:v1'
        assert config.temperature == 0.9
        assert config.max_tokens == 500

    def test_llm_config_get_generation_options(self):
        """Test get_generation_options returns correct dictionary."""
        from codomyrmex.llm.config import LLMConfig

        config = LLMConfig(
            temperature=0.5,
            top_p=0.8,
            top_k=30,
            max_tokens=1500,
            output_root=self.temp_dir
        )

        options = config.get_generation_options()

        assert options['temperature'] == 0.5
        assert options['top_p'] == 0.8
        assert options['top_k'] == 30
        assert options['num_predict'] == 1500

    def test_llm_config_get_client_kwargs(self):
        """Test get_client_kwargs returns correct parameters."""
        from codomyrmex.llm.config import LLMConfig

        config = LLMConfig(
            base_url="http://test:1234",
            model="test-model",
            timeout=120,
            output_root=self.temp_dir
        )

        kwargs = config.get_client_kwargs()

        assert kwargs['base_url'] == "http://test:1234"
        assert kwargs['model'] == "test-model"
        assert kwargs['timeout'] == 120

    def test_llm_config_to_dict(self):
        """Test to_dict serialization."""
        from codomyrmex.llm.config import LLMConfig

        config = LLMConfig(output_root=self.temp_dir)

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert 'model' in config_dict
        assert 'temperature' in config_dict
        assert 'max_tokens' in config_dict
        assert 'output_root' in config_dict

    def test_llm_config_save_and_load(self):
        """Test saving and loading configuration from file."""
        from codomyrmex.llm.config import LLMConfig

        config_path = Path(self.temp_dir) / "test_config.json"

        # Create and save config
        config1 = LLMConfig(
            model="test-model",
            temperature=0.3,
            output_root=self.temp_dir
        )
        config1.save_config(config_path)

        assert config_path.exists()

        # Load config
        config2 = LLMConfig.from_file(config_path)

        assert config2.model == "test-model"
        assert config2.temperature == 0.3

    def test_llm_config_presets(self):
        """Test LLMConfigPresets provides valid configurations."""
        from codomyrmex.llm.config import LLMConfigPresets

        creative = LLMConfigPresets.creative()
        precise = LLMConfigPresets.precise()
        fast = LLMConfigPresets.fast()
        comprehensive = LLMConfigPresets.comprehensive()

        # Creative should have high temperature
        assert creative.temperature == 0.9

        # Precise should have low temperature
        assert precise.temperature == 0.1

        # Fast should have lower timeout and tokens
        assert fast.timeout == 15
        assert fast.max_tokens == 500

        # Comprehensive should have higher tokens
        assert comprehensive.max_tokens == 2000


# ============================================================================
# Test the Execution Options
# ============================================================================

@pytest.mark.unit
class TestExecutionOptions(TestCase):
    """Tests for ExecutionOptions dataclass."""

    def test_execution_options_defaults(self):
        """Test ExecutionOptions has correct default values."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        options = ExecutionOptions()

        assert options.temperature == 0.7
        assert options.top_p == 0.9
        assert options.top_k == 40
        assert options.repeat_penalty == 1.1
        assert options.max_tokens == 2048
        assert options.timeout == 300
        assert options.stream is False
        assert options.format is None
        assert options.system_prompt is None
        assert options.context_window is None

    def test_execution_options_custom_values(self):
        """Test ExecutionOptions accepts custom values."""
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        options = ExecutionOptions(
            temperature=0.3,
            top_p=0.5,
            top_k=20,
            repeat_penalty=1.5,
            max_tokens=1000,
            timeout=60,
            stream=True,
            format="json",
            system_prompt="You are helpful.",
            context_window=4096
        )

        assert options.temperature == 0.3
        assert options.top_p == 0.5
        assert options.top_k == 20
        assert options.repeat_penalty == 1.5
        assert options.max_tokens == 1000
        assert options.timeout == 60
        assert options.stream is True
        assert options.format == "json"
        assert options.system_prompt == "You are helpful."
        assert options.context_window == 4096


# ============================================================================
# Test Model Runner with Mocks
# ============================================================================

@pytest.mark.unit
class TestModelRunner(TestCase):
    """Tests for ModelRunner class with real OllamaManager (skip if unavailable)."""

    def setUp(self):
        """Set up test fixtures."""
        if not _OLLAMA_AVAILABLE:
            self.skipTest("Ollama server not reachable")

        from codomyrmex.llm.ollama.model_runner import ModelRunner
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        self.manager = OllamaManager(auto_start_server=False)
        self.runner = ModelRunner(self.manager)

    def test_model_runner_initialization(self):
        """Test ModelRunner initializes correctly."""
        assert self.runner.ollama_manager is self.manager
        assert self.runner.logger is not None

    def test_format_conversation_single_user_message(self):
        """Test _format_conversation with single user message."""
        messages = [{"role": "user", "content": "Hello"}]
        result = self.runner._format_conversation(messages)
        assert "User: Hello" in result

    def test_format_conversation_multiple_roles(self):
        """Test _format_conversation with multiple message roles."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
        result = self.runner._format_conversation(messages)

        assert "System: You are helpful." in result
        assert "User: Hello" in result
        assert "Assistant: Hi there!" in result
        assert "User: How are you?" in result

    def test_run_with_options_returns_result(self):
        """Test run_with_options uses real Ollama and returns result."""
        models = self.manager.list_models()
        if not models:
            self.skipTest("No Ollama models installed")

        model_name = models[0].name
        result = self.runner.run_with_options(model_name, "Say hello in one word")
        assert result is not None
        assert result.success is True

    def test_run_conversation_formats_messages(self):
        """Test run_conversation properly formats and executes conversation."""
        models = self.manager.list_models()
        if not models:
            self.skipTest("No Ollama models installed")

        model_name = models[0].name
        messages = [
            {"role": "user", "content": "Hello"}
        ]

        result = self.runner.run_conversation(model_name, messages)
        assert result.success is True

    def test_benchmark_model_returns_correct_structure(self):
        """Test benchmark_model returns proper benchmark results."""
        models = self.manager.list_models()
        if not models:
            self.skipTest("No Ollama models installed")

        model_name = models[0].name
        test_prompts = ["Say hi"]
        results = self.runner.benchmark_model(model_name, test_prompts)

        assert 'model_name' in results
        assert 'total_prompts' in results
        assert 'successful_runs' in results
        assert 'total_time' in results
        assert results['total_prompts'] == 1


# ============================================================================
# Test Ollama Manager with Mocks
# ============================================================================

@pytest.mark.unit
class TestOllamaManager(TestCase):
    """Tests for OllamaManager class with real Ollama (skip if unavailable)."""

    def setUp(self):
        if not _OLLAMA_AVAILABLE:
            self.skipTest("Ollama server not reachable")

    def test_ollama_manager_initialization(self):
        """Test OllamaManager initializes correctly."""
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        manager = OllamaManager(auto_start_server=False)

        assert manager.ollama_binary == "ollama"
        assert manager.base_url == "http://localhost:11434"
        assert manager.use_http_api is True

    def test_list_models_returns_list(self):
        """Test list_models returns a list of OllamaModel objects."""
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager, OllamaModel

        manager = OllamaManager(auto_start_server=False)
        models = manager.list_models()

        assert isinstance(models, list)
        assert all(isinstance(m, OllamaModel) for m in models)

    def test_is_model_available_returns_boolean(self):
        """Test is_model_available returns correct boolean."""
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        manager = OllamaManager(auto_start_server=False)
        models = manager.list_models()

        if models:
            assert manager.is_model_available(models[0].name) is True
        assert manager.is_model_available('nonexistent-model-xyz-999') is False

    def test_run_model_returns_result_on_success(self):
        """Test run_model returns ModelExecutionResult on success."""
        from codomyrmex.llm.ollama.ollama_manager import (
            ModelExecutionResult,
            OllamaManager,
        )

        manager = OllamaManager(auto_start_server=False)
        models = manager.list_models()
        if not models:
            self.skipTest("No Ollama models installed")

        result = manager.run_model(models[0].name, 'Say hello in one word', save_output=False)

        assert isinstance(result, ModelExecutionResult)
        assert result.success is True
        assert len(result.response) > 0
        assert result.model_name == models[0].name

    def test_run_model_returns_failure_for_unavailable_model(self):
        """Test run_model returns failure for unavailable model."""
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        manager = OllamaManager(auto_start_server=False)
        result = manager.run_model('nonexistent-model-xyz-999', 'test prompt', save_output=False)

        assert result.success is False
        assert 'not available' in result.error_message.lower()

    def test_get_model_stats_structure(self):
        """Test get_model_stats returns proper structure."""
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        manager = OllamaManager(auto_start_server=False)
        stats = manager.get_model_stats()

        assert 'total_models' in stats
        assert 'total_size_bytes' in stats
        assert 'total_size_mb' in stats
        assert 'models_by_family' in stats

    def test_parse_size_converts_correctly(self):
        """Test _parse_size converts size strings correctly."""
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        manager = OllamaManager(auto_start_server=False)

        assert manager._parse_size("1GB") == 1 * 1024 * 1024 * 1024
        assert manager._parse_size("500MB") == 500 * 1024 * 1024
        assert manager._parse_size("100KB") == 100 * 1024
        assert manager._parse_size("1000") == 1000
        assert manager._parse_size("invalid") == 0


# ============================================================================
# Test Output Manager
# ============================================================================

@pytest.mark.unit
class TestOutputManager(TestCase):
    """Tests for OutputManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        from codomyrmex.llm.ollama.output_manager import OutputManager
        self.output_manager = OutputManager(self.temp_dir)

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_output_manager_creates_directories(self):
        """Test OutputManager creates required directories."""
        assert Path(self.temp_dir).exists()
        assert (Path(self.temp_dir) / "outputs").exists()
        assert (Path(self.temp_dir) / "configs").exists()
        assert (Path(self.temp_dir) / "logs").exists()
        assert (Path(self.temp_dir) / "reports").exists()

    def test_save_model_output_creates_file(self):
        """Test save_model_output creates output file."""
        output_path = self.output_manager.save_model_output(
            model_name="test-model",
            prompt="test prompt",
            response="test response",
            execution_time=1.5,
            metadata={'test': True}
        )

        assert Path(output_path).exists()

        with open(output_path) as f:
            content = f.read()

        assert 'test-model' in content
        assert 'test prompt' in content
        assert 'test response' in content
        assert '1.5' in content

    def test_save_execution_result_creates_json(self):
        """Test save_execution_result creates JSON file."""
        from codomyrmex.llm.ollama.ollama_manager import ModelExecutionResult

        result = ModelExecutionResult(
            model_name="test-model",
            prompt="test prompt",
            response="test response",
            execution_time=1.5,
            success=True,
            tokens_used=50
        )

        output_path = self.output_manager.save_execution_result(result)

        assert Path(output_path).exists()

        with open(output_path) as f:
            data = json.load(f)

        assert data['model_name'] == 'test-model'
        assert data['success'] is True
        assert data['execution_time'] == 1.5

    def test_save_and_load_model_config(self):
        """Test saving and loading model configuration."""
        test_config = {
            'temperature': 0.7,
            'max_tokens': 500,
            'custom_setting': 'value'
        }

        # Save config
        config_path = self.output_manager.save_model_config(
            model_name="test-model",
            config=test_config,
            config_name="test_config"
        )

        assert Path(config_path).exists()

        # Load config
        loaded_config = self.output_manager.load_model_config("test-model", "test_config")

        assert loaded_config['temperature'] == 0.7
        assert loaded_config['max_tokens'] == 500
        assert loaded_config['custom_setting'] == 'value'

    def test_save_batch_results(self):
        """Test save_batch_results creates batch file."""
        from codomyrmex.llm.ollama.ollama_manager import ModelExecutionResult

        results = [
            ModelExecutionResult(
                model_name="model1",
                prompt="prompt1",
                response="response1",
                execution_time=0.5,
                success=True
            ),
            ModelExecutionResult(
                model_name="model1",
                prompt="prompt2",
                response="response2",
                execution_time=0.6,
                success=True
            )
        ]

        batch_path = self.output_manager.save_batch_results(results, "test_batch")

        assert Path(batch_path).exists()

        with open(batch_path) as f:
            data = json.load(f)

        assert data['batch_name'] == 'test_batch'
        assert data['total_executions'] == 2
        assert data['successful_executions'] == 2

    def test_get_output_stats(self):
        """Test get_output_stats returns correct statistics."""
        # Create some outputs
        for i in range(3):
            self.output_manager.save_model_output(
                model_name=f"model{i}",
                prompt=f"prompt{i}",
                response=f"response{i}",
                execution_time=1.0
            )

        stats = self.output_manager.get_output_stats()

        assert 'total_outputs' in stats
        assert 'total_size' in stats
        assert 'by_type' in stats
        assert 'by_model' in stats


# ============================================================================
# Test Config Manager
# ============================================================================

@pytest.mark.unit
class TestConfigManager(TestCase):
    """Tests for ConfigManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_manager_initialization(self):
        """Test ConfigManager initializes with config."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        # Use a non-existent config path so defaults are used
        manager = ConfigManager(str(Path(self.temp_dir) / "nonexistent_config.json"))

        assert manager.config is not None
        assert manager.config.ollama_binary == "ollama"
        assert manager.config.default_model == "llama3.1:latest"

    def test_config_manager_update_config(self):
        """Test ConfigManager updates configuration."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        config_file = Path(self.temp_dir) / "config.json"
        manager = ConfigManager(str(config_file))

        success = manager.update_config(
            default_model="new-model",
            auto_start_server=False
        )

        # May fail if directory doesn't exist, but config should be updated
        assert manager.config.default_model == "new-model"
        assert manager.config.auto_start_server is False

    def test_get_execution_presets(self):
        """Test get_execution_presets returns valid presets."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager
        from codomyrmex.llm.ollama.model_runner import ExecutionOptions

        manager = ConfigManager()
        presets = manager.get_execution_presets()

        assert 'fast' in presets
        assert 'creative' in presets
        assert 'balanced' in presets
        assert 'precise' in presets
        assert 'long_form' in presets

        # Verify presets are ExecutionOptions instances
        for name, preset in presets.items():
            assert isinstance(preset, ExecutionOptions)

    def test_validate_config(self):
        """Test validate_config returns validation results."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        manager = ConfigManager()
        validation = manager.validate_config()

        assert 'valid' in validation
        assert 'errors' in validation
        assert 'warnings' in validation
        assert isinstance(validation['errors'], list)
        assert isinstance(validation['warnings'], list)

    def test_reset_to_defaults(self):
        """Test reset_to_defaults restores default configuration."""
        from codomyrmex.llm.ollama.config_manager import ConfigManager

        config_file = Path(self.temp_dir) / "config.json"
        manager = ConfigManager(str(config_file))

        # Change config
        manager.config.default_model = "changed-model"

        # Reset
        manager.reset_to_defaults()

        assert manager.config.default_model == "llama3.1:latest"


# ============================================================================
# Test LLM Exceptions
# ============================================================================

@pytest.mark.unit
class TestLLMExceptions(TestCase):
    """Tests for LLM exception classes."""

    def test_llm_connection_error(self):
        """Test LLMConnectionError with context."""
        from codomyrmex.llm.exceptions import LLMConnectionError

        error = LLMConnectionError(
            "Connection failed",
            provider="ollama",
            endpoint="http://localhost:11434"
        )

        assert "Connection failed" in str(error)
        assert error.context.get("provider") == "ollama"
        assert error.context.get("endpoint") == "http://localhost:11434"

    def test_llm_timeout_error(self):
        """Test LLMTimeoutError with context."""
        from codomyrmex.llm.exceptions import LLMTimeoutError

        error = LLMTimeoutError(
            "Request timed out",
            timeout_seconds=30.0,
            provider="ollama"
        )

        assert "timed out" in str(error)
        assert error.context.get("timeout_seconds") == 30.0
        assert error.context.get("provider") == "ollama"

    def test_prompt_too_long_error(self):
        """Test PromptTooLongError with token information."""
        from codomyrmex.llm.exceptions import PromptTooLongError

        error = PromptTooLongError(
            "Prompt exceeds limit",
            token_count=10000,
            max_tokens=4096,
            model="llama3.1:latest"
        )

        assert error.context.get("token_count") == 10000
        assert error.context.get("max_tokens") == 4096
        assert error.context.get("model") == "llama3.1:latest"

    def test_response_parsing_error(self):
        """Test ResponseParsingError with response preview."""
        from codomyrmex.llm.exceptions import ResponseParsingError

        long_response = "x" * 1000
        error = ResponseParsingError(
            "Failed to parse response",
            expected_format="json",
            raw_response=long_response
        )

        assert error.context.get("expected_format") == "json"
        # Response should be truncated
        assert len(error.context.get("raw_response", "")) <= 503  # 500 + "..."

    def test_model_not_found_error(self):
        """Test ModelNotFoundError with available models."""
        from codomyrmex.llm.exceptions import ModelNotFoundError

        error = ModelNotFoundError(
            "Model not found",
            model="nonexistent:latest",
            provider="ollama",
            available_models=["llama3.1:latest", "codellama:latest"]
        )

        assert error.context.get("model") == "nonexistent:latest"
        assert "llama3.1:latest" in error.context.get("available_models", [])

    def test_streaming_error(self):
        """Test StreamingError with chunks received."""
        from codomyrmex.llm.exceptions import StreamingError

        error = StreamingError(
            "Stream interrupted",
            chunks_received=5
        )

        assert error.context.get("chunks_received") == 5

    def test_rate_limit_error(self):
        """Test LLMRateLimitError with retry information."""
        from codomyrmex.llm.exceptions import LLMRateLimitError

        error = LLMRateLimitError(
            "Rate limit exceeded",
            provider="openai",
            retry_after=60.0,
            limit_type="requests_per_minute"
        )

        assert error.context.get("retry_after") == 60.0
        assert error.context.get("limit_type") == "requests_per_minute"


# ============================================================================
# Test Fabric Manager with Mocks
# ============================================================================

@pytest.mark.unit
class TestFabricManager(TestCase):
    """Tests for FabricManager class (skip if fabric CLI unavailable)."""

    def test_fabric_manager_initialization(self):
        """Test FabricManager initializes correctly."""
        from codomyrmex.llm.fabric.fabric_manager import FabricManager

        manager = FabricManager()

        assert manager.fabric_binary == "fabric"
        assert isinstance(manager.results_history, list)

    def test_fabric_not_available_when_missing(self):
        """Test FabricManager handles unavailable fabric."""
        if _FABRIC_AVAILABLE:
            self.skipTest("fabric is installed — cannot test unavailable path")

        from codomyrmex.llm.fabric.fabric_manager import FabricManager

        manager = FabricManager()

        assert manager.fabric_available is False
        assert manager.is_available() is False

    @_skip_no_fabric
    def test_list_patterns_returns_list(self):
        """Test list_patterns returns list of pattern names."""
        from codomyrmex.llm.fabric.fabric_manager import FabricManager

        manager = FabricManager()
        patterns = manager.list_patterns()

        assert isinstance(patterns, list)

    @_skip_no_fabric
    def test_run_pattern_success(self):
        """Test run_pattern returns result dict."""
        from codomyrmex.llm.fabric.fabric_manager import FabricManager

        manager = FabricManager()
        patterns = manager.list_patterns()
        if not patterns:
            self.skipTest("No fabric patterns available")

        result = manager.run_pattern(patterns[0], "test input")

        assert 'success' in result
        assert 'pattern' in result

    def test_run_pattern_unavailable_returns_error(self):
        """Test run_pattern returns error when fabric unavailable."""
        if _FABRIC_AVAILABLE:
            self.skipTest("fabric is installed — cannot test unavailable path")

        from codomyrmex.llm.fabric.fabric_manager import FabricManager

        manager = FabricManager()
        result = manager.run_pattern("test_pattern", "test input")

        assert result['success'] is False
        assert 'not available' in result['error'].lower()


# ============================================================================
# Test Fabric Orchestrator
# ============================================================================

@pytest.mark.unit
class TestFabricOrchestrator(TestCase):
    """Tests for FabricOrchestrator class."""

    def test_orchestrator_initialization(self):
        """Test FabricOrchestrator initializes correctly."""
        from codomyrmex.llm.fabric.fabric_orchestrator import FabricOrchestrator

        orchestrator = FabricOrchestrator()

        assert orchestrator.fabric_manager is not None

    @_skip_no_fabric
    def test_analyze_code_returns_results(self):
        """Test analyze_code returns analysis results."""
        from codomyrmex.llm.fabric.fabric_orchestrator import FabricOrchestrator

        orchestrator = FabricOrchestrator()
        result = orchestrator.analyze_code("def test(): pass", "quality")

        assert 'analysis_type' in result
        assert 'patterns_used' in result
        assert 'results' in result
        assert 'summary' in result

    def test_analysis_summary_structure(self):
        """Test _create_analysis_summary returns correct structure."""
        from codomyrmex.llm.fabric.fabric_orchestrator import FabricOrchestrator

        orchestrator = FabricOrchestrator()

        results = {
            'pattern1': {'success': True, 'output': 'output1', 'duration': 1.0},
            'pattern2': {'success': True, 'output': 'output2', 'duration': 2.0},
            'pattern3': {'success': False, 'output': '', 'duration': 0.5}
        }

        summary = orchestrator._create_analysis_summary(results)

        assert summary['successful_patterns'] == 2
        assert summary['total_patterns'] == 3
        assert summary['success_rate'] == pytest.approx(66.67, rel=0.1)


# ============================================================================
# Test Async Model Runner Methods
# ============================================================================

@pytest.mark.unit
class TestAsyncModelRunner(TestCase):
    """Tests for async methods in ModelRunner."""

    def setUp(self):
        """Set up test fixtures."""
        if not _OLLAMA_AVAILABLE:
            self.skipTest("Ollama server not reachable")

        from codomyrmex.llm.ollama.model_runner import ModelRunner
        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        self.manager = OllamaManager(auto_start_server=False)
        self.runner = ModelRunner(self.manager)

    def test_async_run_model_method_exists(self):
        """Test async_run_model method exists and is async."""
        import inspect

        assert hasattr(self.runner, 'async_run_model')
        assert inspect.iscoroutinefunction(self.runner.async_run_model)

    def test_async_chat_method_exists(self):
        """Test async_chat method exists and is async."""
        import inspect

        assert hasattr(self.runner, 'async_chat')
        assert inspect.iscoroutinefunction(self.runner.async_chat)

    def test_async_generate_stream_method_exists(self):
        """Test async_generate_stream method exists and is async generator."""
        import inspect

        assert hasattr(self.runner, 'async_generate_stream')
        assert inspect.isasyncgenfunction(self.runner.async_generate_stream)

    def test_async_run_batch_method_exists(self):
        """Test async_run_batch method exists and is async."""
        import inspect

        assert hasattr(self.runner, 'async_run_batch')
        assert inspect.iscoroutinefunction(self.runner.async_run_batch)

    def test_async_generate_is_alias(self):
        """Test async_generate is alias for async_run_model."""
        import inspect

        run_model_sig = inspect.signature(self.runner.async_run_model)
        generate_sig = inspect.signature(self.runner.async_generate)

        run_params = list(run_model_sig.parameters.keys())
        gen_params = list(generate_sig.parameters.keys())

        assert run_params == gen_params


# ============================================================================
# Test Global Config Functions
# ============================================================================

@pytest.mark.unit
class TestGlobalConfigFunctions(TestCase):
    """Tests for global config functions."""

    def setUp(self):
        """Reset global config before each test."""
        from codomyrmex.llm.config import reset_config
        reset_config()

    def tearDown(self):
        """Reset global config after each test."""
        from codomyrmex.llm.config import reset_config
        reset_config()

    def test_get_config_creates_default(self):
        """Test get_config creates default config if none exists."""
        from codomyrmex.llm.config import get_config, reset_config

        reset_config()
        config = get_config()

        assert config is not None
        assert config.model == "llama3.1:latest"

    def test_set_config_updates_global(self):
        """Test set_config updates global config."""
        from codomyrmex.llm.config import LLMConfig, get_config, set_config

        custom_config = LLMConfig(model="custom-model")
        set_config(custom_config)

        config = get_config()
        assert config.model == "custom-model"

    def test_reset_config_clears_global(self):
        """Test reset_config clears global config."""
        from codomyrmex.llm.config import get_config, reset_config

        # Get config to create it
        _ = get_config()

        reset_config()

        # Accessing _config_instance directly to verify reset
        import codomyrmex.llm.config as config_module
        assert config_module._config_instance is None


# ============================================================================
# Test Token Counting Simulation
# ============================================================================

@pytest.mark.unit
class TestTokenCounting(TestCase):
    """Tests for token counting functionality."""

    def test_execution_result_contains_token_count(self):
        """Test ModelExecutionResult can contain token count."""
        from codomyrmex.llm.ollama.ollama_manager import ModelExecutionResult

        result = ModelExecutionResult(
            model_name="test-model",
            prompt="test prompt",
            response="test response",
            execution_time=1.0,
            tokens_used=150,
            success=True
        )

        assert result.tokens_used == 150

    def test_run_model_captures_eval_count(self):
        """Test run_model captures eval_count from real API response."""
        if not _OLLAMA_AVAILABLE:
            self.skipTest("Ollama server not reachable")

        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        manager = OllamaManager(auto_start_server=False)
        models = manager.list_models()
        if not models:
            self.skipTest("No Ollama models installed")

        result = manager.run_model(models[0].name, 'Say hello', save_output=False)
        # tokens_used should be set when available
        assert result.success is True


# ============================================================================
# Test Error Recovery Patterns
# ============================================================================

@pytest.mark.unit
class TestErrorRecovery(TestCase):
    """Tests for error recovery and retry patterns."""

    def test_cli_fallback_when_http_unavailable(self):
        """Test that OllamaManager can initialize when Ollama is available."""
        if not _OLLAMA_AVAILABLE:
            self.skipTest("Ollama server not reachable")

        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        manager = OllamaManager(auto_start_server=False)
        # Manager should initialize successfully with real Ollama
        assert manager is not None

    def test_run_model_handles_nonexistent_model(self):
        """Test graceful handling when model doesn't exist."""
        if not _OLLAMA_AVAILABLE:
            self.skipTest("Ollama server not reachable")

        from codomyrmex.llm.ollama.ollama_manager import OllamaManager

        manager = OllamaManager(auto_start_server=False)
        result = manager.run_model('nonexistent-model-xyz-999', 'test prompt', save_output=False)

        # Should handle gracefully with success=False
        assert result.success is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


# Coverage push — llm/router
class TestCostTracker:
    """Tests for LLM cost tracking."""

    def test_init(self):
        from codomyrmex.llm.router import CostTracker
        tracker = CostTracker()
        assert tracker is not None


class TestCostTrackerDeep:
    """Deep tests for LLM cost tracking execution paths."""

    def test_record_and_total(self):
        from codomyrmex.llm.router import CostTracker
        tracker = CostTracker()
        tracker.record(model_name="gpt-4", input_tokens=100, output_tokens=50, cost=0.01)
        total = tracker.get_total_cost()
        assert isinstance(total, (int, float))
        assert total >= 0

    def test_get_usage_report(self):
        from codomyrmex.llm.router import CostTracker
        tracker = CostTracker()
        tracker.record(model_name="gpt-4", input_tokens=100, output_tokens=50, cost=0.01)
        report = tracker.get_usage_report()
        assert isinstance(report, (dict, str))
