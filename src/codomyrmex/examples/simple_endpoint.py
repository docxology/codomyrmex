"""
Simple example of creating a REST API endpoint in Codomyrmex.
"""

from codomyrmex.api import (
    APIRequest,
    APIResponse,
    create_api,
    create_router,
)


def create_simple_api():
    """Create an API with a single hello world endpoint."""

    # 1. Create a router
    router = create_router(prefix="/hello")

    # 2. Define the endpoint
    @router.get("/{name}", summary="Say hello")
    def say_hello(request: APIRequest) -> APIResponse:
        """Return a greeting."""
        name = request.path_params.get("name", "World")
        return APIResponse.success({"message": f"Hello, {name}!"})

    # 3. Create API and attach router
    api = create_api(title="Hello API", version="1.0.0")
    api.add_router(router)

    return api


if __name__ == "__main__":
    # Create the API
    api = create_simple_api()

    # Simulate a request to verify it works
    print("Testing GET /hello/Codomyrmex")
    response = api.handle_request("GET", "/hello/Codomyrmex")
    print(f"Status: {response.status_code}")
    print(f"Body: {response.body}")
