import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()
SECRET = os.getenv("JWT_SECRET", "studyhub_local_development_secret")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
def hash_password(password: str) -> str: return pwd_context.hash(password)
def verify_password(password: str, hashed: str) -> bool: return pwd_context.verify(password, hashed)
def create_access_token(user_id: int) -> str:
    return jwt.encode({"sub": str(user_id), "exp": datetime.now(timezone.utc) + timedelta(hours=12)}, SECRET, algorithm=ALGORITHM)
def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> User:
    try: user_id = int(jwt.decode(credentials.credentials, SECRET, algorithms=[ALGORITHM])["sub"])
    except (jwt.PyJWTError, KeyError, ValueError): raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión no válida")
    user = db.get(User, user_id)
    if not user or not user.activo: raise HTTPException(status_code=401, detail="Usuario no disponible")
    return user
