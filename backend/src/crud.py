from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from . import models
from .database import SessionLocal # Import SessionLocal for background tasks
from .youtube_api import (
    extract_video_id,
    get_youtube_video_details,
    get_transcript_from_youtube,
    get_high_quality_transcript
)

def run_high_quality_transcription(video_id: int):
    """This function runs in the background to get the transcript."""
    db = SessionLocal()
    try:
        print(f"[Background Task] Starting transcription for video_id: {video_id}")
        db_video = get_video(db, video_id)
        if not db_video:
            print(f"[Background Task] Video not found: {video_id}")
            return

        video_id_yt = extract_video_id(db_video.url)
        if not video_id_yt:
            raise ValueError("Could not extract YouTube ID from URL")

        transcript = get_high_quality_transcript(video_id_yt)
        
        if transcript is not None:
            db_video.transcript = transcript
            db_video.status = 'completed'
            print(f"[Background Task] Transcription successful for video_id: {video_id}")
        else:
            raise ValueError("Transcription failed to produce a result.")

        db.commit()

    except Exception as e:
        db_video.status = 'failed'
        db_video.memo = f"Transcription failed: {str(e)}"
        print(f"[Background Task] Transcription failed for video_id: {video_id}. Error: {e}")
        db.commit()
    finally:
        db.close()

def get_video(db: Session, video_id: int) -> Optional[models.Video]:
    return db.query(models.Video).filter(models.Video.id == video_id).first()

def search_videos(
    db: Session, 
    title_query: Optional[str] = None, 
    tags_query: Optional[str] = None, 
    sort_by: str = "id", 
    sort_order: str = "asc"
) -> List[models.Video]:
    query = db.query(models.Video)

    if title_query:
        query = query.filter(models.Video.title.ilike(f"%{title_query}%"))
    
    if tags_query:
        tags = [tag.strip() for tag in tags_query.split(',') if tag.strip()]
        for tag in tags:
            query = query.filter(models.Video.tags.ilike(f"%{tag}%"))

    sort_column = getattr(models.Video, sort_by, models.Video.id)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    return query.all()

def create_video(db: Session, video: models.VideoCreate) -> models.Video:
    video_id_yt = extract_video_id(video.url)
    if not video_id_yt:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    title, channel_name = get_youtube_video_details(video_id_yt)
    if not title or not channel_name:
        raise HTTPException(status_code=500, detail="Could not retrieve video details from YouTube API.")

    transcript = None
    status = 'completed' # Default status

    if video.transcriptionOption == 'standard':
        transcript = get_transcript_from_youtube(video_id_yt)
    elif video.transcriptionOption == 'high_quality':
        # Set status to processing, transcript will be fetched in the background
        status = 'processing'

    db_video = models.Video(
        url=video.url,
        title=title,
        channel_name=channel_name,
        tags=video.tags,
        memo=video.memo,
        transcript=transcript,
        status=status
    )
    
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def update_video(db: Session, video_id: int, video: models.VideoUpdate) -> Optional[models.Video]:
    db_video = get_video(db, video_id)
    if not db_video:
        return None

    if video.url != db_video.url:
        video_id_yt = extract_video_id(video.url)
        if not video_id_yt:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        title, channel_name = get_youtube_video_details(video_id_yt)
        if not title or not channel_name:
            raise HTTPException(status_code=500, detail="Could not retrieve video details.")
        db_video.title = title
        db_video.channel_name = channel_name
    
    db_video.url = video.url
    db_video.tags = video.tags
    db_video.memo = video.memo

    db.commit()
    db.refresh(db_video)
    return db_video

def delete_video(db: Session, video_id: int) -> Optional[models.Video]:
    db_video = get_video(db, video_id)
    if not db_video:
        return None
    
    db.delete(db_video)
    db.commit()
    return db_video

def get_all_tags(db: Session) -> List[str]:
    results = db.query(models.Video.tags).filter(models.Video.tags.isnot(None)).all()
    all_tags = set()
    for row in results:
        if row[0]:
            tags = [tag.strip() for tag in row[0].split(',') if tag.strip()]
            all_tags.update(tags)
    return sorted(list(all_tags))

def get_or_create_transcript(db: Session, video_id: int) -> dict:
    db_video = get_video(db, video_id)
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")

    # This endpoint now simply returns the current state
    return {"transcript": db_video.transcript, "status": db_video.status}