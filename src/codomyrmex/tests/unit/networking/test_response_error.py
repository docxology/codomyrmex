
import json

import pytest

from codomyrmex.networking.http_client import NetworkingError, Response


def test_response_json_wrapping():
    """Verify Response.json() raises NetworkingError on invalid JSON."""
    response = Response(
        status_code=200,
        headers={},
        content=b"invalid json",
        text="invalid json",
        json_data=None
    )

    with pytest.raises(NetworkingError, match="Failed to decode JSON"):
        response.json()

def test_response_json_success():
    """Verify Response.json() returns data on valid JSON."""
    data = {"foo": "bar"}
    response = Response(
        status_code=200,
        headers={},
        content=json.dumps(data).encode(),
        text=json.dumps(data),
        json_data=None
    )

    assert response.json() == data
