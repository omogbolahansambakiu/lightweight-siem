from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SearchQuery(BaseModel):
    query: str
    start_time: str
    end_time: str

@router.post("/search")
async def search_events(query: SearchQuery):
    return {
        "hits": [],
        "total": 0
    }
