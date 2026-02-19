"""Centralized default configuration values for Codomyrmex.

All default URLs, ports, and connection strings are defined here as single
sources of truth. Production code should reference these constants via
os.getenv() with these as fallback defaults.

Usage:
    import os
    from codomyrmex.config_management.defaults import DEFAULT_OLLAMA_URL

    ollama_url = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL)
"""

# LLM Service Defaults
DEFAULT_OLLAMA_URL = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llama3.1:latest"

# Database Defaults
DEFAULT_POSTGRES_HOST = "localhost"
DEFAULT_POSTGRES_PORT = "5432"
DEFAULT_POSTGRES_USER = "postgres"

# Cache Defaults
DEFAULT_REDIS_URL = "redis://localhost:6379"

# API Defaults
DEFAULT_API_HOST = "localhost"
DEFAULT_API_PORT = "8000"
DEFAULT_API_BASE_URL = "http://localhost:8000"

# Telemetry Defaults
DEFAULT_OTEL_ENDPOINT = "http://localhost:4317"

# Website Defaults
DEFAULT_CORS_ORIGINS = "http://localhost:8787"
