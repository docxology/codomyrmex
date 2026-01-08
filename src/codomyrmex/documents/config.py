from pathlib import Path
from typing import Optional
import os




"""Configuration management for the Documents module."""



class DocumentsConfig:
    """Configuration for document operations."""
    
    def __init__(
        self,
        default_encoding: str = "utf-8",
        max_file_size: int = 100 * 1024 * 1024,  # 100MB
        enable_caching: bool = True,
        cache_directory: Optional[Path] = None,
        strict_validation: bool = False,
    ):
        self.default_encoding = default_encoding
        self.max_file_size = max_file_size
        self.enable_caching = enable_caching
        
        # Use environment variable for cache directory if set (for testing)
        if cache_directory is None:
            env_cache = os.environ.get('CODOMYRMEX_CACHE_DIR')
            if env_cache:
                cache_directory = Path(env_cache) / "documents_cache"
            else:
                cache_directory = Path.home() / ".codomyrmex" / "documents_cache"
        
        self.cache_directory = cache_directory
        self.strict_validation = strict_validation
        
        # Create cache directory if needed (handle permission errors gracefully)
        if self.enable_caching:
            try:
                self.cache_directory.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError):
                # If we can't create cache directory, disable caching
                self.enable_caching = False


# Global configuration instance
_config: Optional[DocumentsConfig] = None


def get_config() -> DocumentsConfig:
    """Get the global documents configuration."""
    global _config
    if _config is None:
        _config = DocumentsConfig()
    return _config


def set_config(config: DocumentsConfig) -> None:
    """Set the global documents configuration."""
    global _config
    _config = config

