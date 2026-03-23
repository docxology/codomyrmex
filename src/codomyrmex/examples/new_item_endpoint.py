"""
Example of creating a REST API endpoint for 'Items' using FastAPI within Codomyrmex.
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

    name: str = Field(..., min_length=1, max_length=100, description="Name of the item")
    description: str | None = Field(
        None, max_length=500, description="Description of the item"
    )
    price: float = Field(..., gt=0, description="Price of the item")


class ItemCreate(ItemBase):
    """Model for creating a new item."""


class ItemResponse(ItemBase):
    """Model for item response."""

    id: int = Field(..., description="Unique ID")
    created_at: float = Field(default_factory=time.time)

    model_config = {"from_attributes": True}


# --- Mock Database ---
fake_items_db: dict[int, dict] = {}
current_item_id = 0

# --- Router ---
router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Item not found"}},
)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create a new item."""
    global current_item_id
    current_item_id += 1

    item_dict = item.model_dump()
    item_dict["id"] = current_item_id
    item_dict["created_at"] = time.time()

    fake_items_db[current_item_id] = item_dict
    logger.info("Item created: %s (ID: %s)", item.name, current_item_id)
    return item_dict


@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(item_id: int):
    """Get an item by ID."""
    if item_id not in fake_items_db:
        logger.error("Item not found: %s", item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_items_db[item_id]


@router.get("/", response_model=list[ItemResponse])
async def list_items(skip: int = 0, limit: int = 10):
    """list items with pagination."""
    items = list(fake_items_db.values())
    return items[skip : skip + limit]


# --- App Factory ---


def create_app() -> FastAPI:
    """Create the FastAPI app."""
    app = FastAPI(title="Item API Example", version="1.0.0")
    app.include_router(router)
    return app


if __name__ == "__main__":
    app = create_app()
    logger.info("Starting Item API on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
