import pytest
from pydantic import ValidationError

from model_context_protocol.mcp_schemas import (
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)

    MCPToolCall,
    MCPToolResult,
    MCPErrorDetail,
)

# Test data for MCPToolCall
VALID_TOOL_CALL_DATA = {
    "tool_name": "example.do_something",
    "arguments": {"param1": "value1", "param2": 123},
}

INVALID_TOOL_CALL_DATA_MISSING_NAME = {"arguments": {"param1": "value1"}}

INVALID_TOOL_CALL_DATA_MISSING_ARGS = {"tool_name": "example.do_something"}

# Test data for MCPErrorDetail
VALID_ERROR_DETAIL_DATA = {
    "error_type": "ResourceUnavailable",
    "error_message": "The required resource could not be accessed.",
    "error_details": {"resource_id": "res_abc123"},
}

# Test data for MCPToolResult
VALID_SUCCESS_RESULT_DATA = {
    "status": "success",
    "data": {"output_value": "Task completed successfully.", "items_processed": 10},
    "explanation": "The example tool processed 10 items and finished.",
}

VALID_SUCCESS_RESULT_NO_DATA = {
    "status": "success",
    "data": None,  # Explicitly None
    "explanation": "Task completed with no specific data output.",
}

VALID_SUCCESS_RESULT_OMITTED_DATA = {
    "status": "success",
    # data field omitted
    "explanation": "Task completed with no specific data output.",
}

VALID_FAILURE_RESULT_DATA = {"status": "failure", "error": VALID_ERROR_DETAIL_DATA}

INVALID_FAILURE_RESULT_MISSING_ERROR = {"status": "failure"}  # error field is missing

INVALID_FAILURE_RESULT_WITH_DATA = {
    "status": "failure",
    "data": {"some_key": "some_value"},  # data should be None or omitted on failure
    "error": VALID_ERROR_DETAIL_DATA,
}

INVALID_STATUS_TYPE = {
    "status": 123,  # status should be a string
    "error": VALID_ERROR_DETAIL_DATA,
}


class TestMCPErrorDetail:
    def test_valid_error_detail(self):
        error_detail = MCPErrorDetail(**VALID_ERROR_DETAIL_DATA)
        assert error_detail.error_type == VALID_ERROR_DETAIL_DATA["error_type"]
        assert error_detail.error_message == VALID_ERROR_DETAIL_DATA["error_message"]
        assert error_detail.error_details == VALID_ERROR_DETAIL_DATA["error_details"]

    def test_missing_error_type(self):
        with pytest.raises(ValidationError):
            MCPErrorDetail(error_message="msg", error_details={})

    def test_missing_error_message(self):
        with pytest.raises(ValidationError):
            MCPErrorDetail(error_type="type", error_details={})


class TestMCPToolCall:
    def test_valid_tool_call(self):
        tool_call = MCPToolCall(**VALID_TOOL_CALL_DATA)
        assert tool_call.tool_name == VALID_TOOL_CALL_DATA["tool_name"]
        assert tool_call.arguments == VALID_TOOL_CALL_DATA["arguments"]

    def test_tool_call_missing_tool_name(self):
        with pytest.raises(ValidationError):
            MCPToolCall(**INVALID_TOOL_CALL_DATA_MISSING_NAME)

    def test_tool_call_missing_arguments(self):
        with pytest.raises(ValidationError):
            MCPToolCall(**INVALID_TOOL_CALL_DATA_MISSING_ARGS)

    def test_tool_call_arguments_can_be_empty(self):
        data = {"tool_name": "test.tool", "arguments": {}}
        tool_call = MCPToolCall(**data)
        assert tool_call.arguments == {}


class TestMCPToolResult:
    def test_valid_success_result(self):
        result = MCPToolResult(**VALID_SUCCESS_RESULT_DATA)
        assert result.status == "success"
        assert result.data == VALID_SUCCESS_RESULT_DATA["data"]
        assert result.error is None
        assert result.explanation == VALID_SUCCESS_RESULT_DATA["explanation"]

    def test_valid_success_result_with_none_data(self):
        result = MCPToolResult(**VALID_SUCCESS_RESULT_NO_DATA)
        assert result.status == "success"
        assert result.data is None
        assert result.error is None

    def test_valid_success_result_with_omitted_data(self):
        result = MCPToolResult(**VALID_SUCCESS_RESULT_OMITTED_DATA)
        assert result.status == "success"
        assert result.data is None  # Pydantic default for Optional field is None
        assert result.error is None

    def test_valid_failure_result(self):
        result = MCPToolResult(**VALID_FAILURE_RESULT_DATA)
        assert result.status == "failure"
        assert result.data is None
        assert result.error.error_type == VALID_ERROR_DETAIL_DATA["error_type"]

    def test_failure_result_requires_error_field(self):
        # This tests the custom validator: @validator('error', always=True)
        with pytest.raises(ValidationError) as excinfo:
            MCPToolResult(**INVALID_FAILURE_RESULT_MISSING_ERROR)
        assert "'error' field must be populated if status indicates failure" in str(
            excinfo.value
        )

    def test_failure_result_should_not_have_data_field(self):
        # This tests the custom validator: @validator('data', always=True)
        with pytest.raises(ValidationError) as excinfo:
            MCPToolResult(**INVALID_FAILURE_RESULT_WITH_DATA)
        assert (
            "'data' field should be null or omitted if status indicates failure"
            in str(excinfo.value)
        )

    def test_invalid_status_type(self):
        with pytest.raises(ValidationError):
            MCPToolResult(**INVALID_STATUS_TYPE)

    def test_serialization_and_deserialization(self):
        original_result = MCPToolResult(**VALID_SUCCESS_RESULT_DATA)
        json_output = original_result.model_dump_json()
        deserialized_result = MCPToolResult.model_validate_json(json_output)
        assert deserialized_result == original_result

        original_failure = MCPToolResult(**VALID_FAILURE_RESULT_DATA)
        json_failure_output = original_failure.model_dump_json()
        deserialized_failure = MCPToolResult.model_validate_json(json_failure_output)
        assert deserialized_failure == original_failure

    def test_allow_extra_in_data_on_success(self):
        data_with_extra = {
            "status": "success",
            "data": {
                "output_value": "Task completed successfully.",
                "items_processed": 10,
                "extra_field_allowed": "yes_it_is",
            },
        }
        result = MCPToolResult(**data_with_extra)
        assert result.data["extra_field_allowed"] == "yes_it_is"

    def test_allow_extra_in_arguments_in_tool_call(self):
        tool_call_data_extra = {
            "tool_name": "example.do_something",
            "arguments": {"param1": "value1", "param2": 123, "extra_arg": True},
        }
        tool_call = MCPToolCall(**tool_call_data_extra)
        assert tool_call.arguments["extra_arg"] is True
