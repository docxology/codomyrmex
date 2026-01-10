from pathlib import Path
from typing import Optional, Union
import json
import json
import os

from codomyrmex.logging_monitoring import get_logger
























"""Configuration management for Language Models module."""

logger = get_logger(__name__)
class LLMConfig:
    """
    Configuration manager for LLM parameters and settings.

    Provides centralized configuration for model selection, generation parameters,
    and output settings with environment variable support.
    """

    # Default configurations
    DEFAULT_MODEL = "llama3.1:latest"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 1000
    DEFAULT_TOP_P = 0.9
    DEFAULT_TOP_K = 40
    DEFAULT_TIMEOUT = 30
    DEFAULT_BASE_URL = "http://localhost:11434"

    # Output configuration
    OUTPUT_ROOT = Path("src/codomyrmex.llm/outputs")
    TEST_RESULTS_DIR = OUTPUT_ROOT / "test_results"
    LLM_OUTPUTS_DIR = OUTPUT_ROOT / "llm_outputs"
    REPORTS_DIR = OUTPUT_ROOT / "reports"

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        timeout: Optional[int] = None,
        base_url: Optional[str] = None,
        output_root: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize LLM configuration with optional overrides.

        Args:
            model: Model name to use (e.g., "llama3.1:latest")
            temperature: Generation temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            timeout: Request timeout in seconds
            base_url: Ollama server base URL
            output_root: Root directory for outputs
        """
        self.model = model or self._get_env_var("LLM_MODEL", self.DEFAULT_MODEL)
        self.temperature = temperature or self._get_env_float("LLM_TEMPERATURE", self.DEFAULT_TEMPERATURE)
        self.max_tokens = max_tokens or self._get_env_int("LLM_MAX_TOKENS", self.DEFAULT_MAX_TOKENS)
        self.top_p = top_p or self._get_env_float("LLM_TOP_P", self.DEFAULT_TOP_P)
        self.top_k = top_k or self._get_env_int("LLM_TOP_K", self.DEFAULT_TOP_K)
        self.timeout = timeout or self._get_env_int("LLM_TIMEOUT", self.DEFAULT_TIMEOUT)
        self.base_url = base_url or self._get_env_var("LLM_BASE_URL", self.DEFAULT_BASE_URL)

        # Output configuration
        if output_root:
            self.output_root = Path(output_root)
        else:
            self.output_root = Path(self._get_env_var("LLM_OUTPUT_ROOT", str(self.OUTPUT_ROOT)))

        self.test_results_dir = self.output_root / "test_results"
        self.llm_outputs_dir = self.output_root / "llm_outputs"
        self.reports_dir = self.output_root / "reports"
        self.config_dir = self.output_root / "config"
        self.logs_dir = self.output_root / "logs"
        self.models_dir = self.output_root / "models"
        self.performance_dir = self.output_root / "performance"
        self.integration_dir = self.output_root / "integration"

        # Create directories
        self._ensure_directories()

    def _get_env_var(self, key: str, default: str) -> str:
        """Get environment variable with default."""
        return os.getenv(key, default)

    def _get_env_float(self, key: str, default: float) -> float:
        """Get environment variable as float with default."""
        try:
            return float(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    def _get_env_int(self, key: str, default: int) -> int:
        """Get environment variable as int with default."""
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    def _ensure_directories(self):
        """Create output directories if they don't exist."""
        for directory in [
            self.test_results_dir,
            self.llm_outputs_dir,
            self.reports_dir,
            self.config_dir,
            self.logs_dir,
            self.models_dir,
            self.performance_dir,
            self.integration_dir
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_generation_options(self) -> dict:
        """
        Get generation options for LLM requests.

        Returns:
            Dictionary of generation parameters
        """
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "num_predict": self.max_tokens,
        }

    def get_client_kwargs(self) -> dict:
        """
        Get client initialization parameters.

        Returns:
            Dictionary of OllamaClient parameters
        """
        return {
            "base_url": self.base_url,
            "model": self.model,
            "timeout": self.timeout,
        }

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.

        Returns:
            Configuration as dictionary
        """
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "timeout": self.timeout,
            "base_url": self.base_url,
            "output_root": str(self.output_root),
            "test_results_dir": str(self.test_results_dir),
            "llm_outputs_dir": str(self.llm_outputs_dir),
            "reports_dir": str(self.reports_dir),
        }

    def save_config(self, filepath: Optional[Union[str, Path]] = None):
        """
        Save configuration to JSON file.

        Args:
            filepath: Path to save configuration (default: config.json in output root)
        """

        if filepath is None:
            filepath = self.output_root / "config.json"

        # Only save core configuration parameters, not derived paths
        core_config = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "timeout": self.timeout,
            "base_url": self.base_url,
            "output_root": str(self.output_root),
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(core_config, f, indent=2, ensure_ascii=False)

    @classmethod
    def from_file(cls, filepath: Union[str, Path]) -> "LLMConfig":
        """
        Load configuration from JSON file.

        Args:
            filepath: Path to configuration file

        Returns:
            LLMConfig instance
        """

        with open(filepath, encoding='utf-8') as f:
            config_dict = json.load(f)

        return cls(**config_dict)

    def __repr__(self) -> str:
        """String representation of configuration."""
        return (
            "LLMConfig("
            f"model={self.model!r}, "
            f"temperature={self.temperature}, "
            f"max_tokens={self.max_tokens}, "
            f"base_url={self.base_url!r}"
            ")"
        )


# Global configuration instance
_config_instance: Optional[LLMConfig] = None


def get_config() -> LLMConfig:
    """
    Get global LLM configuration instance.

    Returns:
        Global LLMConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = LLMConfig()
    return _config_instance


def set_config(config: LLMConfig):
    """
    Set global LLM configuration instance.

    Args:
        config: LLMConfig instance to set as global
    """
    global _config_instance
    _config_instance = config


def reset_config():
    """Reset global configuration to default."""
    global _config_instance
    _config_instance = None


# Preset configurations for common use cases
class LLMConfigPresets:
    """Preset configurations for different use cases."""

    @staticmethod
    def creative() -> LLMConfig:
        """Configuration optimized for creative tasks."""
        return LLMConfig(
            temperature=0.9,
            top_p=0.95,
            top_k=50,
            max_tokens=1500,
        )

    @staticmethod
    def precise() -> LLMConfig:
        """Configuration optimized for precise, factual responses."""
        return LLMConfig(
            temperature=0.1,
            top_p=0.5,
            top_k=20,
            max_tokens=800,
        )

    @staticmethod
    def fast() -> LLMConfig:
        """Configuration optimized for speed."""
        return LLMConfig(
            temperature=0.5,
            max_tokens=500,
            timeout=15,
        )

    @staticmethod
    def comprehensive() -> LLMConfig:
        """Configuration optimized for detailed responses."""
        return LLMConfig(
            temperature=0.3,
            top_p=0.8,
            max_tokens=2000,
        )
