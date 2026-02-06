"""
Unit tests for the CodaClient class.

Tests client initialization, configuration, and method signatures.
Note: These tests do not make actual API calls.
"""

import pytest


@pytest.mark.unit
class TestCodaClientInitialization:
    """Tests for CodaClient initialization."""

    def test_client_requires_api_token(self):
        """Test that CodaClient requires an API token."""
        from codomyrmex.cloud.coda_io import CodaClient

        # Should work with token
        client = CodaClient(api_token="test-token")
        assert client.api_token == "test-token"

    def test_client_default_base_url(self):
        """Test default base URL is set correctly."""
        from codomyrmex.cloud.coda_io import CodaClient

        client = CodaClient(api_token="test-token")

        assert client.base_url == "https://coda.io/apis/v1"

    def test_client_custom_base_url(self):
        """Test custom base URL can be set."""
        from codomyrmex.cloud.coda_io import CodaClient

        client = CodaClient(
            api_token="test-token",
            base_url="https://custom.coda.io/apis/v1",
        )

        assert client.base_url == "https://custom.coda.io/apis/v1"

    def test_client_strips_trailing_slash_from_base_url(self):
        """Test base URL trailing slash is stripped."""
        from codomyrmex.cloud.coda_io import CodaClient

        client = CodaClient(
            api_token="test-token",
            base_url="https://coda.io/apis/v1/",
        )

        assert client.base_url == "https://coda.io/apis/v1"

    def test_client_default_timeout(self):
        """Test default timeout is set."""
        from codomyrmex.cloud.coda_io import CodaClient

        client = CodaClient(api_token="test-token")

        assert client.timeout == 30

    def test_client_custom_timeout(self):
        """Test custom timeout can be set."""
        from codomyrmex.cloud.coda_io import CodaClient

        client = CodaClient(api_token="test-token", timeout=60)

        assert client.timeout == 60

    def test_client_session_headers(self):
        """Test session has correct authorization headers."""
        from codomyrmex.cloud.coda_io import CodaClient

        client = CodaClient(api_token="my-secret-token")

        assert "Authorization" in client.session.headers
        assert client.session.headers["Authorization"] == "Bearer my-secret-token"
        assert client.session.headers["Content-Type"] == "application/json"


@pytest.mark.unit
class TestCodaClientMethods:
    """Tests for CodaClient method existence and signatures."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from codomyrmex.cloud.coda_io import CodaClient
        return CodaClient(api_token="test-token")

    # Docs API
    def test_has_list_docs(self, client):
        """Test client has list_docs method."""
        assert hasattr(client, "list_docs")
        assert callable(client.list_docs)

    def test_has_create_doc(self, client):
        """Test client has create_doc method."""
        assert hasattr(client, "create_doc")
        assert callable(client.create_doc)

    def test_has_get_doc(self, client):
        """Test client has get_doc method."""
        assert hasattr(client, "get_doc")
        assert callable(client.get_doc)

    def test_has_update_doc(self, client):
        """Test client has update_doc method."""
        assert hasattr(client, "update_doc")
        assert callable(client.update_doc)

    def test_has_delete_doc(self, client):
        """Test client has delete_doc method."""
        assert hasattr(client, "delete_doc")
        assert callable(client.delete_doc)

    # Pages API
    def test_has_list_pages(self, client):
        """Test client has list_pages method."""
        assert hasattr(client, "list_pages")
        assert callable(client.list_pages)

    def test_has_create_page(self, client):
        """Test client has create_page method."""
        assert hasattr(client, "create_page")
        assert callable(client.create_page)

    def test_has_get_page(self, client):
        """Test client has get_page method."""
        assert hasattr(client, "get_page")
        assert callable(client.get_page)

    def test_has_update_page(self, client):
        """Test client has update_page method."""
        assert hasattr(client, "update_page")
        assert callable(client.update_page)

    def test_has_delete_page(self, client):
        """Test client has delete_page method."""
        assert hasattr(client, "delete_page")
        assert callable(client.delete_page)

    def test_has_export_page(self, client):
        """Test client has export_page method."""
        assert hasattr(client, "export_page")
        assert callable(client.export_page)

    # Tables API
    def test_has_list_tables(self, client):
        """Test client has list_tables method."""
        assert hasattr(client, "list_tables")
        assert callable(client.list_tables)

    def test_has_get_table(self, client):
        """Test client has get_table method."""
        assert hasattr(client, "get_table")
        assert callable(client.get_table)

    # Columns API
    def test_has_list_columns(self, client):
        """Test client has list_columns method."""
        assert hasattr(client, "list_columns")
        assert callable(client.list_columns)

    def test_has_get_column(self, client):
        """Test client has get_column method."""
        assert hasattr(client, "get_column")
        assert callable(client.get_column)

    # Rows API
    def test_has_list_rows(self, client):
        """Test client has list_rows method."""
        assert hasattr(client, "list_rows")
        assert callable(client.list_rows)

    def test_has_insert_rows(self, client):
        """Test client has insert_rows method."""
        assert hasattr(client, "insert_rows")
        assert callable(client.insert_rows)

    def test_has_get_row(self, client):
        """Test client has get_row method."""
        assert hasattr(client, "get_row")
        assert callable(client.get_row)

    def test_has_update_row(self, client):
        """Test client has update_row method."""
        assert hasattr(client, "update_row")
        assert callable(client.update_row)

    def test_has_delete_row(self, client):
        """Test client has delete_row method."""
        assert hasattr(client, "delete_row")
        assert callable(client.delete_row)

    def test_has_delete_rows(self, client):
        """Test client has delete_rows method."""
        assert hasattr(client, "delete_rows")
        assert callable(client.delete_rows)

    def test_has_push_button(self, client):
        """Test client has push_button method."""
        assert hasattr(client, "push_button")
        assert callable(client.push_button)

    # Permissions API
    def test_has_get_sharing_metadata(self, client):
        """Test client has get_sharing_metadata method."""
        assert hasattr(client, "get_sharing_metadata")
        assert callable(client.get_sharing_metadata)

    def test_has_list_permissions(self, client):
        """Test client has list_permissions method."""
        assert hasattr(client, "list_permissions")
        assert callable(client.list_permissions)

    def test_has_add_permission(self, client):
        """Test client has add_permission method."""
        assert hasattr(client, "add_permission")
        assert callable(client.add_permission)

    def test_has_delete_permission(self, client):
        """Test client has delete_permission method."""
        assert hasattr(client, "delete_permission")
        assert callable(client.delete_permission)

    def test_has_get_acl_settings(self, client):
        """Test client has get_acl_settings method."""
        assert hasattr(client, "get_acl_settings")
        assert callable(client.get_acl_settings)

    def test_has_update_acl_settings(self, client):
        """Test client has update_acl_settings method."""
        assert hasattr(client, "update_acl_settings")
        assert callable(client.update_acl_settings)

    # Publishing API
    def test_has_get_categories(self, client):
        """Test client has get_categories method."""
        assert hasattr(client, "get_categories")
        assert callable(client.get_categories)

    def test_has_publish_doc(self, client):
        """Test client has publish_doc method."""
        assert hasattr(client, "publish_doc")
        assert callable(client.publish_doc)

    def test_has_unpublish_doc(self, client):
        """Test client has unpublish_doc method."""
        assert hasattr(client, "unpublish_doc")
        assert callable(client.unpublish_doc)

    # Formulas API
    def test_has_list_formulas(self, client):
        """Test client has list_formulas method."""
        assert hasattr(client, "list_formulas")
        assert callable(client.list_formulas)

    def test_has_get_formula(self, client):
        """Test client has get_formula method."""
        assert hasattr(client, "get_formula")
        assert callable(client.get_formula)

    # Controls API
    def test_has_list_controls(self, client):
        """Test client has list_controls method."""
        assert hasattr(client, "list_controls")
        assert callable(client.list_controls)

    def test_has_get_control(self, client):
        """Test client has get_control method."""
        assert hasattr(client, "get_control")
        assert callable(client.get_control)

    # Automations API
    def test_has_trigger_automation(self, client):
        """Test client has trigger_automation method."""
        assert hasattr(client, "trigger_automation")
        assert callable(client.trigger_automation)

    # Analytics API
    def test_has_list_doc_analytics(self, client):
        """Test client has list_doc_analytics method."""
        assert hasattr(client, "list_doc_analytics")
        assert callable(client.list_doc_analytics)

    def test_has_get_doc_analytics_summary(self, client):
        """Test client has get_doc_analytics_summary method."""
        assert hasattr(client, "get_doc_analytics_summary")
        assert callable(client.get_doc_analytics_summary)

    def test_has_list_page_analytics(self, client):
        """Test client has list_page_analytics method."""
        assert hasattr(client, "list_page_analytics")
        assert callable(client.list_page_analytics)

    # Miscellaneous API
    def test_has_whoami(self, client):
        """Test client has whoami method."""
        assert hasattr(client, "whoami")
        assert callable(client.whoami)

    def test_has_resolve_browser_link(self, client):
        """Test client has resolve_browser_link method."""
        assert hasattr(client, "resolve_browser_link")
        assert callable(client.resolve_browser_link)

    def test_has_get_mutation_status(self, client):
        """Test client has get_mutation_status method."""
        assert hasattr(client, "get_mutation_status")
        assert callable(client.get_mutation_status)


@pytest.mark.unit
class TestCodaClientUrlEncoding:
    """Tests for URL encoding in CodaClient."""

    def test_encode_id_simple(self):
        """Test encoding simple ID."""
        from codomyrmex.cloud.coda_io import CodaClient

        result = CodaClient._encode_id("AbCDeFGH")
        assert result == "AbCDeFGH"

    def test_encode_id_with_spaces(self):
        """Test encoding ID with spaces."""
        from codomyrmex.cloud.coda_io import CodaClient

        result = CodaClient._encode_id("My Table Name")
        assert result == "My%20Table%20Name"

    def test_encode_id_with_special_chars(self):
        """Test encoding ID with special characters."""
        from codomyrmex.cloud.coda_io import CodaClient

        result = CodaClient._encode_id("Table/With/Slashes")
        assert result == "Table%2FWith%2FSlashes"


@pytest.mark.unit
class TestCodaClientImports:
    """Tests for module-level imports."""

    def test_import_from_cloud(self):
        """Test importing CodaClient from cloud module."""
        from codomyrmex.cloud import CodaClient

        assert CodaClient is not None

    def test_import_from_coda_io(self):
        """Test importing CodaClient from coda_io submodule."""
        from codomyrmex.cloud.coda_io import CodaClient

        assert CodaClient is not None

    def test_import_models_from_cloud(self):
        """Test importing models from cloud module."""
        from codomyrmex.cloud import (
            Column,
            Control,
            Doc,
            Formula,
            Page,
            Row,
            Table,
            User,
        )

        assert Doc is not None
        assert Page is not None
        assert Table is not None
        assert Row is not None
        assert Column is not None
        assert Formula is not None
        assert Control is not None
        assert User is not None

    def test_import_exceptions_from_cloud(self):
        """Test importing exceptions from cloud module."""
        from codomyrmex.cloud import (
            CodaAPIError,
            CodaAuthenticationError,
            CodaForbiddenError,
            CodaNotFoundError,
            CodaRateLimitError,
            CodaValidationError,
        )

        assert CodaAPIError is not None
        assert CodaAuthenticationError is not None
        assert CodaForbiddenError is not None
        assert CodaNotFoundError is not None
        assert CodaRateLimitError is not None
        assert CodaValidationError is not None


@pytest.mark.unit
class TestCodaClientHelperMethods:
    """Tests for CodaClient helper methods."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        from codomyrmex.cloud.coda_io import CodaClient
        return CodaClient(api_token="test-token")

    def test_get_method_exists(self, client):
        """Test _get helper method exists."""
        assert hasattr(client, "_get")
        assert callable(client._get)

    def test_post_method_exists(self, client):
        """Test _post helper method exists."""
        assert hasattr(client, "_post")
        assert callable(client._post)

    def test_put_method_exists(self, client):
        """Test _put helper method exists."""
        assert hasattr(client, "_put")
        assert callable(client._put)

    def test_patch_method_exists(self, client):
        """Test _patch helper method exists."""
        assert hasattr(client, "_patch")
        assert callable(client._patch)

    def test_delete_method_exists(self, client):
        """Test _delete helper method exists."""
        assert hasattr(client, "_delete")
        assert callable(client._delete)

    def test_request_method_exists(self, client):
        """Test _request helper method exists."""
        assert hasattr(client, "_request")
        assert callable(client._request)
