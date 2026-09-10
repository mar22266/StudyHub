from datetime import date
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.auth import current_user
from app.database import get_db
from app.models import User
from app.schemas import AppointmentCreate, AppointmentOut, AppointmentUpdate
from app.services import appointment_service

router = APIRouter(prefix="/api/appointments", tags=["Sesiones"])


@router.get("", response_model=list[AppointmentOut])
def list_all(
    group_id: int | None = None,
    fecha: date | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return appointment_service.list_appointments(db, user, group_id, fecha)


@router.post("", response_model=AppointmentOut, status_code=201)
def create(
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return appointment_service.create_appointment(data, db, user)


@router.get("/{appointment_id}", response_model=AppointmentOut)
def detail(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return appointment_service.get_appointment_for_authenticated_user(
        appointment_id, db, user
    )


@router.put("/{appointment_id}", response_model=AppointmentOut)
def update(
    appointment_id: int,
    data: AppointmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    return appointment_service.update_appointment(appointment_id, data, db, user)


@router.delete("/{appointment_id}", status_code=204)
def delete(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    appointment_service.delete_appointment(appointment_id, db, user)
    return Response(status_code=204)
