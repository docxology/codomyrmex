
from codomyrmex.logging_monitoring import get_logger

"""Core functionality module

This module provides language_support functionality including:
- 1 functions: validate_language
- 0 classes: 

Usage:
    from language_support import FunctionName, ClassName
    # Example usage here
"""
logger = get_logger(__name__)
"""
Language Support Configuration

Defines supported programming languages and their execution configurations.
"""

# Supported languages and their corresponding Docker images and file extensions
SUPPORTED_LANGUAGES = {
    "python": {
        "image": "python:3.9-slim",
        "extension": "py",
        "command": ["python", "{filename}"],
        "timeout_factor": 1.2,  # Additional time for container start/stop
    },
    "javascript": {
        "image": "node:14-alpine",
        "extension": "js",
        "command": ["node", "{filename}"],
        "timeout_factor": 1.2,
    },
    "java": {
        "image": "openjdk:11-jre-slim",
        "extension": "java",
        "command": [
            "sh",
            "-c",
            "javac {filename} && java $(basename {filename} .java)",
        ],
        "timeout_factor": 1.5,
    },
    "cpp": {
        "image": "gcc:9",
        "extension": "cpp",
        "command": ["sh", "-c", "g++ -o /tmp/program {filename} && /tmp/program"],
        "timeout_factor": 1.5,
    },
    "c": {
        "image": "gcc:9",
        "extension": "c",
        "command": ["sh", "-c", "gcc -o /tmp/program {filename} && /tmp/program"],
        "timeout_factor": 1.5,
    },
    "go": {
        "image": "golang:1.19-alpine",
        "extension": "go",
        "command": ["go", "run", "{filename}"],
        "timeout_factor": 1.3,
    },
    "rust": {
        "image": "rust:1.65-slim",
        "extension": "rs",
        "command": ["sh", "-c", "rustc {filename} -o /tmp/program && /tmp/program"],
        "timeout_factor": 1.5,
    },
    "bash": {
        "image": "bash:5.1",
        "extension": "sh",
        "command": ["bash", "{filename}"],
        "timeout_factor": 1.2,
    },
}


def validate_language(language: str) -> bool:
    """Validate that the requested language is supported."""
    return language in SUPPORTED_LANGUAGES

