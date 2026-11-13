"""Comprobar frontend, navegación SPA, bundle JS, API, base de datos y commit publicado."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


def vercel_response(base: str, path: str) -> tuple[str, str]:
    command = ["vercel", "curl", path, "--deployment", base, "--yes"]
    if os.environ.get("VERCEL_TOKEN"):
        command.extend(["--token", os.environ["VERCEL_TOKEN"]])
    command.extend(["--", "--fail", "--silent", "--show-error", "--max-time", "30",
                    "--write-out", "\n%{http_code}\n%{content_type}"])
    result = subprocess.run(command, text=True, capture_output=True, check=True, timeout=60)
    body, status, content_type = result.stdout.rstrip("\r\n").rsplit("\n", 2)
    if status != "200":
        raise ValueError("Respuesta HTTP inesperada")
    return body, content_type


def verify(base: str, expected_sha: str, use_vercel_cli: bool = False) -> dict:
    headers = {"User-Agent": "StudyHub-CD/1.0"}
    if os.environ.get("VERCEL_AUTOMATION_BYPASS_SECRET"):
        headers["x-vercel-protection-bypass"] = os.environ["VERCEL_AUTOMATION_BYPASS_SECRET"]

    def get(path: str) -> tuple[str, str]:
        if use_vercel_cli:
            return vercel_response(base, path)
        with urlopen(Request(base + path, headers=headers), timeout=30) as response:
            if response.status != 200:
                raise ValueError("Respuesta HTTP inesperada")
            return response.read().decode("utf-8"), response.headers.get("Content-Type", "")

    home, _ = get("/")
    login, _ = get("/login")
    if '<div id="root"' not in home or '<div id="root"' not in login:
        raise ValueError("El frontend o la navegación SPA no funcionan")
    asset = re.search(r'<script[^>]+src="(/assets/[^\"]+\.js)"', home)
    if not asset:
        raise ValueError("No se encontró el bundle de React")
    bundle, content_type = get(asset.group(1))
    if not bundle.strip() or "javascript" not in content_type:
        raise ValueError("El bundle no se sirve como JavaScript")
    health = json.loads(get("/api/health")[0])
    ready = json.loads(get("/api/ready")[0])
    if health.get("status") != "ok" or ready.get("database") != "ok":
        raise ValueError("API o base de datos no disponibles")
    if health.get("commit") != expected_sha or ready.get("commit") != expected_sha:
        raise ValueError("El commit publicado no coincide con el validado por CI")
    return {"frontend_http": 200, "spa_http": 200, "javascript_http": 200,
            "api_http": 200, "database": "ok", "commit": expected_sha}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--vercel", action="store_true", help="Usar la CLI autenticada para URLs protegidas")
    parser.add_argument("--evidence-dir", type=Path, default=Path("deployment-evidence"))
    args = parser.parse_args()
    base = args.url.rstrip("/")
    if not re.fullmatch(r"https://[a-zA-Z0-9.-]+(?::[0-9]+)?", base):
        parser.error("Se requiere una URL HTTPS sin rutas ni credenciales")
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    report = {"url": base, "expected_commit": args.expected_sha, "result": "failure",
              "timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "run_url": os.environ.get("DEPLOY_RUN_URL", "")}
    for attempt in range(1, 7):
        try:
            report["checks"] = verify(base, args.expected_sha, args.vercel)
            report["result"] = "success"
            break
        except (URLError, OSError, ValueError, subprocess.SubprocessError) as error:
            report["error_type"] = type(error).__name__
            print(f"Intento {attempt}/6: verificación pendiente ({type(error).__name__}).", flush=True)
            if attempt < 6:
                time.sleep(5)
    if report["result"] == "success":
        report.pop("error_type", None)
    (args.evidence_dir / "vercel-deployment.json").write_text(json.dumps(report, indent=2) + "\n")
    summary = (f"## CD Vercel\n\nResultado: **{report['result']}**\n\n"
               f"Commit: `{args.expected_sha}`\n\nDespliegue: {base}\n\n"
               "Comprobaciones: frontend, navegación SPA, JavaScript, API, PostgreSQL y commit.\n")
    (args.evidence_dir / "vercel-summary.md").write_text(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as handle:
            handle.write(summary)
    return 0 if report["result"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
