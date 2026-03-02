"""
Unit tests for Coda.io CloudClient implementation.

Uses strictly zero-mock tests with the Stub class.
"""

import pytest
from _stubs import Stub
from codomyrmex.cloud.coda_io import CodaClient
from codomyrmex.cloud.common import ResourceType, CloudProvider


class TestCodaCloudClient:
    """Tests for CodaClient resource management methods."""

    @pytest.fixture
    def client(self):
        """Create a CodaClient with stubbed requests session."""
        # We don't import Session because we're using Stub
        client = CodaClient(api_token="test-token")
        client.session = Stub()
        # Initialize session headers to avoid dict() conversion error
        client.session.headers = {"Authorization": "Bearer test-token", "Content-Type": "application/json"}
        return client

    def test_coda_list_resources(self, client):
        """Test CodaClient list_resources."""
        mock_response = Stub()
        mock_response.status_code = 200
        mock_response.content = b'{"items": []}' # Not used but good to have
        mock_response.json.return_value = {
            "items": [
                {
                    "id": "doc1",
                    "name": "Document 1",
                    "browserLink": "link1",
                    "createdAt": "2023-01-01T12:00:00Z",
                    "updatedAt": "2023-01-01T12:00:00Z",
                    "type": "doc",
                    "href": "href1",
                    "owner": "owner1",
                    "ownerName": "Owner 1"
                }
            ]
        }
        client.session.request.return_value = mock_response
        
        resources = client.list_resources(ResourceType.DOCUMENT)
        
        assert len(resources) == 1
        assert resources[0].id == "doc1"
        assert resources[0].name == "Document 1"
        assert resources[0].provider == CloudProvider.CODA
        assert resources[0].resource_type == ResourceType.DOCUMENT
        assert resources[0].metadata["browser_link"] == "link1"

    def test_coda_get_resource(self, client):
        """Test CodaClient get_resource."""
        mock_response = Stub()
        mock_response.status_code = 200
        doc_data = {
            "id": "doc1",
            "name": "Document 1",
            "browserLink": "link1",
            "createdAt": "2023-01-01T12:00:00Z",
            "updatedAt": "2023-01-01T12:00:00Z",
            "type": "doc",
            "href": "href1",
            "owner": "owner1",
            "ownerName": "Owner 1"
        }
        mock_response.json.return_value = doc_data
        client.session.request.return_value = mock_response
        
        resource = client.get_resource("doc1")
        
        assert resource is not None
        assert resource.id == "doc1"
        assert resource.name == "Document 1"
        assert resource.metadata["browser_link"] == "link1"

    def test_coda_create_resource(self, client):
        """Test CodaClient create_resource."""
        mock_response = Stub()
        mock_response.status_code = 201
        doc_data = {
            "id": "new-doc",
            "name": "New Document",
            "browserLink": "link-new",
            "createdAt": "2023-01-01T12:00:00Z",
            "updatedAt": "2023-01-01T12:00:00Z",
            "type": "doc",
            "href": "href-new",
            "owner": "owner1",
            "ownerName": "Owner 1"
        }
        mock_response.json.return_value = doc_data
        client.session.request.return_value = mock_response
        
        resource = client.create_resource("New Document", ResourceType.DOCUMENT, {})
        
        assert resource.id == "new-doc"
        assert resource.name == "New Document"
        assert resource.provider == CloudProvider.CODA

    def test_coda_delete_resource(self, client):
        """Test CodaClient delete_resource."""
        mock_response = Stub()
        mock_response.status_code = 202
        mock_response.json.return_value = {}
        client.session.request.return_value = mock_response
        
        assert client.delete_resource("doc-to-delete") is True
        client.session.request.assert_called_once()
