"""Publicar el build de Vite en el directorio estático de Vercel."""

from pathlib import Path
import shutil

root = Path(__file__).resolve().parent.parent
source = root / "frontend" / "dist"
if not (source / "index.html").is_file():
    raise SystemExit("Falta frontend/dist/index.html; ejecutar primero npm run build.")
shutil.copytree(source, root / "public", dirs_exist_ok=True)
