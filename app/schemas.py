from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# University schemas
class UniversityBase(BaseModel):
    pubukprn: str
    ukprn: Optional[str] = None
    legal_name: str
    first_trading_name: Optional[str] = None
    other_names: Optional[str] = None
    address: Optional[str] = None
    telephone: Optional[str] = None
    website: Optional[str] = None
    country: Optional[str] = None

class UniversityCreate(UniversityBase):
    pass

class University(UniversityBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Entry requirement schemas
class EntryRequirementBase(BaseModel):
    kiscourseid: str
    kis_mode: Optional[str] = None
    tariff_unavail_reason: Optional[str] = None
    tariff_population: Optional[str] = None
    tariff_agg: Optional[float] = None
    tariff_agg_year: Optional[str] = None
    tariff_year1: Optional[str] = None
    tariff_year2: Optional[str] = None
    tariff_subject: Optional[str] = None
    t001_t048: Optional[float] = None
    t048_t064: Optional[float] = None
    t064_t080: Optional[float] = None
    t080_t096: Optional[float] = None
    t096_t112: Optional[float] = None
    t112_t128: Optional[float] = None
    t128_t144: Optional[float] = None
    t144_t160: Optional[float] = None
    t160_t176: Optional[float] = None
    t176_t192: Optional[float] = None
    t192_t208: Optional[float] = None
    t208_t224: Optional[float] = None
    t224_t240: Optional[float] = None

class EntryRequirementCreate(EntryRequirementBase):
    pass

class EntryRequirement(EntryRequirementBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Course schemas
class CourseBase(BaseModel):
    kiscourseid: str
    pubukprn: str
    title: str
    title_welsh: Optional[str] = None
    kis_mode: Optional[str] = None
    kis_level: Optional[str] = None
    hecos_code: Optional[str] = None
    ucas_prog_id: Optional[str] = None
    honours: Optional[bool] = None
    foundation: Optional[bool] = None
    sandwich: Optional[bool] = None
    year_abroad: Optional[bool] = None
    nhs: Optional[bool] = None
    distance_learning: Optional[bool] = None
    num_stage: Optional[int] = None
    location_change: Optional[bool] = None
    kisaaim_code: Optional[str] = None
    year: Optional[int] = None

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    university: Optional[University] = None
    entry_requirements: Optional[List[EntryRequirement]] = []

    class Config:
        from_attributes = True

# API response schemas
class CourseSearchResponse(BaseModel):
    count: int
    results: List[Course]

class UniversitySearchResponse(BaseModel):
    count: int
    results: List[University]
