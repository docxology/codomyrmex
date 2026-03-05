"""Zero-mock tests for cloud/google_workspace SDK module.

Tests exception/auth class logic directly without SDK calls.
Tests requiring the SDK or live credentials are guarded with skipif.
"""

from __future__ import annotations

import importlib.util
import os

import pytest

_SDK_INSTALLED = importlib.util.find_spec("googleapiclient") is not None
_GWS_CREDS_SET = bool(
    os.getenv("GWS_SERVICE_ACCOUNT_FILE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
)

pytestmark = pytest.mark.google_workspace


class TestGoogleWorkspaceExceptions:
    """Test exception class hierarchy."""

    def test_error_is_exception(self):
        from codomyrmex.cloud.google_workspace.exceptions import GoogleWorkspaceError

        exc = GoogleWorkspaceError("test")
        assert isinstance(exc, Exception)

    def test_auth_error_inherits_base(self):
        from codomyrmex.cloud.google_workspace.exceptions import (
            GoogleWorkspaceAuthError,
            GoogleWorkspaceError,
        )

        exc = GoogleWorkspaceAuthError("no creds")
        assert isinstance(exc, GoogleWorkspaceError)

    def test_not_found_error_inherits_base(self):
        from codomyrmex.cloud.google_workspace.exceptions import (
            GoogleWorkspaceError,
            GoogleWorkspaceNotFoundError,
        )

        exc = GoogleWorkspaceNotFoundError("not found")
        assert isinstance(exc, GoogleWorkspaceError)

    def test_quota_error_inherits_base(self):
        from codomyrmex.cloud.google_workspace.exceptions import (
            GoogleWorkspaceError,
            GoogleWorkspaceQuotaError,
        )

        exc = GoogleWorkspaceQuotaError("quota exceeded")
        assert isinstance(exc, GoogleWorkspaceError)

    def test_api_error_attrs(self):
        from codomyrmex.cloud.google_workspace.exceptions import GoogleWorkspaceAPIError

        exc = GoogleWorkspaceAPIError("bad request", status_code=400, reason="Bad Request")
        assert exc.status_code == 400
        assert exc.reason == "Bad Request"
        assert str(exc) == "bad request"

    def test_api_error_defaults(self):
        from codomyrmex.cloud.google_workspace.exceptions import GoogleWorkspaceAPIError

        exc = GoogleWorkspaceAPIError("err")
        assert exc.status_code == 0
        assert exc.reason == ""

    def test_all_error_types_are_distinct(self):
        from codomyrmex.cloud.google_workspace.exceptions import (
            GoogleWorkspaceAPIError,
            GoogleWorkspaceAuthError,
            GoogleWorkspaceError,
            GoogleWorkspaceNotFoundError,
            GoogleWorkspaceQuotaError,
        )

        types = [
            GoogleWorkspaceError,
            GoogleWorkspaceAuthError,
            GoogleWorkspaceNotFoundError,
            GoogleWorkspaceQuotaError,
            GoogleWorkspaceAPIError,
        ]
        assert len(set(types)) == len(types)

    def test_exception_message_preserved(self):
        from codomyrmex.cloud.google_workspace.exceptions import GoogleWorkspaceError

        msg = "something went wrong"
        exc = GoogleWorkspaceError(msg)
        assert str(exc) == msg


class TestGoogleCredentialsInit:
    """Test GoogleCredentials without SDK calls."""

    def test_from_env_raises_when_no_creds(self):
        saved_sa = os.environ.pop("GWS_SERVICE_ACCOUNT_FILE", None)
        saved_app = os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        try:
            from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
            from codomyrmex.cloud.google_workspace.exceptions import (
                GoogleWorkspaceAuthError,
            )

            with pytest.raises(GoogleWorkspaceAuthError):
                GoogleCredentials.from_env()
        finally:
            if saved_sa is not None:
                os.environ["GWS_SERVICE_ACCOUNT_FILE"] = saved_sa
            if saved_app is not None:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = saved_app

    def test_from_env_prefers_gws_service_account_file(self):
        saved_sa = os.environ.get("GWS_SERVICE_ACCOUNT_FILE")
        saved_app = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["GWS_SERVICE_ACCOUNT_FILE"] = "/path/to/sa.json"
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/other/path.json"
        try:
            from codomyrmex.cloud.google_workspace.auth import GoogleCredentials

            creds = GoogleCredentials.from_env()
            assert creds._credentials_file == "/path/to/sa.json"
        finally:
            if saved_sa is None:
                os.environ.pop("GWS_SERVICE_ACCOUNT_FILE", None)
            else:
                os.environ["GWS_SERVICE_ACCOUNT_FILE"] = saved_sa
            if saved_app is None:
                os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
            else:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = saved_app

    def test_from_env_falls_back_to_google_application_credentials(self):
        saved_sa = os.environ.pop("GWS_SERVICE_ACCOUNT_FILE", None)
        saved_app = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/fallback/path.json"
        try:
            from codomyrmex.cloud.google_workspace.auth import GoogleCredentials

            creds = GoogleCredentials.from_env()
            assert creds._credentials_file == "/fallback/path.json"
        finally:
            if saved_sa is not None:
                os.environ["GWS_SERVICE_ACCOUNT_FILE"] = saved_sa
            if saved_app is None:
                os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
            else:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = saved_app

    def test_from_service_account_file_sets_path(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials

        creds = GoogleCredentials.from_service_account_file("/some/path.json")
        assert creds._credentials_file == "/some/path.json"

    def test_default_scopes_populated(self):
        from codomyrmex.cloud.google_workspace.auth import (
            _DEFAULT_SCOPES,
            GoogleCredentials,
        )

        creds = GoogleCredentials(credentials_file="/path/to/sa.json")
        assert creds._scopes == _DEFAULT_SCOPES

    def test_custom_scopes_accepted(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials

        scopes = ["https://www.googleapis.com/auth/drive.readonly"]
        creds = GoogleCredentials(credentials_file="/p.json", scopes=scopes)
        assert creds._scopes == scopes

    def test_credentials_file_stored(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials

        creds = GoogleCredentials(credentials_file="/my/creds.json")
        assert creds._credentials_file == "/my/creds.json"

    def test_initial_creds_none(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials

        creds = GoogleCredentials(credentials_file="/path.json")
        assert creds._creds is None

    def test_get_credentials_raises_without_sdk(self):
        """Raises ImportError when google-auth not installed (no SDK in test env)."""
        if _SDK_INSTALLED:
            pytest.skip("google-auth SDK is installed — ImportError path not reachable")
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials

        creds = GoogleCredentials(credentials_file="/nonexistent.json")
        with pytest.raises(ImportError, match="google-auth"):
            creds.get_credentials()

    def test_build_service_raises_without_sdk(self):
        """Raises ImportError when google-api-python-client not installed."""
        if _SDK_INSTALLED:
            pytest.skip("google-api-python-client is installed — ImportError path not reachable")
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials

        creds = GoogleCredentials(credentials_file="/nonexistent.json")
        with pytest.raises(ImportError, match="google-api-python-client"):
            creds.build_service("drive", "v3")

    def test_default_scopes_includes_drive(self):
        from codomyrmex.cloud.google_workspace.auth import _DEFAULT_SCOPES

        assert any("drive" in s for s in _DEFAULT_SCOPES)

    def test_default_scopes_includes_gmail(self):
        from codomyrmex.cloud.google_workspace.auth import _DEFAULT_SCOPES

        assert any("gmail" in s for s in _DEFAULT_SCOPES)

    def test_default_scopes_includes_calendar(self):
        from codomyrmex.cloud.google_workspace.auth import _DEFAULT_SCOPES

        assert any("calendar" in s for s in _DEFAULT_SCOPES)


class TestGoogleWorkspaceBaseInit:
    """Test GoogleWorkspaceBase class attributes and context manager."""

    def test_api_name_default_empty(self):
        from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase

        assert GoogleWorkspaceBase._api_name == ""

    def test_api_version_default_v3(self):
        from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase

        assert GoogleWorkspaceBase._api_version == "v3"

    def test_context_manager_enter_returns_self(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleWorkspaceBase(creds)
        assert client.__enter__() is client

    def test_context_manager_exit_returns_false(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleWorkspaceBase(creds)
        assert client.__exit__(None, None, None) is False

    def test_safe_call_returns_default_on_exception(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleWorkspaceBase(creds)

        def failing_op():
            raise RuntimeError("API down")

        result = client._safe_call(failing_op, "list", "files", default=[])
        assert result == []

    def test_safe_call_returns_value_on_success(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleWorkspaceBase(creds)

        result = client._safe_call(lambda: {"files": []}, "list", "files")
        assert result == {"files": []}

    def test_safe_call_default_none_when_unspecified(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleWorkspaceBase(creds)

        result = client._safe_call(lambda: (_ for _ in ()).throw(ValueError("oops")), "get", "item")
        assert result is None

    def test_credentials_stored(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleWorkspaceBase(creds)
        assert client._credentials is creds

    def test_service_initially_none(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleWorkspaceBase(creds)
        assert client._service is None

    def test_from_env_raises_without_creds(self):
        saved_sa = os.environ.pop("GWS_SERVICE_ACCOUNT_FILE", None)
        saved_app = os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        try:
            from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase
            from codomyrmex.cloud.google_workspace.exceptions import (
                GoogleWorkspaceAuthError,
            )

            with pytest.raises(GoogleWorkspaceAuthError):
                GoogleWorkspaceBase.from_env()
        finally:
            if saved_sa is not None:
                os.environ["GWS_SERVICE_ACCOUNT_FILE"] = saved_sa
            if saved_app is not None:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = saved_app


class TestClientApiAttributes:
    """Test that each client sets correct _api_name and _api_version."""

    def test_drive_client_api_attrs(self):
        from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient

        assert GoogleDriveClient._api_name == "drive"
        assert GoogleDriveClient._api_version == "v3"

    def test_gmail_client_api_attrs(self):
        from codomyrmex.cloud.google_workspace.gmail import GoogleGmailClient

        assert GoogleGmailClient._api_name == "gmail"
        assert GoogleGmailClient._api_version == "v1"

    def test_calendar_client_api_attrs(self):
        from codomyrmex.cloud.google_workspace.calendar import GoogleCalendarClient

        assert GoogleCalendarClient._api_name == "calendar"
        assert GoogleCalendarClient._api_version == "v3"

    def test_sheets_client_api_attrs(self):
        from codomyrmex.cloud.google_workspace.sheets import GoogleSheetsClient

        assert GoogleSheetsClient._api_name == "sheets"
        assert GoogleSheetsClient._api_version == "v4"

    def test_docs_client_api_attrs(self):
        from codomyrmex.cloud.google_workspace.docs import GoogleDocsClient

        assert GoogleDocsClient._api_name == "docs"
        assert GoogleDocsClient._api_version == "v1"

    def test_chat_client_api_attrs(self):
        from codomyrmex.cloud.google_workspace.chat import GoogleChatClient

        assert GoogleChatClient._api_name == "chat"
        assert GoogleChatClient._api_version == "v1"

    def test_all_clients_inherit_base(self):
        from codomyrmex.cloud.google_workspace.base import GoogleWorkspaceBase
        from codomyrmex.cloud.google_workspace.calendar import GoogleCalendarClient
        from codomyrmex.cloud.google_workspace.chat import GoogleChatClient
        from codomyrmex.cloud.google_workspace.docs import GoogleDocsClient
        from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient
        from codomyrmex.cloud.google_workspace.gmail import GoogleGmailClient
        from codomyrmex.cloud.google_workspace.sheets import GoogleSheetsClient

        for client_cls in [
            GoogleDriveClient,
            GoogleGmailClient,
            GoogleCalendarClient,
            GoogleSheetsClient,
            GoogleDocsClient,
            GoogleChatClient,
        ]:
            assert issubclass(client_cls, GoogleWorkspaceBase), (
                f"{client_cls.__name__} does not inherit from GoogleWorkspaceBase"
            )


class TestFromEnvRaisesWithoutCreds:
    """Test that from_env() raises GoogleWorkspaceAuthError without creds."""

    def test_drive_from_env_raises_without_creds(self):
        saved_sa = os.environ.pop("GWS_SERVICE_ACCOUNT_FILE", None)
        saved_app = os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        try:
            from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient
            from codomyrmex.cloud.google_workspace.exceptions import (
                GoogleWorkspaceAuthError,
            )

            with pytest.raises(GoogleWorkspaceAuthError):
                GoogleDriveClient.from_env()
        finally:
            if saved_sa is not None:
                os.environ["GWS_SERVICE_ACCOUNT_FILE"] = saved_sa
            if saved_app is not None:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = saved_app

    def test_gmail_from_env_raises_without_creds(self):
        saved_sa = os.environ.pop("GWS_SERVICE_ACCOUNT_FILE", None)
        saved_app = os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
        try:
            from codomyrmex.cloud.google_workspace.exceptions import (
                GoogleWorkspaceAuthError,
            )
            from codomyrmex.cloud.google_workspace.gmail import GoogleGmailClient

            with pytest.raises(GoogleWorkspaceAuthError):
                GoogleGmailClient.from_env()
        finally:
            if saved_sa is not None:
                os.environ["GWS_SERVICE_ACCOUNT_FILE"] = saved_sa
            if saved_app is not None:
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = saved_app


class TestDriveClientBehavior:
    """Test GoogleDriveClient logic that doesn't require a live API service."""

    def test_list_files_returns_list_on_safe_call_default(self):
        """_safe_call returns {} on failure; list_files extracts [] from that."""
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleDriveClient(creds)
        # _get_service() will fail since no real credentials; _safe_call returns default={}
        # list_files handles that gracefully
        result = client.list_files()
        assert isinstance(result, list)

    def test_get_file_returns_dict_on_failure(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleDriveClient(creds)
        result = client.get_file("nonexistent-id")
        assert isinstance(result, dict)

    def test_delete_file_returns_false_on_failure(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleDriveClient(creds)
        result = client.delete_file("nonexistent-id")
        assert result is False

    def test_share_file_returns_dict_on_failure(self):
        from codomyrmex.cloud.google_workspace.auth import GoogleCredentials
        from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient

        creds = GoogleCredentials(credentials_file="/fake.json")
        client = GoogleDriveClient(creds)
        result = client.share_file("file-id", "user@example.com")
        assert isinstance(result, dict)


class TestLiveSDKClients:
    """Live API tests — only run when SDK is installed and creds are configured."""

    @pytest.mark.slow
    @pytest.mark.skipif(not _SDK_INSTALLED, reason="google-api-python-client not installed")
    @pytest.mark.skipif(not _GWS_CREDS_SET, reason="GWS credentials not configured")
    def test_drive_list_files_returns_list(self):
        from codomyrmex.cloud.google_workspace.drive import GoogleDriveClient

        client = GoogleDriveClient.from_env()
        files = client.list_files(page_size=5)
        assert isinstance(files, list)

    @pytest.mark.slow
    @pytest.mark.skipif(not _SDK_INSTALLED, reason="google-api-python-client not installed")
    @pytest.mark.skipif(not _GWS_CREDS_SET, reason="GWS credentials not configured")
    def test_gmail_list_messages_returns_list(self):
        from codomyrmex.cloud.google_workspace.gmail import GoogleGmailClient

        client = GoogleGmailClient.from_env()
        messages = client.list_messages(max_results=5)
        assert isinstance(messages, list)
