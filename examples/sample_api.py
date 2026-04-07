from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Sample Codomyrmex API", version="1.0.0")


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float


@app.post("/api/v1/items", response_model=Item, status_code=201)
async def create_item(item: Item):
    """
    Create a new item.
    """
    if item.price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")

    return item


@app.get("/api/v1/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """
    Retrieve an item by ID.
    """
    return Item(name="Example Item", price=19.99)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
