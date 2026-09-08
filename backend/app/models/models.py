from datetime import date, datetime, time
from enum import Enum
from sqlalchemy import Boolean, Date, DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text, Time, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Role(str, Enum): USER = "USER"; ADMIN = "ADMIN"
class AppointmentStatus(str, Enum): PROGRAMADA = "PROGRAMADA"; FINALIZADA = "FINALIZADA"; CANCELADA = "CANCELADA"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80))
    apellido: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    rol: Mapped[Role] = mapped_column(SqlEnum(Role), default=Role.USER)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class StudyGroup(Base):
    __tablename__ = "study_groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(140), index=True)
    descripcion: Mapped[str] = mapped_column(Text, default="")
    materia: Mapped[str] = mapped_column(String(120), index=True)
    ubicacion: Mapped[str] = mapped_column(String(140))
    cupo_maximo: Mapped[int] = mapped_column(Integer, default=10)
    creador_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creador: Mapped[User] = relationship()
    members: Mapped[list["GroupMember"]] = relationship(back_populates="group", cascade="all, delete-orphan")

class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (UniqueConstraint("grupo_id", "usuario_id", name="uq_group_member"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    grupo_id: Mapped[int] = mapped_column(ForeignKey("study_groups.id", ondelete="CASCADE"))
    usuario_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    fecha_union: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    group: Mapped[StudyGroup] = relationship(back_populates="members")
    user: Mapped[User] = relationship()

class Appointment(Base):
    __tablename__ = "appointments"
    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(160))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    fecha: Mapped[date] = mapped_column(Date)
    hora_inicio: Mapped[time] = mapped_column(Time)
    hora_fin: Mapped[time] = mapped_column(Time)
    ubicacion: Mapped[str] = mapped_column(String(140))
    grupo_id: Mapped[int] = mapped_column(ForeignKey("study_groups.id"))
    creador_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    estado: Mapped[AppointmentStatus] = mapped_column(SqlEnum(AppointmentStatus), default=AppointmentStatus.PROGRAMADA)
    group: Mapped[StudyGroup] = relationship()
    creator: Mapped[User] = relationship()
