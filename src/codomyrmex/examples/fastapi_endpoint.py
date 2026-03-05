import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(title="Example API", description="A simple item management API")


# Pydantic model for data validation
class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


# In-memory database
fake_items_db: list[Item] = []


@app.post("/items/", response_model=Item, status_code=201)
async def create_item(item: Item):
    """
    Create a new item.
    """
    fake_items_db.append(item)
    return item


@app.get("/items/", response_model=list[Item])
async def read_items(skip: int = 0, limit: int = 10):
    """
    Read items with pagination.
    """
    return fake_items_db[skip : skip + limit]


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    """
    Read a specific item by ID (index).
    """
    if item_id < 0 or item_id >= len(fake_items_db):
        raise HTTPException(status_code=404, detail="Item not found")
    return fake_items_db[item_id]


if __name__ == "__main__":
    # Run the application with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
