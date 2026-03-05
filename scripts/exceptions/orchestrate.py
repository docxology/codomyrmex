#!/usr/bin/env python3
"""
Orchestrator for exceptions
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import logging

from codomyrmex.exceptions import (
    AIProviderError,
    CodomyrmexError,
    ConfigurationError,
    FileOperationError,
    InferenceError,
    format_exception_chain,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def demonstrate_exceptions():
    """Demonstrate the improved exception system."""
    logger.info("Starting Codomyrmex Exception Demonstration")
    logger.info("-" * 40)

    # 1. Standard CodomyrmexError with context
    try:
        logger.info("Raising base CodomyrmexError with manual context...")
        raise CodomyrmexError("Something went wrong", user_id="user_123", action="demo")
    except CodomyrmexError as e:
        logger.info(f"Caught: {e}")
        logger.info(f"Context: {e.context}")
        logger.info(f"Error Code: {e.error_code}")

    logger.info("-" * 40)

    # 2. Specialized exception with specific parameters
    try:
        logger.info("Raising AIProviderError with specific parameters...")
        raise AIProviderError(
            "API Limit exceeded", provider_name="OpenAI", model_name="gpt-4o"
        )
    except AIProviderError as e:
        logger.info(f"Caught: {e}")
        logger.info(f"Context: {e.context}")
        if (
            e.context["provider_name"] != "OpenAI"
            or e.context["model_name"] != "gpt-4o"
        ):
            logger.error("Verification failed for AIProviderError context")
            sys.exit(1)

    logger.info("-" * 40)

    # 3. Exception chaining and formatting
    try:
        logger.info("Demonstrating exception chaining...")
        try:
            raise FileOperationError("File not found", file_path="/tmp/missing.txt")
        except FileOperationError as cause:
            raise ConfigurationError(
                "Failed to load configuration", config_file="/tmp/missing.txt"
            ) from cause
    except CodomyrmexError as e:
        logger.info("Caught chained exception:")
        logger.info(format_exception_chain(e))

    logger.info("-" * 40)

    # 4. Cognitive System Errors (CEREBRUM)
    try:
        logger.info("Raising Cerebrum InferenceError...")
        raise InferenceError(
            "Inference engine failure",
            inference_engine="BayesianNet",
            system_component="cerebrum_v1",
        )
    except InferenceError as e:
        logger.info(f"Caught: {e}")
        logger.info(f"Context: {e.context}")

    logger.info("-" * 40)
    logger.info("Demonstration completed successfully.")

    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "exceptions"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/exceptions/config.yaml")


if __name__ == "__main__":
    try:
        demonstrate_exceptions()
    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        sys.exit(1)
