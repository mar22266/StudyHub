import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, SessionLocal, engine
from app.routers import appointments, auth, dashboard, groups
from app.seed.data import seed_database
from app import models  # registers models

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try: seed_database(db)
    finally: db.close()
    yield

app = FastAPI(title="StudyHub API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:6000")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router); app.include_router(groups.router); app.include_router(appointments.router); app.include_router(dashboard.router)
@app.get("/api/health", tags=["Sistema"])
def health(): return {"status": "ok"}
