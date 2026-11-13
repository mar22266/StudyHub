"""Extraer una URL validada de la salida JSON o de texto de Vercel CLI."""

import json
from pathlib import Path
import re
import sys


def deployment_url(raw: str) -> str:
    raw = raw.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        url = raw.splitlines()[-1] if raw else ""
    else:
        url = data.get("deployment", {}).get("url", "")
    if not isinstance(url, str) or not re.fullmatch(r"https://[a-zA-Z0-9.-]+", url):
        raise ValueError("Vercel no devolvió una URL HTTPS de despliegue válida")
    return url


if __name__ == "__main__":
    print(deployment_url(Path(sys.argv[1]).read_text()))
