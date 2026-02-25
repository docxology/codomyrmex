"""
Coda.io REST API v1 Client.

This module provides a comprehensive Python client for the Coda.io API,
enabling programmatic access to Coda docs, pages, tables, rows, and more.

API Documentation: https://coda.io/developers/apis/v1
"""


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
    requests = None  # type: ignore

logger = get_logger(__name__)


class CodaClient(BaseMixin, DocsMixin, PagesMixin, TablesMixin, ElementsMixin, AccessMixin, AnalyticsMixin, UtilsMixin):
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

        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        })
