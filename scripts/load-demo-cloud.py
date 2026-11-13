"""Cargar la semilla de demostración en una base vacía, sin sobrescribir datos."""

import argparse
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
import secrets
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("JWT_SECRET", secrets.token_hex(32))

from sqlalchemy import create_engine, func, select, text  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from app.database import Base  # noqa: E402
from app.models import User  # noqa: E402
from app.seed.data import seed_database  # noqa: E402
from app.auth import hash_password  # noqa: E402

TABLES = Base.metadata.sorted_tables


def counts(connection) -> dict:
    return {table.name: connection.execute(select(func.count()).select_from(table)).scalar_one()
            for table in TABLES}


def demo_snapshot() -> tuple[dict, dict]:
    """Reconstruir la semilla local en memoria y reemplazar las claves conocidas."""
    source = create_engine("sqlite://")
    Base.metadata.create_all(source)
    with Session(source) as session:
        seed_database(session)
        passwords = {}
        for user in session.scalars(select(User)).all():
            password = secrets.token_urlsafe(24)
            user.password = hash_password(password)
            passwords[user.email] = password
        session.commit()
    with source.connect() as connection:
        snapshot = {table.name: [dict(row) for row in connection.execute(select(table)).mappings()]
                    for table in TABLES}
    source.dispose()
    return snapshot, passwords


def restore_into_empty(connection, snapshot: dict) -> dict:
    """El llamador mantiene una transacción. Una base con datos siempre se rechaza."""
    if connection.dialect.name == "postgresql":
        connection.execute(text("LOCK TABLE users, study_groups, group_members, appointments IN SHARE ROW EXCLUSIVE MODE"))
    before = counts(connection)
    if any(before.values()):
        raise ValueError("La base ya contiene datos. No se sobrescribirá ningún registro.")
    for table in TABLES:
        if snapshot[table.name]:
            connection.execute(table.insert(), snapshot[table.name])
    if connection.dialect.name == "postgresql":
        for table in TABLES:
            connection.execute(text(
                f"SELECT setval(pg_get_serial_sequence('{table.name}', 'id'), "
                f"(SELECT COALESCE(MAX(id), 1) FROM {table.name}), true)"
            ))
    after = counts(connection)
    if after != {name: len(rows) for name, rows in snapshot.items()}:
        raise ValueError("Los conteos no coinciden; se debe revertir la transacción.")
    return {"before": before, "after": after}


def cloud_engine(project_file: Path):
    project = json.loads(project_file.read_text())
    auth_file = Path.home() / "Library/Application Support/com.vercel.cli/auth.json"
    auth = json.loads(auth_file.read_text())

    def api(path: str) -> dict:
        request = Request("https://api.vercel.com" + path + "?teamId=" + project["orgId"],
                          headers={"Authorization": "Bearer " + auth["token"]})
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    variables = api(f"/v9/projects/{project['projectId']}/env")["envs"]
    variable = next(item for item in variables if item["key"] == "DATABASE_URL_UNPOOLED"
                    and "production" in item.get("target", []))
    value = api(f"/v1/projects/{project['projectId']}/env/{variable['id']}")["value"]
    url = make_url(value).set(drivername="postgresql+psycopg")
    return create_engine(url, pool_pre_ping=True)


def private_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w") as handle:
        json.dump(value, handle, indent=2, default=str, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--project-file", type=Path, default=ROOT / ".vercel/project.json")
    parser.add_argument("--private-dir", type=Path, default=ROOT / ".private")
    parser.add_argument("--report", type=Path, default=ROOT / "deployment-evidence/actualizacion/demo-load.json")
    args = parser.parse_args()
    engine = cloud_engine(args.project_file)
    with engine.connect() as connection:
        before = counts(connection)
    if not args.apply:
        print(json.dumps({"mode": "read-only", "counts": before}))
        return 0
    if any(before.values()):
        raise SystemExit("La base ya contiene datos; la carga se canceló sin modificarla.")
    snapshot, passwords = demo_snapshot()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = args.private_dir / f"backup-before-demo-{stamp}.json"
    private_json(backup, {"source": "Neon StudyHub before demo load", "counts": before,
                          "tables": {name: [] for name in before}})
    credentials_file = args.private_dir / f"demo-credentials-{stamp}.json"
    private_json(credentials_file, {"url": "https://studyhub-alpha-olive.vercel.app",
                                    "accounts": passwords})
    try:
        with engine.begin() as connection:
            result = restore_into_empty(connection, snapshot)
        with engine.connect() as connection:
            size = connection.execute(text("SELECT pg_database_size(current_database())")).scalar_one()
        report = {"result": "success", "operation": "project demo seed reconstructed locally and loaded into Neon",
                  "timestamp_utc": datetime.now(timezone.utc).isoformat(), **result,
                  "database_bytes": size, "backup": backup.name,
                  "credentials_file": str(credentials_file.relative_to(ROOT)),
                  "known_demo_passwords_replaced": True}
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps({"result": "success", **result, "credentials_file": str(credentials_file.relative_to(ROOT))}))
        return 0
    except Exception:
        credentials_file.unlink(missing_ok=True)
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
