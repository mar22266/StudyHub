# Despliegue continuo de StudyHub

## Arquitectura y decisión

React/Vite se publica como archivos estáticos en Vercel; `index.py` exporta la API FastAPI existente. Las llamadas `/api` conservan el mismo origen. PostgreSQL persiste en Neon. Docker Compose sigue disponible como laboratorio local.

El workflow anterior requería un runner Windows y estaba desactivado. `CD Vercel` utiliza un runner Ubuntu de GitHub, sin depender de la computadora de un integrante. La existencia de este archivo no demuestra un despliegue: el cierre requiere un run exitoso y una URL funcionando.

## Flujo automático

1. Un PR ejecuta Jest, TypeScript, build, escaneo de secretos y CodeQL.
2. CI también construye y levanta un proyecto Compose temporal. Exige tres contenedores saludables y HTTP 200; publica `despliegue-temporal` y elimina solamente ese entorno temporal.
3. Después de integrar en `main`, la CI del push debe terminar correctamente. `workflow_run` filtra pushes de `main` del mismo repositorio; los PR no despliegan producción.
4. CD descarga el commit exacto de esa CI y ejecuta `vercel deploy --prod --skip-domain`.
5. `verify-deployment.py` comprueba `/`, `/login`, el bundle JavaScript, `/api/health`, `/api/ready`, PostgreSQL y el SHA publicado. Los reintentos permiten absorber el arranque inicial de los servicios.
6. Solo si las verificaciones pasan se ejecuta `vercel promote`. Si fallan, no se mueve el dominio de producción.
7. El resumen del run y el artefacto `evidencia-cd-vercel-<run_id>` guardan resultados, URL y commit sin contraseñas, tokens ni cadenas de conexión.

La concurrencia serializa despliegues a producción. El disparo manual se restringe a `main` y sirve para reintentar la activación; el camino normal es CI → CD.

## Configuración externa necesaria

Proyecto Vercel: `studyhub`, en `andys-projects-81532423` (Hobby). La raíz del proyecto es la raíz del repositorio y el framework es FastAPI. No conectar otro flujo de publicación automática que omita la validación de CI.

Configurar en Vercel, ambiente **Production**:

| Variable | Uso |
| --- | --- |
| `DATABASE_URL` | URL PostgreSQL de Neon, preferiblemente pooled y con TLS; se acepta el prefijo `postgresql://` y se utiliza psycopg 3. |
| `JWT_SECRET` | Secreto aleatorio de al menos 32 caracteres, nunca incluido en Git. |
| `SEED_DEMO_DATA=false` | Evita crear cuentas del laboratorio con contraseñas conocidas. En Vercel ese es también el valor predeterminado. |

`STUDYHUB_COMMIT_SHA` se inyecta en cada despliegue desde GitHub; los endpoints de salud permiten comprobar qué versión está funcionando. Las tablas se crean al iniciar la API, como en el laboratorio actual; antes de añadir cambios de esquema incompatibles se necesitan migraciones y respaldos.

Configurar en **GitHub Secrets** de `mar22266/StudyHub`:

| Secret | Uso |
| --- | --- |
| `VERCEL_TOKEN` | Token limitado al proyecto StudyHub. Rotarlo antes de su vencimiento; el token de esta configuración se solicitó por 90 días. |
| `VERCEL_ORG_ID` | Identificador del equipo propietario. |
| `VERCEL_PROJECT_ID` | Identificador del proyecto StudyHub. |
| `VERCEL_AUTOMATION_BYPASS_SECRET` | Solo si Deployment Protection protege la URL que comprueba el pipeline; debe configurarse desde el proyecto. |

La aceptación de términos de Neon se completa por el titular en el navegador. Elegir el plan `free_v3` sin actualizar a un plan de pago. Un plan gratuito tiene cuotas y no implica capacidad ilimitada.

## Evidencias para la entrega

- URL de PR, commits y CI aprobada.
- Run **CD Vercel** disparado automáticamente por la CI del push a `main`.
- Paso de promoción exitoso y URL de producción accesible.
- Artefacto del CD: `vercel-deployment.json` y `vercel-summary.md`.
- Capturas de nombres de variables de Vercel y GitHub Secrets, ocultando sus valores.
- Artefacto de CI `despliegue-temporal`: reporte de salud y consumo puntual de recursos.

Actualizar informe y presentación solo después de reunir esos resultados. Mientras falten la base, los secretos o un run real, el estado continúa como **pendiente de activación**, aunque el código y las pruebas del pipeline estén preparados.

## Reversión y límites

Revertir el commit mediante PR y dejar que CI → CD publique el código anterior. También se puede promover desde Vercel un despliegue anterior conocido. No borrar el volumen Docker local ni la base Neon para revertir código.

La promoción conserva el dominio anterior si falla la verificación; no revierte datos ni cambios de esquema. `/api/ready` ejecuta `SELECT 1`: verifica conexión, no reemplaza pruebas funcionales, de carga o de recuperación.

Referencias: [GitHub Actions con Vercel](https://vercel.com/kb/guide/how-can-i-use-github-actions-with-vercel), [FastAPI en Vercel](https://vercel.com/docs/frameworks/backend/fastapi), [despliegue y promoción](https://vercel.com/docs/cli/deploying-from-cli), [integraciones de almacenamiento](https://vercel.com/docs/marketplace-storage).
