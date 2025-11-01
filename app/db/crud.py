from app.db.base import async_session
from app.db.models import Course, University, EntryRequirement
from sqlalchemy import select, or_, and_
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import selectinload
import redis.asyncio as redis
import json
from app.config import settings

# Redis client
redis_client = redis.from_url(settings.redis_url)

async def find_courses(
    university: Optional[str] = None,
    subject: Optional[str] = None,
    year: Optional[int] = None,
    course_name: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Find courses with optional filtering.
    Returns courses with university and entry requirements data.
    """
    # Create cache key
    cache_key = f"courses:v2:{university or ''}:{subject or ''}:{year or ''}:{course_name or ''}:{limit}:{offset}"
    
    # Try to get from cache
    try:
        cached_result = await redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
    except Exception:
        pass  # Continue to DB query if cache fails
    
    async with async_session() as session:
        query = (
            select(Course)
            .options(
                selectinload(Course.university),
                selectinload(Course.entry_requirements)
            )
        )

        # Build filters
        filters = []
        if university:
            # Search in university name or legal name
            filters.append(
                or_(
                    University.legal_name.ilike(f"%{university}%"),
                    University.first_trading_name.ilike(f"%{university}%"),
                    University.other_names.ilike(f"%{university}%")
                )
            )
            # Join with university for filtering
            query = query.join(University, Course.pubukprn == University.pubukprn)

        if subject:
            # Search in course title or HECoS code
            filters.append(
                or_(
                    Course.title.ilike(f"%{subject}%"),
                    Course.hecos_code.ilike(f"%{subject}%"),
                    Course.kisaaim_code.ilike(f"%{subject}%")
                )
            )

        if course_name:
            filters.append(Course.title == course_name)

        if year:
            filters.append(
                Course.kiscourseid.in_(
                    select(EntryRequirement.kiscourseid).where(EntryRequirement.tariff_agg_year.like(f'{year}%'))
                )
            )

        if filters:
            query = query.where(and_(*filters))

        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        courses = result.scalars().all()

        # Convert to dict format for API response
        course_list = []
        for course in courses:
            course_dict = {
                "id": course.id,
                "kiscourseid": course.kiscourseid,
                "pubukprn": course.pubukprn,
                "title": course.title,
                "title_welsh": course.title_welsh,
                "kis_mode": course.kis_mode,
                "kis_level": course.kis_level,
                "hecos_code": course.hecos_code,
                "ucas_prog_id": course.ucas_prog_id,
                "honours": course.honours,
                "foundation": course.foundation,
                "sandwich": course.sandwich,
                "year_abroad": course.year_abroad,
                "nhs": course.nhs,
                "distance_learning": course.distance_learning,
                "num_stage": course.num_stage,
                "location_change": course.location_change,
                "kisaaim_code": course.kisaaim_code,
                "year": course.year,
                "created_at": course.created_at,
                "updated_at": course.updated_at,
                "university": {
                    "id": course.university.id,
                    "pubukprn": course.university.pubukprn,
                    "ukprn": course.university.ukprn,
                    "legal_name": course.university.legal_name,
                    "first_trading_name": course.university.first_trading_name,
                    "other_names": course.university.other_names,
                    "address": course.university.address,
                    "telephone": course.university.telephone,
                    "website": course.university.website,
                    "country": course.university.country,
                    "created_at": course.university.created_at,
                    "updated_at": course.university.updated_at,
                } if course.university else None,
                "entry_requirements": [
                    {
                        "id": req.id,
                        "kiscourseid": req.kiscourseid,
                        "kis_mode": req.kis_mode,
                        "tariff_unavail_reason": req.tariff_unavail_reason,
                        "tariff_population": req.tariff_population,
                        "tariff_agg": req.tariff_agg,
                        "tariff_agg_year": req.tariff_agg_year,
                        "tariff_year1": req.tariff_year1,
                        "tariff_year2": req.tariff_year2,
                        "tariff_subject": req.tariff_subject,
                        "t001_t048": req.t001_t048,
                        "t048_t064": req.t048_t064,
                        "t064_t080": req.t064_t080,
                        "t080_t096": req.t080_t096,
                        "t096_t112": req.t096_t112,
                        "t112_t128": req.t112_t128,
                        "t128_t144": req.t128_t144,
                        "t144_t160": req.t144_t160,
                        "t160_t176": req.t160_t176,
                        "t176_t192": req.t176_t192,
                        "t192_t208": req.t192_t208,
                        "t208_t224": req.t208_t224,
                        "t224_t240": req.t224_t240,
                        "created_at": req.created_at,
                    } for req in course.entry_requirements
                ]
            }
            course_list.append(course_dict)

        # Cache the result
        try:
            await redis_client.setex(cache_key, 3600, json.dumps(course_list))  # Cache for 1 hour
        except Exception:
            pass  # Ignore cache errors

        return course_list

async def get_course_by_id(course_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific course by its KISCOURSEID."""
    async with async_session() as session:
        query = (
            select(Course)
            .options(
                selectinload(Course.university),
                selectinload(Course.entry_requirements)
            )
            .where(Course.kiscourseid == course_id)
        )
        result = await session.execute(query)
        course = result.scalar_one_or_none()

        if not course:
            return None

        return {
            "id": course.id,
            "kiscourseid": course.kiscourseid,
            "pubukprn": course.pubukprn,
            "title": course.title,
            "title_welsh": course.title_welsh,
            "kis_mode": course.kis_mode,
            "kis_level": course.kis_level,
            "hecos_code": course.hecos_code,
            "ucas_prog_id": course.ucas_prog_id,
            "honours": course.honours,
            "foundation": course.foundation,
            "sandwich": course.sandwich,
            "year_abroad": course.year_abroad,
            "nhs": course.nhs,
            "distance_learning": course.distance_learning,
            "num_stage": course.num_stage,
            "location_change": course.location_change,
            "kisaaim_code": course.kisaaim_code,
            "year": course.year,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
            "university": {
                "id": course.university.id,
                "pubukprn": course.university.pubukprn,
                "legal_name": course.university.legal_name,
                "first_trading_name": course.university.first_trading_name,
                "website": course.university.website,
                "country": course.university.country,
            } if course.university else None,
            "entry_requirements": [
                {
                    "id": req.id,
                    "kis_mode": req.kis_mode,
                    "tariff_agg": req.tariff_agg,
                    "tariff_agg_year": req.tariff_agg_year,
                    "tariff_unavail_reason": req.tariff_unavail_reason,
                    "tariff_population": req.tariff_population,
                    "t001_t048": req.t001_t048,
                    "t048_t064": req.t048_t064,
                    "t064_t080": req.t064_t080,
                    "t080_t096": req.t080_t096,
                    "t096_t112": req.t096_t112,
                    "t112_t128": req.t112_t128,
                    "t128_t144": req.t128_t144,
                    "t144_t160": req.t144_t160,
                    "t160_t176": req.t160_t176,
                    "t176_t192": req.t176_t192,
                    "t192_t208": req.t192_t208,
                    "t208_t224": req.t208_t224,
                    "t224_t240": req.t224_t240,
                } for req in course.entry_requirements
            ]
        }

async def find_universities(
    name: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Find universities with optional filtering."""
    async with async_session() as session:
        query = select(University)

        filters = []
        if name:
            filters.append(
                or_(
                    University.legal_name.ilike(f"%{name}%"),
                    University.first_trading_name.ilike(f"%{name}%"),
                    University.other_names.ilike(f"%{name}%")
                )
            )

        if country:
            filters.append(University.country.ilike(f"%{country}%"))

        if filters:
            query = query.where(and_(*filters))

        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        universities = result.scalars().all()

        return [
            {
                "id": uni.id,
                "pubukprn": uni.pubukprn,
                "ukprn": uni.ukprn,
                "legal_name": uni.legal_name,
                "first_trading_name": uni.first_trading_name,
                "website": uni.website,
                "country": uni.country,
                "created_at": uni.created_at,
            } for uni in universities
        ]

async def get_course_count(
    university: Optional[str] = None,
    subject: Optional[str] = None,
    year: Optional[int] = None,
    course_name: Optional[str] = None,
) -> int:
    """Get the count of courses matching the filters."""
    async with async_session() as session:
        query = select(Course)

        filters = []
        if university:
            query = query.join(University, Course.pubukprn == University.pubukprn)
            filters.append(
                or_(
                    University.legal_name.ilike(f"%{university}%"),
                    University.first_trading_name.ilike(f"%{university}%"),
                    University.other_names.ilike(f"%{university}%")
                )
            )

        if subject:
            filters.append(
                or_(
                    Course.title.ilike(f"%{subject}%"),
                    Course.hecos_code.ilike(f"%{subject}%"),
                    Course.kisaaim_code.ilike(f"%{subject}%")
                )
            )

        if course_name:
            filters.append(Course.title == course_name)

        if year:
            filters.append(
                Course.kiscourseid.in_(
                    select(EntryRequirement.kiscourseid).where(EntryRequirement.tariff_agg_year.like(f'{year}%'))
                )
            )

        if filters:
            query = query.where(and_(*filters))

        result = await session.execute(query)
        return len(result.scalars().all())
