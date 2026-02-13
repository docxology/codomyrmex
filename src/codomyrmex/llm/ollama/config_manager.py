"""
Configuration Manager - Handles Ollama configurations and settings

Manages model configurations, execution settings, and integration
preferences for the Codomyrmex Ollama integration.
"""

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .model_runner import ExecutionOptions


@dataclass
class OllamaConfig:
    """
    Complete Ollama configuration for Codomyrmex.

    All configuration parameters are modular and independently configurable.
    Settings are organized into logical groups for clarity.

    Configuration Groups:
        General Settings: Server and binary configuration
        Output Settings: File output and cleanup configuration
        Model Preferences: Default models and preferences
        Execution Defaults: Default execution options
        Integration Settings: Feature flags for integrations
    """
    # General settings
    ollama_binary: str = "ollama"  # Path to ollama binary
    auto_start_server: bool = True  # Automatically start Ollama server if not running
    server_host: str = "localhost"  # Ollama server hostname
    server_port: int = 11434  # Ollama server port

    # Output settings
    base_output_dir: str = "examples/output/ollama"  # Base directory for all outputs
    save_all_outputs: bool = True  # Whether to save all model outputs
    save_configs: bool = True  # Whether to save configurations
    auto_cleanup_days: int = 30  # Days before auto-cleaning old outputs

    # Model preferences
    default_model: str = "llama3.1:latest"  # Default model to use
    preferred_models: list[str] = None  # List of preferred models (fallback order)

    # Execution defaults
    default_options: ExecutionOptions = None  # Default execution options

    # Integration settings
    enable_logging: bool = True  # Enable logging integration
    enable_visualization: bool = True  # Enable visualization features
    enable_benchmarks: bool = True  # Enable benchmarking features

    def __post_init__(self):

        if self.preferred_models is None:
            self.preferred_models = ["llama3.1:latest", "codellama:latest", "gemma2:2b"]
        if self.default_options is None:
            self.default_options = ExecutionOptions()


class ConfigManager:
    """
    Manages all configuration aspects of the Ollama integration.

    Handles loading, saving, and managing configurations for models,
    execution settings, and integration preferences.
    """

    def __init__(self, config_file: str | None = None):
        """
        Initialize the configuration manager.

        Args:
            config_file: Path to configuration file (default: auto-detect)
        """
        self.logger = get_logger(__name__)

        if config_file:
            self.config_file = Path(config_file)
        else:
            # Default configuration location
            self.config_file = Path("examples/output/ollama/configs/ollama_config.json")

        # Current configuration
        self.config: OllamaConfig | None = None

        # Initialize with defaults first, then try to load
        self.config = OllamaConfig()

        # Load configuration if file exists
        if self.config_file.exists():
            self.load_config()

    def load_config(self) -> bool:
        """
        Load configuration from file.

        Returns:
            True if configuration loaded successfully
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, encoding='utf-8') as f:
                    config_data = json.load(f)

                # Filter out metadata fields that aren't part of OllamaConfig
                filtered_config = {}
                for key, value in config_data.items():
                    if key not in ['saved_at', 'config_version', 'export_timestamp', 'main_config', 'execution_presets', 'model_configs']:
                        filtered_config[key] = value

                self.config = OllamaConfig(**filtered_config)
                self.logger.info(f"Loaded configuration from: {self.config_file}")
                return True
            else:
                self.logger.info("Configuration file not found, using defaults")
                return True

        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            # Keep existing config (defaults)
            return False

    def save_config(self) -> bool:
        """
        Save current configuration to file.

        Returns:
            True if configuration saved successfully
        """
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dictionary
            config_dict = asdict(self.config)

            # Add metadata
            config_dict['saved_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            config_dict['config_version'] = '1.0.0'

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, default=str)

            self.logger.info(f"Saved configuration to: {self.config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False

    def create_default_config(self) -> OllamaConfig:
        """Create a default configuration."""
        return OllamaConfig()

    def update_config(self, **kwargs) -> bool:
        """
        Update configuration with new values.

        Args:
            **kwargs: Configuration values to update

        Returns:
            True if configuration updated successfully
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    self.logger.warning(f"Unknown configuration key: {key}")

            return self.save_config()

        except Exception as e:
            self.logger.error(f"Error updating configuration: {e}")
            return False

    def get_model_config(self, model_name: str) -> dict[str, Any] | None:
        """
        Get configuration for a specific model.

        Args:
            model_name: Name of the model

        Returns:
            Model configuration dictionary or None if not found
        """
        if not self.config:
            return None

        # Look for model-specific configuration
        model_config_file = Path(self.config.base_output_dir) / "configs" / model_name / "model_config.json"

        if model_config_file.exists():
            try:
                with open(model_config_file, encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading model config for {model_name}: {e}")

        return None

    def save_model_config(self, model_name: str, config: dict[str, Any]) -> bool:
        """
        Save configuration for a specific model.

        Args:
            model_name: Name of the model
            config: Model configuration dictionary

        Returns:
            True if configuration saved successfully
        """
        if not self.config:
            return False

        try:
            model_config_dir = Path(self.config.base_output_dir) / "configs" / model_name
            model_config_dir.mkdir(parents=True, exist_ok=True)

            model_config_file = model_config_dir / "model_config.json"

            # Add metadata
            config_with_metadata = {
                'model_name': model_name,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'configuration': config
            }

            with open(model_config_file, 'w', encoding='utf-8') as f:
                json.dump(config_with_metadata, f, indent=2, default=str)

            self.logger.info(f"Saved model config for {model_name} to: {model_config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving model config for {model_name}: {e}")
            return False

    def get_execution_presets(self) -> dict[str, ExecutionOptions]:
        """
        Get predefined execution option presets.

        Returns:
            Dictionary of preset names to ExecutionOptions
        """
        return {
            'fast': ExecutionOptions(
                temperature=0.1,
                top_p=0.5,
                max_tokens=512,
                timeout=60
            ),
            'creative': ExecutionOptions(
                temperature=0.9,
                top_p=0.95,
                max_tokens=1024,
                timeout=120
            ),
            'balanced': ExecutionOptions(
                temperature=0.7,
                top_p=0.9,
                max_tokens=1024,
                timeout=120
            ),
            'precise': ExecutionOptions(
                temperature=0.3,
                top_p=0.7,
                max_tokens=2048,
                timeout=180
            ),
            'long_form': ExecutionOptions(
                temperature=0.7,
                top_p=0.9,
                max_tokens=4096,
                timeout=300
            )
        }

    def export_config(self, export_path: str) -> bool:
        """
        Export complete configuration to a file.

        Args:
            export_path: Path to export configuration to

        Returns:
            True if export successful
        """
        try:
            export_file = Path(export_path)

            # Create comprehensive export
            export_data = {
                'export_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'main_config': asdict(self.config) if self.config else {},
                'execution_presets': {name: asdict(preset) for name, preset in self.get_execution_presets().items()},
                'model_configs': {}
            }

            # Include model-specific configurations
            if self.config:
                configs_dir = Path(self.config.base_output_dir) / "configs"
                if configs_dir.exists():
                    for model_dir in configs_dir.iterdir():
                        if model_dir.is_dir():
                            model_config_file = model_dir / "model_config.json"
                            if model_config_file.exists():
                                try:
                                    with open(model_config_file, encoding='utf-8') as f:
                                        export_data['model_configs'][model_dir.name] = json.load(f)
                                except Exception as e:
                                    self.logger.warning(f"Error reading model config for {model_dir.name}: {e}")

            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)

            self.logger.info(f"Exported configuration to: {export_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return False

    def import_config(self, import_path: str) -> bool:
        """
        Import configuration from a file.

        Args:
            import_path: Path to configuration file to import

        Returns:
            True if import successful
        """
        try:
            import_file = Path(import_path)

            if not import_file.exists():
                self.logger.error(f"Import file not found: {import_file}")
                return False

            with open(import_file, encoding='utf-8') as f:
                import_data = json.load(f)

            # Update main configuration
            if 'main_config' in import_data:
                self.config = OllamaConfig(**import_data['main_config'])

            # Import model-specific configurations
            if 'model_configs' in import_data and self.config:
                for model_name, model_config in import_data['model_configs'].items():
                    self.save_model_config(model_name, model_config)

            # Save updated configuration
            self.save_config()

            self.logger.info(f"Imported configuration from: {import_file}")
            return True

        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values.

        Returns:
            True if reset successful
        """
        try:
            self.config = OllamaConfig()
            return self.save_config()

        except Exception as e:
            self.logger.error(f"Error resetting configuration: {e}")
            return False

    def validate_config(self) -> dict[str, Any]:
        """
        Validate current configuration.

        Returns:
            Validation results dictionary
        """
        if not self.config:
            return {'valid': False, 'errors': ['No configuration loaded']}

        errors = []
        warnings = []

        # Validate paths
        try:
            base_path = Path(self.config.base_output_dir)
            if not base_path.exists():
                warnings.append(f"Base output directory does not exist: {base_path}")
        except Exception as e:
            errors.append(f"Invalid base output directory: {e}")

        # Validate binary path
        try:
            import shutil
            if not shutil.which(self.config.ollama_binary):
                warnings.append(f"Ollama binary not found in PATH: {self.config.ollama_binary}")
        except Exception as e:
            errors.append(f"Error checking ollama binary: {e}")

        # Validate model preferences
        if self.config.preferred_models:
            for model in self.config.preferred_models:
                if not model or not isinstance(model, str):
                    errors.append(f"Invalid model in preferred_models: {model}")

        # Validate execution options
        if self.config.default_options and isinstance(self.config.default_options, ExecutionOptions):
            if not (0.0 <= self.config.default_options.temperature <= 2.0):
                errors.append("Temperature must be between 0.0 and 2.0")

            if not (0.0 <= self.config.default_options.top_p <= 1.0):
                errors.append("top_p must be between 0.0 and 1.0")

            if self.config.default_options.max_tokens < 1:
                errors.append("max_tokens must be positive")

            if self.config.default_options.timeout < 1:
                errors.append("timeout must be positive")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def get_available_models(self) -> list[str]:
        """
        Get list of available models from Ollama server.

        Returns:
            List of model names available in Ollama
        """
        if not self.config:
            return []

        try:
            import requests
            url = f"http://{self.config.server_host}:{self.config.server_port}/api/tags"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except Exception as e:
            self.logger.warning(f"Failed to fetch models from Ollama: {e}")

        # Fallback to configured models if API fails
        if self.config and self.config.preferred_models:
            return self.config.preferred_models
        return ["llama3.1:latest"]
