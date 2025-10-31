from fastapi import APIRouter, Query
from typing import Optional
from app.db.crud import find_courses

router = APIRouter()

@router.get("", summary="Search courses")
async def list_courses(
    university: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    limit: int = 50
):
    rows = await find_courses(university=university, subject=subject, year=year, limit=limit)
    return {"count": len(rows), "results": rows}
