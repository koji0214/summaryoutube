from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from . import models
from .youtube_api import (
    extract_video_id,
    get_youtube_video_details,
    get_transcript_from_youtube,
    get_high_quality_transcript
)

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
        # Assuming tags_query is a comma-separated string of tags to match ALL
        tags = [tag.strip() for tag in tags_query.split(',') if tag.strip()]
        for tag in tags:
            query = query.filter(models.Video.tags.ilike(f"%{tag}%"))

    # Sorting
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
    if video.transcriptionOption == 'standard':
        transcript = get_transcript_from_youtube(video_id_yt)
    elif video.transcriptionOption == 'high_quality':
        # This is the part we will make asynchronous later.
        transcript = get_high_quality_transcript(video_id_yt)

    db_video = models.Video(
        url=video.url,
        title=title,
        channel_name=channel_name,
        tags=video.tags,
        memo=video.memo,
        transcript=transcript
    )
    
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video

def update_video(db: Session, video_id: int, video: models.VideoUpdate) -> Optional[models.Video]:
    db_video = get_video(db, video_id)
    if not db_video:
        return None

    # Check if URL has changed
    if video.url != db_video.url:
        video_id_yt = extract_video_id(video.url)
        if not video_id_yt:
            raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        title, channel_name = get_youtube_video_details(video_id_yt)
        if not title or not channel_name:
            raise HTTPException(status_code=500, detail="Could not retrieve video details.")
        db_video.title = title
        db_video.channel_name = channel_name
    
    # Update other fields
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
        tags = [tag.strip() for tag in row[0].split(',') if tag.strip()]
        all_tags.update(tags)
    return sorted(list(all_tags))

def get_or_create_transcript(db: Session, video_id: int) -> dict:
    db_video = get_video(db, video_id)
    if not db_video:
        raise HTTPException(status_code=404, detail="Video not found")

    if db_video.transcript:
        return {"transcript": db_video.transcript}

    video_id_yt = extract_video_id(db_video.url)
    if not video_id_yt:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL in database")

    new_transcript = get_transcript_from_youtube(video_id_yt)
    if not new_transcript:
        return {"transcript": ""}

    db_video.transcript = new_transcript
    db.commit()
    db.refresh(db_video)

    return {"transcript": new_transcript}
