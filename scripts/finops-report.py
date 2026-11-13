"""Comparar escenarios declarados con cuotas publicadas sin contratar servicios."""

import argparse
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def compute_hours(compute_units: float, active_hours_per_day: float, days: int) -> float:
    if compute_units <= 0 or not 0 <= active_hours_per_day <= 24 or not 1 <= days <= 31:
        raise ValueError("Supuestos de uso inválidos")
    return round(compute_units * active_hours_per_day * days, 4)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=ROOT/"config/finops.json")
    parser.add_argument("--database-report", type=Path)
    parser.add_argument("--out", type=Path, default=ROOT/"deployment-evidence/actualizacion/finops.json")
    args = parser.parse_args()
    policy = json.loads(args.policy.read_text())
    quota = policy["neon_published_compute_cu_hours"]
    scenarios = []
    for scenario in policy["scenarios"]:
        cu_hours = compute_hours(scenario["compute_units"], scenario["active_hours_per_day"], scenario["days"])
        scenarios.append({**scenario, "estimated_cu_hours": cu_hours,
                          "quota_ratio": round(cu_hours/quota, 4),
                          "requires_review": cu_hours >= quota*policy["review_threshold"]})
    report = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "policy": policy,
              "scenarios": scenarios, "scenarios_are_assumptions_not_measured_usage": True}
    if args.database_report:
        snapshot = json.loads(args.database_report.read_text())
        report["database_snapshot"] = {"bytes": snapshot["database_bytes"],
            "timestamp_utc": snapshot.get("timestamp_utc"),
            "note": "pg_database_size no equivale al almacenamiento facturado ni incluye todas las métricas del proveedor."}
    files = [p for p in (ROOT/"frontend/dist").rglob("*") if p.suffix in {".html", ".css", ".js"}]
    if files:
        report["frontend_build"] = {"files": len(files), "bytes": sum(p.stat().st_size for p in files),
                                     "gzip_bytes_local": sum(len(gzip.compress(p.read_bytes(), mtime=0)) for p in files),
                                     "note": "Estimación local de archivos estáticos, sin API ni encabezados HTTP."}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    print(json.dumps({"base_budget_usd": policy["monthly_base_budget"], "scenarios": scenarios}, ensure_ascii=False))


if __name__ == "__main__":
    main()
