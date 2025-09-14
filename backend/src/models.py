from sqlalchemy import Column, Integer, String, Text, DateTime, func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .database import Base

# SQLAlchemy Model
class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False)
    title = Column(String(255), nullable=False)
    channel_name = Column(String(255), nullable=False)
    tags = Column(Text, nullable=True)
    memo = Column(Text, nullable=True)
    transcript = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default='completed') # processing, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Pydantic Models (Schemas)
class VideoBase(BaseModel):
    url: str
    tags: Optional[str] = None
    memo: Optional[str] = None
    transcriptionOption: Optional[str] = None # This is not stored in DB, used for creation logic

class VideoCreate(VideoBase):
    pass

class VideoUpdate(VideoBase):
    pass

class VideoSchema(VideoBase):
    id: int
    title: str
    channel_name: str
    transcript: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Replaces orm_mode = True
