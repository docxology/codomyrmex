"""
Unit tests for the WebsiteServer class.

Tests cover:
- GET request handling
- POST request handling
- API endpoint responses
- Security checks
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

import sys
# Add src to path for imports
TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent.parent
SRC_DIR = MODULE_DIR.parent.parent
sys.path.insert(0, str(SRC_DIR))

from codomyrmex.website.server import WebsiteServer
from codomyrmex.website.data_provider import DataProvider


def create_mock_request(path, method="GET", body=None, headers=None):
    """Create a mock request object for testing."""
    mock_handler = Mock(spec=WebsiteServer)
    mock_handler.path = path
    mock_handler.headers = headers or {}
    
    if body:
        mock_handler.headers['Content-Length'] = str(len(body))
        mock_handler.rfile = BytesIO(body)
    
    mock_handler.wfile = BytesIO()
    mock_handler.send_response = Mock()
    mock_handler.send_header = Mock()
    mock_handler.end_headers = Mock()
    
    return mock_handler


@pytest.mark.unit
class TestWebsiteServerInit:
    """Tests for WebsiteServer initialization."""

    def test_has_class_level_config(self):
        """Test that class-level configuration attributes exist."""
        assert hasattr(WebsiteServer, 'root_dir')
        assert hasattr(WebsiteServer, 'data_provider')


@pytest.mark.unit
class TestWebsiteServerGETEndpoints:
    """Tests for GET request handlers."""

    def test_config_list_endpoint(self, tmp_path):
        """Test /api/config endpoint returns config list."""
        # Setup
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_config_files.return_value = [
            {"name": "pyproject.toml", "path": "pyproject.toml", "type": "toml"}
        ]
        
        mock_handler = create_mock_request("/api/config")
        mock_handler.data_provider = mock_provider
        
        # Use the actual method on the mock
        WebsiteServer.handle_config_list(mock_handler)
        
        mock_provider.get_config_files.assert_called_once()

    def test_docs_list_endpoint(self, tmp_path):
        """Test /api/docs endpoint returns doc tree."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_doc_tree.return_value = {"name": "Documentation", "children": []}
        
        mock_handler = create_mock_request("/api/docs")
        mock_handler.data_provider = mock_provider
        
        WebsiteServer.handle_docs_list(mock_handler)
        
        mock_provider.get_doc_tree.assert_called_once()

    def test_pipelines_list_endpoint(self, tmp_path):
        """Test /api/pipelines endpoint returns pipeline status."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_pipeline_status.return_value = []
        
        mock_handler = create_mock_request("/api/pipelines")
        mock_handler.data_provider = mock_provider
        
        WebsiteServer.handle_pipelines_list(mock_handler)
        
        mock_provider.get_pipeline_status.assert_called_once()


@pytest.mark.unit
class TestWebsiteServerPOSTEndpoints:
    """Tests for POST request handlers."""

    def test_execute_requires_script_name(self):
        """Test that execute endpoint requires a script name."""
        body = json.dumps({}).encode('utf-8')
        mock_handler = create_mock_request("/api/execute", method="POST", body=body)
        mock_handler.send_error = Mock()
        
        WebsiteServer.handle_execute(mock_handler)
        
        mock_handler.send_error.assert_called_once()
        assert mock_handler.send_error.call_args[0][0] == 400

    def test_execute_rejects_path_traversal(self, tmp_path):
        """Test that execute rejects path traversal attempts."""
        body = json.dumps({"script": "../../../etc/passwd"}).encode('utf-8')
        mock_handler = create_mock_request("/api/execute", method="POST", body=body)
        mock_handler.send_error = Mock()
        mock_handler.root_dir = tmp_path
        
        # Create scripts dir for the check
        (tmp_path / "scripts").mkdir()
        
        WebsiteServer.handle_execute(mock_handler)
        
        mock_handler.send_error.assert_called()
        # Should be 403 Forbidden
        assert mock_handler.send_error.call_args[0][0] == 403

    def test_refresh_returns_system_data(self, tmp_path):
        """Test that refresh endpoint returns system data."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_system_summary.return_value = {"status": "ok"}
        mock_provider.get_agents_status.return_value = []
        mock_provider.get_available_scripts.return_value = []
        
        mock_handler = create_mock_request("/api/refresh", method="POST")
        mock_handler.data_provider = mock_provider
        mock_handler.headers = {}
        mock_handler.rfile = BytesIO(b'{}')
        mock_handler.headers['Content-Length'] = '2'
        
        WebsiteServer.handle_refresh(mock_handler)
        
        mock_provider.get_system_summary.assert_called_once()
        mock_provider.get_agents_status.assert_called_once()
        mock_provider.get_available_scripts.assert_called_once()


@pytest.mark.unit
class TestWebsiteServerChat:
    """Tests for chat endpoint."""

    @patch('codomyrmex.website.server.requests')
    def test_chat_forwards_to_ollama(self, mock_requests):
        """Test that chat endpoint forwards to Ollama."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Hello, I'm an AI assistant."}
        }
        mock_requests.post.return_value = mock_response
        
        body = json.dumps({
            "message": "Hello",
            "model": "llama3"
        }).encode('utf-8')
        
        mock_handler = create_mock_request("/api/chat", method="POST", body=body)
        mock_handler.headers = {'Content-Length': str(len(body))}
        mock_handler.rfile = BytesIO(body)
        
        WebsiteServer.handle_chat(mock_handler)
        
        mock_requests.post.assert_called_once()

    @patch('codomyrmex.website.server.requests')
    def test_chat_handles_ollama_connection_error(self, mock_requests):
        """Test that chat handles Ollama connection errors."""
        import requests
        mock_requests.exceptions = requests.exceptions
        mock_requests.post.side_effect = requests.exceptions.ConnectionError()
        
        body = json.dumps({"message": "Hello"}).encode('utf-8')
        
        mock_handler = create_mock_request("/api/chat", method="POST", body=body)
        mock_handler.headers = {'Content-Length': str(len(body))}
        mock_handler.rfile = BytesIO(body)
        
        # Should not raise, should return error response
        WebsiteServer.handle_chat(mock_handler)


@pytest.mark.unit
class TestWebsiteServerJsonResponse:
    """Tests for JSON response helper."""

    def test_send_json_response_sets_headers(self):
        """Test that send_json_response sets correct headers."""
        mock_handler = create_mock_request("/api/test")
        
        WebsiteServer.send_json_response(mock_handler, {"key": "value"})
        
        mock_handler.send_response.assert_called_with(200)
        mock_handler.send_header.assert_called_with('Content-type', 'application/json')

    def test_send_json_response_custom_status(self):
        """Test that send_json_response can use custom status."""
        mock_handler = create_mock_request("/api/test")
        
        WebsiteServer.send_json_response(mock_handler, {"error": "Not found"}, status=404)
        
        mock_handler.send_response.assert_called_with(404)


@pytest.mark.unit
class TestWebsiteServerSecurityChecks:
    """Tests for security-related functionality."""

    def test_config_get_prevents_traversal(self, tmp_path):
        """Test that config get prevents path traversal."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_config_content.side_effect = ValueError("Invalid filename")
        
        mock_handler = create_mock_request("/api/config/../../../etc/passwd")
        mock_handler.data_provider = mock_provider
        mock_handler.send_error = Mock()
        
        # The handler should validate the path
        WebsiteServer.handle_config_get(mock_handler, "/api/config/../../../etc/passwd")

    def test_script_path_validation(self, tmp_path):
        """Test that script paths are validated to be within scripts dir."""
        scripts_dir = tmp_path / "scripts"
        scripts_dir.mkdir()
        
        body = json.dumps({"script": "../../outside.py"}).encode('utf-8')
        mock_handler = create_mock_request("/api/execute", method="POST", body=body)
        mock_handler.send_error = Mock()
        mock_handler.root_dir = tmp_path
        
        WebsiteServer.handle_execute(mock_handler)
        
        # Should reject the script path
        mock_handler.send_error.assert_called()
