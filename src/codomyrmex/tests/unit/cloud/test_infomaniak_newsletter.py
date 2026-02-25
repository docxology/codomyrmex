"""
Unit tests for Infomaniak newsletter.

Zero ``unittest.mock`` — uses ``Stub`` from ``conftest.py``.
"""

import os

import pytest
from _stubs import Stub

# =========================================================================

class TestInfomaniakNewsletterClient:
    """Tests for InfomaniakNewsletterClient.

    Uses instance-level mocking: creates a real client (exercises __init__,
    URL construction, header setup, payload building), then replaces
    ``_session.get/post/put/delete`` with mocks so only HTTP transport
    is faked.
    """

    BASE = "https://api.infomaniak.com"
    NL_ID = "nl-123"
    URL_PREFIX = f"{BASE}/1/newsletters/{NL_ID}"

    def _make_client(self):
        """Create a newsletter client and replace its session with a mock."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        client = InfomaniakNewsletterClient(
            token="test-token",
            newsletter_id=self.NL_ID,
            base_url=self.BASE,
        )
        client._session = Stub()
        return client

    @staticmethod
    def _mock_response(json_data, status_code=200):
        resp = Stub()
        resp.status_code = status_code
        resp.json.return_value = json_data
        resp.raise_for_status = Stub()
        return resp

    # ------------------------------------------------------------------
    # Factory methods & construction
    # ------------------------------------------------------------------

    def test_from_credentials(self):
        """from_credentials stores token and newsletter_id."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        client = InfomaniakNewsletterClient.from_credentials(
            token="tok-abc", newsletter_id="nl-456",
        )
        assert client._token == "tok-abc"
        assert client._newsletter_id == "nl-456"

    def test_from_env(self, monkeypatch):
        """from_env reads correct environment variables."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        monkeypatch.setenv("INFOMANIAK_NEWSLETTER_TOKEN", "env-token")
        monkeypatch.setenv("INFOMANIAK_NEWSLETTER_ID", "env-nl-id")

        client = InfomaniakNewsletterClient.from_env()
        assert client._token == "env-token"
        assert client._newsletter_id == "env-nl-id"

    def test_from_env_missing(self, monkeypatch):
        """from_env raises ValueError when env vars are missing."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        for key in list(os.environ):
            if key.startswith("INFOMANIAK_NEWSLETTER"):
                monkeypatch.delenv(key, raising=False)
        with pytest.raises(ValueError, match="Missing required environment variables"):
            InfomaniakNewsletterClient.from_env()

    def test_auth_header_set(self):
        """__init__ sets Authorization Bearer header on session."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient

        client = InfomaniakNewsletterClient(
            token="my-secret-token", newsletter_id="nl-1",
        )
        assert client._session.headers["Authorization"] == "Bearer my-secret-token"
        assert client._session.headers["Content-Type"] == "application/json"

    def test_context_manager(self):
        """Context manager protocol calls close on exit."""
        client = self._make_client()
        client.__enter__()
        client.__exit__(None, None, None)
        client._session.close.assert_called_once()

    def test_inherits_rest_base(self):
        """Client inherits from InfomaniakRESTBase."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase
        client = self._make_client()
        assert isinstance(client, InfomaniakRESTBase)

    def test_validate_connection(self):
        """validate_connection calls GET credits endpoint."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"remaining": 100}},
        )
        assert client.validate_connection() is True
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/credits"

    # ------------------------------------------------------------------
    # Campaign operations
    # ------------------------------------------------------------------

    def test_list_campaigns(self):
        """list_campaigns GETs campaigns URL and returns list."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": [{"id": "c-1", "subject": "Hello"}]},
        )
        result = client.list_campaigns()

        assert len(result) == 1
        assert result[0]["id"] == "c-1"
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns"

    def test_get_campaign(self):
        """get_campaign GETs campaign by ID."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"id": "c-99", "subject": "Detail"}},
        )
        result = client.get_campaign("c-99")

        assert result["id"] == "c-99"
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-99"

    def test_create_campaign(self):
        """create_campaign POSTs with all 5 payload fields."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"id": "c-new"}},
        )
        result = client.create_campaign(
            subject="New",
            sender_email="news@test.com",
            sender_name="Tester",
            content_html="<p>Hi</p>",
            mailing_list_id="ml-1",
        )

        assert result["id"] == "c-new"
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns"
        payload = client._session.post.call_args[1]["json"]
        assert payload["subject"] == "New"
        assert payload["sender_email"] == "news@test.com"
        assert payload["sender_name"] == "Tester"
        assert payload["content"] == "<p>Hi</p>"
        assert payload["mailing_list_id"] == "ml-1"

    def test_update_campaign(self):
        """update_campaign PUTs kwargs to campaign URL."""
        client = self._make_client()
        client._session.put.return_value = self._mock_response(
            {"data": {"id": "c-1", "subject": "Updated"}},
        )
        result = client.update_campaign("c-1", subject="Updated")

        assert result["subject"] == "Updated"
        url = client._session.put.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1"
        payload = client._session.put.call_args[1]["json"]
        assert payload == {"subject": "Updated"}

    def test_delete_campaign(self):
        """delete_campaign DELETEs campaign URL and returns True."""
        client = self._make_client()
        resp = Stub()
        resp.raise_for_status = Stub()
        client._session.delete.return_value = resp

        assert client.delete_campaign("c-del") is True
        url = client._session.delete.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-del"

    def test_send_test(self):
        """send_test POSTs email payload to test endpoint."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"status": "sent"}},
        )
        assert client.send_test("c-1", "test@example.com") is True
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1/test"
        payload = client._session.post.call_args[1]["json"]
        assert payload == {"email": "test@example.com"}

    def test_schedule_campaign(self):
        """schedule_campaign POSTs send_at to schedule endpoint."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"scheduled": True}},
        )
        assert client.schedule_campaign("c-1", "2026-03-01T10:00:00Z") is True
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1/schedule"
        payload = client._session.post.call_args[1]["json"]
        assert payload == {"send_at": "2026-03-01T10:00:00Z"}

    def test_unschedule_campaign(self):
        """unschedule_campaign POSTs to unschedule endpoint."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"unscheduled": True}},
        )
        assert client.unschedule_campaign("c-1") is True
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1/unschedule"

    def test_send_campaign(self):
        """send_campaign POSTs to send endpoint."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"status": "sending"}},
        )
        assert client.send_campaign("c-1") is True
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1/send"

    def test_get_campaign_statistics(self):
        """get_campaign_statistics GETs statistics URL."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"sent": 1000, "opened": 450}},
        )
        stats = client.get_campaign_statistics("c-1")

        assert stats["sent"] == 1000
        assert stats["opened"] == 450
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/campaigns/c-1/statistics"

    # ------------------------------------------------------------------
    # Mailing list operations
    # ------------------------------------------------------------------

    def test_list_mailing_lists(self):
        """list_mailing_lists GETs mailing-lists URL."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": [{"id": "ml-1", "name": "Subs"}, {"id": "ml-2", "name": "VIPs"}]},
        )
        result = client.list_mailing_lists()

        assert len(result) == 2
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists"

    def test_get_mailing_list(self):
        """get_mailing_list GETs specific list by ID."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"id": "ml-1", "name": "Subs"}},
        )
        result = client.get_mailing_list("ml-1")

        assert result["id"] == "ml-1"
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-1"

    def test_create_mailing_list(self):
        """create_mailing_list POSTs name payload."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"id": "ml-new", "name": "New List"}},
        )
        result = client.create_mailing_list("New List")

        assert result["name"] == "New List"
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists"
        payload = client._session.post.call_args[1]["json"]
        assert payload == {"name": "New List"}

    def test_update_mailing_list(self):
        """update_mailing_list PUTs kwargs."""
        client = self._make_client()
        client._session.put.return_value = self._mock_response(
            {"data": {"id": "ml-1", "name": "Renamed"}},
        )
        result = client.update_mailing_list("ml-1", name="Renamed")

        assert result["name"] == "Renamed"
        url = client._session.put.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-1"

    def test_delete_mailing_list(self):
        """delete_mailing_list DELETEs list URL."""
        client = self._make_client()
        resp = Stub()
        resp.raise_for_status = Stub()
        client._session.delete.return_value = resp

        assert client.delete_mailing_list("ml-del") is True
        url = client._session.delete.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-del"

    def test_get_list_contacts(self):
        """get_list_contacts GETs contacts for a list."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": [{"id": "ct-1", "email": "a@test.com"}]},
        )
        result = client.get_list_contacts("ml-1")

        assert len(result) == 1
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-1/contacts"

    def test_import_contacts(self):
        """import_contacts POSTs contacts list."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"task_id": "task-123", "imported": 3}},
        )
        contacts = [{"email": "a@test.com"}, {"email": "b@test.com"}]
        result = client.import_contacts("ml-1", contacts)

        assert result["task_id"] == "task-123"
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-1/contacts/import"
        payload = client._session.post.call_args[1]["json"]
        assert payload == {"contacts": contacts}

    def test_manage_contact(self):
        """manage_contact POSTs to action URL."""
        client = self._make_client()
        client._session.post.return_value = self._mock_response(
            {"data": {"subscribed": True}},
        )
        assert client.manage_contact("ml-1", "ct-5", "subscribe") is True
        url = client._session.post.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/mailing-lists/ml-1/contacts/ct-5/subscribe"

    # ------------------------------------------------------------------
    # Contact operations
    # ------------------------------------------------------------------

    def test_get_contact(self):
        """get_contact GETs contact by ID."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"id": "ct-1", "email": "a@test.com"}},
        )
        result = client.get_contact("ct-1")

        assert result["email"] == "a@test.com"
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/contacts/ct-1"

    def test_update_contact(self):
        """update_contact PUTs kwargs."""
        client = self._make_client()
        client._session.put.return_value = self._mock_response(
            {"data": {"id": "ct-1", "name": "Updated"}},
        )
        result = client.update_contact("ct-1", name="Updated")

        assert result["name"] == "Updated"
        url = client._session.put.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/contacts/ct-1"
        payload = client._session.put.call_args[1]["json"]
        assert payload == {"name": "Updated"}

    def test_delete_contact(self):
        """delete_contact DELETEs contact URL."""
        client = self._make_client()
        resp = Stub()
        resp.raise_for_status = Stub()
        client._session.delete.return_value = resp

        assert client.delete_contact("ct-del") is True
        url = client._session.delete.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/contacts/ct-del"

    # ------------------------------------------------------------------
    # Utility operations
    # ------------------------------------------------------------------

    def test_get_task_status(self):
        """get_task_status GETs tasks URL."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"id": "t-1", "status": "completed"}},
        )
        result = client.get_task_status("t-1")

        assert result["status"] == "completed"
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/tasks/t-1"

    def test_get_credits(self):
        """get_credits GETs credits URL."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"remaining": 5000, "used": 1500}},
        )
        credits = client.get_credits()

        assert credits["remaining"] == 5000
        url = client._session.get.call_args[0][0]
        assert url == f"{self.URL_PREFIX}/credits"

    # ------------------------------------------------------------------
    # Error paths
    # ------------------------------------------------------------------

    def test_error_get_returns_none(self):
        """GET error returns None."""
        client = self._make_client()
        resp = Stub()
        resp.raise_for_status.side_effect = Exception("500 Server Error")
        client._session.get.return_value = resp

        assert client.get_campaign("c-1") is None

    def test_error_post_returns_none(self):
        """POST error returns None (bool methods return False)."""
        client = self._make_client()
        resp = Stub()
        resp.raise_for_status.side_effect = Exception("500 Server Error")
        client._session.post.return_value = resp

        assert client.send_campaign("c-1") is False

    def test_error_delete_returns_false(self):
        """DELETE error returns False."""
        client = self._make_client()
        resp = Stub()
        resp.raise_for_status.side_effect = Exception("500 Server Error")
        client._session.delete.return_value = resp

        assert client.delete_campaign("c-1") is False

    def test_list_returns_empty_on_error(self):
        """list_campaigns and list_mailing_lists return [] on error."""
        client = self._make_client()
        resp = Stub()
        resp.raise_for_status.side_effect = Exception("Connection refused")
        client._session.get.return_value = resp

        assert client.list_campaigns() == []
        assert client.list_mailing_lists() == []

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_list_campaigns_dict_response(self):
        """list_campaigns extracts items from dict-wrapped response."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"data": {"total": 5, "items": [{"id": "c1"}]}},
        )
        result = client.list_campaigns()
        # Dict-wrapped response: items extracted
        assert isinstance(result, list)
        assert result == [{"id": "c1"}]

    def test_list_campaigns_none_response(self):
        """list_campaigns returns [] when _get returns None."""
        client = self._make_client()
        resp = Stub()
        resp.raise_for_status.side_effect = Exception("error")
        client._session.get.return_value = resp

        assert client.list_campaigns() == []

    def test_get_response_without_data_key(self):
        """_get returns full dict when no 'data' key in response."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response(
            {"result": "ok", "value": 42},
        )
        result = client.get_credits()
        # dict.get("data", dict) returns dict itself
        assert result["result"] == "ok"
        assert result["value"] == 42

    def test_put_error_returns_none(self):
        """PUT error returns None."""
        client = self._make_client()
        resp = Stub()
        resp.raise_for_status.side_effect = Exception("500 Server Error")
        client._session.put.return_value = resp

        assert client.update_campaign("c-1", subject="X") is None

    def test_base_url_trailing_slash_stripped(self):
        """Trailing slash in base_url is stripped."""
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(
            token="t", newsletter_id="n", base_url="https://api.test.com/"
        )
        assert client._base_url == "https://api.test.com"

    def test_service_name_is_newsletter(self):
        """Client _service_name is 'newsletter'."""
        client = self._make_client()
        assert client._service_name == "newsletter"

    def test_get_list_contacts_empty(self):
        """get_list_contacts returns [] for empty contact list."""
        client = self._make_client()
        client._session.get.return_value = self._mock_response({"data": []})
        assert client.get_list_contacts("ml-1") == []

    def test_validate_connection_failure(self):
        """validate_connection returns False on error."""
        client = self._make_client()
        resp = Stub()
        resp.raise_for_status.side_effect = Exception("timeout")
        client._session.get.return_value = resp

        assert client.validate_connection() is False


# =========================================================================
# Test Exception Hierarchy
# =========================================================================


# =========================================================================

class TestNewsletterValidationExpanded:
    """Tests for newsletter input validation and edge cases."""

    def _make_client(self):
        from codomyrmex.cloud.infomaniak.newsletter import InfomaniakNewsletterClient
        client = InfomaniakNewsletterClient(
            token="test-token", newsletter_id="nl-1",
            base_url="https://api.infomaniak.com"
        )
        client._session = Stub()
        return client

    def test_manage_contact_invalid_action(self):
        """manage_contact raises ValueError for invalid action."""
        client = self._make_client()
        with pytest.raises(ValueError, match="Invalid action"):
            client.manage_contact("list-1", "contact-1", "delete")

    def test_manage_contact_subscribe(self):
        """manage_contact accepts 'subscribe' action."""
        client = self._make_client()
        resp = Stub(status_code=200)
        resp.json.return_value = {"data": {"ok": True}}
        resp.raise_for_status = Stub()
        client._session.post.return_value = resp
        assert client.manage_contact("list-1", "c1", "subscribe") is True

    def test_manage_contact_unsubscribe(self):
        """manage_contact accepts 'unsubscribe' action."""
        client = self._make_client()
        resp = Stub(status_code=200)
        resp.json.return_value = {"data": {"ok": True}}
        resp.raise_for_status = Stub()
        client._session.post.return_value = resp
        assert client.manage_contact("list-1", "c1", "unsubscribe") is True

    def test_list_campaigns_dict_with_items_key(self):
        """list_campaigns extracts from dict with 'items' key."""
        client = self._make_client()
        resp = Stub(status_code=200)
        resp.json.return_value = {"data": {"items": [{"id": "c1"}], "total": 1}}
        resp.raise_for_status = Stub()
        client._session.get.return_value = resp
        result = client.list_campaigns()
        assert result == [{"id": "c1"}]

    def test_list_mailing_lists_dict_with_items_key(self):
        """list_mailing_lists extracts from dict with 'items' key."""
        client = self._make_client()
        resp = Stub(status_code=200)
        resp.json.return_value = {"data": {"items": [{"id": "ml1"}], "total": 1}}
        resp.raise_for_status = Stub()
        client._session.get.return_value = resp
        result = client.list_mailing_lists()
        assert result == [{"id": "ml1"}]


