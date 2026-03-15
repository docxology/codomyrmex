"""Paperclip agent integration for Codomyrmex.

Provides CLI and REST API clients for the Paperclip zero-human
company orchestration platform.

See: https://github.com/paperclipai/paperclip
"""

from .paperclip_api_client import PaperclipAPIClient
from .paperclip_client import PaperclipClient
from .paperclip_integration import PaperclipIntegrationAdapter

__all__ = [
    "PaperclipAPIClient",
    "PaperclipClient",
    "PaperclipIntegrationAdapter",
]
