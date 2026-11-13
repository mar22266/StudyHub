"""Despliegue Docker repetible para Linux, macOS y Windows (Python 3.12+)."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent


def prepare_env(path: Path, port: int) -> None:
    """Crear secretos una sola vez; nunca imprimir ni regenerar un entorno existente."""
    if path.exists():
        content = path.read_text(encoding="utf-8-sig")
        if any(marker in content for marker in (
            "replace-with", "change-me", "studyhub_local_development_secret"
        )):
            raise ValueError("El archivo de entorno todavía contiene secretos de ejemplo.")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    password = secrets.token_hex(24)
    content = "\n".join([
        "POSTGRES_DB=studyhub",
        "POSTGRES_USER=studyhub_user",
        f"POSTGRES_PASSWORD={password}",
        f"DATABASE_URL=postgresql+psycopg://studyhub_user:{password}@db:5432/studyhub",
        f"JWT_SECRET={secrets.token_hex(32)}",
        f"FRONTEND_URL=http://localhost:{port}",
        f"FRONTEND_PORT={port}",
        "",
    ])
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(content)
    print("Se creó el archivo de entorno con secretos aleatorios (valores ocultos).", flush=True)


def container_status(raw: str) -> list[dict]:
    """Compose puede devolver un array o un objeto JSON por línea."""
    try:
        parsed = json.loads(raw)
        entries = parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        entries = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return [{key: entry.get(key, "") for key in ("Service", "State", "Health")}
            for entry in entries]


def verify_services(services: list[dict]) -> None:
    expected = {"db", "backend", "frontend"}
    if {entry["Service"] for entry in services} != expected or any(
        entry["State"] != "running" or entry["Health"] != "healthy" for entry in services
    ):
        raise RuntimeError("Los tres servicios deben estar running y healthy.")


def verify_http(port: int) -> dict:
    base = f"http://127.0.0.1:{port}"
    with urlopen(f"{base}/api/health", timeout=15) as response:
        api_status = response.status
        if api_status != 200 or json.load(response).get("status") != "ok":
            raise RuntimeError("La API no devolvió HTTP 200 y status=ok.")
    with urlopen(base + "/", timeout=15) as response:
        frontend_status = response.status
        if frontend_status != 200 or '<div id="root"' not in response.read().decode("utf-8"):
            raise RuntimeError("El frontend no devolvió HTTP 200 y la raíz de React.")
    return {"api": api_status, "frontend": frontend_status, "url": base}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--project-name", default="studyhub-local")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--evidence-dir", type=Path, default=ROOT / "deployment-evidence")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("El puerto debe estar entre 1024 y 65535.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", args.project_name):
        parser.error("Nombre de proyecto Compose inválido.")

    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "commit": os.environ.get("DEPLOY_SHA") or subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "run_url": os.environ.get("DEPLOY_RUN_URL", ""),
        "project": args.project_name,
        "result": "failure",
        "services": [],
    }
    # El puerto debe coincidir tanto en Compose como en la comprobación HTTP.
    env = {**os.environ, "FRONTEND_PORT": str(args.port)}
    compose = ["docker", "compose", "--project-name", args.project_name,
               "--env-file", str(args.env_file.resolve()), "-f", str(ROOT / "compose.deploy.yml")]

    def run(*command: str, capture: bool = False) -> str:
        result = subprocess.run(command, cwd=ROOT, env=env, check=True,
                                text=True, stdout=subprocess.PIPE if capture else None)
        return result.stdout or ""

    try:
        prepare_env(args.env_file, args.port)
        run("docker", "info", "--format", "{{.ServerVersion}}", capture=True)
        run(*compose, "config", "--quiet")
        if not args.skip_build:
            run(*compose, "build")
        run(*compose, "up", "-d", "--wait", "--wait-timeout", "180")
        report["services"] = container_status(run(*compose, "ps", "--format", "json", capture=True))
        verify_services(report["services"])
        report["http"] = verify_http(args.port)
        ids = run(*compose, "ps", "-q", capture=True).split()
        stats = run("docker", "stats", "--no-stream", "--format",
                    "{{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}", *ids, capture=True)
        (args.evidence_dir / "resources.txt").write_text(stats, encoding="utf-8")
        report["result"] = "success"
        print(f"StudyHub operativo: http://127.0.0.1:{args.port}/", flush=True)
    except (subprocess.CalledProcessError, OSError, ValueError, RuntimeError) as error:
        # No guardar respuestas, variables ni mensajes de terceros que puedan contener secretos.
        report["error_type"] = type(error).__name__
        print(f"Falló el despliegue ({type(error).__name__}). Revisar el paso anterior.", file=sys.stderr)
    finally:
        (args.evidence_dir / "deployment.json").write_text(
            json.dumps(report, indent=2) + "\n", encoding="utf-8"
        )
        summary = ["## Despliegue de StudyHub", "", f"- Resultado: {report['result']}",
                   f"- Commit: `{report['commit']}`", f"- Proyecto: `{report['project']}`",
                   "", "| Servicio | Estado | Salud |", "| --- | --- | --- |"]
        summary.extend(f"| {s['Service']} | {s['State']} | {s['Health']} |" for s in report["services"])
        if "http" in report:
            summary.extend(["", f"API: HTTP {report['http']['api']}. Frontend: HTTP {report['http']['frontend']}."])
        markdown = "\n".join(summary) + "\n"
        (args.evidence_dir / "summary.md").write_text(markdown, encoding="utf-8")
        if os.environ.get("GITHUB_STEP_SUMMARY"):
            with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
                handle.write(markdown)
    return 0 if report["result"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
