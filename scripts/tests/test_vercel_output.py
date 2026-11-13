import importlib.util
from pathlib import Path
from unittest import TestCase

spec = importlib.util.spec_from_file_location("vercel_output", Path(__file__).parents[1] / "vercel-output.py")
output = importlib.util.module_from_spec(spec)
spec.loader.exec_module(output)


class VercelOutputTests(TestCase):
    def test_accepts_json_and_legacy_url_formats(self):
        for raw in ('{"status":"ok","deployment":{"url":"https://studyhub.vercel.app"}}',
                    'https://studyhub.vercel.app\n'):
            self.assertEqual(output.deployment_url(raw), "https://studyhub.vercel.app")

    def test_rejects_empty_response_and_untrusted_destinations(self):
        for raw in ("", "Build failed", "http://studyhub.vercel.app", "https://user:password@example.com",
                    '{"deployment":{"url":"https://example.com/path"}}'):
            with self.assertRaises(ValueError):
                output.deployment_url(raw)
