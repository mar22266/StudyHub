import os
import unittest
from unittest.mock import patch
from app.main import app, lifespan


class CloudStartupTests(unittest.IsolatedAsyncioTestCase):
    async def test_cloud_liveness_startup_does_not_open_database(self):
        with patch.dict(os.environ, {"VERCEL": "1", "SEED_DEMO_DATA": "false", "INITIALIZE_DATABASE_AT_STARTUP": "false"}):
            with patch("app.main.Base.metadata.create_all") as schema, patch("app.main.SessionLocal") as session:
                async with lifespan(app):
                    pass
        schema.assert_not_called()
        session.assert_not_called()

    async def test_local_environment_keeps_explicit_bootstrap(self):
        with patch.dict(os.environ, {"VERCEL": "", "SEED_DEMO_DATA": "true", "INITIALIZE_DATABASE_AT_STARTUP": "true"}):
            with patch("app.main.Base.metadata.create_all") as schema, patch("app.main.SessionLocal") as session, patch("app.main.seed_database") as seed:
                async with lifespan(app):
                    pass
        schema.assert_called_once()
        seed.assert_called_once_with(session.return_value)
        session.return_value.close.assert_called_once()
