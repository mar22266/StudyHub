# StudyHub

Una plataforma web para organizar grupos de estudio y sesiones académicas.

## REQUISITOS

Docker Desktop

## INICIAR

```bash
docker compose up --build
```

Frontend: http://localhost:5173  
Backend: http://localhost:8001
Swagger: http://localhost:8001/docs

## DETENER

```bash
docker compose down
```

## REINICIAR

```bash
docker compose up
```

## RECONSTRUIR

```bash
docker compose up --build
```

## BORRAR COMPLETAMENTE LA BASE DE DATOS

```bash
docker compose down -v
```

## VER LOGS

```bash
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```
