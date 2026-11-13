import importlib.util
import json
from pathlib import Path
import subprocess
from unittest import TestCase
from unittest.mock import patch
import os

spec = importlib.util.spec_from_file_location("verification", Path(__file__).parents[1] / "verify-deployment.py")
verification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verification)


class Response:
    status = 200

    def __init__(self, body, content_type="text/html"):
        self.body = body.encode()
        self.headers = {"Content-Type": content_type}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self.body


class VercelVerificationTests(TestCase):
    def test_cli_failure_never_exposes_deployment_token(self):
        response = subprocess.CompletedProcess([], 1, stdout='', stderr='Error: rejected test-private-token')
        with patch.dict(os.environ, {"VERCEL_TOKEN": "test-private-token", "VERCEL_ORG_ID": "team_test"}):
            with patch.object(verification.subprocess, "run", return_value=response) as run:
                with self.assertRaisesRegex(ValueError, r"rejected \[oculto\]") as raised:
                    verification.vercel_response("https://studyhub.example", "/")
                self.assertNotIn("test-private-token", str(raised.exception))
                self.assertIn("--scope", run.call_args.args[0])

    def test_authenticated_cli_preserves_multiline_body_and_content_type(self):
        response = subprocess.CompletedProcess([], 0, stdout='line1\nline2\n200\ntext/javascript\n')
        with patch.object(verification.subprocess, "run", return_value=response):
            self.assertEqual(verification.vercel_response("https://studyhub.example", "/asset.js"),
                             ("line1\nline2", "text/javascript"))

    def responses(self, sha="expected", bundle_type="text/javascript"):
        page = '<div id="root"></div><script type="module" src="/assets/index-abc.js"></script>'
        return [Response(page), Response(page), Response("console.log('app')", bundle_type),
                Response(json.dumps({"status": "ok", "commit": sha}), "application/json"),
                Response(json.dumps({"status": "ok", "database": "ok", "commit": sha}), "application/json")]

    def test_requires_real_bundle_and_matching_database_revision(self):
        with patch.object(verification, "urlopen", side_effect=self.responses()):
            result = verification.verify("https://studyhub.example", "expected")
        self.assertEqual(result["database"], "ok")
        self.assertEqual(result["commit"], "expected")

    def test_rejects_previous_version_even_if_http_is_successful(self):
        with patch.object(verification, "urlopen", side_effect=self.responses(sha="old")):
            with self.assertRaisesRegex(ValueError, "commit"):
                verification.verify("https://studyhub.example", "expected")

    def test_rejects_spa_fallback_returned_instead_of_javascript(self):
        with patch.object(verification, "urlopen", side_effect=self.responses(bundle_type="text/html")):
            with self.assertRaisesRegex(ValueError, "JavaScript"):
                verification.verify("https://studyhub.example", "expected")
