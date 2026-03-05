"""
Generated REST API endpoint example using FastAPI.
Follows Codomyrmex conventions for logging and structure.
"""

import time

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from codomyrmex.logging_monitoring import get_logger

# Initialize logger
logger = get_logger(__name__)

# --- Models ---


class ItemBase(BaseModel):
    """Base Item model."""

    name: str = Field(..., min_length=1, description="Name of the item")
    description: str | None = Field(None, description="Optional description")
    price: float = Field(..., gt=0, description="Price of the item")


class ItemCreate(ItemBase):
    """Model for creating a new item."""


class Item(ItemBase):
    """Model for item response."""

    id: int
    created_at: float


# --- Mock Database ---
fake_items_db = {}
current_id = 0

# --- Router ---
router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item."""
    global current_id
    current_id += 1
    item_dict = item.model_dump()
    item_dict["id"] = current_id
    item_dict["created_at"] = time.time()
    fake_items_db[current_id] = item_dict
    logger.info(f"Created item {current_id}: {item.name}")
    return item_dict


@router.get("/", response_model=list[Item])
async def read_items(skip: int = 0, limit: int = 10):
    """Retrieve items with pagination."""
    return list(fake_items_db.values())[skip : skip + limit]


@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    """Get a specific item by ID."""
    if item_id not in fake_items_db:
        logger.warning(f"Item not found: {item_id}")
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_items_db[item_id]


# --- App Factory ---


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Generated API",
        description="A generated API endpoint example.",
        version="1.0.0",
    )
    app.include_router(router)
    return app


if __name__ == "__main__":
    app = create_app()
    logger.info("Starting generated API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
