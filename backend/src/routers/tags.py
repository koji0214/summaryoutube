from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from src.crud import get_all_tags
from src.database import get_db

router = APIRouter()

@router.get("/tags/", response_model=List[str])
def read_tags(db: Session = Depends(get_db)):
    return get_all_tags(db=db)
