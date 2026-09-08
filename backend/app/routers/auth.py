from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth import create_access_token, current_user, hash_password, verify_password
from app.database import get_db
from app.models import User
from app.schemas import LoginInput, TokenOut, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])
@router.post("/register", response_model=TokenOut, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == data.email.lower())): raise HTTPException(409, "El correo ya está registrado")
    user = User(nombre=data.nombre, apellido=data.apellido, email=data.email.lower(), password=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    return TokenOut(access_token=create_access_token(user.id), user=user)
@router.post("/login", response_model=TokenOut)
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not user.activo or not verify_password(data.password, user.password): raise HTTPException(401, "Correo o contraseña incorrectos")
    return TokenOut(access_token=create_access_token(user.id), user=user)
@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)): return user
