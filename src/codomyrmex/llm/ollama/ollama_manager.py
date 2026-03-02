"""
Ollama Manager - Main integration class for Codomyrmex

Provides comprehensive Ollama model management, execution, and integration
with the Codomyrmex ecosystem.
"""

import asyncio
import json
import os
import subprocess
import time
from dataclasses import dataclass
from typing import Any

import requests

from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL
from codomyrmex.logging_monitoring import get_logger


@dataclass
class OllamaModel:
    """Represents an Ollama model with metadata."""
    name: str
    id: str
    size: int  # Size in bytes
    modified: str
    parameters: str | None = None
    family: str | None = None
    format: str | None = None
    status: str = "available"


@dataclass
class ModelExecutionResult:
    """Result of a model execution."""
    model_name: str
    prompt: str
    response: str
    execution_time: float
    tokens_used: int | None = None
    success: bool = True
    error_message: str | None = None
    metadata: dict[str, Any] | None = None


class OllamaManager:
    """
    Main Ollama integration manager for Codomyrmex.

    Provides comprehensive model management, execution, and output handling
    with seamless integration into the Codomyrmex ecosystem.
    """

    def __init__(
        self,
        ollama_binary: str = "ollama",
        auto_start_server: bool = True,
        base_url: str = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL),
        use_http_api: bool = True
    ):
        """
        Initialize the Ollama manager.

        Args:
            ollama_binary: Path to ollama binary (default: "ollama")
            auto_start_server: Whether to automatically start Ollama server if not running
            base_url: Base URL for Ollama HTTP API (default: "http://localhost:11434")
            use_http_api: Whether to use HTTP API instead of subprocess (default: True)
        """
        self.ollama_binary = ollama_binary
        self.auto_start_server = auto_start_server
        self.base_url = base_url.rstrip('/')
        self.use_http_api = use_http_api
        self.logger = get_logger(__name__)
        self.server_process = None
        self._ensure_server_running()

        # Initialize sub-managers
        self.output_manager = None  # Will be set after import
        self.config_manager = None  # Will be set after import

        # Import and initialize sub-managers
        self._initialize_sub_managers()

        # Model cache
        self._models_cache: list[OllamaModel] | None = None
        self._cache_timestamp: float | None = None
        self._cache_ttl = 30  # Cache for 30 seconds

    def _ensure_server_running(self) -> bool:
        """Ensure Ollama server is running."""
        if self.use_http_api:
            # Check HTTP API connectivity
            try:
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    self.logger.info("Ollama server is already running (HTTP API)")
                    return True
            except requests.exceptions.RequestException as e:
                self.logger.debug("Ollama HTTP API not responding, trying CLI check: %s", str(e))

        # Fallback to subprocess check
        try:
            result = subprocess.run(
                [self.ollama_binary, "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.logger.info("Ollama server is already running (CLI)")
                return True

        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.logger.debug("Ollama CLI check failed, will attempt to start server: %s", str(e))

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
            if self.use_http_api:
                try:
                    response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                    if response.status_code == 200:
                        self.logger.info("Ollama server started successfully (HTTP API)")
                        return True
                except requests.exceptions.RequestException as e:
                    self.logger.debug("Ollama HTTP API still not responding after start: %s", str(e))

            # Fallback to subprocess test
            result = subprocess.run(
                [self.ollama_binary, "list"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.logger.info("Ollama server started successfully (CLI)")
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

        models = []

        # Try HTTP API first if enabled
        if self.use_http_api:
            try:
                response = requests.get(f"{self.base_url}/api/tags", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for model_data in data.get('models', []):
                        # Parse size - ensure it's an integer
                        size = model_data.get('size', 0)
                        if isinstance(size, str):
                            size = self._parse_size(size)
                        elif not isinstance(size, int):
                            size = int(size) if size else 0

                        # Parse modified_at - ensure it's a valid timestamp
                        modified_at = model_data.get('modified_at', time.time())
                        if isinstance(modified_at, str):
                            try:
                                modified_at = float(modified_at)
                            except (ValueError, TypeError):
                                modified_at = time.time()

                        model = OllamaModel(
                            name=model_data.get('name', ''),
                            id=model_data.get('digest', '')[:12] if model_data.get('digest') else '',
                            size=size,
                            modified=time.strftime('%Y-%m-%d', time.localtime(modified_at)),
                            status="available"
                        )
                        # Get additional info
                        model_info = self._get_model_info(model.name)
                        if model_info:
                            model.parameters = model_info.get('parameter_size')
                            model.family = model_info.get('family')
                            model.format = model_info.get('file_type')
                        models.append(model)

                    # Update cache
                    self._models_cache = models
                    self._cache_timestamp = current_time
                    self.logger.info(f"Found {len(models)} Ollama models via HTTP API")
                    return models
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"HTTP API failed, falling back to CLI: {e}")
            except Exception as e:
                self.logger.warning(f"HTTP API parsing error, falling back to CLI: {e}")

        # Fallback to subprocess
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

            self.logger.info(f"Found {len(models)} Ollama models via CLI")
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
        except (ValueError, IndexError, TypeError) as e:
            self.logger.warning("Failed to parse model size '%s': %s", size_str, e)
            return 0

    def _get_model_info(self, model_name: str) -> dict[str, Any] | None:
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
        Download (pull) a model from Ollama library.

        Args:
            model_name: Name of the model to download

        Returns:
            True if successful
        """
        self.logger.info(f"Pulling model: {model_name}")

        # Try HTTP API first if enabled
        if self.use_http_api:
            try:
                response = requests.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_name},
                    timeout=3600,  # 1 hour timeout for large models
                    stream=True
                )

                if response.status_code == 200:
                    # Stream the pull progress
                    completed = False
                    last_status = ""
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                status = data.get('status', '')
                                if status and status != last_status:
                                    # Log significant status changes
                                    if any(keyword in status.lower() for keyword in ['pulling', 'downloading', 'verifying', 'writing']):
                                        if 'manifest' in status.lower() or 'digest' in status.lower() or 'layer' in status.lower():
                                            self.logger.info(f"Pull status: {status}")
                                    last_status = status

                                # Check for completion
                                if data.get('completed', False):
                                    completed = True
                                    self.logger.info(f"Model {model_name} pull completed via HTTP API")
                                    break
                                elif data.get('status') == 'success':
                                    completed = True
                                    self.logger.info(f"Model {model_name} pull successful via HTTP API")
                                    break
                            except json.JSONDecodeError:
                                # Skip non-JSON lines (like ANSI escape codes)
                                continue

                    # Wait a moment for model to be registered
                    if completed:
                        time.sleep(3)  # Give more time for model registration

                    # Check if model is now available (with retry for cache refresh)
                    self._models_cache = None  # Clear cache
                    for _attempt in range(5):  # More retries
                        if self.is_model_available(model_name):
                            self.logger.info(f"Model {model_name} verified as available via HTTP API")
                            return True
                        time.sleep(2)  # Longer wait between retries
                        self._models_cache = None  # Clear cache again

                    # Final check - maybe model name has a tag or different format
                    models = self.list_models(force_refresh=True)
                    base_name = model_name.split(':')[0]
                    model_found = any(base_name in m.name for m in models)
                    if model_found:
                        matching_models = [m.name for m in models if base_name in m.name]
                        self.logger.info(f"Model {base_name} appears to be available: {matching_models}")
                        # Update model name to match what's actually available
                        if matching_models:
                            self.logger.info(f"Using model: {matching_models[0]}")
                        return True

                    # If pull completed, assume success even if not in list yet
                    if completed:
                        self.logger.info(f"Pull completed for {model_name}, model should be available")
                        return True

                    self.logger.warning(f"Pull may not have completed for {model_name}")
                    return False
                else:
                    error_text = response.text[:200] if response.text else "Unknown error"
                    self.logger.error(f"Pull failed: HTTP {response.status_code}: {error_text}")
                    return False
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"HTTP API pull failed, falling back to CLI: {e}")

        # Fallback to subprocess
        try:
            # Use ollama pull to download the model
            result = subprocess.run(
                [self.ollama_binary, "pull", model_name],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout for large models
            )

            success = result.returncode == 0

            if success:
                self.logger.info(f"Model {model_name} pulled successfully via CLI")
                # Clear cache to force refresh
                self._models_cache = None
            else:
                self.logger.error(f"Failed to pull model {model_name}: {result.stderr}")

            return success

        except subprocess.TimeoutExpired:
            self.logger.error(f"Model pull timed out for {model_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error pulling model {model_name}: {e}")
            return False

    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available."""
        models = self.list_models()
        return any(model.name == model_name for model in models)

    def get_model_by_name(self, model_name: str) -> OllamaModel | None:
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
        options: dict[str, Any] | None = None,
        save_output: bool = True,
        output_dir: str | None = None
    ) -> ModelExecutionResult:
        """
        Run a model with the given prompt.

        Args:
            model_name: Name of the model to run
            prompt: Input prompt
            options: Additional options for model execution (temperature, top_p, etc.)
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

        # Try HTTP API first if enabled
        if self.use_http_api:
            try:
                # Prepare request payload
                payload = {
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False
                }

                # Add options if provided
                if options:
                    # Map ExecutionOptions to Ollama API format
                    payload['options'] = payload.get('options', {})

                    if 'temperature' in options:
                        payload['options']['temperature'] = options['temperature']
                    if 'top_p' in options:
                        payload['options']['top_p'] = options['top_p']
                    if 'top_k' in options:
                        payload['options'] = payload.get('options', {})
                        payload['options']['top_k'] = options['top_k']
                    if 'repeat_penalty' in options:
                        payload['options'] = payload.get('options', {})
                        payload['options']['repeat_penalty'] = options['repeat_penalty']
                    if 'max_tokens' in options or 'num_predict' in options:
                        payload['options']['num_predict'] = options.get('num_predict', options.get('max_tokens', 2048))
                    if 'num_ctx' in options:
                        payload['options']['num_ctx'] = options['num_ctx']
                    if 'format' in options:
                        payload['format'] = options['format']
                    if 'system' in options or 'system_prompt' in options:
                        payload['system'] = options.get('system') or options.get('system_prompt')

                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=300  # 5 minute timeout
                )

                execution_time = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('response', '').strip()
                    success = True
                    error_msg = None
                    tokens_used = data.get('eval_count')  # Approximate token count

                    self.logger.info(f"Model {model_name} completed successfully in {execution_time:.2f}s")

                    # Save output if requested
                    if save_output and self.output_manager and output_dir:
                        self.output_manager.save_model_output(
                            model_name, prompt, response_text, execution_time, output_dir
                        )

                    return ModelExecutionResult(
                        model_name=model_name,
                        prompt=prompt,
                        response=response_text,
                        execution_time=execution_time,
                        tokens_used=tokens_used,
                        success=success,
                        error_message=error_msg,
                        metadata={'api_method': 'http'}
                    )
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    self.logger.error(f"Model {model_name} failed: {error_msg}")
                    return ModelExecutionResult(
                        model_name=model_name,
                        prompt=prompt,
                        response="",
                        execution_time=execution_time,
                        success=False,
                        error_message=error_msg
                    )

            except requests.exceptions.Timeout:
                execution_time = time.time() - start_time
                return ModelExecutionResult(
                    model_name=model_name,
                    prompt=prompt,
                    response="",
                    execution_time=execution_time,
                    success=False,
                    error_message="Model execution timed out"
                )
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"HTTP API failed, falling back to CLI: {e}")

        # Fallback to subprocess
        try:
            # Prepare the command - Ollama uses different parameter format
            cmd = [self.ollama_binary, "run", model_name]

            # Note: CLI doesn't support runtime parameter flags
            # Options would need to be set via model configuration

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
                error_message=error_msg,
                metadata={'api_method': 'cli'}
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
        options: dict[str, Any] | None = None
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
