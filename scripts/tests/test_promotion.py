import importlib.util
from pathlib import Path
from unittest import TestCase

spec = importlib.util.spec_from_file_location("promotion", Path(__file__).parents[1] / "promote-vercel.py")
promotion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(promotion)


class PromotionTests(TestCase):
    def test_uses_production_domains_even_when_deployment_alias_is_empty(self):
        domains = {"alias": [], "domains": [
            {"name": "studyhub.vercel.app", "gitBranch": None},
            {"name": "preview.vercel.app", "gitBranch": "feature"},
            {"name": "invalid.example/path", "gitBranch": None},
        ]}
        self.assertEqual(promotion.production_urls(domains), ["https://studyhub.vercel.app"])

    def report(self):
        return {"result": "success", "url": "https://studyhub.example", "expected_commit": "current",
                "checks": {"commit": "current", "database": "ok"}}

    def test_accepts_successful_verification_of_exact_deployment(self):
        promotion.require_verified(self.report(), "https://studyhub.example", "current")

    def test_refuses_failure_stale_commit_wrong_url_or_unready_database(self):
        for field, value in (("result", "failure"), ("expected_commit", "old"),
                             ("url", "https://other.example"), ("checks", {"commit": "current"})):
            report = self.report()
            report[field] = value
            with self.assertRaises(ValueError):
                promotion.require_verified(report, "https://studyhub.example", "current")
