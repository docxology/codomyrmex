"""BaseMixin functionality."""

import json
from typing import Any
from urllib.parse import quote

from codomyrmex.cloud.coda_io.exceptions import raise_for_status
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

class BaseMixin:
    """BaseMixin class."""

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Make an HTTP request to the Coda API.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: API endpoint path (e.g., "/docs")
            params: Query parameters
            json_data: JSON body for POST/PUT/PATCH requests
            headers: Additional headers

        Returns:
            Parsed JSON response

        Raises:
            CodaAPIError: On API errors
        """
        url = f"{self.base_url}{path}"

        # Filter out None values from params
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        request_headers = dict(self.session.headers)
        if headers:
            request_headers.update(headers)

        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=request_headers,
            timeout=self.timeout,
        )

        # Parse response body
        try:
            response_body = response.json() if response.content else {}
        except json.JSONDecodeError:
            response_body = {}

        # Raise exception for error status codes
        raise_for_status(response.status_code, response_body)

        return response_body

    def _get(self, path: str, params: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", path, params=params, **kwargs)

    def _post(self, path: str, json_data: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", path, json_data=json_data, **kwargs)

    def _put(self, path: str, json_data: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
        """Make a PUT request."""
        return self._request("PUT", path, json_data=json_data, **kwargs)

    def _patch(self, path: str, json_data: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
        """Make a PATCH request."""
        return self._request("PATCH", path, json_data=json_data, **kwargs)

    def _delete(self, path: str, json_data: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
        """Make a DELETE request."""
        return self._request("DELETE", path, json_data=json_data, **kwargs)

    @staticmethod
    def _encode_id(id_or_name: str) -> str:
        """URL-encode an ID or name for use in paths."""
        return quote(id_or_name, safe="")

