from fastapi import FastAPI, HTTPException
from src.models import Video
from src.database import create_tables
from src.crud import create_video_db, get_videos_db, update_video_db, delete_video_db, get_all_tags_db, search_videos_db
from typing import Optional

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await create_tables()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/videos/")
def create_video(video: Video):
    return create_video_db(video)

@app.get("/videos/")
def read_videos(title_query: Optional[str] = None, tags_query: Optional[str] = None, sort_by: str = "id", sort_order: str = "asc"):
    return search_videos_db(title_query, tags_query, sort_by, sort_order)

@app.get("/tags/")
def read_tags():
    return get_all_tags_db()

@app.put("/videos/{video_id}")
def update_video(video_id: int, video: Video):
    return update_video_db(video_id, video)

@app.delete("/videos/{video_id}")
def delete_video(video_id: int):
    return delete_video_db(video_id)