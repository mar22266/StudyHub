from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import current_user
from app.database import get_db
from app.models import GroupMember, StudyGroup, User
from app.services.appointment_service import list_appointments

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("")
def dashboard(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    mine_ids = set(
        db.scalars(
            select(GroupMember.grupo_id).where(GroupMember.usuario_id == user.id)
        ).all()
    )

    mine_count = len(mine_ids)
    today = date.today()
    week_end = today + timedelta(days=7)

    sessions = [
        appointment
        for appointment in list_appointments(
            db=db,
            user=user,
            group_id=None,
            on_date=None,
        )
        if appointment.fecha >= today
    ]

    return {
        "my_groups": mine_count,
        "available_groups": db.scalar(
            select(func.count())
            .select_from(StudyGroup)
            .where(StudyGroup.activo.is_(True))
        )
        or 0,
        "upcoming_sessions": len(sessions),
        "week_sessions": sum(
            today <= appointment.fecha <= week_end for appointment in sessions
        ),
        "appointments": [
            appointment.model_dump(mode="json") for appointment in sessions[:8]
        ],
    }
