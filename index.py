"""Entrada de FastAPI para Vercel; Docker conserva app.main:app."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

from app.main import app  # noqa: E402, F401
