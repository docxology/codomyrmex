import json
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from codomyrmex.llm.ollama import (
        ModelRunner,
        OllamaAttributes,
        OllamaManager,
        OllamaModel,
        OllamaResponse,
        OllamaRunner,
    )
    from codomyrmex.llm.ollama.config_manager import ConfigManager
    from codomyrmex.llm.ollama.model_runner import ExecutionOptions
    from codomyrmex.llm.ollama.output_manager import OutputManager
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    OllamaManager = None
    ModelRunner = None
    OllamaAttributes = None
    OllamaModel = None
    OllamaResponse = None
    OllamaRunner = None
    ExecutionOptions = None
    OutputManager = None
    ConfigManager = None

"""
Test Utilities and Helpers for Ollama Integration Tests

Provides reusable utilities, fixtures, and helpers for comprehensive
Ollama integration testing. All utilities use real Ollama API calls (no mocks).
"""

@dataclass
class TestModel:
    """Test model information."""
    name: str
    description: str
    recommended_for: list[str]  # e.g., ["quick_tests", "parameter_tests"]


# Common test models (smaller models for faster tests)
TEST_MODELS = [
    TestModel(
        name="gemma3:4b",
        description="Small model for quick tests",
        recommended_for=["quick_tests", "parameter_tests", "integration_tests"]
    ),
    TestModel(
        name="llama3:latest",
        description="Standard model for general tests",
        recommended_for=["general_tests", "execution_tests"]
    ),
]


class OllamaTestFixture:
    """
    Test fixture providing initialized managers and test utilities.

    Purpose: Centralize test setup and provide consistent test environment
    Context: Used by all Ollama integration tests to ensure consistent initialization
    """

    def __init__(
        self,
        use_http_api: bool = True,
        output_dir: str | None = None,
        auto_cleanup: bool = True
    ):
        """
        Initialize test fixture.

        Args:
            use_http_api: Whether to use HTTP API (default: True)
            output_dir: Custom output directory (default: temp directory)
            auto_cleanup: Whether to cleanup on exit (default: True)
        """
        if not OLLAMA_AVAILABLE:
            raise ImportError("Ollama integration not available")

        self.use_http_api = use_http_api
        self.auto_cleanup = auto_cleanup

        # Create temporary output directory if not provided
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.temp_dir = tempfile.mkdtemp(prefix="ollama_test_")
            self.output_dir = Path(self.temp_dir)

        # Initialize managers
        self.manager = OllamaManager(use_http_api=use_http_api)
        self.runner = ModelRunner(self.manager)
        self.output_manager = OutputManager(str(self.output_dir))
        self.config_manager = ConfigManager()

        # Test data
        self.test_prompts = [
            "What is artificial intelligence?",
            "Explain machine learning in simple terms.",
            "Write a Python function to calculate fibonacci numbers.",
            "What are the benefits of using local LLMs?",
        ]

    def get_available_model(self, preferred: str | None = None) -> str | None:
        """
        Get an available model for testing.

        Purpose: Find a model that's actually available for testing
        Context: Tests need real models, but availability varies

        Args:
            preferred: Preferred model name (will use if available)

        Returns:
            Model name if available, None otherwise
        """
        if preferred and self.manager.is_model_available(preferred):
            return preferred

        # Try test models in order
        for test_model in TEST_MODELS:
            if self.manager.is_model_available(test_model.name):
                return test_model.name

        # Fall back to any available model
        models = self.manager.list_models()
        if models:
            return models[0].name

        return None

    def cleanup(self):
        """Clean up test resources."""
        if self.auto_cleanup and hasattr(self, 'temp_dir'):
            if Path(self.temp_dir).exists():
                shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestDataGenerator:
    """
    Generate test data for Ollama tests.

    Purpose: Provide consistent test data across all tests
    Context: Ensures tests use realistic, varied data
    """

    @staticmethod
    def simple_prompts() -> list[str]:
        """Generate simple test prompts."""
        return [
            "Hello, how are you?",
            "What is Python?",
            "Explain recursion.",
        ]

    @staticmethod
    def code_generation_prompts() -> list[str]:
        """Generate code generation test prompts."""
        return [
            "Write a Python function to reverse a string.",
            "Create a JavaScript function to find the maximum value in an array.",
            "Write a SQL query to find all users with age > 25.",
        ]

    @staticmethod
    def analysis_prompts() -> list[str]:
        """Generate analysis test prompts."""
        return [
            "Analyze the benefits and drawbacks of microservices architecture.",
            "Compare Python and JavaScript for web development.",
            "What are the key considerations for choosing a database?",
        ]

    @staticmethod
    def conversation_prompts() -> list[dict[str, str]]:
        """Generate conversation-style test prompts."""
        return [
            {"role": "user", "content": "What is machine learning?"},
            {"role": "assistant", "content": "Machine learning is..."},
            {"role": "user", "content": "Can you give me an example?"},
        ]

    @staticmethod
    def execution_options_variations() -> list[ExecutionOptions]:
        """Generate various execution option configurations."""
        return [
            ExecutionOptions(temperature=0.1, max_tokens=100),  # Fast, deterministic
            ExecutionOptions(temperature=0.7, max_tokens=500),  # Balanced
            ExecutionOptions(temperature=0.9, max_tokens=1000),  # Creative
            ExecutionOptions(top_p=0.5, top_k=20),  # Narrow sampling
            ExecutionOptions(top_p=0.95, top_k=100),  # Wide sampling
            ExecutionOptions(repeat_penalty=1.0),  # No penalty
            ExecutionOptions(repeat_penalty=1.2),  # High penalty
            ExecutionOptions(format="json"),  # JSON output
            ExecutionOptions(system_prompt="You are a helpful coding assistant."),  # System prompt
            ExecutionOptions(context_window=32768),  # Large context
        ]


class AssertionHelpers:
    """
    Custom assertion helpers for Ollama tests.

    Purpose: Provide domain-specific assertions for clearer test failures
    Context: Makes test failures more informative and easier to debug
    """

    @staticmethod
    def assert_model_execution_success(result: Any, model_name: str = ""):
        """
        Assert that model execution was successful.

        Purpose: Verify execution completed successfully
        Context: Used in all execution tests

        Args:
            result: ModelExecutionResult object
            model_name: Model name for error messages
        """
        assert result is not None, f"Execution result is None for {model_name}"
        assert result.success, f"Execution failed for {model_name}: {result.error_message}"
        assert result.response is not None, f"Response is None for {model_name}"
        assert len(result.response) > 0, f"Response is empty for {model_name}"
        assert result.execution_time > 0, f"Execution time is invalid for {model_name}"

    @staticmethod
    def assert_model_available(manager: OllamaManager, model_name: str):
        """
        Assert that a model is available.

        Purpose: Verify model can be used
        Context: Used before execution tests

        Args:
            manager: OllamaManager instance
            model_name: Model name to check
        """
        assert manager.is_model_available(model_name), \
            f"Model {model_name} is not available. Available models: {[m.name for m in manager.list_models()]}"

    @staticmethod
    def assert_valid_execution_options(options: ExecutionOptions):
        """
        Assert that execution options are valid.

        Purpose: Verify options are within acceptable ranges
        Context: Used in configuration tests

        Args:
            options: ExecutionOptions object
        """
        assert 0.0 <= options.temperature <= 2.0, f"Temperature out of range: {options.temperature}"
        assert 0.0 <= options.top_p <= 1.0, f"Top P out of range: {options.top_p}"
        assert options.top_k >= 1, f"Top K must be >= 1: {options.top_k}"
        assert options.repeat_penalty >= 1.0, f"Repeat penalty must be >= 1.0: {options.repeat_penalty}"
        assert options.max_tokens > 0, f"Max tokens must be > 0: {options.max_tokens}"

    @staticmethod
    def assert_output_saved(output_manager: OutputManager, model_name: str):
        """
        Assert that output was saved correctly.

        Purpose: Verify output management works
        Context: Used in output management tests

        Args:
            output_manager: OutputManager instance
            model_name: Model name to check
        """
        stats = output_manager.get_output_stats()
        assert stats['total_outputs'] > 0, "No outputs were saved"
        assert stats['total_size'] > 0, "Output size is invalid"


class ModelAvailabilityChecker:
    """
    Check model availability and provide fallback strategies.

    Purpose: Handle model availability gracefully in tests
    Context: Models may not always be available, tests should handle this
    """

    def __init__(self, manager: OllamaManager):
        """Initialize with OllamaManager."""
        self.manager = manager
        self._available_models_cache = None

    def get_available_models(self, force_refresh: bool = False) -> list[str]:
        """
        Get list of available model names.

        Args:
            force_refresh: Force refresh of model list

        Returns:
            List of available model names
        """
        if force_refresh or self._available_models_cache is None:
            models = self.manager.list_models(force_refresh=force_refresh)
            self._available_models_cache = [m.name for m in models]
        return self._available_models_cache

    def find_suitable_model(self, requirements: list[str] = None) -> str | None:
        """
        Find a model suitable for testing.

        Purpose: Select best available model for tests
        Context: Different tests may need different model characteristics

        Args:
            requirements: List of requirements (e.g., ["small", "fast"])

        Returns:
            Suitable model name or None
        """
        available = self.get_available_models()

        if not available:
            return None

        # If no requirements, return first available
        if not requirements:
            return available[0]

        # Try to match requirements
        for model_name in available:
            # Simple matching logic (can be enhanced)
            if "small" in requirements and "4b" in model_name.lower():
                return model_name
            if "fast" in requirements and any(x in model_name.lower() for x in ["4b", "7b", "8b"]):
                return model_name

        # Fallback to first available
        return available[0]

    def ensure_model_available(self, model_name: str, timeout: int = 300) -> bool:
        """
        Ensure a model is available, pulling if necessary.

        Purpose: Make model available for testing
        Context: Tests may need specific models

        Args:
            model_name: Model name to ensure
            timeout: Timeout in seconds for pull operation

        Returns:
            True if model is available, False otherwise
        """
        if self.manager.is_model_available(model_name):
            return True

        # Attempt to pull
        print(f"Model {model_name} not available, attempting to pull...")
        start_time = time.time()
        success = self.manager.download_model(model_name)

        if success and (time.time() - start_time) < timeout:
            # Wait a bit for model to register
            time.sleep(2)
            return self.manager.is_model_available(model_name)

        return False


def create_test_config(output_dir: Path) -> dict[str, Any]:
    """
    Create a test configuration file.

    Purpose: Generate test configuration for configuration tests
    Context: Tests need valid configuration files

    Args:
        output_dir: Directory to save config

    Returns:
        Configuration dictionary
    """
    config = {
        "default_model": "gemma3:4b",
        "preferred_models": ["gemma3:4b", "llama3:latest"],
        "execution_defaults": {
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 0.9,
        },
        "output_settings": {
            "save_all_outputs": True,
            "base_output_dir": str(output_dir),
        }
    }

    config_path = output_dir / "test_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    return config


def cleanup_test_resources(path: Path):
    """
    Clean up test resources.

    Purpose: Remove test artifacts after tests
    Context: Keep test environment clean

    Args:
        path: Path to clean up
    """
    if path.exists():
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path, ignore_errors=True)
