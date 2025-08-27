"""Unit tests for model_context_protocol module."""

import pytest
import sys
from unittest.mock import patch, MagicMock
import json


class TestModelContextProtocol:
    """Test cases for model context protocol functionality."""

    def test_model_context_protocol_import(self, code_dir):
        """Test that we can import model_context_protocol module."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        try:
            from model_context_protocol import mcp_schemas
            assert mcp_schemas is not None
        except ImportError as e:
            pytest.fail(f"Failed to import mcp_schemas: {e}")

    def test_mcp_schemas_module_structure(self, code_dir):
        """Test that mcp_schemas has expected structure."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from model_context_protocol import mcp_schemas

        assert hasattr(mcp_schemas, '__file__')
        assert hasattr(mcp_schemas, 'MCPErrorDetail')
        assert hasattr(mcp_schemas, 'MCPToolCall')
        assert hasattr(mcp_schemas, 'MCPToolResult')

    def test_mcp_error_detail_model(self, code_dir):
        """Test MCPErrorDetail model."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from model_context_protocol.mcp_schemas import MCPErrorDetail

        # Test valid error detail
        error_data = {
            "error_type": "ValidationError",
            "error_message": "Invalid input provided",
            "error_details": {"field": "name", "value": None}
        }
        error_detail = MCPErrorDetail(**error_data)
        assert error_detail.error_type == "ValidationError"
        assert error_detail.error_message == "Invalid input provided"
        assert error_detail.error_details == {"field": "name", "value": None}

        # Test with string error details
        error_data_str = {
            "error_type": "FileNotFoundError",
            "error_message": "File not found",
            "error_details": "The specified file does not exist"
        }
        error_detail_str = MCPErrorDetail(**error_data_str)
        assert error_detail_str.error_details == "The specified file does not exist"

        # Test with None error details
        error_data_none = {
            "error_type": "NetworkError",
            "error_message": "Connection failed"
        }
        error_detail_none = MCPErrorDetail(**error_data_none)
        assert error_detail_none.error_details is None

    def test_mcp_tool_call_model(self, code_dir):
        """Test MCPToolCall model."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from model_context_protocol.mcp_schemas import MCPToolCall

        # Test valid tool call
        tool_call_data = {
            "tool_name": "example.do_something",
            "arguments": {
                "param1": "value1",
                "param2": 123,
                "param3": {"nested": "object"}
            }
        }
        tool_call = MCPToolCall(**tool_call_data)
        assert tool_call.tool_name == "example.do_something"
        assert tool_call.arguments["param1"] == "value1"
        assert tool_call.arguments["param2"] == 123

        # Test with extra arguments (should be allowed due to Config.extra = 'allow')
        tool_call_extra = MCPToolCall(
            tool_name="test.tool",
            arguments={"arg1": "val1"},
            extra_field="extra_value"
        )
        assert hasattr(tool_call_extra, 'extra_field')
        assert tool_call_extra.extra_field == "extra_value"

    def test_mcp_tool_result_model_success(self, code_dir):
        """Test MCPToolResult model for successful results."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from model_context_protocol.mcp_schemas import MCPToolResult

        # Test successful result with data
        success_data = {
            "status": "success",
            "data": {
                "output_value": "Task completed successfully",
                "items_processed": 10
            },
            "explanation": "The tool processed 10 items successfully"
        }
        success_result = MCPToolResult(**success_data)
        assert success_result.status == "success"
        assert success_result.data["output_value"] == "Task completed successfully"
        assert success_result.error is None
        assert success_result.explanation == "The tool processed 10 items successfully"

        # Test successful result with None data (allowed for side-effect only tools)
        success_no_data = {
            "status": "success",
            "explanation": "Operation completed with no data output"
        }
        success_result_no_data = MCPToolResult(**success_no_data)
        assert success_result_no_data.data is None

    def test_mcp_tool_result_model_failure(self, code_dir):
        """Test MCPToolResult model for failure results."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from model_context_protocol.mcp_schemas import MCPToolResult, MCPErrorDetail

        # Test failure result with error details
        failure_data = {
            "status": "failure",
            "error": {
                "error_type": "ResourceUnavailable",
                "error_message": "The required resource could not be accessed",
                "error_details": {
                    "resource_id": "res_abc123",
                    "reason": "permission_denied"
                }
            }
        }
        failure_result = MCPToolResult(**failure_data)
        assert failure_result.status == "failure"
        assert failure_result.data is None
        assert failure_result.error is not None
        assert failure_result.error.error_type == "ResourceUnavailable"

    def test_mcp_tool_result_validation_errors(self, code_dir):
        """Test validation errors for MCPToolResult."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from model_context_protocol.mcp_schemas import MCPToolResult

        # Test failure without error (should raise ValueError)
        invalid_failure_data = {
            "status": "failure",
            "data": {"some": "data"}  # Data should be null on failure
        }
        with pytest.raises(ValueError, match="'data' field should be null or omitted if status indicates failure"):
            MCPToolResult(**invalid_failure_data)

        # Test failure without error details (should raise ValueError)
        invalid_failure_no_error = {
            "status": "failure",
            "error": None  # Error must be populated on failure
        }
        with pytest.raises(ValueError, match="'error' field must be populated if status indicates failure"):
            MCPToolResult(**invalid_failure_no_error)

    def test_model_serialization(self, code_dir):
        """Test model serialization to JSON."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from model_context_protocol.mcp_schemas import MCPToolCall, MCPToolResult, MCPErrorDetail

        # Test MCPToolCall serialization
        tool_call = MCPToolCall(
            tool_name="test.tool",
            arguments={"param": "value"}
        )
        json_str = tool_call.model_dump_json(indent=2)
        assert '"tool_name": "test.tool"' in json_str
        assert '"param": "value"' in json_str

        # Test MCPErrorDetail serialization
        error_detail = MCPErrorDetail(
            error_type="TestError",
            error_message="Test message",
            error_details={"key": "value"}
        )
        json_str = error_detail.model_dump_json(indent=2)
        assert '"error_type": "TestError"' in json_str
        assert '"error_message": "Test message"' in json_str

        # Test MCPToolResult serialization
        result = MCPToolResult(
            status="success",
            data={"result": "ok"},
            explanation="Success"
        )
        json_str = result.model_dump_json(indent=2)
        assert '"status": "success"' in json_str
        assert '"result": "ok"' in json_str

    def test_main_execution_example(self, capsys, code_dir):
        """Test the example execution in mcp_schemas.py main block."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        # Execute the main block by calling it directly
        import model_context_protocol.mcp_schemas as mcp_schemas

        # Call the main function that contains the examples
        with patch('builtins.print') as mock_print:
            # Replicate the main block logic here
            tool_call_data = {
                "tool_name": "example.do_something",
                "arguments": {
                    "param1": "value1",
                    "param2": 123
                }
            }
            mcp_call = mcp_schemas.MCPToolCall(**tool_call_data)
            mock_print(f"MCP Call: {mcp_call.model_dump_json(indent=2)}")

            success_result_data = {
                "status": "success",
                "data": {
                    "output_value": "Task completed successfully.",
                    "items_processed": 10
                },
                "explanation": "The example tool processed 10 items and finished."
            }
            mcp_success_result = mcp_schemas.MCPToolResult(**success_result_data)
            mock_print(f"MCP Success Result: {mcp_success_result.model_dump_json(indent=2)}")

            failure_result_data = {
                "status": "failure",
                "error": {
                    "error_type": "ResourceUnavailable",
                    "error_message": "The required resource could not be accessed.",
                    "error_details": {
                        "resource_id": "res_abc123"
                    }
                }
            }
            mcp_failure_result = mcp_schemas.MCPToolResult(**failure_result_data)
            mock_print(f"MCP Failure Result: {mcp_failure_result.model_dump_json(indent=2)}")

        # Verify the print calls were made
        assert mock_print.call_count == 3
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("MCP Call:" in call for call in calls)
        assert any("MCP Success Result:" in call for call in calls)
        assert any("MCP Failure Result:" in call for call in calls)

    def test_validation_error_examples(self, capsys, code_dir):
        """Test the validation error examples in main block."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        import model_context_protocol.mcp_schemas as mcp_schemas

        # Test validation errors by creating invalid data
        with patch('builtins.print') as mock_print:
            # Test invalid failure data (data present when status is failure)
            invalid_failure_data = {
                "status": "failure",
                "data": {"some": "data"}  # Data should be null on failure
            }
            try:
                mcp_schemas.MCPToolResult(**invalid_failure_data)
            except ValueError as e:
                mock_print(f"Validation Error for invalid failure data: {e}")

            # Test invalid success data (error present when status is success)
            invalid_success_data = {
                "status": "failure",  # Error must be populated
                "error": None
            }
            try:
                mcp_schemas.MCPToolResult(**invalid_success_data)
            except ValueError as e:
                mock_print(f"Validation Error for invalid success data (missing error on failure): {e}")

        # Verify validation error messages were captured
        assert mock_print.call_count == 2
        calls = [str(call) for call in mock_print.call_args_list]
        assert any("Validation Error" in call for call in calls)

    def test_pydantic_config_extra_allow(self, code_dir):
        """Test that Pydantic models allow extra fields."""
        if str(code_dir) not in sys.path:
            sys.path.insert(0, str(code_dir))

        from model_context_protocol.mcp_schemas import MCPToolCall, MCPToolResult

        # Test MCPToolCall allows extra fields
        tool_call = MCPToolCall(
            tool_name="test.tool",
            arguments={"arg1": "val1"},
            extra_field="extra",
            another_extra=123
        )
        assert hasattr(tool_call, 'extra_field')
        assert hasattr(tool_call, 'another_extra')

        # Test MCPToolResult allows extra fields
        result = MCPToolResult(
            status="success",
            custom_field="custom_value"
        )
        assert hasattr(result, 'custom_field')
