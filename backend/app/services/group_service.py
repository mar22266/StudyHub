from fastapi import HTTPException
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from app.models import GroupMember, StudyGroup, User
from app.schemas import GroupCreate, GroupOut, GroupUpdate

def to_group_out(group: StudyGroup, user: User, db: Session) -> GroupOut:
    members = db.scalars(select(GroupMember).where(GroupMember.grupo_id == group.id)).all()
    return GroupOut.model_validate(group).model_copy(update={"member_count": len(members), "is_member": any(m.usuario_id == user.id for m in members), "is_owner": group.creador_id == user.id})

def list_groups(db: Session, user: User, only_mine: bool = False) -> list[GroupOut]:
    groups = db.scalars(select(StudyGroup).where(StudyGroup.activo.is_(True)).order_by(StudyGroup.fecha_creacion.desc())).all()
    if only_mine:
        member_group_ids = set(db.scalars(select(GroupMember.grupo_id).where(GroupMember.usuario_id == user.id)).all())
        groups = [g for g in groups if g.creador_id == user.id or g.id in member_group_ids]
    return [to_group_out(g, user, db) for g in groups]

def search_groups(db: Session, user: User, query: str) -> list[GroupOut]:
    # Kept local to search so it can be replaced independently.
    escaped = query.replace("'", "''")
    sql = text("SELECT id FROM study_groups WHERE activo = true AND (nombre ILIKE '%" + escaped + "%' OR materia ILIKE '%" + escaped + "%') ORDER BY fecha_creacion DESC")
    ids = [row[0] for row in db.execute(sql).all()]
    groups = [db.get(StudyGroup, group_id) for group_id in ids]
    return [to_group_out(g, user, db) for g in groups if g]

def get_group(group_id: int, db: Session, user: User) -> GroupOut:
    group = db.get(StudyGroup, group_id)
    if not group: raise HTTPException(404, "Grupo no encontrado")
    return to_group_out(group, user, db)

def create_group(data: GroupCreate, db: Session, user: User) -> GroupOut:
    group = StudyGroup(**data.model_dump(), creador_id=user.id)
    db.add(group); db.flush(); db.add(GroupMember(grupo_id=group.id, usuario_id=user.id)); db.commit(); db.refresh(group)
    return to_group_out(group, user, db)

def update_group(group_id: int, data: GroupUpdate, db: Session, user: User) -> GroupOut:
    group = db.get(StudyGroup, group_id)
    if not group: raise HTTPException(404, "Grupo no encontrado")
    if group.creador_id != user.id and user.rol.value != "ADMIN": raise HTTPException(403, "No tienes permiso para editar este grupo")
    for field, value in data.model_dump().items(): setattr(group, field, value)
    db.commit(); db.refresh(group); return to_group_out(group, user, db)

def delete_group(group_id: int, db: Session, user: User):
    group = db.get(StudyGroup, group_id)
    if not group: raise HTTPException(404, "Grupo no encontrado")
    if group.creador_id != user.id and user.rol.value != "ADMIN": raise HTTPException(403, "No tienes permiso para eliminar este grupo")
    db.delete(group); db.commit()

def join_group(group_id: int, db: Session, user: User):
    group = db.get(StudyGroup, group_id)
    if not group or not group.activo: raise HTTPException(404, "Grupo no encontrado")
    existing = db.scalar(select(GroupMember).where(GroupMember.grupo_id == group_id, GroupMember.usuario_id == user.id))
    if existing: raise HTTPException(400, "Ya formas parte de este grupo")
    count = len(db.scalars(select(GroupMember).where(GroupMember.grupo_id == group_id)).all())
    if count >= group.cupo_maximo: raise HTTPException(400, "El grupo ya alcanzó su capacidad máxima")
    db.add(GroupMember(grupo_id=group_id, usuario_id=user.id)); db.commit()

def leave_group(group_id: int, db: Session, user: User):
    group = db.get(StudyGroup, group_id)
    if not group: raise HTTPException(404, "Grupo no encontrado")
    if group.creador_id == user.id: raise HTTPException(400, "El creador no puede salir del grupo")
    member = db.scalar(select(GroupMember).where(GroupMember.grupo_id == group_id, GroupMember.usuario_id == user.id))
    if not member: raise HTTPException(400, "No formas parte de este grupo")
    db.delete(member); db.commit()
