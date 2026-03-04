from codomyrmex.api import RESTAPI, APIRequest, APIResponse, create_router, HTTPStatus

# Initialize the API
app = RESTAPI(title="User Service", version="1.0.0")

# Create a router for user operations
user_router = create_router(prefix="/users")

# Simulated database
users_db = {}


@user_router.post("/", summary="Create a new user")
def create_user(request: APIRequest) -> APIResponse:
    """Create a new user from the request body."""
    data = request.json_body
    if not data or "username" not in data:
        return APIResponse.bad_request("Missing username")

    user_id = str(len(users_db) + 1)
    users_db[user_id] = {"id": user_id, "username": data["username"]}

    return APIResponse.success(users_db[user_id], status_code=HTTPStatus.CREATED)


@user_router.get("/{user_id}", summary="Get user by ID")
def get_user(request: APIRequest) -> APIResponse:
    """Retrieve a user by their ID."""
    user_id = request.path_params.get("user_id")
    user = users_db.get(user_id)

    if not user:
        return APIResponse.not_found("User")

    return APIResponse.success(user)


# Add router to the app
app.add_router(user_router)

# Example usage (simulated)
if __name__ == "__main__":
    print("--- Simulating API Requests ---")

    # Simulate a POST request
    print("1. Creating a user...")
    response = app.handle_request("POST", "/users", body=b'{"username": "alice"}')
    print(f"Status: {response.status_code}")
    print(f"Body: {response.body}")

    # Simulate a GET request
    print("\n2. Fetching the user...")
    response = app.handle_request("GET", "/users/1")
    print(f"Status: {response.status_code}")
    print(f"Body: {response.body}")
