import importlib.util
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

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
