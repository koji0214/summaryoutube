from fastapi import APIRouter
from src.crud import get_all_tags_db

router = APIRouter()

@router.get("/tags/")
def read_tags():
    return get_all_tags_db()