from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class University(Base):
    __tablename__ = "universities"
    id = Column(Integer, primary_key=True)
    provider_id = Column(String, unique=True, index=True)
    name = Column(String, nullable=False)
    ukprn = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    course_id = Column(String, unique=True, index=True)
    provider_id = Column(String, index=True)
    course_name = Column(Text)
    subject = Column(String)
    level = Column(String)
    study_mode = Column(String)
    year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EntryRequirement(Base):
    __tablename__ = "entry_requirements"
    id = Column(Integer, primary_key=True)
    course_id = Column(String, index=True)
    requirement_text = Column(Text)
    typical_offers = Column(String)
    tariff_points = Column(Integer)
