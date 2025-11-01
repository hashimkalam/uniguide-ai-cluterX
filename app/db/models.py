from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class University(Base):
    __tablename__ = "universities"
    id = Column(Integer, primary_key=True)
    pubukprn = Column(String, unique=True, index=True, nullable=False)  # Provider ID
    ukprn = Column(String, nullable=True)
    legal_name = Column(String, nullable=False)
    first_trading_name = Column(String, nullable=True)
    other_names = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    telephone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    courses = relationship("Course", back_populates="university")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    kiscourseid = Column(String, unique=True, index=True, nullable=False)  # Course ID
    pubukprn = Column(String, ForeignKey("universities.pubukprn"), index=True, nullable=False)
    title = Column(String, nullable=False)  # Course title
    title_welsh = Column(String, nullable=True)
    kis_mode = Column(String, nullable=True)  # Full-time, part-time, etc.
    kis_level = Column(String, nullable=True)  # Level of course
    hecos_code = Column(String, nullable=True)
    ucas_prog_id = Column(String, nullable=True)
    honours = Column(Boolean, nullable=True)
    foundation = Column(Boolean, nullable=True)
    sandwich = Column(Boolean, nullable=True)
    year_abroad = Column(Boolean, nullable=True)
    nhs = Column(Boolean, nullable=True)
    distance_learning = Column(Boolean, nullable=True)
    num_stage = Column(Integer, nullable=True)  # Number of stages
    location_change = Column(Boolean, nullable=True)
    kisaaim_code = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    university = relationship("University", back_populates="courses")
    entry_requirements = relationship("EntryRequirement", back_populates="course")

class EntryRequirement(Base):
    __tablename__ = "entry_requirements"
    id = Column(Integer, primary_key=True)
    kiscourseid = Column(String, ForeignKey("courses.kiscourseid"), index=True, nullable=False)
    kis_mode = Column(String, nullable=True)
    tariff_unavail_reason = Column(String, nullable=True)
    tariff_population = Column(String, nullable=True)
    tariff_agg = Column(Float, nullable=True)  # Aggregate tariff score
    tariff_agg_year = Column(String, nullable=True)
    tariff_year1 = Column(String, nullable=True)
    tariff_year2 = Column(String, nullable=True)
    tariff_subject = Column(String, nullable=True)
    # Tariff points for different ranges
    t001_t048 = Column(Float, nullable=True)
    t048_t064 = Column(Float, nullable=True)
    t064_t080 = Column(Float, nullable=True)
    t080_t096 = Column(Float, nullable=True)
    t096_t112 = Column(Float, nullable=True)
    t112_t128 = Column(Float, nullable=True)
    t128_t144 = Column(Float, nullable=True)
    t144_t160 = Column(Float, nullable=True)
    t160_t176 = Column(Float, nullable=True)
    t176_t192 = Column(Float, nullable=True)
    t192_t208 = Column(Float, nullable=True)
    t208_t224 = Column(Float, nullable=True)
    t224_t240 = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship
    course = relationship("Course", back_populates="entry_requirements")
