"""
Ollama Manager - Main integration class for Codomyrmex

Provides comprehensive Ollama model management, execution, and integration
with the Codomyrmex ecosystem.
"""

import asyncio
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Optional

from codomyrmex.logging_monitoring import get_logger


@dataclass
class OllamaModel:
    """Represents an Ollama model with metadata."""
    name: str
    id: str
    size: int  # Size in bytes
    modified: str
    parameters: Optional[str] = None
    family: Optional[str] = None
    format: Optional[str] = None
    status: str = "available"


@dataclass
class ModelExecutionResult:
    """Result of a model execution."""
    model_name: str
    prompt: str
    response: str
    execution_time: float
    tokens_used: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class OllamaManager:
    """
    Main Ollama integration manager for Codomyrmex.

    Provides comprehensive model management, execution, and output handling
    with seamless integration into the Codomyrmex ecosystem.
    """

    def __init__(self, ollama_binary: str = "ollama", auto_start_server: bool = True):
        """
        Initialize the Ollama manager.

        Args:
            ollama_binary: Path to ollama binary (default: "ollama")
            auto_start_server: Whether to automatically start Ollama server if not running
        """
        self.ollama_binary = ollama_binary
        self.auto_start_server = auto_start_server
        self.logger = get_logger(__name__)
        self.server_process = None
        self._ensure_server_running()

        # Initialize sub-managers
        self.output_manager = None  # Will be set after import
        self.config_manager = None  # Will be set after import

        # Import and initialize sub-managers
        self._initialize_sub_managers()

        # Model cache
        self._models_cache: Optional[list[OllamaModel]] = None
        self._cache_timestamp: Optional[float] = None
        self._cache_ttl = 30  # Cache for 30 seconds

    def _ensure_server_running(self) -> bool:
        """Ensure Ollama server is running."""
        try:
            # Try to connect to existing server
            result = subprocess.run(
                [self.ollama_binary, "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.logger.info("Ollama server is already running")
                return True

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        if not self.auto_start_server:
            self.logger.error("Ollama server not running and auto_start disabled")
            return False

        # Start server in background
        self.logger.info("Starting Ollama server...")
        try:
            self.server_process = subprocess.Popen(
                [self.ollama_binary, "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for server to start
            time.sleep(3)

            # Test connection
            result = subprocess.run(
                [self.ollama_binary, "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.logger.info("Ollama server started successfully")
                return True
            else:
                self.logger.error("Failed to start Ollama server")
                return False

        except Exception as e:
            self.logger.error(f"Error starting Ollama server: {e}")
            return False

    def _initialize_sub_managers(self):
        """Initialize output and configuration managers."""
        try:
            from .config_manager import ConfigManager
            from .output_manager import OutputManager

            self.output_manager = OutputManager()
            self.config_manager = ConfigManager()

            self.logger.info("Initialized Ollama sub-managers successfully")

        except ImportError as e:
            self.logger.warning(f"Could not initialize some sub-managers: {e}")
            # Continue without sub-managers - core functionality still works

    def list_models(self, force_refresh: bool = False) -> list[OllamaModel]:
        """
        List all available Ollama models.

        Args:
            force_refresh: Force refresh of model cache

        Returns:
            List of available models
        """
        # Check cache first
        current_time = time.time()
        if (not force_refresh and self._models_cache and self._cache_timestamp and
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._models_cache

        try:
            result = subprocess.run(
                [self.ollama_binary, "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.logger.error(f"Ollama list failed: {result.stderr}")
                return []

            models = []
            lines = result.stdout.strip().split('\n')[1:]  # Skip header

            for line in lines:
                if not line.strip():
                    continue

                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    model_id = parts[1]
                    size_str = parts[2]

                    # Parse size (convert to bytes)
                    size = self._parse_size(size_str)

                    # Extract additional info if available
                    modified = parts[3] if len(parts) > 3 else "unknown"

                    model = OllamaModel(
                        name=name,
                        id=model_id,
                        size=size,
                        modified=modified,
                        status="available"
                    )

                    # Try to get more details
                    model_info = self._get_model_info(name)
                    if model_info:
                        model.parameters = model_info.get('parameter_size')
                        model.family = model_info.get('family')
                        model.format = model_info.get('file_type')

                    models.append(model)

            # Update cache
            self._models_cache = models
            self._cache_timestamp = current_time

            self.logger.info(f"Found {len(models)} Ollama models")
            return models

        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []

    def _parse_size(self, size_str: str) -> int:
        """Parse size string to bytes."""
        try:
            if size_str.endswith('GB'):
                return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
            elif size_str.endswith('MB'):
                return int(float(size_str[:-2]) * 1024 * 1024)
            elif size_str.endswith('KB'):
                return int(float(size_str[:-2]) * 1024)
            else:
                return int(size_str)
        except (ValueError, IndexError, TypeError):
            return 0

    def _get_model_info(self, model_name: str) -> Optional[dict[str, Any]]:
        """Get detailed information about a specific model."""
        try:
            result = subprocess.run(
                [self.ollama_binary, "show", model_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return None

            # Parse the output (this is a simplified parser)
            info = {}
            lines = result.stdout.strip().split('\n')

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()

            return info

        except Exception as e:
            self.logger.warning(f"Could not get model info for {model_name}: {e}")
            return None

    def download_model(self, model_name: str) -> bool:
        """
        Download a model from Ollama library.

        Args:
            model_name: Name of the model to download

        Returns:
            True if successful
        """
        self.logger.info(f"Downloading model: {model_name}")

        try:
            # Use ollama run which downloads and runs the model
            result = subprocess.run(
                [self.ollama_binary, "run", model_name, "--help"],
                capture_output=True,
                text=True,
                timeout=30
            )

            # If it runs without error, the model is available
            success = result.returncode == 0

            if success:
                self.logger.info(f"Model {model_name} downloaded successfully")
                # Clear cache to force refresh
                self._models_cache = None
            else:
                self.logger.error(f"Failed to download model {model_name}: {result.stderr}")

            return success

        except Exception as e:
            self.logger.error(f"Error downloading model {model_name}: {e}")
            return False

    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available."""
        models = self.list_models()
        return any(model.name == model_name for model in models)

    def get_model_by_name(self, model_name: str) -> Optional[OllamaModel]:
        """Get model information by name."""
        models = self.list_models()
        for model in models:
            if model.name == model_name:
                return model
        return None

    def run_model(
        self,
        model_name: str,
        prompt: str,
        options: Optional[dict[str, Any]] = None,
        save_output: bool = True,
        output_dir: Optional[str] = None
    ) -> ModelExecutionResult:
        """
        Run a model with the given prompt.

        Args:
            model_name: Name of the model to run
            prompt: Input prompt
            options: Additional options for model execution
            save_output: Whether to save output to files
            output_dir: Directory to save outputs (if save_output is True)

        Returns:
            ModelExecutionResult with execution details
        """
        if not self.is_model_available(model_name):
            return ModelExecutionResult(
                model_name=model_name,
                prompt=prompt,
                response="",
                execution_time=0,
                success=False,
                error_message=f"Model {model_name} not available"
            )

        self.logger.info(f"Running model {model_name} with prompt length: {len(prompt)}")

        start_time = time.time()

        try:
            # Prepare the command - Ollama uses different parameter format
            cmd = [self.ollama_binary, "run", model_name]

            # Note: Ollama doesn't support runtime parameter flags like --temperature
            # These would need to be set when the model is initially configured or
            # through environment variables/model-specific settings

            # Run the model
            result = subprocess.run(
                cmd,
                input=prompt,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            execution_time = time.time() - start_time

            if result.returncode == 0:
                response = result.stdout.strip()
                success = True
                error_msg = None

                self.logger.info(f"Model {model_name} completed successfully in {execution_time:.2f}s")

                # Save output if requested
                if save_output and self.output_manager and output_dir:
                    self.output_manager.save_model_output(
                        model_name, prompt, response, execution_time, output_dir
                    )

            else:
                response = ""
                success = False
                error_msg = result.stderr.strip()

                self.logger.error(f"Model {model_name} failed: {error_msg}")

            return ModelExecutionResult(
                model_name=model_name,
                prompt=prompt,
                response=response,
                execution_time=execution_time,
                success=success,
                error_message=error_msg
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=prompt,
                response="",
                execution_time=execution_time,
                success=False,
                error_message="Model execution timed out"
            )

        except Exception as e:
            execution_time = time.time() - start_time
            return ModelExecutionResult(
                model_name=model_name,
                prompt=prompt,
                response="",
                execution_time=execution_time,
                success=False,
                error_message=f"Execution error: {str(e)}"
            )

    def run_model_async(
        self,
        model_name: str,
        prompt: str,
        options: Optional[dict[str, Any]] = None
    ) -> asyncio.Future[ModelExecutionResult]:
        """
        Run a model asynchronously.

        Args:
            model_name: Name of the model to run
            prompt: Input prompt
            options: Additional options for model execution

        Returns:
            Future that resolves to ModelExecutionResult
        """
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(
            None,
            self.run_model,
            model_name,
            prompt,
            options
        )

    def get_model_stats(self) -> dict[str, Any]:
        """Get statistics about available models."""
        models = self.list_models()

        stats = {
            'total_models': len(models),
            'total_size_bytes': sum(model.size for model in models),
            'total_size_mb': sum(model.size for model in models) / (1024 * 1024),
            'models_by_family': {},
            'largest_model': None,
            'smallest_model': None
        }

        # Group by family
        for model in models:
            family = model.family or 'unknown'
            if family not in stats['models_by_family']:
                stats['models_by_family'][family] = []
            stats['models_by_family'][family].append(model.name)

        # Find largest and smallest
        if models:
            stats['largest_model'] = max(models, key=lambda m: m.size).name
            stats['smallest_model'] = min(models, key=lambda m: m.size).name

        return stats

    def cleanup(self):
        """Cleanup resources."""
        if self.server_process:
            self.logger.info("Stopping Ollama server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            self.server_process = None
