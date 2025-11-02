import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from app.db.base import async_session
from app.config import settings

async def inspect_database():
    """Inspect database records and show summary."""
    print(f"🔍 Inspecting database: {settings.database_url}")
    print("=" * 60)

    try:
        async with async_session() as session:
            # Check table counts
            tables = ['universities', 'courses', 'entry_requirements']

            for table in tables:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"📊 {table}: {count} records")

            print("\n" + "=" * 60)

            # Show sample universities
            print("🏫 Sample Universities:")
            result = await session.execute(text("""
                SELECT pubukprn, legal_name, country
                FROM universities
                LIMIT 5
            """))
            universities = result.fetchall()
            for uni in universities:
                print(f"  • {uni[1]} ({uni[0]}) - {uni[2]}")

            print("\n" + "=" * 60)

            # Show sample courses
            print("📚 Sample Courses:")
            result = await session.execute(text("""
                SELECT c.title, u.legal_name, c.kis_mode
                FROM courses c
                JOIN universities u ON c.pubukprn = u.pubukprn
                LIMIT 5
            """))
            courses = result.fetchall()
            for course in courses:
                print(f"  • {course[0]} at {course[1]} ({course[2]})")

            print("\n" + "=" * 60)

            # Show entry requirements sample
            print("📈 Sample Entry Requirements:")
            result = await session.execute(text("""
                SELECT c.title, er.tariff_agg, er.tariff_agg_year
                FROM entry_requirements er
                JOIN courses c ON er.kiscourseid = c.kiscourseid
                WHERE er.tariff_agg IS NOT NULL
                LIMIT 5
            """))
            requirements = result.fetchall()
            for req in requirements:
                print(f"  • {req[0]}: Tariff {req[1]} (Year {req[2]})")

    except Exception as e:
        print(f"❌ Database inspection failed: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_database())