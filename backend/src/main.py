from fastapi import FastAPI, HTTPException
from src.models import Video
from src.database import create_tables
from src.crud import create_video_db, get_videos_db, update_video_db, delete_video_db, get_all_tags_db, search_videos_db, get_video_by_id_db, get_or_create_transcript_db
from src.seeder import seed_data
from typing import Optional
from src.youtube_api import get_transcript_from_youtube, extract_video_id

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await create_tables()
    seed_data()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/videos/")
def create_video(video: Video):
    return create_video_db(video)

@app.get("/videos/")
def read_videos(title_query: Optional[str] = None, tags_query: Optional[str] = None, sort_by: str = "id", sort_order: str = "asc"):
    return search_videos_db(title_query, tags_query, sort_by, sort_order)

@app.get("/videos/{video_id}")
def read_video(video_id: int):
    return get_video_by_id_db(video_id)

@app.get("/videos/{video_id}/transcript")
def read_transcript(video_id: int):
    return get_or_create_transcript_db(video_id)

@app.get("/tags/")
def read_tags():
    return get_all_tags_db()

@app.put("/videos/{video_id}")
def update_video(video_id: int, video: Video):
    return update_video_db(video_id, video)

@app.delete("/videos/{video_id}")
def delete_video(video_id: int):
    return delete_video_db(video_id)