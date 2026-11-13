"""Promover solo un despliegue verificado, usando la API limitada al proyecto."""

import argparse
import json
import os
from pathlib import Path
import re
import time
from urllib.error import URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen


def require_verified(report: dict, url: str, sha: str) -> None:
    if (report.get("result") != "success" or report.get("url") != url
            or report.get("expected_commit") != sha
            or report.get("checks", {}).get("commit") != sha
            or report.get("checks", {}).get("database") != "ok"):
        raise ValueError("No se puede promover sin evidencia exitosa del mismo despliegue y commit.")


def public_ready(url: str, sha: str) -> bool:
    # No enviar ni el token de API ni el bypass: comprobar acceso público real.
    with urlopen(url + "/", timeout=20) as response:
        if response.status != 200 or '<div id="root"' not in response.read().decode():
            return False
    with urlopen(url + "/api/ready", timeout=20) as response:
        data = json.load(response)
        return (response.status == 200 and data.get("commit") == sha
                and data.get("database") == "ok" and data.get("status") == "ok")


def production_urls(domains: dict) -> list[str]:
    # El despliegue puede conservar alias=[] después de una promoción exitosa.
    # La lista de dominios del proyecto es la fuente de los destinos de producción.
    return ["https://" + domain["name"] for domain in domains.get("domains", [])
            if not domain.get("gitBranch")
            and re.fullmatch(r"[a-zA-Z0-9.-]+", domain.get("name", ""))]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--evidence-dir", type=Path, default=Path("deployment-evidence"))
    args = parser.parse_args()
    report_path = args.evidence_dir / "vercel-deployment.json"
    require_verified(json.loads(report_path.read_text()), args.url, args.expected_sha)
    project = os.environ["VERCEL_PROJECT_ID"]
    team = os.environ["VERCEL_ORG_ID"]
    token = os.environ["VERCEL_TOKEN"]

    def api(path: str, method: str = "GET") -> dict:
        request = Request("https://api.vercel.com" + path + "?teamId=" + quote(team),
                          method=method, headers={"Authorization": "Bearer " + token})
        with urlopen(request, timeout=30) as response:
            raw = response.read()
            return json.loads(raw) if raw else {}

    result = {"result": "failure", "commit": args.expected_sha, "deployment_url": args.url}
    try:
        deployment = api("/v13/deployments/" + quote(urlsplit(args.url).netloc))
        if (deployment.get("projectId") != project or deployment.get("readyState") != "READY"
                or deployment.get("meta", {}).get("githubCommitSha") != args.expected_sha):
            raise ValueError("El despliegue no pertenece al proyecto o al commit verificado.")
        deployment_id = deployment["id"]
        api(f"/v10/projects/{quote(project)}/promote/{quote(deployment_id)}", "POST")
        for _ in range(60):
            domains = api(f"/v9/projects/{quote(project)}/domains")
            for url in production_urls(domains):
                try:
                    ready = public_ready(url, args.expected_sha)
                except (URLError, OSError, ValueError):
                    ready = False
                if ready:
                    result.update(result="success", production_url=url, deployment_id=deployment_id)
                    print(f"Producción verificada: {url}", flush=True)
                    if os.environ.get("GITHUB_OUTPUT"):
                        with open(os.environ["GITHUB_OUTPUT"], "a") as handle:
                            handle.write(f"url={url}\n")
                    if os.environ.get("GITHUB_STEP_SUMMARY"):
                        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as handle:
                            handle.write(f"\nPromoción exitosa. Producción pública: {url}\n")
                    return 0
            time.sleep(3)
        raise RuntimeError("El dominio público no confirmó el commit promovido dentro del plazo.")
    except (URLError, OSError, ValueError, RuntimeError) as error:
        result["error_type"] = type(error).__name__
        print(f"Promoción fallida: {type(error).__name__}: {error}", flush=True)
        return 1
    finally:
        (args.evidence_dir / "promotion.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
