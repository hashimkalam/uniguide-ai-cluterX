from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.db.crud import find_courses, get_course_by_id, get_course_count
from app.schemas import CourseSearchResponse

router = APIRouter()

@router.get("", summary="Search courses")
async def list_courses(
    university: Optional[str] = Query(None, description="Filter by university name"),
    subject: Optional[str] = Query(None, description="Filter by subject or course title"),
    course_name: Optional[str] = Query(None, description="Filter by specific course name"),
    year: Optional[int] = Query(None, description="Filter by academic year"),
    limit: int = Query(50, description="Maximum number of results", le=100),
    offset: int = Query(0, description="Number of results to skip", ge=0),
):
    """
    Search for university courses with various filters.

    - **university**: Search in university name (legal name, trading name, etc.)
    - **subject**: Search in course title, HECoS code, or KISAIM code
    - **course_name**: Exact match on course title
    - **year**: Filter by academic year
    - **limit**: Maximum results to return (max 100)
    - **offset**: Number of results to skip for pagination
    """
    try:
        courses = await find_courses(
            university=university,
            subject=subject,
            course_name=course_name,
            year=year,
            limit=limit,
            offset=offset
        )
        total_count = await get_course_count(
            university=university,
            subject=subject,
            course_name=course_name,
            year=year
        )
        return CourseSearchResponse(count=total_count, results=courses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{course_id}", summary="Get course details")
async def get_course(course_id: str):
    """
    Get detailed information about a specific course by its KISCOURSEID.

    Includes university information and entry requirements.
    """
    try:
        course = await get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
