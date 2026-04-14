from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.db.database import Base, engine
from app import models
from app.db.database import SessionLocal
from app.services.skill_service import backfill_skill_metadata


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Keep startup bootstrap lightweight for local development until migrations are run.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        backfill_skill_metadata(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.project_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def healthcheck():
    return {"message": f"{settings.project_name} API is running"}
