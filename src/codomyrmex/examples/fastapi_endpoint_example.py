"""
Example of creating a REST API endpoint using FastAPI within Codomyrmex.
This follows the APIScaffold patterns with Pydantic V2 models.
"""

import time

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from codomyrmex.logging_monitoring import get_logger

# Initialize logger
logger = get_logger(__name__)

# --- Models (Pydantic V2) ---


class UserBase(BaseModel):
    """Base User model with shared attributes."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="The user's unique username"
    )
    email: EmailStr = Field(..., description="The user's email address")
    full_name: str | None = Field(
        None, max_length=100, description="The user's full name"
    )


class UserCreate(UserBase):
    """Model for creating a new user (password would go here in a real app)."""


class UserResponse(UserBase):
    """Model for user response, including system-generated fields."""

    id: int = Field(..., description="Unique identifier for the user")
    created_at: float = Field(
        default_factory=time.time, description="Timestamp of creation"
    )

    model_config = {"from_attributes": True}


# --- In-memory Database (Mock) ---
# In a real application, use a proper database session dependency
fake_users_db: dict[int, dict] = {}
current_id = 0

# --- Router ---
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user.

    - **username**: must be unique
    - **email**: must be a valid email format
    """
    global current_id

    # Check for existing username
    for existing_user in fake_users_db.values():
        if existing_user["username"] == user.username:
            logger.warning(f"Attempt to create duplicate user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

    current_id += 1
    user_dict = user.model_dump()
    user_dict["id"] = current_id
    user_dict["created_at"] = time.time()

    fake_users_db[current_id] = user_dict
    logger.info(f"User created: {user.username} (ID: {current_id})")

    return user_dict


@router.get("/", response_model=list[UserResponse])
async def read_users(skip: int = 0, limit: int = 10):
    """
    Retrieve users with pagination.
    """
    users = list(fake_users_db.values())
    return users[skip : skip + limit]


@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int):
    """
    Get a specific user by ID.
    """
    if user_id not in fake_users_db:
        logger.error(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return fake_users_db[user_id]


# --- App Factory ---


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Codomyrmex Example API",
        description="An example API endpoint demonstrating Codomyrmex standards.",
        version="1.0.0",
    )

    app.include_router(router)

    @app.get("/health")
    async def health_check():
        return {"status": "ok", "timestamp": time.time()}

    return app


# --- Main Execution ---

if __name__ == "__main__":
    # Run the application using uvicorn
    app = create_app()
    logger.info("Starting API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
