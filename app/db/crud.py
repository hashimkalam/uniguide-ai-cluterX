from app.db.base import async_session
from app.db.models import Course, University
from sqlalchemy import select
from typing import Optional, List

async def find_courses(university: Optional[str]=None, subject: Optional[str]=None, year: Optional[int]=None, limit:int=50):
    async with async_session() as s:
        q = select(Course)
        if university:
            # join University to filter by name
            q = q.join(University, Course.provider_id == University.provider_id).where(
                University.name.ilike(f"%{university}%")
            )
        if subject:
            q = q.where(Course.subject.ilike(f"%{subject}%"))
        if year:
            q = q.where(Course.year == year)
        q = q.limit(limit)
        res = await s.execute(q)
        rows = []
        for c in res.scalars().all():
            rows.append({
                "course_id": c.course_id,
                "course_name": c.course_name,
                "subject": c.subject,
                "provider_id": c.provider_id
            })
        return rows
