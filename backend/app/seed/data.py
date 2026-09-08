from datetime import date, time, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth import hash_password
from app.models import Appointment, GroupMember, Role, StudyGroup, User

def seed_database(db: Session):
    if db.scalar(select(User.id).limit(1)): return
    admin = User(nombre="Administrador", apellido="StudyHub", email="admin@studyhub.local", password=hash_password("Admin123!"), rol=Role.ADMIN)
    ana = User(nombre="Ana", apellido="Martínez", email="ana@studyhub.local", password=hash_password("Ana123!"))
    carlos = User(nombre="Carlos", apellido="López", email="carlos@studyhub.local", password=hash_password("Carlos123!"))
    db.add_all([admin, ana, carlos]); db.flush()
    data = [("Programación Web", "Práctica colaborativa de interfaces y APIs.", "Desarrollo Web", "Sala A-101", 12, ana), ("Bases de Datos", "Modelado, consultas y diseño de datos.", "Bases de Datos", "Biblioteca", 10, carlos), ("Cálculo II", "Resolución guiada de ejercicios semanales.", "Matemáticas", "Sala B-204", 15, ana), ("Redes", "Repaso de protocolos y arquitectura de red.", "Redes", "Laboratorio 3", 10, carlos), ("Algoritmos", "Estrategias para resolver problemas.", "Ciencias de la Computación", "Sala C-120", 12, ana)]
    groups = []
    for name, desc, subject, location, capacity, creator in data:
        group = StudyGroup(nombre=name, descripcion=desc, materia=subject, ubicacion=location, cupo_maximo=capacity, creador_id=creator.id); db.add(group); db.flush(); db.add(GroupMember(grupo_id=group.id, usuario_id=creator.id)); groups.append(group)
    db.add_all([GroupMember(grupo_id=groups[0].id, usuario_id=carlos.id), GroupMember(grupo_id=groups[1].id, usuario_id=ana.id), GroupMember(grupo_id=groups[2].id, usuario_id=carlos.id)])
    today = date.today()
    for index in range(8):
        group = groups[index % len(groups)]
        db.add(Appointment(titulo=f"Sesión de {group.nombre}", descripcion="Espacio de trabajo y repaso en equipo.", fecha=today + timedelta(days=index + 1), hora_inicio=time(15 + index % 3, 0), hora_fin=time(16 + index % 3, 30), ubicacion=group.ubicacion, grupo_id=group.id, creador_id=group.creador_id))
    db.commit()
