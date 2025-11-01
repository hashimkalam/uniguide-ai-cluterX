import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List
from app.db.base import async_session
from app.db.models import University, Course, EntryRequirement
from app.config import settings
from sqlalchemy import select

logger = logging.getLogger(__name__)

class DataIngestionService:
    """Service for ingesting Discover Uni data into the database."""

    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir or settings.data_directory)
        self.encodings = ['utf-8', 'latin1', 'cp1252']

    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load a CSV file with automatic encoding detection."""
        file_path = self.data_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        for encoding in self.encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding, low_memory=False)
                logger.info(f"Successfully loaded {filename} with encoding {encoding}")
                return df
            except UnicodeDecodeError:
                continue

        raise ValueError(f"Could not load {filename} with any encoding")

    async def ingest_universities(self) -> int:
        """Ingest university data from INSTITUTION.csv."""
        logger.info("Starting university data ingestion...")

        df = self.load_csv("INSTITUTION.csv")
        count = 0

        async with async_session() as session:
            for _, row in df.iterrows():
                # Check if university already exists
                existing = await session.execute(
                    select(University).where(University.pubukprn == str(row['PUBUKPRN']))
                )
                if existing.scalar_one_or_none():
                    continue

                university = University(
                    pubukprn=str(row['PUBUKPRN']),
                    ukprn=str(row['UKPRN']) if pd.notna(row['UKPRN']) else None,
                    legal_name=str(row['LEGAL_NAME']) if pd.notna(row['LEGAL_NAME']) else "",
                    first_trading_name=str(row['FIRST_TRADING_NAME']) if pd.notna(row['FIRST_TRADING_NAME']) else None,
                    other_names=str(row['OTHER_NAMES']) if pd.notna(row['OTHER_NAMES']) else None,
                    address=str(row['PROVADDRESS']) if pd.notna(row['PROVADDRESS']) else None,
                    telephone=str(row['PROVTEL']) if pd.notna(row['PROVTEL']) else None,
                    website=str(row['PROVURL']) if pd.notna(row['PROVURL']) else None,
                    country=str(row['COUNTRY']) if pd.notna(row['COUNTRY']) else None,
                )

                session.add(university)
                count += 1

                if count % 100 == 0:
                    await session.commit()
                    logger.info(f"Processed {count} universities...")

            await session.commit()

        logger.info(f"Completed university ingestion: {count} new universities added")
        return count

    async def ingest_courses(self) -> int:
        """Ingest course data from KISCOURSE.csv."""
        logger.info("Starting course data ingestion...")

        df = self.load_csv("KISCOURSE.csv")
        count = 0

        async with async_session() as session:
            for _, row in df.iterrows():
                # Check if course already exists
                existing = await session.execute(
                    select(Course).where(Course.kiscourseid == str(row['KISCOURSEID']))
                )
                if existing.scalar_one_or_none():
                    continue

                # Check if university exists
                university_exists = await session.execute(
                    select(University).where(University.pubukprn == str(row['PUBUKPRN']))
                )
                if not university_exists.scalar_one_or_none():
                    logger.warning(f"University {row['PUBUKPRN']} not found for course {row['KISCOURSEID']}")
                    continue

                course = Course(
                    kiscourseid=str(row['KISCOURSEID']),
                    pubukprn=str(row['PUBUKPRN']),
                    title=str(row['TITLE']) if pd.notna(row['TITLE']) else "",
                    title_welsh=str(row['TITLEW']) if pd.notna(row['TITLEW']) else None,
                    kis_mode=str(row['KISMODE']) if pd.notna(row['KISMODE']) else None,
                    kis_level=str(row['KISLEVEL']) if pd.notna(row['KISLEVEL']) else None,
                    hecos_code=str(row['HECOS']) if pd.notna(row['HECOS']) else None,
                    ucas_prog_id=str(row['UCASPROGID']) if pd.notna(row['UCASPROGID']) else None,
                    honours=bool(row['HONOURS']) if pd.notna(row['HONOURS']) else None,
                    foundation=bool(row['FOUNDATION']) if pd.notna(row['FOUNDATION']) else None,
                    sandwich=bool(row['SANDWICH']) if pd.notna(row['SANDWICH']) else None,
                    year_abroad=bool(row['YEARABROAD']) if pd.notna(row['YEARABROAD']) else None,
                    nhs=bool(row['NHS']) if pd.notna(row['NHS']) else None,
                    distance_learning=bool(row['DISTANCE']) if pd.notna(row['DISTANCE']) else None,
                    num_stage=int(row['NUMSTAGE']) if pd.notna(row['NUMSTAGE']) else None,
                    location_change=bool(row['LOCCHNGE']) if pd.notna(row['LOCCHNGE']) else None,
                    kisaaim_code=str(row['KISAIMCODE']) if pd.notna(row['KISAIMCODE']) else None,
                )

                session.add(course)
                count += 1

                if count % 500 == 0:
                    await session.commit()
                    logger.info(f"Processed {count} courses...")

            await session.commit()

        logger.info(f"Completed course ingestion: {count} new courses added")
        return count

    async def ingest_entry_requirements(self) -> int:
        """Ingest entry requirements data from TARIFF.csv."""
        logger.info("Starting entry requirements data ingestion...")

        df = self.load_csv("TARIFF.csv")
        count = 0

        async with async_session() as session:
            for _, row in df.iterrows():
                # Check if entry requirement already exists (composite key)
                existing = await session.execute(
                    select(EntryRequirement).where(
                        EntryRequirement.kiscourseid == str(row['KISCOURSEID']),
                        EntryRequirement.kis_mode == str(row['KISMODE']) if pd.notna(row['KISMODE']) else None
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                # Check if course exists
                course_exists = await session.execute(
                    select(Course).where(Course.kiscourseid == str(row['KISCOURSEID']))
                )
                if not course_exists.scalar_one_or_none():
                    logger.warning(f"Course {row['KISCOURSEID']} not found for entry requirements")
                    continue

                entry_req = EntryRequirement(
                    kiscourseid=str(row['KISCOURSEID']),
                    kis_mode=str(row['KISMODE']) if pd.notna(row['KISMODE']) else None,
                    tariff_unavail_reason=str(row['TARUNAVAILREASON']) if pd.notna(row['TARUNAVAILREASON']) else None,
                    tariff_population=str(row['TARPOP']) if pd.notna(row['TARPOP']) else None,
                    tariff_agg=float(row['TARAGG']) if pd.notna(row['TARAGG']) else None,
                    tariff_agg_year=str(row['TARAGGYEAR']) if pd.notna(row['TARAGGYEAR']) else None,
                    tariff_year1=str(row['TARYEAR1']) if pd.notna(row['TARYEAR1']) else None,
                    tariff_year2=str(row['TARYEAR2']) if pd.notna(row['TARYEAR2']) else None,
                    tariff_subject=str(row['TARSBJ']) if pd.notna(row['TARSBJ']) else None,
                    t001_t048=float(row['T001']) if pd.notna(row['T001']) else None,
                    t048_t064=float(row['T048']) if pd.notna(row['T048']) else None,
                    t064_t080=float(row['T064']) if pd.notna(row['T064']) else None,
                    t080_t096=float(row['T080']) if pd.notna(row['T080']) else None,
                    t096_t112=float(row['T096']) if pd.notna(row['T096']) else None,
                    t112_t128=float(row['T112']) if pd.notna(row['T112']) else None,
                    t128_t144=float(row['T128']) if pd.notna(row['T128']) else None,
                    t144_t160=float(row['T144']) if pd.notna(row['T144']) else None,
                    t160_t176=float(row['T160']) if pd.notna(row['T160']) else None,
                    t176_t192=float(row['T176']) if pd.notna(row['T176']) else None,
                    t192_t208=float(row['T192']) if pd.notna(row['T192']) else None,
                    t208_t224=float(row['T208']) if pd.notna(row['T208']) else None,
                    t224_t240=float(row['T224']) if pd.notna(row['T224']) else None,
                )

                session.add(entry_req)
                count += 1

                if count % 500 == 0:
                    await session.commit()
                    logger.info(f"Processed {count} entry requirements...")

            await session.commit()

        logger.info(f"Completed entry requirements ingestion: {count} new entry requirements added")
        return count

    async def ingest_all_data(self) -> Dict[str, int]:
        """Ingest all data from CSV files."""
        logger.info("Starting full data ingestion...")

        results = {}

        try:
            results['universities'] = await self.ingest_universities()
            results['courses'] = await self.ingest_courses()
            results['entry_requirements'] = await self.ingest_entry_requirements()

            logger.info("Data ingestion completed successfully")
            logger.info(f"Results: {results}")

        except Exception as e:
            logger.error(f"Data ingestion failed: {str(e)}")
            raise

        return results

# Convenience function for running ingestion
async def run_data_ingestion():
    """Run the complete data ingestion process."""
    service = DataIngestionService()
    return await service.ingest_all_data()
