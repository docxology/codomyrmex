"""
Unit tests for Infomaniak authentication module.

Tests cover:
- InfomaniakAuthError re-export from exceptions module
- InfomaniakCredentials dataclass and from_env factory
- InfomaniakS3Credentials dataclass and from_env factory
- to_openstack_auth() conversion
- S3Credentials defaults
- create_openstack_connection with mock openstack module
- create_s3_client with mock boto3 module
- Error paths for missing credentials and import failures

Total: ~16 tests in 1 test class.
"""

import os
import sys

import pytest
from _stubs import Stub


class TestInfomaniakAuthModule:
    """Comprehensive tests for the Infomaniak auth module."""

    # -----------------------------------------------------------------
    # InfomaniakAuthError re-export
    # -----------------------------------------------------------------

    def test_auth_error_reexported_from_auth_module(self):
        """InfomaniakAuthError is importable directly from auth.py."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakAuthError

        assert InfomaniakAuthError is not None

    def test_auth_error_is_subclass_of_cloud_error(self):
        """InfomaniakAuthError inherits from InfomaniakCloudError."""
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakAuthError,
            InfomaniakCloudError,
        )

        assert issubclass(InfomaniakAuthError, InfomaniakCloudError)
        # Also verify it is raiseable with the expected attributes
        err = InfomaniakAuthError(
            "auth failed", service="identity", operation="login"
        )
        assert err.service == "identity"
        assert err.operation == "login"
        assert "auth failed" in str(err)

    def test_auth_error_same_class_in_auth_and_exceptions(self):
        """The re-exported InfomaniakAuthError is the exact same class object."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakAuthError as AuthFromAuth,
        )
        from codomyrmex.cloud.infomaniak.exceptions import (
            InfomaniakAuthError as AuthFromExceptions,
        )

        assert AuthFromAuth is AuthFromExceptions

    # -----------------------------------------------------------------
    # InfomaniakCredentials.from_env
    # -----------------------------------------------------------------

    def test_credentials_from_env_valid(self, infomaniak_openstack_env):
        """Credentials are correctly populated from valid environment variables."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        creds = InfomaniakCredentials.from_env()

        assert creds.application_credential_id == "test-cred-id"
        assert creds.application_credential_secret == "test-cred-secret"
        assert creds.auth_url == "https://api.pub1.infomaniak.cloud/identity/v3/"
        assert creds.region == "dc3-a"

    def test_credentials_from_env_missing_raises(self):
        """Missing required env vars raise InfomaniakAuthError."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakAuthError,
            InfomaniakCredentials,
        )

        saved = {k: v for k, v in os.environ.items() if k.startswith("INFOMANIAK")}
        try:
            for key in saved:
                del os.environ[key]
            with pytest.raises(
                InfomaniakAuthError, match="Missing required environment variables"
            ):
                InfomaniakCredentials.from_env()
        finally:
            for key, value in saved.items():
                os.environ[key] = value

    def test_credentials_from_env_defaults(self):
        """Defaults are applied when optional env vars are absent."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        # Clear existing env vars and set only required ones
        saved = {k: v for k, v in os.environ.items() if k.startswith("INFOMANIAK")}
        try:
            for key in saved:
                del os.environ[key]
            os.environ["INFOMANIAK_APP_CREDENTIAL_ID"] = "id-only"
            os.environ["INFOMANIAK_APP_CREDENTIAL_SECRET"] = "secret-only"
            creds = InfomaniakCredentials.from_env()
            assert creds.auth_url == "https://api.pub1.infomaniak.cloud/identity/v3/"
            assert creds.region == "dc3-a"
            assert creds.project_id is None
        finally:
            os.environ.pop("INFOMANIAK_APP_CREDENTIAL_ID", None)
            os.environ.pop("INFOMANIAK_APP_CREDENTIAL_SECRET", None)
            for key, value in saved.items():
                os.environ[key] = value

    # -----------------------------------------------------------------
    # to_openstack_auth()
    # -----------------------------------------------------------------

    def test_to_openstack_auth_returns_correct_dict(self):
        """to_openstack_auth() produces the expected auth dict for the SDK."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        creds = InfomaniakCredentials(
            application_credential_id="my-id",
            application_credential_secret="my-secret",
            auth_url="https://custom.api/identity/v3/",
        )

        auth_dict = creds.to_openstack_auth()

        assert auth_dict == {
            "auth_url": "https://custom.api/identity/v3/",
            "application_credential_id": "my-id",
            "application_credential_secret": "my-secret",
        }

    # -----------------------------------------------------------------
    # InfomaniakS3Credentials.from_env
    # -----------------------------------------------------------------

    def test_s3_credentials_from_env_valid(self, infomaniak_s3_env):
        """S3 credentials are correctly populated from valid environment variables."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakS3Credentials

        creds = InfomaniakS3Credentials.from_env()

        assert creds.access_key == "test-s3-access"
        assert creds.secret_key == "test-s3-secret"
        assert creds.endpoint_url == "https://s3.pub1.infomaniak.cloud/"

    def test_s3_credentials_from_env_missing_raises(self):
        """Missing required S3 env vars raise InfomaniakAuthError."""
        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakAuthError,
            InfomaniakS3Credentials,
        )

        saved = {k: v for k, v in os.environ.items() if k.startswith("INFOMANIAK")}
        try:
            for key in saved:
                del os.environ[key]
            with pytest.raises(
                InfomaniakAuthError, match="Missing required environment variables"
            ):
                InfomaniakS3Credentials.from_env()
        finally:
            for key, value in saved.items():
                os.environ[key] = value

    def test_s3_credentials_defaults(self):
        """S3 credentials use correct defaults for endpoint and region."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakS3Credentials

        creds = InfomaniakS3Credentials(
            access_key="ak",
            secret_key="sk",
        )

        assert creds.endpoint_url == "https://s3.pub1.infomaniak.cloud/"
        assert creds.region == "us-east-1"


# =========================================================================

class TestAuthFunctions:
    """Tests for create_openstack_connection and create_s3_client."""

    def test_create_openstack_connection_import_error(self):
        """create_openstack_connection raises ImportError when openstacksdk missing."""

        from codomyrmex.cloud.infomaniak.auth import create_openstack_connection

        # Temporarily hide openstack module
        saved = sys.modules.get("openstack")
        sys.modules["openstack"] = None
        try:
            with pytest.raises(ImportError, match="openstacksdk is required"):
                create_openstack_connection(
                    Stub()  # credentials arg doesn't matter — import fails first
                )
        finally:
            if saved is not None:
                sys.modules["openstack"] = saved
            else:
                sys.modules.pop("openstack", None)

    def test_create_openstack_connection_auth_failure(self):
        """create_openstack_connection raises InfomaniakAuthError on connection failure."""

        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakAuthError,
            InfomaniakCredentials,
            create_openstack_connection,
        )

        mock_openstack = Stub()
        mock_openstack.connect.side_effect = Exception("auth failed")
        sys.modules["openstack"] = mock_openstack
        try:
            creds = InfomaniakCredentials(
                application_credential_id="id",
                application_credential_secret="secret",
            )
            with pytest.raises(InfomaniakAuthError, match="Authentication failed"):
                create_openstack_connection(creds)
        finally:
            sys.modules.pop("openstack", None)

    def test_create_openstack_connection_success(self):
        """create_openstack_connection returns Connection on success."""

        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakCredentials,
            create_openstack_connection,
        )

        mock_conn = Stub()
        mock_openstack = Stub()
        mock_openstack.connect.return_value = mock_conn
        sys.modules["openstack"] = mock_openstack
        try:
            creds = InfomaniakCredentials(
                application_credential_id="id",
                application_credential_secret="secret",
            )
            result = create_openstack_connection(creds)
            assert result is mock_conn
            mock_openstack.connect.assert_called_once()
        finally:
            sys.modules.pop("openstack", None)

    def test_create_s3_client_import_error(self):
        """create_s3_client raises ImportError when boto3 missing."""

        from codomyrmex.cloud.infomaniak.auth import create_s3_client

        saved = sys.modules.get("boto3")
        sys.modules["boto3"] = None
        try:
            with pytest.raises(ImportError, match="boto3 is required"):
                create_s3_client(Stub())
        finally:
            if saved is not None:
                sys.modules["boto3"] = saved
            else:
                sys.modules.pop("boto3", None)

    def test_create_s3_client_success(self):
        """create_s3_client returns boto3 client on success."""

        from codomyrmex.cloud.infomaniak.auth import (
            InfomaniakS3Credentials,
            create_s3_client,
        )

        mock_s3 = Stub()
        mock_boto3 = Stub()
        mock_boto3.client.return_value = mock_s3
        sys.modules["boto3"] = mock_boto3
        try:
            creds = InfomaniakS3Credentials(
                access_key="ak", secret_key="sk",
            )
            result = create_s3_client(creds)
            assert result is mock_s3
            mock_boto3.client.assert_called_once_with(
                "s3",
                endpoint_url=creds.endpoint_url,
                aws_access_key_id="ak",
                aws_secret_access_key="sk",
                region_name=creds.region,
            )
        finally:
            sys.modules.pop("boto3", None)

    def test_credentials_to_openstack_auth(self):
        """InfomaniakCredentials.to_openstack_auth returns correct dict."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        creds = InfomaniakCredentials(
            application_credential_id="id-123",
            application_credential_secret="secret-456",
            auth_url="https://custom.url/identity/v3/",
        )
        auth = creds.to_openstack_auth()

        assert auth["auth_url"] == "https://custom.url/identity/v3/"
        assert auth["application_credential_id"] == "id-123"
        assert auth["application_credential_secret"] == "secret-456"
        assert len(auth) == 3

    def test_credentials_metadata_field(self):
        """InfomaniakCredentials supports metadata dict."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        creds = InfomaniakCredentials(
            application_credential_id="id",
            application_credential_secret="secret",
            metadata={"env": "prod"},
        )
        assert creds.metadata == {"env": "prod"}

    def test_credentials_default_metadata_empty(self):
        """InfomaniakCredentials metadata defaults to empty dict."""
        from codomyrmex.cloud.infomaniak.auth import InfomaniakCredentials

        creds = InfomaniakCredentials(
            application_credential_id="id",
            application_credential_secret="secret",
        )
        assert creds.metadata == {}

    def test_auth_constants(self):
        """Auth module defines correct default constants."""
        from codomyrmex.cloud.infomaniak.auth import (
            DEFAULT_AUTH_URL,
            DEFAULT_S3_ENDPOINT,
            DEFAULT_S3_REGION,
        )
        assert DEFAULT_AUTH_URL == "https://api.pub1.infomaniak.cloud/identity/v3/"
        assert DEFAULT_S3_ENDPOINT == "https://s3.pub1.infomaniak.cloud/"
        assert DEFAULT_S3_REGION == "us-east-1"


# =========================================================================
# Test Module Exports (expanded)
# =========================================================================


# =========================================================================

try:
    import openstack
    HAS_OPENSTACK = True
except ImportError:
    HAS_OPENSTACK = False

# =========================================================================
# NEWSLETTER VALIDATION TESTS
# =========================================================================
