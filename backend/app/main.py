import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, SessionLocal, engine
from app.routers import appointments, auth, dashboard, groups
from app.seed.data import seed_database
from app import models  # registers models

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Las cuentas conocidas del laboratorio no deben crearse en una nube pública.
        if os.getenv("SEED_DEMO_DATA", "false" if os.getenv("VERCEL") else "true").lower() == "true":
            seed_database(db)
    finally: db.close()
    yield

app = FastAPI(title="StudyHub API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:6000")], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router); app.include_router(groups.router); app.include_router(appointments.router); app.include_router(dashboard.router)
@app.get("/api/health", tags=["Sistema"])
def health(): return {"status": "ok", "commit": os.getenv("STUDYHUB_COMMIT_SHA", "local")}

@app.get("/api/ready", tags=["Sistema"])
def ready():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Base de datos no disponible") from None
    return {"status": "ok", "database": "ok", "commit": os.getenv("STUDYHUB_COMMIT_SHA", "local")}
