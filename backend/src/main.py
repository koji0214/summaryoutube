from fastapi import FastAPI
from src.database import create_tables
from src.seeder import seed_data
from src.routers import videos, tags
import os

app = FastAPI()

# /apiプレフィックスを環境変数で制御できるようにする
API_PREFIX = os.getenv("API_PREFIX", "/api")

app.include_router(videos.router, prefix=API_PREFIX)
app.include_router(tags.router, prefix=API_PREFIX)

@app.on_event("startup")
def startup_event():
    create_tables()
    seed_data()

@app.get("/")
def read_root():
    return {"Hello": "World"}
