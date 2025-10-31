import sys
from pathlib import Path

# ensure project root is on sys.path so 'app' package imports work when running main.py directly
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from app.routes.courses import router as courses_router
from app.jobs.scheduler import start_scheduler

app = FastAPI(title="UniGuide AI")
app.include_router(courses_router, prefix="/courses")

# Start scheduler (in-process; OK for demo)
start_scheduler()

@app.get("/")
async def root():
    return {"status": "ok"}