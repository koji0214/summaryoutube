from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Video(BaseModel):
    url: str
    tags: Optional[str] = None
    memo: Optional[str] = None

class VideoResponse(BaseModel):
    id: int
    url: str
    title: str
    channel_name: str
    tags: Optional[str] = None
    memo: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True