# StudyHub: plan estratégico ITIL + DevOps

**Fecha:** 3 de noviembre de 2026

**Proyecto:** [mar22266/StudyHub](https://github.com/mar22266/StudyHub)
**Alcance:** automatizar calidad, seguridad y despliegue local. Por decisión del equipo, la aplicación no se publica en la nube.

## 1. Servicio y criterio de diseño

StudyHub permite registrar usuarios, crear y buscar grupos de estudio, unirse a ellos, programar sesiones y consultar un panel. React/Vite consume una API FastAPI; PostgreSQL guarda usuarios, grupos y sesiones. Docker Compose agrupa los tres servicios. Es un laboratorio OWASP: las prácticas de seguridad son parte del aprendizaje y deben tener evidencia verificable.

El plan adopta **habilitación de cambios** de ITIL mediante ramas, pull requests y revisiones; **gestión de despliegues** mediante un script reproducible; **gestión de configuración** mediante `.env` y variables de GitHub Actions; **seguridad de la información** mediante escaneos y correcciones; **monitoreo y gestión de incidentes** mediante health checks y una ruta de reversión; y **mejora continua** mediante métricas y revisión periódica. DevOps convierte esas decisiones en comprobaciones automáticas para cada cambio.

## 2. Soluciones aplicadas y evidencia

| Componente | Decisión y aplicación | Evidencia verificable |
|---|---|---|
| 1. CI | GitHub Actions corre en cada PR y push a `main`: `npm ci`, seis pruebas Jest, cobertura, TypeScript, Vite, compilación Python, dos imágenes Docker, auditoría npm y Gitleaks. CodeQL analiza TypeScript y Python en un flujo separado. | [ci.yml](../.github/workflows/ci.yml), [codeql.yml](../.github/workflows/codeql.yml), [PR #4](https://github.com/mar22266/StudyHub/pull/4) |
| 2. CD | `deploy-local.ps1` genera secretos locales si faltan, valida Compose, construye imágenes, espera tres health checks y prueba HTTP. `cd-local.yml` conecta CI con un runner Windows propio cuando se habilite. | [script](../scripts/deploy-local.ps1), [Compose](../compose.deploy.yml); ejecución local exitosa: frontend y API HTTP 200, tres contenedores saludables |
| 3. Jest | Tres casos de horario y tres de mensajes de error prueban funciones utilizadas por formularios y llamadas a la API. TypeScript 5.9.3 queda fijado para evitar el fallo observado con 7.0.2. | [tests](../frontend/tests/); 6/6 aprobadas, cobertura de las dos utilidades probadas: 100 % en líneas, ramas y funciones |
| 4. Configuración | `.env.example` documenta claves; `.env` se ignora en Git y el script crea valores aleatorios. GitHub Actions usa variables de repositorio `CI_NODE_VERSION=22`, `CI_PYTHON_VERSION=3.12` y `ENABLE_LOCAL_CD=false`. Los secretos de la aplicación permanecen en la máquina local. | [.env.example](../.env.example), [.gitignore](../.gitignore), configuración de [Actions variables](https://github.com/mar22266/StudyHub/settings/variables/actions) |
| 5. Git | Rama `codex/itil-devops`, commit `9aca2df` con identidad de André Marroquin y PR #4 hacia `main`. La plantilla pide pruebas, revisión de seguridad y plan de reversión. | [CONTRIBUTING.md](../CONTRIBUTING.md), [plantilla PR](../.github/PULL_REQUEST_TEMPLATE.md), [historial del PR](https://github.com/mar22266/StudyHub/pull/4/commits) |
| 6. DevSecOps | Consulta SQL parametrizada; API sin dependencia Axios vulnerable; auditoría npm de producción sin vulnerabilidades altas; JWT obligatorio de 32+ caracteres; API con usuario no privilegiado; Nginx añade CSP y otras cabeceras; la app solo escucha en loopback. Dependabot propone actualizaciones semanales. | [group_service.py](../backend/app/services/group_service.py), [api.ts](../frontend/src/services/api.ts), [Dockerfile](../backend/Dockerfile), [nginx.conf](../frontend/nginx.conf), [Dependabot](../.github/dependabot.yml) |
| 7. FinOps | El entorno local evita un cargo de hosting. Compose limita memoria a 384 MiB para DB, 256 MiB para API y 128 MiB para frontend. La imagen frontend multietapa no incluye Node ni dependencias de desarrollo en ejecución; caché de npm y Docker acorta reconstrucciones. | [Compose](../compose.deploy.yml), [Dockerfile multietapa](../frontend/Dockerfile.deploy); medición local: 62.33 + 77.62 + 23.04 = **162.99 MiB** usados frente a un límite conjunto de 768 MiB |

### Evidencia de ejecución local

El 3 de noviembre de 2026 se ejecutó `./scripts/deploy-local.ps1`. Docker marcó **healthy** a `db`, `backend` y `frontend`; `GET /api/health` respondió `200 {"status":"ok"}` y la página inicial respondió 200 con una cabecera CSP. Un usuario de ejemplo inició sesión y el dashboard mostró grupos y sesiones. La búsqueda de “Programación” devolvió un grupo; una cadena `' OR 1=1 --` devolvió cero resultados después de parametrizar SQL. `npm run build` terminó correctamente y `npm audit --omit=dev --audit-level=high` reportó **0 vulnerabilidades**. El PR #4 pasó sus seis checks; sigue pendiente la revisión exigida para integrarlo a `main`.

La cobertura de 100 % corresponde **solo a las dos utilidades incluidas en Jest**, no a toda la interfaz o la API. La auditoría completa de npm todavía muestra avisos en dependencias de desarrollo; Dependabot y CodeQL ayudan a revisarlos. El workflow de CD automático está preparado pero no se habilita hasta conectar un runner propio. El despliegue local sí se ejecutó y verificó. No hay despliegue público ni servicio de nube.

## 3. Gestión operativa ITIL

| Práctica | Responsable y decisión | Señal de control |
|---|---|---|
| Habilitación de cambios | Un integrante propone el PR; otro revisa permisos, datos y resultado de CI antes de integrar. | PR, revisión y checks visibles. |
| Despliegue y configuración | El script despliega exactamente el commit revisado y mantiene secretos fuera de Git. | Commit, `.env` ignorado, health checks. |
| Incidentes | Si falla un check, se detiene la integración; si falla el entorno local, se inspeccionan `docker compose logs` y se vuelve al commit anterior. | Estado de Actions, logs, `GET /api/health`. |
| Mejora continua | Cada semana se revisan PRs de Dependabot, hallazgos CodeQL y tiempos de CI. | Registro de hallazgos y tendencia de fallos. |

**Indicadores propuestos:** al menos 95 % de ejecuciones CI exitosas tras revisión, cero secretos nuevos en Git, cero vulnerabilidades altas en dependencias de producción y recuperación local en menos de 15 minutos. Son metas de operación, no resultados medidos todavía.

## 4. FinOps y evolución

El gasto monetario de infraestructura pública para esta entrega es **cero** porque no hay hosting. Esto no significa costo total cero: Docker consume memoria, CPU, energía y tiempo del equipo. Para comparar alternativas futuras se propone medir **costo mensual = horas de ejecución × tarifa del recurso + almacenamiento + transferencia + tiempo de mantenimiento**. Antes de contratar un proveedor, el equipo debe registrar uso real, presupuesto y alertas, y apagar entornos de prueba fuera del horario de trabajo. Para este laboratorio, conviene mantener el despliegue en loopback y usar caché de builds.

El siguiente incremento sería agregar métricas de latencia, tasa de errores y uso de DB, más alertas cuando `/api/health` falle. También conviene ampliar las pruebas a autorización y flujos API, automatizar restauraciones de respaldo y usar DevSecMonOps para correlacionar hallazgos de CodeQL, dependencias, logs y métricas. Si el equipo desea CD tras cada merge sin nube, debe instalar un runner propio con acceso a Docker y cambiar `ENABLE_LOCAL_CD` a `true` después de probar la seguridad del equipo anfitrión.

## 5. Análisis y reflexión

**1. Ventajas obtenidas.** Cada PR recibe la misma validación técnica; las seis pruebas detectan errores de horario y mensajes antes de integrar. El script reduce pasos manuales y confirma que la aplicación realmente arranca. Eliminar Axios quitó avisos altos de dependencias de producción y la consulta parametrizada evita que la búsqueda interprete datos como SQL. Los límites de memoria hacen visible el presupuesto de recursos.

**2. Retos principales.** El proyecto usaba versiones `latest`: TypeScript 7.0.2 falló internamente y hubo que fijar 5.9.3 y simplificar el typecheck. El cambio de Axios a `fetch` exigió conservar la forma de respuestas y errores; se verificó con Jest, build y un inicio de sesión real. Docker necesitó secretos, health checks y un frontend estático para que CD no fuera solo un comando de compilación. La ausencia de un runner propio impide activar el disparo automático local desde GitHub sin contradecir la decisión de no desplegar en nube.

**3. Mejoras siguientes.** Ampliar cobertura a permisos, flujos de registro, creación de grupos y fallos de DB; resolver avisos de desarrollo al actualizar dependencias; agregar métricas, alertas y una prueba periódica de recuperación; registrar duración de CI, consumo de recursos y gasto si alguna vez se contrata hosting. La prioridad es conectar un runner local aislado y ejecutar un despliegue automático controlado tras CI exitosa.

## 6. Guion de presentación (máximo 20 minutos)

Distribuir los bloques entre todos los integrantes antes de exponer: contexto e ITIL (3 min), CI/Jest/Git (5 min), CD/configuración/seguridad (6 min), FinOps/reflexión y demostración (5 min), preguntas (1 min). Los nombres y tiempos por persona se acuerdan en el grupo; el material no atribuye trabajo no confirmado.
