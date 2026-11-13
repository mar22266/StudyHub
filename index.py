"""Entrada de FastAPI para Vercel; Docker conserva app.main:app."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app.main import app  # noqa: E402, F401
from fastapi.staticfiles import StaticFiles  # noqa: E402

# La API conserva prioridad; Vercel detecta este montaje y publica el build estático.
app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent / "frontend" / "dist",
                          html=True, check_dir=False), name="frontend")
