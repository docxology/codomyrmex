"""Utilities Package.

Common utility functions and helpers used across the codomyrmex codebase.
"""

import functools
import hashlib
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Union

T = TypeVar("T")


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path to ensure exists
        
    Returns:
        Path object for the directory
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely parse JSON with a fallback default.
    
    Args:
        text: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, indent: int = 2, default: str = "{}") -> str:
    """Safely serialize to JSON with fallback.
    
    Args:
        obj: Object to serialize
        indent: Indentation level
        default: Default string if serialization fails
        
    Returns:
        JSON string
    """
    try:
        return json.dumps(obj, indent=indent, default=str)
    except (TypeError, ValueError):
        return default


def hash_content(content: Union[str, bytes], algorithm: str = "sha256") -> str:
    """Generate hash of content.
    
    Args:
        content: String or bytes to hash
        algorithm: Hash algorithm (sha256, sha512, md5)
        
    Returns:
        Hex digest of hash
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    
    h = hashlib.new(algorithm)
    h.update(content)
    return h.hexdigest()


def hash_file(path: Union[str, Path], algorithm: str = "sha256") -> Optional[str]:
    """Generate hash of file contents.
    
    Args:
        path: Path to file
        algorithm: Hash algorithm
        
    Returns:
        Hex digest or None if file not found
    """
    try:
        with open(path, "rb") as f:
            return hash_content(f.read(), algorithm)
    except (OSError, IOError):
        return None


def timing_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to measure function execution time.
    
    Adds execution_time_ms to function result if it's a dict,
    otherwise logs the time.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        
        if isinstance(result, dict):
            result["execution_time_ms"] = round(elapsed, 2)
        
        return result
    return wrapper


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for retrying failed operations with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            raise last_exception
        return wrapper
    return decorator


def get_timestamp(fmt: str = "%Y-%m-%d_%H-%M-%S") -> str:
    """Get current timestamp as formatted string.
    
    Args:
        fmt: strftime format string
        
    Returns:
        Formatted timestamp
    """
    return datetime.now().strftime(fmt)


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate string to maximum length with suffix.
    
    Args:
        s: String to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated string
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Get environment variable with options.
    
    Args:
        key: Environment variable name
        default: Default value if not set
        required: If True, raise ValueError when not set
        
    Returns:
        Environment variable value
    """
    value = os.environ.get(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    return value


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Flatten a nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Prefix for keys
        sep: Separator between key levels
        
    Returns:
        Flattened dictionary
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        override: Dictionary with values to merge/override
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


__all__ = [
    "ensure_directory",
    "safe_json_loads",
    "safe_json_dumps",
    "hash_content",
    "hash_file",
    "timing_decorator",
    "retry",
    "get_timestamp",
    "truncate_string",
    "get_env",
    "flatten_dict",
    "deep_merge",
]
