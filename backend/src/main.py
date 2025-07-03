from fastapi import FastAPI, HTTPException
from src.models import Video
from src.database import create_tables
from src.crud import create_video_db, get_videos_db, update_video_db, delete_video_db

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
def read_videos():
    return get_videos_db()

@app.put("/videos/{video_id}")
def update_video(video_id: int, video: Video):
    return update_video_db(video_id, video)

@app.delete("/videos/{video_id}")
def delete_video(video_id: int):
    return delete_video_db(video_id)