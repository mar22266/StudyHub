from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.models import AppointmentStatus, Role

class EmailPayload(BaseModel):
    email: str = Field(min_length=5, max_length=255)
    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Ingresa un correo electrónico válido")
        return value

class UserCreate(EmailPayload):
    nombre: str = Field(min_length=2, max_length=80); apellido: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=128)
class LoginInput(EmailPayload): password: str
class UserOut(EmailPayload):
    model_config = ConfigDict(from_attributes=True)
    id: int; nombre: str; apellido: str; rol: Role; activo: bool; created_at: datetime
class TokenOut(BaseModel): access_token: str; token_type: str = "bearer"; user: UserOut

class GroupBase(BaseModel):
    nombre: str = Field(min_length=2, max_length=140)
    descripcion: str = ""
    materia: str = Field(min_length=2, max_length=120)
    ubicacion: str = Field(min_length=2, max_length=140)
    cupo_maximo: int = Field(ge=2, le=100)

    @field_validator("descripcion")
    @classmethod
    def validate_description(cls, value: str) -> str:
        if "<" in value or ">" in value:
            raise ValueError("La descripción no puede contener HTML")
        return value
class GroupCreate(GroupBase): pass
class GroupUpdate(GroupBase): activo: bool = True
class GroupOut(GroupBase):
    model_config = ConfigDict(from_attributes=True)
    id: int; creador_id: int; fecha_creacion: datetime; activo: bool; member_count: int = 0; is_member: bool = False; is_owner: bool = False

class AppointmentBase(BaseModel):
    titulo: str = Field(min_length=2, max_length=160); descripcion: str = ""; fecha: date; hora_inicio: time; hora_fin: time
    ubicacion: str = Field(min_length=2, max_length=140); grupo_id: int
class AppointmentCreate(AppointmentBase): pass
class AppointmentUpdate(AppointmentBase): estado: AppointmentStatus = AppointmentStatus.PROGRAMADA
class AppointmentOut(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int; creador_id: int; estado: AppointmentStatus; group_name: str = ""
