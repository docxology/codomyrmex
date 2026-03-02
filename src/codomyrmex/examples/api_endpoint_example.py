"""
Example of creating a REST API endpoint using the Codomyrmex API framework.
"""

import sys
from pathlib import Path

# Add project root to path if needed, for standalone execution
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from codomyrmex.api import create_api, APIRouter, APIRequest, APIResponse, HTTPStatus
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


def create_example_api():
    """Create an example API with a user endpoint."""

    # 1. Create a router with a prefix
    router = APIRouter(prefix="/users")

    # 2. Define an endpoint handler
    @router.get("/{user_id}", summary="Get user profile")
    def get_user_profile(request: APIRequest) -> APIResponse:
        """Fetch a user profile by ID."""
        user_id = request.path_params.get("user_id")

        # Simulate database lookup
        if user_id == "123":
            return APIResponse.success(
                {"id": "123", "name": "Alice Smith", "role": "developer"}
            )

        return APIResponse.error("User not found", HTTPStatus.NOT_FOUND)

    @router.post("/", summary="Create a new user")
    def create_user(request: APIRequest) -> APIResponse:
        """Create a new user from JSON body."""
        data = request.json_body
        if not data or "name" not in data:
            return APIResponse.bad_request("Missing 'name' in request body")

        return APIResponse.success(
            {"id": "456", "name": data["name"], "status": "created"},
            status_code=HTTPStatus.CREATED,
        )

    # 3. Create the API application and add the router
    api = create_api(title="User Management API", version="1.0.0")
    api.add_router(router)

    return api


def main():
    """Demonstrate usage of the API."""
    api = create_example_api()

    print(f"API Created: {api.title} v{api.version}")

    # Simulate a GET request
    print("\n--- Simulating GET /users/123 ---")
    response = api.handle_request(method="GET", path="/users/123")
    print(f"Status: {response.status_code.value}")
    print(f"Body: {response.body}")

    # Simulate a POST request
    print("\n--- Simulating POST /users/ ---")
    import json

    response = api.handle_request(
        method="POST",
        path="/users/",
        body=json.dumps({"name": "Bob Jones"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    print(f"Status: {response.status_code.value}")
    print(f"Body: {response.body}")


if __name__ == "__main__":
    main()
