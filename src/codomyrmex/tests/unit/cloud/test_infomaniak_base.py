"""
Unit tests for Infomaniak base.

Zero ``unittest.mock`` — uses ``Stub`` from ``conftest.py``.
"""


import pytest
from _stubs import Stub

# =========================================================================

class TestInfomaniakOpenStackBaseClass:
    """Tests for InfomaniakOpenStackBase protocol methods."""

    def test_context_manager_calls_close(self):
        """__exit__ calls close()."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = Stub()
        client = InfomaniakOpenStackBase(mock_conn)
        client.__enter__()
        result = client.__exit__(None, None, None)

        assert result is False
        mock_conn.close.assert_called_once()

    def test_exit_does_not_suppress_exception(self):
        """__exit__ returns False — does not suppress exceptions."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = Stub()
        client = InfomaniakOpenStackBase(mock_conn)

        result = client.__exit__(ValueError, ValueError("boom"), None)
        assert result is False

    def test_close_handles_exception(self):
        """close() logs warning when conn.close() raises."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = Stub()
        mock_conn.close.side_effect = RuntimeError("close failed")

        client = InfomaniakOpenStackBase(mock_conn)
        # Should not raise
        client.close()

    def test_close_no_close_method(self):
        """close() is safe when connection has no close() method."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = Stub(spec=[])  # no close attribute
        client = InfomaniakOpenStackBase(mock_conn)
        client.close()  # Should not raise

    def test_validate_connection_success(self):
        """validate_connection returns True on success."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = Stub()
        mock_conn.identity.projects.return_value = []
        client = InfomaniakOpenStackBase(mock_conn)
        assert client.validate_connection() is True

    def test_validate_connection_failure(self):
        """validate_connection returns False on exception."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase

        mock_conn = Stub()
        mock_conn.identity.projects.side_effect = Exception("auth expired")
        client = InfomaniakOpenStackBase(mock_conn)
        assert client.validate_connection() is False

    def test_service_name_default(self):
        """Default _service_name is 'openstack'."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakOpenStackBase
        assert InfomaniakOpenStackBase._service_name == "openstack"


class TestInfomaniakS3BaseClass:
    """Tests for InfomaniakS3Base protocol methods."""

    def test_context_manager(self):
        """Context manager protocol enters and exits cleanly."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        mock_client = Stub()
        s3 = InfomaniakS3Base(mock_client)
        assert s3.__enter__() is s3
        assert s3.__exit__(None, None, None) is False

    def test_close_is_noop(self):
        """close() is a no-op for S3 (boto3 doesn't need explicit close)."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        mock_client = Stub()
        s3 = InfomaniakS3Base(mock_client)
        s3.close()
        # No assertions needed — just verify no exceptions

    def test_validate_connection_success(self):
        """validate_connection returns True when list_buckets succeeds."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        mock_client = Stub()
        mock_client.list_buckets.return_value = {"Buckets": []}
        s3 = InfomaniakS3Base(mock_client)
        assert s3.validate_connection() is True

    def test_validate_connection_failure(self):
        """validate_connection returns False on exception."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        mock_client = Stub()
        mock_client.list_buckets.side_effect = Exception("invalid creds")
        s3 = InfomaniakS3Base(mock_client)
        assert s3.validate_connection() is False

    def test_default_constants(self):
        """S3Base has correct default endpoint and region."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        assert InfomaniakS3Base.DEFAULT_ENDPOINT == "https://s3.pub1.infomaniak.cloud/"
        assert InfomaniakS3Base.DEFAULT_REGION == "us-east-1"

    def test_exit_does_not_suppress_exception(self):
        """__exit__ returns False — does not suppress exceptions."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakS3Base

        mock_client = Stub()
        s3 = InfomaniakS3Base(mock_client)
        result = s3.__exit__(TypeError, TypeError("bad"), None)
        assert result is False


class TestInfomaniakRESTBaseClass:
    """Tests for InfomaniakRESTBase protocol methods."""

    def test_from_env_raises_not_implemented(self):
        """Base from_env() raises NotImplementedError."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        with pytest.raises(NotImplementedError, match="must override from_env"):
            InfomaniakRESTBase.from_env()

    def test_close_handles_exception(self):
        """close() logs warning when session.close() raises."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase(token="t")
        client._session = Stub()
        client._session.close.side_effect = RuntimeError("close boom")
        # Should not raise
        client.close()

    def test_close_no_session(self):
        """close() is safe when _session doesn't exist."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase.__new__(InfomaniakRESTBase)
        # _session never set
        client.close()  # Should not raise

    def test_validate_connection_base_returns_true(self):
        """Base validate_connection() returns True (stub)."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase(token="t")
        assert client.validate_connection() is True

    def test_init_strips_trailing_slash(self):
        """base_url trailing slash is stripped."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase(token="t", base_url="https://api.test.com/")
        assert client._base_url == "https://api.test.com"

    def test_init_sets_headers(self):
        """__init__ configures Bearer auth and JSON content type."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase(token="my-token")
        assert client._session.headers["Authorization"] == "Bearer my-token"
        assert client._session.headers["Content-Type"] == "application/json"

    def test_service_name_default(self):
        """Default _service_name is 'rest'."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase
        assert InfomaniakRESTBase._service_name == "rest"

    def test_exit_does_not_suppress_exception(self):
        """__exit__ returns False — does not suppress exceptions."""
        from codomyrmex.cloud.infomaniak.base import InfomaniakRESTBase

        client = InfomaniakRESTBase(token="t")
        result = client.__exit__(ValueError, ValueError("test"), None)
        assert result is False


# =========================================================================
# Test Auth Module
# =========================================================================

