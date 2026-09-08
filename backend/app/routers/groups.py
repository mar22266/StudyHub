from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.auth import current_user
from app.database import get_db
from app.models import User
from app.schemas import GroupCreate, GroupOut, GroupUpdate
from app.services import group_service

router = APIRouter(prefix="/api/groups", tags=["Grupos"])
@router.get("/search", response_model=list[GroupOut])
def search(q: str = "", db: Session = Depends(get_db), user: User = Depends(current_user)): return group_service.search_groups(db, user, q)
@router.get("", response_model=list[GroupOut])
def list_all(mine: bool = False, db: Session = Depends(get_db), user: User = Depends(current_user)): return group_service.list_groups(db, user, mine)
@router.post("", response_model=GroupOut, status_code=201)
def create(data: GroupCreate, db: Session = Depends(get_db), user: User = Depends(current_user)): return group_service.create_group(data, db, user)
@router.get("/{group_id}", response_model=GroupOut)
def detail(group_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)): return group_service.get_group(group_id, db, user)
@router.put("/{group_id}", response_model=GroupOut)
def update(group_id: int, data: GroupUpdate, db: Session = Depends(get_db), user: User = Depends(current_user)): return group_service.update_group(group_id, data, db, user)
@router.delete("/{group_id}", status_code=204)
def delete(group_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)): group_service.delete_group(group_id, db, user); return Response(status_code=204)
@router.post("/{group_id}/join", status_code=204)
def join(group_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)): group_service.join_group(group_id, db, user); return Response(status_code=204)
@router.delete("/{group_id}/leave", status_code=204)
def leave(group_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)): group_service.leave_group(group_id, db, user); return Response(status_code=204)
