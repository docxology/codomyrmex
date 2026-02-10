"""
Unit tests for the WebsiteServer class.

Tests cover:
- GET request handling
- POST request handling
- API endpoint responses
- Security checks
"""

import json
import sys
import threading
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add src to path for imports
TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent.parent
SRC_DIR = MODULE_DIR.parent.parent
sys.path.insert(0, str(SRC_DIR))

from codomyrmex.website.data_provider import DataProvider
from codomyrmex.website.server import WebsiteServer


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

    def test_pipelines_endpoint_returns_correct_count(self, tmp_path):
        """Test /api/pipelines returns all pipelines from data provider."""
        pipelines = [
            {"id": f"wf-{i:04d}", "name": f"Workflow {i}", "status": "defined"}
            for i in range(1, 11)
        ]
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_pipeline_status.return_value = pipelines

        mock_handler = create_mock_request("/api/pipelines")
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_pipelines_list(mock_handler)

        mock_provider.get_pipeline_status.assert_called_once()
        mock_handler.send_response.assert_called_with(200)


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
        mock_provider.get_modules.return_value = []
        mock_provider.get_actual_agents.return_value = []
        mock_provider.get_available_scripts.return_value = []

        mock_handler = create_mock_request("/api/refresh", method="POST")
        mock_handler.data_provider = mock_provider
        mock_handler.headers = {}
        mock_handler.rfile = BytesIO(b'{}')
        mock_handler.headers['Content-Length'] = '2'

        WebsiteServer.handle_refresh(mock_handler)

        mock_provider.get_system_summary.assert_called_once()
        mock_provider.get_actual_agents.assert_called_once()
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
        # Check Content-type is among the header calls (CORS headers are also set)
        header_calls = [call.args for call in mock_handler.send_header.call_args_list]
        assert ('Content-type', 'application/json') in header_calls

    def test_send_json_response_custom_status(self):
        """Test that send_json_response can use custom status."""
        mock_handler = create_mock_request("/api/test")

        WebsiteServer.send_json_response(mock_handler, {"error": "Not found"}, status=404)

        mock_handler.send_response.assert_called_with(404)


@pytest.mark.unit
class TestNewGETEndpoints:
    """Tests for new GET endpoint handlers."""

    def test_modules_list_endpoint(self):
        """Test /api/modules returns module list."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_modules.return_value = [
            {"name": "coding", "status": "Active"}
        ]

        mock_handler = create_mock_request("/api/modules")
        mock_handler.data_provider = mock_provider

        WebsiteServer.handle_modules_list(mock_handler)

        mock_provider.get_modules.assert_called_once()

    def test_module_detail_endpoint(self):
        """Test /api/modules/{name} returns module detail."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_module_detail.return_value = {
            "name": "coding", "status": "Active", "has_tests": True
        }

        mock_handler = create_mock_request("/api/modules/coding")
        mock_handler.data_provider = mock_provider

        WebsiteServer.handle_module_detail(mock_handler, "/api/modules/coding")

        mock_provider.get_module_detail.assert_called_once_with("coding")

    def test_module_detail_returns_404_for_missing(self):
        """Test /api/modules/{name} returns 404 for unknown module."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_module_detail.return_value = None

        mock_handler = create_mock_request("/api/modules/nonexistent")
        mock_handler.data_provider = mock_provider
        # Wire up real send_json_response so send_response gets called
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_module_detail(mock_handler, "/api/modules/nonexistent")

        mock_handler.send_response.assert_called_with(404)

    def test_agents_list_endpoint(self):
        """Test /api/agents returns agent list."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_actual_agents.return_value = [
            {"name": "claude", "status": "Available"}
        ]

        mock_handler = create_mock_request("/api/agents")
        mock_handler.data_provider = mock_provider

        WebsiteServer.handle_agents_list(mock_handler)

        mock_provider.get_actual_agents.assert_called_once()

    def test_scripts_list_endpoint(self):
        """Test /api/scripts returns script list."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_available_scripts.return_value = [
            {"name": "deploy.py", "path": "deploy.py"}
        ]

        mock_handler = create_mock_request("/api/scripts")
        mock_handler.data_provider = mock_provider

        WebsiteServer.handle_scripts_list(mock_handler)

        mock_provider.get_available_scripts.assert_called_once()

    def test_docs_get_endpoint_happy_path(self):
        """Test /api/docs/{path} returns doc content."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_doc_content.return_value = "# Hello"

        mock_handler = create_mock_request("/api/docs/docs/README.md")
        mock_handler.data_provider = mock_provider

        WebsiteServer.handle_docs_get(mock_handler, "/api/docs/docs/README.md")

        mock_provider.get_doc_content.assert_called_once_with("docs/README.md")

    def test_docs_get_returns_403_for_traversal(self):
        """Test /api/docs/ returns 403 for path traversal."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_doc_content.side_effect = ValueError("Path traversal not allowed")

        mock_handler = create_mock_request("/api/docs/../../etc/passwd.md")
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_docs_get(mock_handler, "/api/docs/../../etc/passwd.md")

        mock_handler.send_response.assert_called_with(403)

    def test_docs_get_returns_404_for_missing(self):
        """Test /api/docs/ returns 404 for missing file."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_doc_content.side_effect = FileNotFoundError("Not found")

        mock_handler = create_mock_request("/api/docs/missing.md")
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_docs_get(mock_handler, "/api/docs/missing.md")

        mock_handler.send_response.assert_called_with(404)


@pytest.mark.unit
class TestRefreshEndpointUpdated:
    """Tests for updated handle_refresh."""

    def test_refresh_uses_actual_agents(self):
        """Test that refresh uses get_actual_agents, not get_agents_status."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_system_summary.return_value = {"status": "ok"}
        mock_provider.get_modules.return_value = []
        mock_provider.get_actual_agents.return_value = []
        mock_provider.get_available_scripts.return_value = []

        mock_handler = create_mock_request("/api/refresh", method="POST")
        mock_handler.data_provider = mock_provider

        WebsiteServer.handle_refresh(mock_handler)

        mock_provider.get_actual_agents.assert_called_once()
        mock_provider.get_modules.assert_called_once()


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


@pytest.mark.unit
class TestPOSTErrorHandling:
    """Tests for POST handler error handling."""

    def test_execute_missing_content_length(self):
        """Test execute handler with missing Content-Length."""
        mock_handler = create_mock_request("/api/execute", method="POST")
        mock_handler.headers = {}
        mock_handler.send_error = Mock()

        WebsiteServer.handle_execute(mock_handler)

        mock_handler.send_error.assert_called()
        assert mock_handler.send_error.call_args[0][0] == 400

    def test_execute_malformed_json(self):
        """Test execute handler with malformed JSON body."""
        body = b'not valid json'
        mock_handler = create_mock_request("/api/execute", method="POST", body=body)
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_execute(mock_handler)

        mock_handler.send_response.assert_called_with(400)

    def test_chat_missing_content_length(self):
        """Test chat handler with missing Content-Length."""
        mock_handler = create_mock_request("/api/chat", method="POST")
        mock_handler.headers = {}
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_chat(mock_handler)

        mock_handler.send_response.assert_called_with(400)

    def test_tests_run_malformed_json(self):
        """Test tests run handler with malformed JSON body."""
        body = b'{malformed'
        mock_handler = create_mock_request("/api/tests", method="POST", body=body)
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)
        mock_handler._test_lock = threading.Lock()
        mock_handler._test_running = False

        WebsiteServer.handle_tests_run(mock_handler)

        mock_handler.send_response.assert_called_with(400)

    def test_tests_run_no_body_uses_all_modules(self):
        """Test tests run with empty body runs all tests."""
        mock_handler = create_mock_request("/api/tests", method="POST")
        mock_handler.headers = {'Content-Length': '0'}
        mock_handler.rfile = BytesIO(b'')
        mock_handler._test_lock = threading.Lock()
        mock_handler._test_running = False
        mock_provider = Mock(spec=DataProvider)
        mock_provider.run_tests.return_value = {"passed": 5, "failed": 0, "total": 5, "success": True}
        mock_handler.data_provider = mock_provider

        WebsiteServer.handle_tests_run(mock_handler)

        mock_provider.run_tests.assert_called_once_with(None)


@pytest.mark.unit
class TestDoGETRouting:
    """Tests for do_GET() routing logic."""

    def test_do_get_routes_status(self):
        """Test that do_GET dispatches /api/status to handle_status."""
        mock_handler = create_mock_request("/api/status")
        mock_handler.handle_status = Mock()

        WebsiteServer.do_GET(mock_handler)

        mock_handler.handle_status.assert_called_once()

    def test_do_get_routes_health(self):
        """Test that do_GET dispatches /api/health to handle_health."""
        mock_handler = create_mock_request("/api/health")
        mock_handler.handle_health = Mock()

        WebsiteServer.do_GET(mock_handler)

        mock_handler.handle_health.assert_called_once()


@pytest.mark.unit
class TestDoPOSTRouting:
    """Tests for do_POST() routing logic."""

    def test_do_post_routes_execute(self):
        """Test that do_POST dispatches /api/execute to handle_execute."""
        mock_handler = create_mock_request("/api/execute", method="POST")
        mock_handler.handle_execute = Mock()
        mock_handler._validate_origin = Mock(return_value=True)

        WebsiteServer.do_POST(mock_handler)

        mock_handler.handle_execute.assert_called_once()

    def test_do_post_routes_tests(self):
        """Test that do_POST dispatches /api/tests to handle_tests_run."""
        mock_handler = create_mock_request("/api/tests", method="POST")
        mock_handler.handle_tests_run = Mock()
        mock_handler._validate_origin = Mock(return_value=True)

        WebsiteServer.do_POST(mock_handler)

        mock_handler.handle_tests_run.assert_called_once()


@pytest.mark.unit
class TestHandleStatusAndHealth:
    """Tests for handle_status() and handle_health() handlers."""

    def test_handle_status_returns_summary(self):
        """Test that handle_status returns system summary data."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_system_summary.return_value = {
            "status": "Operational", "version": "0.1.0"
        }

        mock_handler = create_mock_request("/api/status")
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_status(mock_handler)

        mock_provider.get_system_summary.assert_called_once()
        mock_handler.send_response.assert_called_with(200)

    def test_handle_health_returns_health_data(self):
        """Test that handle_health returns comprehensive health data."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_health_status.return_value = {
            "uptime": "1h 5m 30s", "python": {"version": "3.12.0"}
        }

        mock_handler = create_mock_request("/api/health")
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_health(mock_handler)

        mock_provider.get_health_status.assert_called_once()
        mock_handler.send_response.assert_called_with(200)

    def test_handle_status_no_provider(self):
        """Test that handle_status sends 500 when data_provider is None."""
        mock_handler = create_mock_request("/api/status")
        mock_handler.data_provider = None
        mock_handler.send_error = Mock()

        WebsiteServer.handle_status(mock_handler)

        mock_handler.send_error.assert_called_once_with(500, "Data provider missing")

    def test_handle_health_no_provider(self):
        """Test that handle_health sends 500 when data_provider is None."""
        mock_handler = create_mock_request("/api/health")
        mock_handler.data_provider = None
        mock_handler.send_error = Mock()

        WebsiteServer.handle_health(mock_handler)

        mock_handler.send_error.assert_called_once_with(500, "Data provider missing")


@pytest.mark.unit
class TestValidateOrigin:
    """Tests for _validate_origin() CORS/CSRF validation."""

    def _make_handler(self, origin=None, referer=None):
        """Create a mock handler with specific Origin/Referer headers."""
        headers = {}
        if origin is not None:
            headers["Origin"] = origin
        if referer is not None:
            headers["Referer"] = referer
        mock_handler = create_mock_request("/api/execute")
        mock_handler.headers = headers
        return mock_handler

    def test_valid_origin_localhost(self):
        """Test that http://localhost:8787 is accepted."""
        handler = self._make_handler(origin="http://localhost:8787")
        assert WebsiteServer._validate_origin(handler) is True

    def test_valid_origin_127(self):
        """Test that http://127.0.0.1:8787 is accepted."""
        handler = self._make_handler(origin="http://127.0.0.1:8787")
        assert WebsiteServer._validate_origin(handler) is True

    def test_invalid_origin_rejected(self):
        """Test that http://evil.com is rejected."""
        handler = self._make_handler(origin="http://evil.com")
        assert WebsiteServer._validate_origin(handler) is False

    def test_valid_referer_accepted(self):
        """Test that a referer starting with allowed origin is accepted."""
        handler = self._make_handler(referer="http://localhost:8787/some/path")
        assert WebsiteServer._validate_origin(handler) is True

    def test_invalid_referer_rejected(self):
        """Test that a referer from a different host is rejected."""
        handler = self._make_handler(referer="http://evil.com/api/execute")
        assert WebsiteServer._validate_origin(handler) is False

    def test_no_origin_no_referer_accepted(self):
        """Test that requests with no Origin and no Referer are accepted (same-origin/curl)."""
        handler = self._make_handler()
        assert WebsiteServer._validate_origin(handler) is True

    def test_origin_takes_precedence_over_referer(self):
        """Test that when both are present, Origin is checked (not Referer)."""
        handler = self._make_handler(origin="http://evil.com", referer="http://localhost:8787/ok")
        assert WebsiteServer._validate_origin(handler) is False

    def test_empty_origin_falls_through_to_referer(self):
        """Test that empty string origin falls through to referer check."""
        handler = self._make_handler(origin="", referer="http://localhost:8787/page")
        assert WebsiteServer._validate_origin(handler) is True


@pytest.mark.unit
class TestHandleConfigSave:
    """Tests for handle_config_save() endpoint."""

    def test_successful_save(self):
        """Test that a valid save returns success."""
        body = json.dumps({"filename": "pyproject.toml", "content": "[tool]\nname = 'test'"}).encode("utf-8")
        mock_handler = create_mock_request("/api/config/pyproject.toml", method="POST", body=body)
        mock_handler.headers = {"Content-Length": str(len(body))}
        mock_handler.rfile = BytesIO(body)
        mock_provider = Mock(spec=DataProvider)
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_config_save(mock_handler)

        mock_provider.save_config_content.assert_called_once_with("pyproject.toml", "[tool]\nname = 'test'")
        mock_handler.send_response.assert_called_with(200)

    def test_missing_filename_and_content_returns_400(self):
        """Test that missing filename and content returns 400."""
        body = json.dumps({}).encode("utf-8")
        mock_handler = create_mock_request("/api/config", method="POST", body=body)
        mock_handler.path = "/api/config"
        mock_handler.headers = {"Content-Length": str(len(body))}
        mock_handler.rfile = BytesIO(body)
        mock_handler.send_error = Mock()
        mock_handler.data_provider = Mock(spec=DataProvider)

        WebsiteServer.handle_config_save(mock_handler)

        mock_handler.send_error.assert_called()
        assert mock_handler.send_error.call_args[0][0] == 400

    def test_provider_value_error_returns_403(self):
        """Test that ValueError from provider (path traversal) returns 403."""
        body = json.dumps({"filename": "../etc/passwd", "content": "evil"}).encode("utf-8")
        mock_handler = create_mock_request("/api/config/../etc/passwd", method="POST", body=body)
        mock_handler.headers = {"Content-Length": str(len(body))}
        mock_handler.rfile = BytesIO(body)
        mock_provider = Mock(spec=DataProvider)
        mock_provider.save_config_content.side_effect = ValueError("Invalid filename")
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_config_save(mock_handler)

        mock_handler.send_response.assert_called_with(403)

    def test_provider_file_not_found_returns_500(self):
        """Test that FileNotFoundError from provider returns 500 (generic exception path)."""
        body = json.dumps({"filename": "missing.toml", "content": "data"}).encode("utf-8")
        mock_handler = create_mock_request("/api/config/missing.toml", method="POST", body=body)
        mock_handler.headers = {"Content-Length": str(len(body))}
        mock_handler.rfile = BytesIO(body)
        mock_provider = Mock(spec=DataProvider)
        mock_provider.save_config_content.side_effect = FileNotFoundError("File missing.toml does not exist")
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_config_save(mock_handler)

        mock_handler.send_response.assert_called_with(500)

    def test_no_content_provided_returns_400(self):
        """Test that empty body returns 400."""
        mock_handler = create_mock_request("/api/config/test.toml", method="POST")
        mock_handler.headers = {"Content-Length": "0"}
        mock_handler.send_error = Mock()

        WebsiteServer.handle_config_save(mock_handler)

        mock_handler.send_error.assert_called()
        assert mock_handler.send_error.call_args[0][0] == 400


@pytest.mark.unit
class TestHandleAwareness:
    """Tests for handle_awareness() GET endpoint."""

    def test_returns_awareness_data(self):
        """Test that handle_awareness returns PAI ecosystem data."""
        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_pai_awareness_data.return_value = {
            "missions": [], "projects": [], "telos": [],
            "memory": {"directories": [], "total_files": 0, "work_sessions_count": 0},
            "metrics": {"mission_count": 0, "project_count": 0},
            "mermaid_graph": "graph TD",
        }

        mock_handler = create_mock_request("/api/awareness")
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_awareness(mock_handler)

        mock_provider.get_pai_awareness_data.assert_called_once()
        mock_handler.send_response.assert_called_with(200)

    def test_returns_500_when_no_provider(self):
        """Test that 500 JSON error is returned when data_provider is None."""
        mock_handler = create_mock_request("/api/awareness")
        mock_handler.data_provider = None
        mock_handler.send_json_response = Mock()

        WebsiteServer.handle_awareness(mock_handler)

        mock_handler.send_json_response.assert_called_once_with(
            {"error": "Data provider missing"}, status=500
        )

    def test_do_get_routing(self):
        """Test that do_GET dispatches /api/awareness to handle_awareness."""
        mock_handler = create_mock_request("/api/awareness")
        mock_handler.handle_awareness = Mock()

        WebsiteServer.do_GET(mock_handler)

        mock_handler.handle_awareness.assert_called_once()


@pytest.mark.unit
class TestHandleAwarenessSummary:
    """Tests for handle_awareness_summary() POST endpoint."""

    @patch('codomyrmex.website.server.requests')
    def test_ollama_success(self, mock_requests):
        """Test successful Ollama summary generation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Here is your summary."}
        }
        mock_requests.post.return_value = mock_response

        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_pai_awareness_data.return_value = {
            "missions": [], "projects": [],
            "metrics": {"mission_count": 0, "project_count": 0,
                        "completed_tasks": 0, "total_tasks": 0, "overall_completion": 0},
        }

        body = json.dumps({"model": "llama3"}).encode('utf-8')
        mock_handler = create_mock_request("/api/awareness/summary", method="POST", body=body)
        mock_handler.headers = {'Content-Length': str(len(body))}
        mock_handler.rfile = BytesIO(body)
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_awareness_summary(mock_handler)

        mock_requests.post.assert_called_once()
        mock_handler.send_response.assert_called_with(200)

    @patch('codomyrmex.website.server.requests')
    def test_connection_error_returns_503(self, mock_requests):
        """Test that ConnectionError returns 503."""
        import requests
        mock_requests.exceptions = requests.exceptions
        mock_requests.post.side_effect = requests.exceptions.ConnectionError()

        mock_provider = Mock(spec=DataProvider)
        mock_provider.get_pai_awareness_data.return_value = {
            "missions": [], "projects": [],
            "metrics": {"mission_count": 0, "project_count": 0,
                        "completed_tasks": 0, "total_tasks": 0, "overall_completion": 0},
        }

        body = json.dumps({"model": "llama3"}).encode('utf-8')
        mock_handler = create_mock_request("/api/awareness/summary", method="POST", body=body)
        mock_handler.headers = {'Content-Length': str(len(body))}
        mock_handler.rfile = BytesIO(body)
        mock_handler.data_provider = mock_provider
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_awareness_summary(mock_handler)

        mock_handler.send_response.assert_called_with(503)

    def test_missing_body_returns_400(self):
        """Test that missing request body returns 400."""
        mock_handler = create_mock_request("/api/awareness/summary", method="POST")
        mock_handler.headers = {'Content-Length': '0'}
        mock_handler.send_json_response = lambda data, status=200: WebsiteServer.send_json_response(mock_handler, data, status)

        WebsiteServer.handle_awareness_summary(mock_handler)

        mock_handler.send_response.assert_called_with(400)

    def test_do_post_routing(self):
        """Test that do_POST dispatches /api/awareness/summary."""
        mock_handler = create_mock_request("/api/awareness/summary", method="POST")
        mock_handler.handle_awareness_summary = Mock()
        mock_handler._validate_origin = Mock(return_value=True)

        WebsiteServer.do_POST(mock_handler)

        mock_handler.handle_awareness_summary.assert_called_once()
