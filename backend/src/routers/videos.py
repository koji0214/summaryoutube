from fastapi import APIRouter, HTTPException
from typing import Optional
from src.models import Video
from src.crud import create_video_db, update_video_db, delete_video_db, search_videos_db, get_video_by_id_db, get_or_create_transcript_db
from src.youtube_api import extract_video_id

router = APIRouter()

@router.post("/videos/", response_model=Video)
def create_video(video: Video):
    return create_video_db(video)

@router.get("/videos/")
def read_videos(title_query: Optional[str] = None, tags_query: Optional[str] = None, sort_by: str = "id", sort_order: str = "asc"):
    return search_videos_db(title_query, tags_query, sort_by, sort_order)

@router.get("/videos/{video_id}")
def read_video(video_id: int):
    return get_video_by_id_db(video_id)

@router.put("/videos/{video_id}")
def update_video(video_id: int, video: Video):
    return update_video_db(video_id, video)

@router.delete("/videos/{video_id}")
def delete_video(video_id: int):
    return delete_video_db(video_id)

@router.get("/videos/{video_id}/transcript")
def read_transcript(video_id: int):
    return get_or_create_transcript_db(video_id)