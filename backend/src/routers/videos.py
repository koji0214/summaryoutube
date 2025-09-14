from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src import crud, models
from src.database import get_db

router = APIRouter()

@router.post("/videos/", response_model=models.VideoSchema)
def create_video(video: models.VideoCreate, db: Session = Depends(get_db)):
    # Note: In the next step, we will make this asynchronous.
    return crud.create_video(db=db, video=video)

@router.get("/videos/", response_model=List[models.VideoSchema])
def read_videos(
    title_query: Optional[str] = None, 
    tags_query: Optional[str] = None, 
    sort_by: str = "id", 
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):
    return crud.search_videos(db, title_query, tags_query, sort_by, sort_order)

@router.get("/videos/{video_id}", response_model=models.VideoSchema)
def read_video(video_id: int, db: Session = Depends(get_db)):
    db_video = crud.get_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@router.put("/videos/{video_id}", response_model=models.VideoSchema)
def update_video(video_id: int, video: models.VideoUpdate, db: Session = Depends(get_db)):
    db_video = crud.update_video(db=db, video_id=video_id, video=video)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return db_video

@router.delete("/videos/{video_id}")
def delete_video(video_id: int, db: Session = Depends(get_db)):
    db_video = crud.delete_video(db, video_id=video_id)
    if db_video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"message": "Video deleted successfully"}

@router.get("/videos/{video_id}/transcript")
def read_transcript(video_id: int, db: Session = Depends(get_db)):
    return crud.get_or_create_transcript(db, video_id=video_id)
