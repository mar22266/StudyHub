import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("deployment", Path(__file__).parents[1] / "deploy-local.py")
deployment = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deployment)


class DeploymentTests(unittest.TestCase):
    def test_redeploy_preserves_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "local.env"
            deployment.prepare_env(path, 18080)
            original = path.read_bytes()
            deployment.prepare_env(path, 18080)
            self.assertEqual(original, path.read_bytes())
            self.assertIn(b"FRONTEND_PORT=18080", original)
            self.assertNotIn(b"replace-with", original)

    def test_rejects_placeholder_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "local.env"
            path.write_text("JWT_SECRET=replace-with-a-secret")
            with self.assertRaises(ValueError):
                deployment.prepare_env(path, 8080)

    def test_supports_compose_json_formats_and_discards_extra_fields(self):
        rows = [{"Service": name, "State": "running", "Health": "healthy", "Command": "ignored"}
                for name in ("db", "backend", "frontend")]
        for raw in (json.dumps(rows), "\n".join(json.dumps(row) for row in rows)):
            result = deployment.container_status(raw)
            deployment.verify_services(result)
            self.assertNotIn("Command", result[0])

    def test_rejects_missing_or_unhealthy_services(self):
        healthy = [{"Service": name, "State": "running", "Health": "healthy"}
                   for name in ("db", "backend", "frontend")]
        with self.assertRaises(RuntimeError):
            deployment.verify_services(healthy[:2])
        healthy[0]["Health"] = "unhealthy"
        with self.assertRaises(RuntimeError):
            deployment.verify_services(healthy)


if __name__ == "__main__":
    unittest.main()
