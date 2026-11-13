# Seguridad aplicada a StudyHub

Actualización: 13 de noviembre de 2026. No se declara ausencia total de riesgos.

## Correcciones y evidencia

La revisión inicial de Dependabot registró 40 alertas abiertas. Se actualizan
PyJWT de 2.10.1 a 2.15.1, FastAPI a 0.162.7, Starlette a 1.10.0,
Vite a 8.3.8 y source-map-js a 1.2.2. Docker y Vercel mantienen iguales
dependencias Python; CI comprueba esa igualdad. Docker y CI actualizan pip a 26.3.

Las auditorías locales posteriores de los requisitos Python y del entorno
instalado no encontraron vulnerabilidades conocidas. npm no encontró
vulnerabilidades en dependencias de producción. Los JSON reales se guardan en
`deployment-evidence/actualizacion/`, fuera de Git. CI conserva auditorías como
artefactos durante 14 días y bloquea vulnerabilidades Python, cualquier severidad
en npm de producción y severidad moderada o superior en el árbol npm completo.

## Excepción pendiente: dependencia de pruebas

[GHSA-gcqx-w48m-w2h4](https://github.com/advisories/GHSA-gcqx-w48m-w2h4)
afecta deepmerge 4.3.1, dependencia transitiva de Jest. Al revisar el aviso no
existe versión corregida. El auditor npm cuenta siete paquetes afectados por la
misma cadena; no son siete avisos diferentes. La aplicación no incluye Jest ni
deepmerge en su bundle de producción. La configuración de Jest es código revisado
del repositorio, sin entrada de usuarios de la aplicación.

Se mantiene visible el aviso bajo; no se oculta en Dependabot ni se degrada Jest
para aparentar una corrección. El responsable de seguridad del equipo (por asignar)
deberá revisar semanalmente versiones de Jest/deepmerge y actualizar al publicarse
un parche. Revaluar inmediatamente si se procesa configuración de pruebas no
confiable. Esta excepción no permite nuevos hallazgos de mayor severidad.

## Controles operativos

- JWT exige firma válida, algoritmo fijo, `exp` y `sub`; rechaza tokens vencidos,
  sin expiración, con otra clave o sujeto inválido. Cinco pruebas verifican casos.
- CodeQL analiza JavaScript/TypeScript y Python; Gitleaks revisa secretos.
- Consultas SQL parametrizadas, autorización de propietario y validación de
  entradas se conservan; las pruebas HTTP comprueban acceso denegado y búsquedas.
- GitHub Secrets contiene credenciales de despliegue y bypass de protección.
  Vercel almacena variables de producción cifradas; nunca se incluyen en PDF/Git.
- La semilla pública tiene claves conocidas: el cargador las reemplaza por claves
  aleatorias antes de escribir Neon. `SEED_DEMO_DATA=false` en producción.
- `.private/` guarda únicamente respaldos y credenciales locales; permisos de
  directorio 0700 y archivos 0600, excluidos de Git.

Limitaciones: aún faltan rate limiting de autenticación, migraciones de esquema
versionadas, simulacro de restauración y alertas operativas centralizadas. Las
pruebas no constituyen una auditoría de penetración ni certificación de seguridad.
