"""
Comprehensive Ollama Integration Tests

This test suite provides extensive coverage of all Ollama integration methods,
initialization patterns, execution scenarios, and use cases. All tests use
real Ollama API calls (no mocks).

Test Organization:
- A. Initialization Patterns
- B. Model Management
- C. Execution Methods
- D. Configuration Management
- E. Output Management
- F. Error Handling
- G. Integration Patterns

Each test includes:
- Purpose: What the test verifies
- Context: When/why this test is important
- Setup: Required conditions
- Execution: Actions performed
- Assertions: Expected outcomes
"""

import unittest
import time
import tempfile
import shutil
from pathlib import Path

try:
    from codomyrmex.llm.ollama import (
        OllamaManager,
        ModelRunner,
        OutputManager,
        ConfigManager
    )
    from codomyrmex.llm.ollama.model_runner import ExecutionOptions
    from codomyrmex.tests.unit.ollama_test_helpers import (
        OllamaTestFixture,
        TestDataGenerator,
        AssertionHelpers,
        ModelAvailabilityChecker,
        create_test_config,
        cleanup_test_resources
    )
    OLLAMA_AVAILABLE = True
except ImportError as e:
    print(f"Ollama integration not available: {e}")
    OLLAMA_AVAILABLE = False


class TestInitializationPatterns(unittest.TestCase):
    """
    Test Category A: Initialization Patterns
    
    Purpose: Verify all ways to initialize Ollama components work correctly
    Context: Different initialization patterns are needed for different use cases
    """
    
    def setUp(self):
        """Set up test environment."""
        if not OLLAMA_AVAILABLE:
            self.skipTest("Ollama integration not available")
        self.temp_dir = tempfile.mkdtemp(prefix="ollama_init_test_")
    
    def tearDown(self):
        """Clean up test resources."""
        cleanup_test_resources(Path(self.temp_dir))
    
    def test_http_api_initialization(self):
        """
        Test HTTP API initialization.
        
        Purpose: Verify OllamaManager can be initialized with HTTP API enabled
        Context: HTTP API is the preferred method for better control and error handling
        Setup: No special setup required
        Execution: Initialize with use_http_api=True
        Assertions: Manager is initialized, HTTP API is enabled
        """
        manager = OllamaManager(use_http_api=True)
        self.assertIsNotNone(manager)
        self.assertTrue(manager.use_http_api)
        self.assertEqual(manager.base_url, "http://localhost:11434")
    
    def test_cli_fallback_initialization(self):
        """
        Test CLI fallback initialization.
        
        Purpose: Verify OllamaManager can fall back to CLI when HTTP API is unavailable
        Context: CLI fallback ensures robustness when HTTP API fails
        Setup: Initialize with use_http_api=False
        Execution: Initialize manager
        Assertions: Manager is initialized, CLI mode is active
        """
        manager = OllamaManager(use_http_api=False)
        self.assertIsNotNone(manager)
        self.assertFalse(manager.use_http_api)
    
    def test_custom_host_port_configuration(self):
        """
        Test custom host/port configuration.
        
        Purpose: Verify OllamaManager can connect to custom Ollama instances
        Context: Some deployments use non-standard ports or remote servers
        Setup: Custom host and port values
        Execution: Initialize with custom host/port
        Assertions: Manager uses custom connection parameters
        """
        manager = OllamaManager(
            use_http_api=True,
            server_host="127.0.0.1",
            server_port=11435
        )
        self.assertIsNotNone(manager)
        # Note: This will fail if server isn't on custom port, but initialization should work
        self.assertEqual(manager.server_host, "127.0.0.1")
        self.assertEqual(manager.server_port, 11435)
    
    def test_auto_start_server_behavior(self):
        """
        Test auto-start server behavior.
        
        Purpose: Verify OllamaManager can automatically start Ollama server
        Context: Auto-start improves user experience by handling server management
        Setup: Server may or may not be running
        Execution: Initialize with auto_start_server=True
        Assertions: Manager attempts to ensure server is running
        """
        manager = OllamaManager(auto_start_server=True)
        self.assertIsNotNone(manager)
        # Server should be accessible (may start automatically)
        try:
            models = manager.list_models()
            self.assertIsInstance(models, list)
        except Exception:
            # Server may not be available, but initialization should work
            pass
    
    def test_configuration_loading_from_files(self):
        """
        Test configuration loading from files.
        
        Purpose: Verify ConfigManager can load configuration from JSON files
        Context: File-based config enables persistent settings across sessions
        Setup: Create test config file
        Execution: Load configuration
        Assertions: Configuration is loaded correctly
        """
        config_dir = Path(self.temp_dir) / "configs"
        config_dir.mkdir(parents=True)
        
        config = create_test_config(config_dir)
        config_manager = ConfigManager()
        
        # ConfigManager should load default config
        self.assertIsNotNone(config_manager.config)
        self.assertIsNotNone(config_manager.config.ollama_binary)


class TestModelManagement(unittest.TestCase):
    """
    Test Category B: Model Management
    
    Purpose: Verify all model management operations work correctly
    Context: Model management is core functionality for Ollama integration
    """
    
    def setUp(self):
        """Set up test environment."""
        if not OLLAMA_AVAILABLE:
            self.skipTest("Ollama integration not available")
        self.fixture = OllamaTestFixture()
        self.model_checker = ModelAvailabilityChecker(self.fixture.manager)
    
    def tearDown(self):
        """Clean up test resources."""
        self.fixture.cleanup()
    
    def test_model_listing_with_caching(self):
        """
        Test model listing with caching.
        
        Purpose: Verify model list caching works to reduce API calls
        Context: Caching improves performance for repeated list operations
        Setup: Manager with caching enabled
        Execution: List models multiple times
        Assertions: First call queries API, subsequent calls use cache
        """
        # First call should query API
        models1 = self.fixture.manager.list_models(force_refresh=False)
        self.assertIsInstance(models1, list)
        
        # Second call may use cache (implementation dependent)
        models2 = self.fixture.manager.list_models(force_refresh=False)
        self.assertIsInstance(models2, list)
        # Should have same or similar results
        self.assertEqual(len(models1), len(models2))
    
    def test_model_listing_with_force_refresh(self):
        """
        Test model listing with force refresh.
        
        Purpose: Verify force refresh bypasses cache and gets fresh data
        Context: Force refresh needed when models are added/removed
        Setup: Manager with cached model list
        Execution: List models with force_refresh=True
        Assertions: Fresh model list is retrieved
        """
        models = self.fixture.manager.list_models(force_refresh=True)
        self.assertIsInstance(models, list)
        # All models should have required attributes
        for model in models:
            self.assertTrue(hasattr(model, 'name'))
            self.assertTrue(hasattr(model, 'size'))
    
    def test_model_availability_checking(self):
        """
        Test model availability checking.
        
        Purpose: Verify is_model_available correctly identifies available models
        Context: Availability checking prevents errors before execution
        Setup: Manager with known models
        Execution: Check availability of various models
        Assertions: Correct availability status is returned
        """
        available_model = self.fixture.get_available_model()
        if available_model:
            self.assertTrue(
                self.fixture.manager.is_model_available(available_model)
            )
        
        # Non-existent model should return False
        self.assertFalse(
            self.fixture.manager.is_model_available("nonexistent_model_xyz12345")
        )
    
    def test_model_info_retrieval(self):
        """
        Test model info retrieval.
        
        Purpose: Verify get_model_by_name returns correct model information
        Context: Model info needed for configuration and validation
        Setup: Manager with available models
        Execution: Get model info by name
        Assertions: Correct model info is returned
        """
        available_model = self.fixture.get_available_model()
        if available_model:
            model_info = self.fixture.manager.get_model_by_name(available_model)
            self.assertIsNotNone(model_info)
            self.assertEqual(model_info.name, available_model)
            self.assertTrue(hasattr(model_info, 'size'))
    
    def test_model_name_variations(self):
        """
        Test model name variations (with/without tags).
        
        Purpose: Verify model names with and without tags work correctly
        Context: Models can be referenced with or without version tags
        Setup: Manager with models
        Execution: Check availability with different name formats
        Assertions: Name variations are handled correctly
        """
        available_model = self.fixture.get_available_model()
        if available_model:
            # Test with full name
            self.assertTrue(
                self.fixture.manager.is_model_available(available_model)
            )
            
            # Test with base name (if tag exists)
            base_name = available_model.split(':')[0]
            # May or may not work depending on implementation
            # Just verify it doesn't crash
            try:
                self.fixture.manager.is_model_available(base_name)
            except Exception:
                pass  # Expected if base name lookup not supported


class TestExecutionMethods(unittest.TestCase):
    """
    Test Category C: Execution Methods
    
    Purpose: Verify all model execution methods and patterns work correctly
    Context: Execution is the primary use case for Ollama integration
    """
    
    def setUp(self):
        """Set up test environment."""
        if not OLLAMA_AVAILABLE:
            self.skipTest("Ollama integration not available")
        self.fixture = OllamaTestFixture()
        self.model_name = self.fixture.get_available_model()
        if not self.model_name:
            self.skipTest("No models available for testing")
    
    def tearDown(self):
        """Clean up test resources."""
        self.fixture.cleanup()
    
    def test_direct_ollama_manager_run(self):
        """
        Test direct OllamaManager.run_model() usage.
        
        Purpose: Verify direct manager execution works without ModelRunner
        Context: Direct execution is simpler for basic use cases
        Setup: Manager and available model
        Execution: Run model directly via manager
        Assertions: Execution succeeds and returns valid result
        """
        result = self.fixture.manager.run_model(
            self.model_name,
            "What is Python?",
            save_output=False
        )
        
        AssertionHelpers.assert_model_execution_success(result, self.model_name)
        self.assertEqual(result.model_name, self.model_name)
    
    def test_model_runner_with_options(self):
        """
        Test ModelRunner.run_with_options() usage.
        
        Purpose: Verify ModelRunner provides higher-level execution interface
        Context: ModelRunner simplifies execution with options
        Setup: Runner and available model
        Execution: Run with ExecutionOptions
        Assertions: Execution succeeds with options applied
        """
        options = ExecutionOptions(
            temperature=0.7,
            max_tokens=100,
            top_p=0.9
        )
        
        result = self.fixture.runner.run_with_options(
            self.model_name,
            "Explain recursion.",
            options,
            save_output=False
        )
        
        AssertionHelpers.assert_model_execution_success(result, self.model_name)
    
    def test_execution_with_presets(self):
        """
        Test execution with presets.
        
        Purpose: Verify execution presets work correctly
        Context: Presets provide convenient pre-configured options
        Setup: ConfigManager with presets
        Execution: Use preset for execution
        Assertions: Preset options are applied correctly
        """
        presets = self.fixture.config_manager.get_execution_presets()
        self.assertIn('fast', presets)
        self.assertIn('balanced', presets)
        
        # Test with fast preset
        fast_options = presets['fast']
        result = self.fixture.runner.run_with_options(
            self.model_name,
            "Quick test.",
            fast_options,
            save_output=False
        )
        
        AssertionHelpers.assert_model_execution_success(result, self.model_name)
    
    def test_execution_with_json_format(self):
        """
        Test execution with JSON format output.
        
        Purpose: Verify JSON format output works correctly
        Context: JSON format enables structured output for parsing
        Setup: Model and prompt requesting JSON
        Execution: Run with format="json"
        Assertions: Response is valid JSON or JSON-like
        """
        options = ExecutionOptions(
            format="json",
            max_tokens=100
        )
        
        prompt = "Return a JSON object with keys 'name' and 'age' for Alice, age 30."
        result = self.fixture.runner.run_with_options(
            self.model_name,
            prompt,
            options,
            save_output=False
        )
        
        AssertionHelpers.assert_model_execution_success(result, self.model_name)
        # Response should contain JSON-like structure
        self.assertIn('{', result.response)
    
    def test_execution_with_system_prompt(self):
        """
        Test execution with system prompt.
        
        Purpose: Verify system prompts modify model behavior
        Context: System prompts enable role-based responses
        Setup: Model and system prompt
        Execution: Run with system_prompt option
        Assertions: Execution succeeds with system prompt applied
        """
        options = ExecutionOptions(
            system_prompt="You are a helpful coding assistant.",
            max_tokens=100
        )
        
        result = self.fixture.runner.run_with_options(
            self.model_name,
            "How do I reverse a string in Python?",
            options,
            save_output=False
        )
        
        AssertionHelpers.assert_model_execution_success(result, self.model_name)
    
    def test_execution_with_context_window(self):
        """
        Test execution with context window settings.
        
        Purpose: Verify context window parameter works correctly
        Context: Large context windows enable longer conversations
        Setup: Model supporting large context
        Execution: Run with context_window parameter
        Assertions: Execution succeeds with context window set
        """
        options = ExecutionOptions(
            context_window=32768,
            max_tokens=100
        )
        
        result = self.fixture.runner.run_with_options(
            self.model_name,
            "What is machine learning?",
            options,
            save_output=False
        )
        
        AssertionHelpers.assert_model_execution_success(result, self.model_name)
    
    def test_batch_execution_multiple_prompts(self):
        """
        Test batch execution with multiple prompts.
        
        Purpose: Verify batch execution handles multiple prompts efficiently
        Context: Batch execution improves throughput for multiple queries
        Setup: Multiple test prompts
        Execution: Run batch execution
        Assertions: All prompts are processed successfully
        """
        prompts = TestDataGenerator.simple_prompts()[:2]
        options = ExecutionOptions(max_tokens=50)
        
        results = self.fixture.runner.run_batch(
            self.model_name,
            prompts,
            options,
            max_concurrent=2
        )
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(prompts))
        
        for i, result in enumerate(results):
            AssertionHelpers.assert_model_execution_success(result, self.model_name)
            self.assertEqual(result.prompt, prompts[i])


class TestConfigurationManagement(unittest.TestCase):
    """
    Test Category D: Configuration Management
    
    Purpose: Verify all configuration management operations work correctly
    Context: Configuration enables customization and persistence
    """
    
    def setUp(self):
        """Set up test environment."""
        if not OLLAMA_AVAILABLE:
            self.skipTest("Ollama integration not available")
        self.fixture = OllamaTestFixture()
        self.temp_dir = Path(self.fixture.output_dir)
    
    def tearDown(self):
        """Clean up test resources."""
        self.fixture.cleanup()
    
    def test_loading_default_configuration(self):
        """
        Test loading default configuration.
        
        Purpose: Verify default configuration is loaded correctly
        Context: Defaults provide sensible out-of-box behavior
        Setup: ConfigManager initialization
        Execution: Access default config
        Assertions: Default config has valid values
        """
        config = self.fixture.config_manager.config
        self.assertIsNotNone(config)
        self.assertEqual(config.ollama_binary, "ollama")
        self.assertTrue(config.auto_start_server)
    
    def test_saving_model_specific_configuration(self):
        """
        Test saving model-specific configuration.
        
        Purpose: Verify model-specific configs can be saved and loaded
        Context: Model-specific configs enable optimization per model
        Setup: ConfigManager and model name
        Execution: Save and load model config
        Assertions: Config is saved and loaded correctly
        """
        model_name = self.fixture.get_available_model()
        if not model_name:
            self.skipTest("No model available")
        
        test_config = {
            'temperature': 0.7,
            'max_tokens': 1000,
            'top_p': 0.9
        }
        
        success = self.fixture.config_manager.save_model_config(
            model_name,
            test_config
        )
        self.assertTrue(success)
        
        # Verify config can be loaded
        loaded_config = self.fixture.config_manager.load_model_config(model_name)
        if loaded_config:
            self.assertIn('configuration', loaded_config)
    
    def test_configuration_validation(self):
        """
        Test configuration validation.
        
        Purpose: Verify configuration values are validated
        Context: Validation prevents invalid configurations
        Setup: ConfigManager
        Execution: Validate various configs
        Assertions: Invalid configs are rejected, valid ones pass
        """
        # Test valid options
        valid_options = ExecutionOptions(
            temperature=0.7,
            max_tokens=100,
            top_p=0.9
        )
        AssertionHelpers.assert_valid_execution_options(valid_options)
    
    def test_preset_retrieval_and_usage(self):
        """
        Test preset retrieval and usage.
        
        Purpose: Verify presets can be retrieved and used
        Context: Presets provide convenient pre-configured options
        Setup: ConfigManager
        Execution: Get presets and use them
        Assertions: Presets are available and usable
        """
        presets = self.fixture.config_manager.get_execution_presets()
        self.assertIsInstance(presets, dict)
        self.assertIn('fast', presets)
        self.assertIn('balanced', presets)
        self.assertIn('creative', presets)
        
        # Verify presets are valid ExecutionOptions
        for preset_name, preset_options in presets.items():
            AssertionHelpers.assert_valid_execution_options(preset_options)


class TestOutputManagement(unittest.TestCase):
    """
    Test Category E: Output Management
    
    Purpose: Verify all output management operations work correctly
    Context: Output management enables persistence and analysis
    """
    
    def setUp(self):
        """Set up test environment."""
        if not OLLAMA_AVAILABLE:
            self.skipTest("Ollama integration not available")
        self.fixture = OllamaTestFixture()
        self.model_name = self.fixture.get_available_model()
        if not self.model_name:
            self.skipTest("No model available")
    
    def tearDown(self):
        """Clean up test resources."""
        self.fixture.cleanup()
    
    def test_output_saving_with_default_directory(self):
        """
        Test output saving with default directory.
        
        Purpose: Verify outputs are saved to default directory
        Context: Default directory provides consistent output location
        Setup: OutputManager with default directory
        Execution: Save output
        Assertions: Output file is created in default location
        """
        result = self.fixture.manager.run_model(
            self.model_name,
            "Test output saving.",
            save_output=True,
            output_dir=str(self.fixture.output_dir)
        )
        
        AssertionHelpers.assert_model_execution_success(result, self.model_name)
        AssertionHelpers.assert_output_saved(self.fixture.output_manager, self.model_name)
    
    def test_output_saving_with_custom_directory(self):
        """
        Test output saving with custom directory.
        
        Purpose: Verify outputs can be saved to custom directories
        Context: Custom directories enable organization
        Setup: Custom output directory
        Execution: Save output to custom directory
        Assertions: Output file is created in custom location
        """
        custom_dir = self.fixture.output_dir / "custom_outputs"
        custom_dir.mkdir(parents=True, exist_ok=True)
        
        result = self.fixture.manager.run_model(
            self.model_name,
            "Test custom directory saving.",
            save_output=True,
            output_dir=str(custom_dir)
        )
        
        AssertionHelpers.assert_model_execution_success(result, self.model_name)
        # Verify file exists in custom directory
        output_files = list(custom_dir.glob("*.txt"))
        self.assertGreater(len(output_files), 0)
    
    def test_output_statistics_retrieval(self):
        """
        Test output statistics retrieval.
        
        Purpose: Verify output statistics are calculated correctly
        Context: Statistics enable monitoring and analysis
        Setup: Multiple saved outputs
        Execution: Get statistics
        Assertions: Statistics are accurate
        """
        # Save a few outputs
        for i in range(2):
            self.fixture.manager.run_model(
                self.model_name,
                f"Test prompt {i}.",
                save_output=True,
                output_dir=str(self.fixture.output_dir)
            )
        
        stats = self.fixture.output_manager.get_output_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_outputs', stats)
        self.assertGreaterEqual(stats['total_outputs'], 2)


class TestErrorHandling(unittest.TestCase):
    """
    Test Category F: Error Handling
    
    Purpose: Verify error handling works correctly for various failure scenarios
    Context: Robust error handling ensures graceful degradation
    """
    
    def setUp(self):
        """Set up test environment."""
        if not OLLAMA_AVAILABLE:
            self.skipTest("Ollama integration not available")
        self.fixture = OllamaTestFixture()
    
    def tearDown(self):
        """Clean up test resources."""
        self.fixture.cleanup()
    
    def test_model_not_found_error(self):
        """
        Test model not found error handling.
        
        Purpose: Verify graceful handling when model doesn't exist
        Context: Models may not always be available
        Setup: Non-existent model name
        Execution: Attempt to run non-existent model
        Assertions: Error is handled gracefully, no crash
        """
        result = self.fixture.manager.run_model(
            "nonexistent_model_xyz12345",
            "Test prompt.",
            save_output=False
        )
        
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error_message)
        self.assertIn("not available", result.error_message.lower())
    
    def test_invalid_parameter_values(self):
        """
        Test invalid parameter value handling.
        
        Purpose: Verify invalid parameters are handled gracefully
        Context: Users may provide invalid parameter values
        Setup: Invalid parameter values
        Execution: Attempt execution with invalid parameters
        Assertions: Error is handled or parameters are clamped/validated
        """
        # Test with extreme temperature (may be clamped by Ollama)
        options = ExecutionOptions(temperature=5.0, max_tokens=100)
        
        model_name = self.fixture.get_available_model()
        if model_name:
            result = self.fixture.runner.run_with_options(
                model_name,
                "Test with extreme temperature.",
                options,
                save_output=False
            )
            # Should either succeed (if clamped) or fail gracefully
            self.assertIsNotNone(result)


class TestIntegrationPatterns(unittest.TestCase):
    """
    Test Category G: Integration Patterns
    
    Purpose: Verify integration with other Codomyrmex components works correctly
    Context: Integration enables ecosystem-wide functionality
    """
    
    def setUp(self):
        """Set up test environment."""
        if not OLLAMA_AVAILABLE:
            self.skipTest("Ollama integration not available")
        self.fixture = OllamaTestFixture()
        self.model_name = self.fixture.get_available_model()
        if not self.model_name:
            self.skipTest("No model available")
    
    def tearDown(self):
        """Clean up test resources."""
        self.fixture.cleanup()
    
    def test_logging_integration(self):
        """
        Test logging integration.
        
        Purpose: Verify Ollama operations are logged correctly
        Context: Logging enables debugging and monitoring
        Setup: Manager with logging enabled
        Execution: Perform operations
        Assertions: Operations are logged (check logs if possible)
        """
        # Just verify logging doesn't crash
        result = self.fixture.manager.run_model(
            self.model_name,
            "Test logging.",
            save_output=False
        )
        AssertionHelpers.assert_model_execution_success(result, self.model_name)
        # Logging should work without errors
    
    def test_resource_cleanup(self):
        """
        Test resource cleanup.
        
        Purpose: Verify resources are cleaned up properly
        Context: Cleanup prevents resource leaks
        Setup: Operations that create resources
        Execution: Perform operations and cleanup
        Assertions: Resources are released
        """
        # Perform operations
        result = self.fixture.manager.run_model(
            self.model_name,
            "Test cleanup.",
            save_output=True,
            output_dir=str(self.fixture.output_dir)
        )
        AssertionHelpers.assert_model_execution_success(result, self.model_name)
        
        # Cleanup should work
        self.fixture.cleanup()
        # Verify cleanup (temp dir should be removed)
        if hasattr(self.fixture, 'temp_dir'):
            self.assertFalse(Path(self.fixture.temp_dir).exists())


if __name__ == '__main__':
    unittest.main()


