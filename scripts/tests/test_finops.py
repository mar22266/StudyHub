import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("finops", Path(__file__).parents[1]/"finops-report.py")
finops = importlib.util.module_from_spec(spec)
spec.loader.exec_module(finops)


class FinOpsTests(unittest.TestCase):
    def test_academic_and_continuous_compute_scenarios(self):
        self.assertEqual(finops.compute_hours(0.25, 2, 22), 11)
        self.assertEqual(finops.compute_hours(0.25, 24, 30), 180)

    def test_rejects_impossible_or_negative_usage(self):
        for values in [(0.25, 25, 30), (-1, 2, 22), (0.25, 2, 0)]:
            with self.assertRaises(ValueError):
                finops.compute_hours(*values)
