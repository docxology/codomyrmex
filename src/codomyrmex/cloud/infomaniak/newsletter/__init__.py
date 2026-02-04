"""
Infomaniak Newsletter API Client.

Provides campaign management, mailing list operations, and contact
management via the Infomaniak REST API.

Usage:
    from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

    client = InfomaniakNewsletterClient.from_env()
    campaigns = client.list_campaigns()
"""

from .client import InfomaniakNewsletterClient

__all__ = ["InfomaniakNewsletterClient"]
