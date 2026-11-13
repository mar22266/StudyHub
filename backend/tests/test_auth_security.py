import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

os.environ.setdefault("JWT_SECRET", "studyhub-test-key-for-unit-tests-only-32")

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from app.auth.auth import ALGORITHM, SECRET, create_access_token, current_user


class AuthSecurityTests(unittest.TestCase):
    def token(self, payload):
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=jwt.encode(payload, SECRET, algorithm=ALGORITHM))

    def test_valid_signed_token_resolves_active_user(self):
        db = Mock()
        db.get.return_value.activo = True
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=create_access_token(7))
        self.assertIs(current_user(credentials, db), db.get.return_value)

    def test_expired_token_is_rejected_without_querying_database(self):
        db = Mock()
        with self.assertRaises(HTTPException) as error:
            current_user(self.token({"sub": "7", "exp": datetime.now(timezone.utc)-timedelta(seconds=1)}), db)
        self.assertEqual(error.exception.status_code, 401)
        db.get.assert_not_called()

    def test_unsigned_or_invalid_subject_tokens_are_rejected(self):
        db = Mock()
        tokens = [self.token({"sub": None}), self.token({"sub": "invalid"}),
                  HTTPAuthorizationCredentials(scheme="Bearer", credentials=jwt.encode({"sub": "7"}, key="", algorithm="none"))]
        for token in tokens:
            with self.assertRaises(HTTPException) as error:
                current_user(token, db)
            self.assertEqual(error.exception.status_code, 401)
        db.get.assert_not_called()

    def test_token_signed_with_another_key_is_rejected(self):
        db = Mock()
        token = jwt.encode({"sub": "7"}, "another-unit-test-secret-with-32-characters", algorithm=ALGORITHM)
        with self.assertRaises(HTTPException) as error:
            current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), db)
        self.assertEqual(error.exception.status_code, 401)
        db.get.assert_not_called()

    def test_token_without_expiration_is_rejected(self):
        db = Mock()
        with self.assertRaises(HTTPException) as error:
            current_user(self.token({"sub": "7"}), db)
        self.assertEqual(error.exception.status_code, 401)
        db.get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
