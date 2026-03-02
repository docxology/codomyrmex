"""
Infomaniak Newsletter REST API Client.

Uses the Infomaniak API (https://api.infomaniak.com) with OAuth2 Bearer
token authentication for newsletter/mailing list operations.

Environment Variables:
    INFOMANIAK_NEWSLETTER_TOKEN: OAuth2 bearer token
    INFOMANIAK_NEWSLETTER_ID: Newsletter product ID
"""

import os
from typing import Any

from ..base import InfomaniakRESTBase
from ..exceptions import classify_http_error
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

BASE_URL = "https://api.infomaniak.com"


class InfomaniakNewsletterClient(InfomaniakRESTBase):
    """Client for the Infomaniak Newsletter API.

    Supports campaign management, mailing list operations, contact
    management, and statistics retrieval.
    """

    _service_name: str = "newsletter"

    def __init__(self, token: str, newsletter_id: str, base_url: str = BASE_URL):
        super().__init__(token=token, base_url=base_url)
        self._newsletter_id = newsletter_id

    @classmethod
    def from_env(cls) -> "InfomaniakNewsletterClient":
        """Create client from environment variables.

        Requires:
            INFOMANIAK_NEWSLETTER_TOKEN: OAuth2 bearer token
            INFOMANIAK_NEWSLETTER_ID: Newsletter product ID

        Raises:
            ValueError: If required environment variables are missing.
        """
        token = os.environ.get("INFOMANIAK_NEWSLETTER_TOKEN")
        newsletter_id = os.environ.get("INFOMANIAK_NEWSLETTER_ID")

        if not token or not newsletter_id:
            raise ValueError(
                "Missing required environment variables: "
                "INFOMANIAK_NEWSLETTER_TOKEN, INFOMANIAK_NEWSLETTER_ID"
            )

        return cls(token=token, newsletter_id=newsletter_id)

    @classmethod
    def from_credentials(
        cls,
        token: str,
        newsletter_id: str,
        base_url: str = BASE_URL,
    ) -> "InfomaniakNewsletterClient":
        """Create client from explicit credentials."""
        return cls(token=token, newsletter_id=newsletter_id, base_url=base_url)

    def validate_connection(self) -> bool:
        """Health check by fetching newsletter credits."""
        result = self._get("credits")
        return result is not None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        """Build full API URL."""
        return f"{self._base_url}/1/newsletters/{self._newsletter_id}/{path}"

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any | None:
        """Perform GET request."""
        try:
            resp = self._session.get(self._url(path), params=params)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", data)
        except Exception as e:
            classified = classify_http_error(
                e, service=self._service_name, operation=f"GET {path}"
            )
            logger.error("GET %s failed: %s", path, classified)
            return None

    def _post(self, path: str, json_data: dict[str, Any] | None = None) -> Any | None:
        """Perform POST request."""
        try:
            resp = self._session.post(self._url(path), json=json_data)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", data)
        except Exception as e:
            classified = classify_http_error(
                e, service=self._service_name, operation=f"POST {path}"
            )
            logger.error("POST %s failed: %s", path, classified)
            return None

    def _put(self, path: str, json_data: dict[str, Any] | None = None) -> Any | None:
        """Perform PUT request."""
        try:
            resp = self._session.put(self._url(path), json=json_data)
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", data)
        except Exception as e:
            classified = classify_http_error(
                e, service=self._service_name, operation=f"PUT {path}"
            )
            logger.error("PUT %s failed: %s", path, classified)
            return None

    def _delete(self, path: str) -> bool:
        """Perform DELETE request."""
        try:
            resp = self._session.delete(self._url(path))
            resp.raise_for_status()
            return True
        except Exception as e:
            classified = classify_http_error(
                e, service=self._service_name, operation=f"DELETE {path}"
            )
            logger.error("DELETE %s failed: %s", path, classified)
            return False

    # ------------------------------------------------------------------
    # Campaigns
    # ------------------------------------------------------------------

    def list_campaigns(self) -> list[dict[str, Any]]:
        """List all campaigns."""
        result = self._get("campaigns")
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return result.get("items", result.get("data", []))
        return []

    def get_campaign(self, campaign_id: str) -> dict[str, Any] | None:
        """Get campaign details."""
        return self._get(f"campaigns/{campaign_id}")

    def create_campaign(
        self,
        subject: str,
        sender_email: str,
        sender_name: str,
        content_html: str,
        mailing_list_id: str,
    ) -> dict[str, Any] | None:
        """Create a new campaign."""
        payload = {
            "subject": subject,
            "sender_email": sender_email,
            "sender_name": sender_name,
            "content": content_html,
            "mailing_list_id": mailing_list_id,
        }
        return self._post("campaigns", json_data=payload)

    def update_campaign(self, campaign_id: str, **kwargs: Any) -> dict[str, Any] | None:
        """Update a campaign. Pass keyword arguments for fields to update."""
        return self._put(f"campaigns/{campaign_id}", json_data=kwargs)

    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign."""
        return self._delete(f"campaigns/{campaign_id}")

    def send_test(self, campaign_id: str, email: str) -> bool:
        """Send a test email for a campaign."""
        result = self._post(
            f"campaigns/{campaign_id}/test",
            json_data={"email": email},
        )
        return result is not None

    def schedule_campaign(self, campaign_id: str, send_at: str) -> bool:
        """Schedule a campaign for future delivery.

        Args:
            campaign_id: Campaign ID.
            send_at: ISO 8601 datetime string for scheduled send time.
        """
        result = self._post(
            f"campaigns/{campaign_id}/schedule",
            json_data={"send_at": send_at},
        )
        return result is not None

    def unschedule_campaign(self, campaign_id: str) -> bool:
        """Cancel a scheduled campaign."""
        result = self._post(f"campaigns/{campaign_id}/unschedule")
        return result is not None

    def send_campaign(self, campaign_id: str) -> bool:
        """Send a campaign immediately."""
        result = self._post(f"campaigns/{campaign_id}/send")
        return result is not None

    def get_campaign_statistics(self, campaign_id: str) -> dict[str, Any] | None:
        """Get campaign statistics (opens, clicks, bounces, etc.)."""
        return self._get(f"campaigns/{campaign_id}/statistics")

    # ------------------------------------------------------------------
    # Mailing Lists
    # ------------------------------------------------------------------

    def list_mailing_lists(self) -> list[dict[str, Any]]:
        """List all mailing lists."""
        result = self._get("mailing-lists")
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return result.get("items", result.get("data", []))
        return []

    def get_mailing_list(self, list_id: str) -> dict[str, Any] | None:
        """Get mailing list details."""
        return self._get(f"mailing-lists/{list_id}")

    def create_mailing_list(self, name: str) -> dict[str, Any] | None:
        """Create a new mailing list."""
        return self._post("mailing-lists", json_data={"name": name})

    def update_mailing_list(self, list_id: str, **kwargs: Any) -> dict[str, Any] | None:
        """Update a mailing list."""
        return self._put(f"mailing-lists/{list_id}", json_data=kwargs)

    def delete_mailing_list(self, list_id: str) -> bool:
        """Delete a mailing list."""
        return self._delete(f"mailing-lists/{list_id}")

    def get_list_contacts(self, list_id: str) -> list[dict[str, Any]]:
        """Get contacts in a mailing list."""
        result = self._get(f"mailing-lists/{list_id}/contacts")
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return result.get("items", result.get("data", []))
        return []

    def import_contacts(
        self, list_id: str, contacts: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Import contacts into a mailing list.

        Args:
            list_id: Mailing list ID.
            contacts: List of contact dicts with at least 'email' key.
        """
        return self._post(
            f"mailing-lists/{list_id}/contacts/import",
            json_data={"contacts": contacts},
        )

    _VALID_ACTIONS = frozenset({"subscribe", "unsubscribe"})

    def manage_contact(
        self, list_id: str, contact_id: str, action: str
    ) -> bool:
        """Manage a contact's subscription status in a mailing list.

        Args:
            list_id: Mailing list ID.
            contact_id: Contact ID.
            action: One of 'subscribe', 'unsubscribe'.

        Raises:
            ValueError: If action is not 'subscribe' or 'unsubscribe'.
        """
        if action not in self._VALID_ACTIONS:
            raise ValueError(
                f"Invalid action {action!r}; must be one of {sorted(self._VALID_ACTIONS)}"
            )
        result = self._post(
            f"mailing-lists/{list_id}/contacts/{contact_id}/{action}",
        )
        return result is not None

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------

    def get_contact(self, contact_id: str) -> dict[str, Any] | None:
        """Get contact details."""
        return self._get(f"contacts/{contact_id}")

    def update_contact(self, contact_id: str, **kwargs: Any) -> dict[str, Any] | None:
        """Update a contact."""
        return self._put(f"contacts/{contact_id}", json_data=kwargs)

    def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact."""
        return self._delete(f"contacts/{contact_id}")

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        """Check the status of an asynchronous task."""
        return self._get(f"tasks/{task_id}")

    def get_credits(self) -> dict[str, Any] | None:
        """Get newsletter credit balance."""
        return self._get("credits")
