# StudyHub

Aplicación para organizar grupos de estudio y sesiones académicas. React y Vite forman el frontend; FastAPI y PostgreSQL forman la API. El repositorio también sirve como laboratorio OWASP.

## REQUISITOS

Docker Desktop y PowerShell 7 para el despliegue local automatizado.

## INICIAR

```powershell
./scripts/deploy-local.ps1
```

La aplicación desplegada queda en http://127.0.0.1:8080/. Para desarrollo con recarga en vivo, usar `docker compose up --build` después de crear `.env`; el frontend estará en 5173 y la API en 8001.

## DETENER

```bash
docker compose -f compose.deploy.yml down
```

## REINICIAR

```bash
./scripts/deploy-local.ps1 -SkipBuild
```

## RECONSTRUIR

```bash
./scripts/deploy-local.ps1
```

## BORRAR COMPLETAMENTE LA BASE DE DATOS

```bash
docker compose -f compose.deploy.yml down -v
```

## VER LOGS

```bash
docker compose -f compose.deploy.yml logs -f
docker compose -f compose.deploy.yml logs -f backend
docker compose -f compose.deploy.yml logs -f frontend
docker compose -f compose.deploy.yml logs -f db
```

## CI, CD Y SEGURIDAD

En `frontend`, ejecutar `npm ci`, `npm run test:coverage` y `npm run build`. GitHub Actions ejecuta esas comprobaciones, valida Python y Docker, busca secretos y analiza TypeScript y Python con CodeQL.

`scripts/deploy-local.ps1` crea `.env` con secretos aleatorios si no existe, construye los contenedores, espera su estado saludable y verifica la API y el frontend. El workflow `CD local` puede ejecutarlo automáticamente después de CI en un runner propio con etiquetas `self-hosted`, `Windows`, `studyhub` cuando `ENABLE_LOCAL_CD=true`. No se publica la aplicación en una nube.

`.env.example` enumera los parámetros, mientras `.env` contiene los valores reales ignorados por Git. El grafo de dependencias y las alertas de Dependabot están activos. Las actualizaciones automáticas de versiones y los PR automáticos de seguridad están desactivados para mantener una sola rama remota estable; las alertas se revisan manualmente. Las normas de ramas y pull requests están en [CONTRIBUTING.md](CONTRIBUTING.md).
