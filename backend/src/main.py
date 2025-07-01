from fastapi import FastAPI, HTTPException
from src.models import Item
from src.database import create_tables
from src.crud import create_item_db, get_items_db, update_item_db, delete_item_db

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await create_tables()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/items/")
def create_item(item: Item):
    return create_item_db(item.url)

@app.get("/items/")
def read_items():
    return get_items_db()

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return update_item_db(item_id, item.url)

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    return delete_item_db(item_id)