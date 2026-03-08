"""
Coda.io REST API v1 Client.

This module provides a comprehensive Python client for the Coda.io API,
enabling programmatic access to Coda docs, pages, tables, rows, and more.

API Documentation: https://coda.io/developers/apis/v1
"""

from codomyrmex.cloud.common import (
    CloudClient,
    CloudProvider,
    CloudResource,
    ResourceType,
)
from codomyrmex.logging_monitoring import get_logger

from .mixins.access import AccessMixin
from .mixins.analytics import AnalyticsMixin
from .mixins.base import BaseMixin
from .mixins.docs import DocsMixin
from .mixins.elements import ElementsMixin
from .mixins.pages import PagesMixin
from .mixins.tables import TablesMixin
from .mixins.utils import UtilsMixin

try:
    import requests
except ImportError:
    pass

logger = get_logger(__name__)


class CodaClient(
    BaseMixin,
    DocsMixin,
    PagesMixin,
    TablesMixin,
    ElementsMixin,
    AccessMixin,
    AnalyticsMixin,
    UtilsMixin,
    CloudClient,
):
    """
    Coda.io REST API v1 client.

    This client provides methods for all Coda API v1 endpoints including:
    - Docs: List, create, get, update, delete documents
    - Pages: Manage pages and their content
    - Tables: Access tables and views
    - Columns: Read column definitions
    - Rows: CRUD operations on table rows
    - Permissions: Manage doc sharing
    - Publishing: Publish/unpublish docs
    - Formulas: Access named formulas
    - Controls: Read control values
    - Automations: Trigger webhooks
    - Analytics: Usage analytics

    Example:
        >>> client = CodaClient(api_token="your-api-token")
        >>> docs = client.list_docs()
        >>> for doc in docs.items:
        ...     print(doc.name)

    Attributes:
        api_token: The Coda API token for authentication
        base_url: The base URL for the Coda API (default: https://coda.io/apis/v1)
        session: The requests session used for HTTP calls
    """

    DEFAULT_BASE_URL = "https://coda.io/apis/v1"
    provider = CloudProvider.CODA

    def __init__(
        self,
        api_token: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = 30,
    ):
        """
        Initialize the Coda API client.

        Args:
            api_token: Your Coda API token. Get one from https://coda.io/account
            base_url: Base URL for the API. Defaults to the production API.
            timeout: Default timeout for requests in seconds.

        Raises:
            ImportError: If the requests library is not installed.
        """
        if requests is None:
            raise ImportError(
                "The 'requests' library is required. "
                "Install it with: pip install requests"
            )

        super().__init__(
            credentials=None
        )  # We'll just store api_token directly for now as per original design
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            }
        )

    def list_resources(
        self, resource_type: ResourceType | None = None
    ) -> list[CloudResource]:
        """List Coda documents as cloud resources."""
        if resource_type and resource_type != ResourceType.DOCUMENT:
            return []

        docs = self.list_docs()
        return [
            CloudResource(
                id=doc.id,
                name=doc.name,
                resource_type=ResourceType.DOCUMENT,
                provider=self.provider,
                region="global",
                status="active",
                created_at=doc.created_at,
                metadata={"browser_link": doc.browser_link},
            )
            for doc in docs.items
        ]

    def get_resource(self, resource_id: str) -> CloudResource | None:
        """Get a Coda document as a cloud resource."""
        try:
            doc = self.get_doc(resource_id)
            return CloudResource(
                id=doc.id,
                name=doc.name,
                resource_type=ResourceType.DOCUMENT,
                provider=self.provider,
                region="global",
                status="active",
                created_at=doc.created_at,
                metadata={"browser_link": doc.browser_link},
            )
        except Exception as _exc:
            return None

    def create_resource(
        self, name: str, resource_type: ResourceType, config: dict
    ) -> CloudResource:
        """Create a new Coda document."""
        if resource_type != ResourceType.DOCUMENT:
            raise ValueError(f"Unsupported resource type for Coda: {resource_type}")

        doc = self.create_doc(title=name, **config)
        return CloudResource(
            id=doc.id,
            name=doc.name,
            resource_type=ResourceType.DOCUMENT,
            provider=self.provider,
            region="global",
            status="active",
            created_at=doc.created_at,
            metadata={"browser_link": doc.browser_link},
        )

    def delete_resource(self, resource_id: str) -> bool:
        """Delete a Coda document."""
        try:
            self.delete_doc(resource_id)
            return True
        except Exception as _exc:
            return False
