from datetime import date
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Appointment, GroupMember, StudyGroup, User
from app.schemas import AppointmentCreate, AppointmentOut, AppointmentUpdate
from sqlalchemy import or_, select


def to_out(item: Appointment) -> AppointmentOut:
    return AppointmentOut.model_validate(item).model_copy(
        update={"group_name": item.group.nombre}
    )


def can_manage_group(group_id: int, user: User, db: Session) -> bool:
    group = db.get(StudyGroup, group_id)
    return bool(group and (group.creador_id == user.id or user.rol.value == "ADMIN"))


def can_access_group(group_id: int, user: User, db: Session) -> bool:
    if user.rol.value == "ADMIN":
        return True

    group = db.get(StudyGroup, group_id)

    if not group:
        return False

    if group.creador_id == user.id:
        return True

    membership = db.scalar(
        select(GroupMember.id).where(
            GroupMember.grupo_id == group_id,
            GroupMember.usuario_id == user.id,
        )
    )

    return membership is not None


def list_appointments(
    db: Session, user: User, group_id: int | None, on_date: date | None
) -> list[AppointmentOut]:
    statement = select(Appointment).order_by(
        Appointment.fecha,
        Appointment.hora_inicio,
    )

    if user.rol.value != "ADMIN":
        allowed_group_ids = (
            select(StudyGroup.id)
            .outerjoin(GroupMember, GroupMember.grupo_id == StudyGroup.id)
            .where(
                or_(
                    StudyGroup.creador_id == user.id,
                    GroupMember.usuario_id == user.id,
                )
            )
        )
        statement = statement.where(Appointment.grupo_id.in_(allowed_group_ids))

    if group_id:
        statement = statement.where(Appointment.grupo_id == group_id)

    if on_date:
        statement = statement.where(Appointment.fecha == on_date)

    return [to_out(item) for item in db.scalars(statement).all()]


def get_appointment_for_authenticated_user(
    appointment_id: int, db: Session, user: User
) -> AppointmentOut:
    item = db.get(Appointment, appointment_id)

    if not item:
        raise HTTPException(404, "Sesión no encontrada")

    if not can_access_group(item.grupo_id, user, db):
        raise HTTPException(
            status_code=403,
            detail="No tienes permiso para consultar esta sesión",
        )

    return to_out(item)


def create_appointment(
    data: AppointmentCreate, db: Session, user: User
) -> AppointmentOut:
    if data.hora_fin <= data.hora_inicio:
        raise HTTPException(400, "La hora de finalización debe ser posterior")
    if not can_manage_group(data.grupo_id, user, db):
        raise HTTPException(403, "Solo el creador del grupo puede crear sesiones")
    item = Appointment(**data.model_dump(), creador_id=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_out(item)


def update_appointment(
    appointment_id: int, data: AppointmentUpdate, db: Session, user: User
) -> AppointmentOut:
    item = db.get(Appointment, appointment_id)
    if not item:
        raise HTTPException(404, "Sesión no encontrada")
    if item.creador_id != user.id and user.rol.value != "ADMIN":
        raise HTTPException(403, "No tienes permiso para editar esta sesión")
    if data.hora_fin <= data.hora_inicio:
        raise HTTPException(400, "La hora de finalización debe ser posterior")
    for field, value in data.model_dump().items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return to_out(item)


def delete_appointment(appointment_id: int, db: Session, user: User):
    item = db.get(Appointment, appointment_id)
    if not item:
        raise HTTPException(404, "Sesión no encontrada")
    if item.creador_id != user.id and user.rol.value != "ADMIN":
        raise HTTPException(403, "No tienes permiso para eliminar esta sesión")
    db.delete(item)
    db.commit()
