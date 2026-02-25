"""
Unit tests for Infomaniak exceptions.

Zero ``unittest.mock`` — uses ``Stub`` from ``conftest.py``.
"""



from _stubs import Stub

# =========================================================================

class TestInfomaniakExceptionHierarchy:
    """Tests for Infomaniak exception hierarchy and attributes."""

    def test_cloud_error_attributes(self):
        """InfomaniakCloudError stores service, operation, resource_id."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakCloudError

        err = InfomaniakCloudError(
            "test msg", service="compute", operation="create", resource_id="srv-1"
        )
        assert str(err) == "test msg"
        assert err.service == "compute"
        assert err.operation == "create"
        assert err.resource_id == "srv-1"

    def test_cloud_error_default_attributes(self):
        """InfomaniakCloudError defaults to empty strings."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakCloudError

        err = InfomaniakCloudError("msg")
        assert err.service == ""
        assert err.operation == ""
        assert err.resource_id == ""

    def test_all_exceptions_inherit_from_cloud_error(self):
        """All custom exceptions inherit from InfomaniakCloudError."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakAuthError,
            InfomaniakCloudError,
            InfomaniakConflictError,
            InfomaniakConnectionError,
            InfomaniakNotFoundError,
            InfomaniakQuotaExceededError,
            InfomaniakTimeoutError,
        )

        for exc_cls in [
            InfomaniakAuthError,
            InfomaniakNotFoundError,
            InfomaniakConflictError,
            InfomaniakQuotaExceededError,
            InfomaniakConnectionError,
            InfomaniakTimeoutError,
        ]:
            err = exc_cls("test", service="svc")
            assert isinstance(err, InfomaniakCloudError)
            assert isinstance(err, Exception)
            assert err.service == "svc"

    def test_exception_message_propagation(self):
        """Message passes through to Exception base class."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakAuthError

        err = InfomaniakAuthError("auth failed", service="identity")
        assert "auth failed" in str(err)

    def test_exception_kwargs_preserved(self):
        """All kwargs preserved on all subclasses."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakNotFoundError

        err = InfomaniakNotFoundError(
            "not found", service="dns", operation="get_zone", resource_id="zone-42"
        )
        assert err.service == "dns"
        assert err.operation == "get_zone"
        assert err.resource_id == "zone-42"


# =========================================================================
# Test classify_openstack_error
# =========================================================================


# =========================================================================

class TestClassifyOpenstackError:
    """Tests for classify_openstack_error() string-based classification."""

    def _classify(self, msg, **kwargs):
        from codomyrmex.cloud.infomaniak.exceptions import classify_openstack_error
        return classify_openstack_error(Exception(msg), **kwargs)

    def test_401_returns_auth_error(self):
        """Test functionality: 401 returns auth error."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakAuthError
        assert isinstance(self._classify("HTTP 401 Unauthorized"), InfomaniakAuthError)

    def test_403_returns_auth_error(self):
        """Test functionality: 403 returns auth error."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakAuthError
        assert isinstance(self._classify("403 Forbidden"), InfomaniakAuthError)

    def test_authentication_keyword_returns_auth_error(self):
        """Test functionality: authentication keyword returns auth error."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakAuthError
        assert isinstance(self._classify("Authentication required"), InfomaniakAuthError)

    def test_404_returns_not_found(self):
        """Test functionality: 404 returns not found."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakNotFoundError
        assert isinstance(self._classify("HTTP 404"), InfomaniakNotFoundError)

    def test_not_found_keyword(self):
        """Test functionality: not found keyword."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakNotFoundError
        assert isinstance(self._classify("Resource not found"), InfomaniakNotFoundError)

    def test_409_returns_conflict(self):
        """Test functionality: 409 returns conflict."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakConflictError
        assert isinstance(self._classify("HTTP 409"), InfomaniakConflictError)

    def test_conflict_keyword(self):
        """Test functionality: conflict keyword."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakConflictError
        assert isinstance(self._classify("State conflict detected"), InfomaniakConflictError)

    def test_413_returns_quota(self):
        """Test functionality: 413 returns quota."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakQuotaExceededError
        assert isinstance(self._classify("HTTP 413 Request Entity Too Large"), InfomaniakQuotaExceededError)

    def test_quota_keyword(self):
        """Test functionality: quota keyword."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakQuotaExceededError
        assert isinstance(self._classify("Quota exceeded"), InfomaniakQuotaExceededError)

    def test_limit_keyword(self):
        """Test functionality: limit keyword."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakQuotaExceededError
        assert isinstance(self._classify("Rate limit hit"), InfomaniakQuotaExceededError)

    def test_timeout_keyword(self):
        """Test functionality: timeout keyword."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakTimeoutError
        assert isinstance(self._classify("Request timeout"), InfomaniakTimeoutError)

    def test_timed_out_keyword(self):
        """Test functionality: timed out keyword."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakTimeoutError
        assert isinstance(self._classify("Connection timed out"), InfomaniakTimeoutError)

    def test_connection_keyword(self):
        """Test functionality: connection keyword."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakConnectionError
        assert isinstance(self._classify("Connection refused"), InfomaniakConnectionError)

    def test_refused_keyword(self):
        """Test functionality: refused keyword."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakConnectionError
        assert isinstance(self._classify("refused by server"), InfomaniakConnectionError)

    def test_unreachable_keyword(self):
        """Test functionality: unreachable keyword."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakConnectionError
        assert isinstance(self._classify("Host unreachable"), InfomaniakConnectionError)

    def test_generic_error_fallback(self):
        """Test functionality: generic error fallback."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakCloudError
        result = self._classify("Something unknown went wrong")
        assert type(result) is InfomaniakCloudError

    def test_case_insensitive(self):
        """Test functionality: case insensitive."""
        from codomyrmex.cloud.infomaniak.exceptions import InfomaniakAuthError
        assert isinstance(self._classify("AUTHENTICATION FAILED"), InfomaniakAuthError)

    def test_kwargs_propagated(self):
        """Test functionality: kwargs propagated."""
        result = self._classify(
            "HTTP 404", service="dns", operation="get_zone", resource_id="z-1"
        )
        assert result.service == "dns"
        assert result.operation == "get_zone"
        assert result.resource_id == "z-1"

    def test_preserves_original_message(self):
        """Test functionality: preserves original message."""
        result = self._classify("HTTP 404 zone missing")
        assert "HTTP 404 zone missing" in str(result)


# =========================================================================
# Test classify_http_error
# =========================================================================


# =========================================================================

class TestClassifyHttpError:
    """Tests for classify_http_error() status-code-based classification."""

    def _make_http_error(self, status_code):
        """Create a requests-like HTTPError with a response object."""
        import requests
        resp = Stub()
        resp.status_code = status_code
        err = requests.exceptions.HTTPError(f"HTTP {status_code}")
        err.response = resp
        return err

    def test_connection_error_instance(self):
        """requests.ConnectionError maps to InfomaniakConnectionError."""
        import requests

        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakConnectionError,
            classify_http_error,
        )
        err = requests.exceptions.ConnectionError("refused")
        result = classify_http_error(err, service="newsletter")
        assert isinstance(result, InfomaniakConnectionError)
        assert result.service == "newsletter"

    def test_timeout_instance(self):
        """requests.Timeout maps to InfomaniakTimeoutError."""
        import requests

        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakTimeoutError,
            classify_http_error,
        )
        err = requests.exceptions.Timeout("timed out")
        result = classify_http_error(err, operation="GET credits")
        assert isinstance(result, InfomaniakTimeoutError)
        assert result.operation == "GET credits"

    def test_401_response(self):
        """Test functionality: 401 response."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakAuthError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(401))
        assert isinstance(result, InfomaniakAuthError)

    def test_403_response(self):
        """Test functionality: 403 response."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakAuthError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(403))
        assert isinstance(result, InfomaniakAuthError)

    def test_404_response(self):
        """Test functionality: 404 response."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakNotFoundError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(404))
        assert isinstance(result, InfomaniakNotFoundError)

    def test_409_response(self):
        """Test functionality: 409 response."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakConflictError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(409))
        assert isinstance(result, InfomaniakConflictError)

    def test_413_response(self):
        """Test functionality: 413 response."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakQuotaExceededError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(413))
        assert isinstance(result, InfomaniakQuotaExceededError)

    def test_429_response(self):
        """Test functionality: 429 response."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakQuotaExceededError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(429))
        assert isinstance(result, InfomaniakQuotaExceededError)

    def test_no_response_attribute(self):
        """Error without response falls back to string classification."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakCloudError,
            classify_http_error,
        )
        err = Exception("Something generic happened")
        result = classify_http_error(err)
        assert isinstance(result, InfomaniakCloudError)

    def test_response_without_status_code(self):
        """Response without status_code falls back to string classification."""
        from codomyrmex.cloud.infomaniak.exceptions import classify_http_error
        err = Exception("weird error")
        err.response = Stub(spec=[])  # no status_code attr
        result = classify_http_error(err)
        assert result is not None

    def test_500_falls_through_to_string_classification(self):
        """HTTP 500 has no explicit mapping, falls to string classifier."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakCloudError,
            classify_http_error,
        )
        result = classify_http_error(self._make_http_error(500))
        assert isinstance(result, InfomaniakCloudError)

    def test_kwargs_propagated(self):
        """Test functionality: kwargs propagated."""
        from codomyrmex.cloud.infomaniak.exceptions import classify_http_error
        result = classify_http_error(
            self._make_http_error(404),
            service="newsletter",
            operation="GET campaigns/1",
            resource_id="camp-1",
        )
        assert result.service == "newsletter"
        assert result.operation == "GET campaigns/1"
        assert result.resource_id == "camp-1"


# =========================================================================
# Test Base Classes (OpenStack, S3, REST)
# =========================================================================

