from typing import Dict, List, Any, Optional, Callable, Union, Type
import inspect
import json
import logging
import re
import time

from dataclasses import dataclass, field
from enum import Enum
from urllib.parse import urlparse, parse_qs

from codomyrmex.logging_monitoring.logger_config import get_logger







"""REST API Implementation for Codomyrmex

This module provides a standardized REST API framework with automatic routing,
middleware support, and comprehensive error handling.
"""

# Import logging
try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

class HTTPMethod(Enum):
    """HTTP methods supported by the REST API."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"

class HTTPStatus(Enum):
    """Common HTTP status codes."""
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503

@dataclass
class APIRequest:
    """Represents an API request."""
    method: HTTPMethod
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, List[str]] = field(default_factory=dict)
    body: Optional[bytes] = None
    path_params: Dict[str, str] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def json_body(self) -> Optional[Dict[str, Any]]:
        """Parse JSON body if present."""
        if self.body:
            try:
                return json.loads(self.body.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
        return None

@dataclass
class APIResponse:
    """Represents an API response."""
    status_code: HTTPStatus
    body: Optional[Union[str, bytes, Dict[str, Any]]] = None
    headers: Dict[str, str] = field(default_factory=dict)
    content_type: str = "application/json"

    def __post_init__(self):
        """Set default headers based on content type."""
        if self.content_type and "content-type" not in [h.lower() for h in self.headers.keys()]:
            self.headers["Content-Type"] = self.content_type

    @classmethod
    def success(cls, data: Any = None, status_code: HTTPStatus = HTTPStatus.OK) -> 'APIResponse':
        """Create a successful response."""
        return cls(
            status_code=status_code,
            body=data,
            content_type="application/json"
        )

    @classmethod
    def error(cls, message: str, status_code: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR) -> 'APIResponse':
        """Create an error response."""
        return cls(
            status_code=status_code,
            body={"error": message, "status_code": status_code.value},
            content_type="application/json"
        )

    @classmethod
    def not_found(cls, resource: str = "Resource") -> 'APIResponse':
        """Create a not found response."""
        return cls.error(f"{resource} not found", HTTPStatus.NOT_FOUND)

    @classmethod
    def bad_request(cls, message: str = "Bad request") -> 'APIResponse':
        """Create a bad request response."""
        return cls.error(message, HTTPStatus.BAD_REQUEST)

@dataclass
class APIEndpoint:
    """Represents an API endpoint configuration."""
    path: str
    method: HTTPMethod
    handler: Callable[[APIRequest], APIResponse]
    summary: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    middleware: List[Callable[[APIRequest], Optional[APIResponse]]] = field(default_factory=list)

class APIRouter:
    """Router for managing API endpoints."""

    def __init__(self, prefix: str = ""):
        """
        Initialize the API router.

        Args:
            prefix: URL prefix for all routes in this router
        """
        self.prefix = prefix.rstrip('/')
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.sub_routers: List['APIRouter'] = []
        self.middleware: List[Callable[[APIRequest], Optional[APIResponse]]] = []

    def add_endpoint(self, endpoint: APIEndpoint) -> None:
        """
        Add an endpoint to the router.

        Args:
            endpoint: API endpoint to add
        """
        key = f"{endpoint.method.value}:{self._normalize_path(endpoint.path)}"
        self.endpoints[key] = endpoint
        logger.debug(f"Added endpoint: {key}")

    def add_router(self, router: 'APIRouter') -> None:
        """
        Add a sub-router.

        Args:
            router: Router to add as sub-router
        """
        self.sub_routers.append(router)

    def add_middleware(self, middleware: Callable[[APIRequest], Optional[APIResponse]]) -> None:
        """
        Add middleware to the router.

        Args:
            middleware: Middleware function
        """
        self.middleware.append(middleware)

    def get(self, path: str, summary: Optional[str] = None, **kwargs) -> Callable:
        """Decorator for GET endpoints."""
        return self._method_decorator(HTTPMethod.GET, path, summary, **kwargs)

    def post(self, path: str, summary: Optional[str] = None, **kwargs) -> Callable:
        """Decorator for POST endpoints."""
        return self._method_decorator(HTTPMethod.POST, path, summary, **kwargs)

    def put(self, path: str, summary: Optional[str] = None, **kwargs) -> Callable:
        """Decorator for PUT endpoints."""
        return self._method_decorator(HTTPMethod.PUT, path, summary, **kwargs)

    def delete(self, path: str, summary: Optional[str] = None, **kwargs) -> Callable:
        """Decorator for DELETE endpoints."""
        return self._method_decorator(HTTPMethod.DELETE, path, summary, **kwargs)

    def patch(self, path: str, summary: Optional[str] = None, **kwargs) -> Callable:
        """Decorator for PATCH endpoints."""
        return self._method_decorator(HTTPMethod.PATCH, path, summary, **kwargs)

    def _method_decorator(self, method: HTTPMethod, path: str, summary: Optional[str] = None,
                         tags: Optional[List[str]] = None, **kwargs) -> Callable:
        """Create a decorator for the specified HTTP method."""
        def decorator(func: Callable[[APIRequest], APIResponse]) -> Callable[[APIRequest], APIResponse]:

            endpoint = APIEndpoint(
                path=self._normalize_path(path),
                method=method,
                handler=func,
                summary=summary or func.__doc__,
                tags=tags or [],
                **kwargs
            )
            self.add_endpoint(endpoint)
            return func
        return decorator

    def _normalize_path(self, path: str) -> str:
        """Normalize path by adding prefix and ensuring leading slash."""
        if not path.startswith('/'):
            path = '/' + path
        if self.prefix:
            path = self.prefix + path
        return path

    def match_endpoint(self, method: HTTPMethod, path: str) -> Optional[tuple[APIEndpoint, Dict[str, str]]]:
        """
        Match an incoming request to an endpoint.

        Args:
            method: HTTP method
            path: Request path

        Returns:
            Tuple of (endpoint, path_parameters) if matched, None otherwise
        """
        # Check direct endpoints
        key = f"{method.value}:{path}"
        if key in self.endpoints:
            return self.endpoints[key], {}

        # Check pattern matching for parameterized routes
        for endpoint_key, endpoint in self.endpoints.items():
            if endpoint_key.startswith(f"{method.value}:"):
                pattern, param_names = self._path_to_regex(endpoint.path)
                match = pattern.match(path)
                if match:
                    path_params = {param: match.group(param) for param in param_names if match.group(param)}
                    return endpoint, path_params

        # Check sub-routers
        for router in self.sub_routers:
            result = router.match_endpoint(method, path)
            if result:
                return result

        return None

    def _path_to_regex(self, path: str) -> tuple:
        """
        Convert a path pattern to regex for parameter matching.

        Args:
            path: Path pattern (e.g., "/users/{id}")

        Returns:
            Tuple of (compiled_regex, parameter_names)
        """
        # Replace {param} with named capture groups
        param_pattern = re.compile(r'\{([^}]+)\}')
        param_names = param_pattern.findall(path)

        # Convert to regex pattern
        regex_pattern = param_pattern.sub(r'(?P<\1>[^/]+)', path)
        regex_pattern = f'^{regex_pattern}$'

        return re.compile(regex_pattern), param_names

    def get_all_endpoints(self) -> List[APIEndpoint]:
        """
        Get all endpoints from this router and sub-routers.

        Returns:
            List of all endpoints
        """
        endpoints = list(self.endpoints.values())

        for router in self.sub_routers:
            endpoints.extend(router.get_all_endpoints())

        return endpoints

class RESTAPI:
    """
    Main REST API class that handles HTTP requests and responses.
    """

    def __init__(self, title: str = "Codomyrmex API", version: str = "1.0.0",
                 description: str = "REST API for Codomyrmex"):
        """
        Initialize the REST API.

        Args:
            title: API title
            version: API version
            description: API description
        """
        self.title = title
        self.version = version
        self.description = description
        self.router = APIRouter()
        self.global_middleware: List[Callable[[APIRequest], Optional[APIResponse]]] = []
        self.request_count = 0
        self.error_count = 0

        # Add default middleware
        self.add_middleware(self._logging_middleware)
        self.add_middleware(self._error_handling_middleware)

        logger.info(f"REST API initialized: {title} v{version}")

    def add_middleware(self, middleware: Callable[[APIRequest], Optional[APIResponse]]) -> None:
        """
        Add global middleware.

        Args:
            middleware: Middleware function
        """
        self.global_middleware.append(middleware)

    def add_router(self, router: APIRouter) -> None:
        """
        Add a router to the API.

        Args:
            router: Router to add
        """
        self.router.add_router(router)

    def handle_request(self, method: str, path: str, headers: Optional[Dict[str, str]] = None,
                      body: Optional[bytes] = None, query_string: Optional[str] = None) -> APIResponse:
        """
        Handle an incoming HTTP request.

        Args:
            method: HTTP method
            path: Request path
            headers: Request headers
            body: Request body
            query_string: Query string

        Returns:
            API response
        """
        start_time = time.time()

        try:
            # Parse method
            try:
                http_method = HTTPMethod(method.upper())
            except ValueError:
                return APIResponse.error("Invalid HTTP method", HTTPStatus.METHOD_NOT_ALLOWED)

            # Parse headers
            headers = headers or {}

            # Parse query parameters
            query_params = {}
            if query_string:
                parsed = urlparse(f"?{query_string}")
                query_params = parse_qs(parsed.query)

            # Create request object
            request = APIRequest(
                method=http_method,
                path=path,
                headers=headers,
                query_params=query_params,
                body=body
            )

            # Apply global middleware
            for middleware in self.global_middleware:
                response = middleware(request)
                if response:
                    return response

            # Match endpoint
            match_result = self.router.match_endpoint(http_method, path)
            if not match_result:
                return APIResponse.not_found("Endpoint")

            endpoint, path_params = match_result
            request.path_params = path_params

            # Apply endpoint middleware
            for middleware in endpoint.middleware:
                response = middleware(request)
                if response:
                    return response

            # Apply router middleware
            for middleware in self.router.middleware:
                response = middleware(request)
                if response:
                    return response

            # Call handler
            response = endpoint.handler(request)

            # Ensure response is proper type
            if not isinstance(response, APIResponse):
                response = APIResponse.success(response)

            # Update metrics
            self.request_count += 1

            processing_time = time.time() - start_time
            logger.info(f"Request completed: {method} {path} -> {response.status_code.value} ({processing_time:.3f}s)")

            return response

        except Exception as e:
            self.error_count += 1
            logger.error(f"Request error: {method} {path} - {e}")
            return APIResponse.error("Internal server error", HTTPStatus.INTERNAL_SERVER_ERROR)

    def _logging_middleware(self, request: APIRequest) -> Optional[APIResponse]:
        """Middleware for request logging."""
        logger.debug(f"Incoming request: {request.method.value} {request.path}")
        return None

    def _error_handling_middleware(self, request: APIRequest) -> Optional[APIResponse]:
        """Middleware for basic error handling."""
        # Add CORS headers for all requests
        if request.method == HTTPMethod.OPTIONS:
            return APIResponse(
                status_code=HTTPStatus.OK,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization"
                }
            )
        return None

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get API metrics.

        Returns:
            Dictionary with API metrics
        """
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "endpoints_count": len(self.router.get_all_endpoints())
        }

    def get_endpoints(self) -> List[APIEndpoint]:
        """
        Get all registered endpoints.

        Returns:
            List of all endpoints
        """
        return self.router.get_all_endpoints()

# Convenience functions
def create_api(title: str = "Codomyrmex API", version: str = "1.0.0") -> RESTAPI:
    """
    Create a new REST API instance.

    Args:
        title: API title
        version: API version

    Returns:
        RESTAPI instance
    """
    return RESTAPI(title=title, version=version)

def create_router(prefix: str = "") -> APIRouter:
    """
    Create a new API router.

    Args:
        prefix: Router prefix

    Returns:
        APIRouter instance
    """
    return APIRouter(prefix=prefix)
