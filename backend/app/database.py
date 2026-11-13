import os
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://studyhub_user:studyhub_password@db:5432/studyhub")
if os.getenv("VERCEL") and not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL es obligatoria en Vercel")
database_url = make_url(DATABASE_URL)
if database_url.drivername in ("postgres", "postgresql"):
    database_url = database_url.set(drivername="postgresql+psycopg")
engine = create_engine(database_url, pool_pre_ping=True,
                       **({"poolclass": NullPool} if os.getenv("VERCEL") else {}))
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
