from datetime import date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.auth import current_user
from app.database import get_db
from app.models import Appointment, GroupMember, StudyGroup, User
from app.services.appointment_service import to_out

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
@router.get("")
def dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)):
    mine_ids = set(db.scalars(select(GroupMember.grupo_id).where(GroupMember.usuario_id == user.id)).all())
    mine_count = len(mine_ids)
    today = date.today(); week_end = today + timedelta(days=7)
    sessions = db.scalars(select(Appointment).where(Appointment.fecha >= today).order_by(Appointment.fecha, Appointment.hora_inicio)).all()
    return {"my_groups": mine_count, "available_groups": db.scalar(select(func.count()).select_from(StudyGroup).where(StudyGroup.activo.is_(True))) or 0, "upcoming_sessions": len(sessions), "week_sessions": sum(today <= x.fecha <= week_end for x in sessions), "appointments": [to_out(x).model_dump(mode="json") for x in sessions[:8]]}
