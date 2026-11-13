import importlib.util
from pathlib import Path
import unittest
from sqlalchemy import create_engine
from app.database import Base

spec = importlib.util.spec_from_file_location("demo_loader", Path(__file__).parents[2]/"scripts/load-demo-cloud.py")
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)


class DemoLoadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot, cls.passwords = loader.demo_snapshot()

    def setUp(self):
        self.target = create_engine("sqlite://")
        Base.metadata.create_all(self.target)

    def tearDown(self):
        self.target.dispose()

    def test_restores_all_related_demo_records(self):
        with self.target.begin() as connection:
            report = loader.restore_into_empty(connection, self.snapshot)
        self.assertEqual(report["after"], {"users": 3, "study_groups": 5, "group_members": 8, "appointments": 8})
        self.assertTrue(all(password not in {"Admin123!", "Ana123!", "Carlos123!"} for password in self.passwords.values()))

    def test_second_load_refuses_to_duplicate_or_overwrite(self):
        with self.target.begin() as connection:
            loader.restore_into_empty(connection, self.snapshot)
        with self.assertRaises(ValueError):
            with self.target.begin() as connection:
                loader.restore_into_empty(connection, self.snapshot)
        with self.target.connect() as connection:
            self.assertEqual(loader.counts(connection), {"users": 3, "study_groups": 5, "group_members": 8, "appointments": 8})
