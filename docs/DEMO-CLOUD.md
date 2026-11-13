# Datos de demostración en la nube

Se reconstruyó la semilla `backend/app/seed/data.py` localmente en SQLite en
memoria y se cargó en Neon el 13 de noviembre de 2026. No se migró una base local
histórica: en esta Mac no estaban sus contenedores, volúmenes ni respaldo original.

Resultado: 3 usuarios, 5 grupos, 8 membresías y 8 sesiones. Las fechas de las
sesiones se generan respecto al día de carga. No contienen datos personales reales.

`scripts/load-demo-cloud.py` funciona por defecto en modo de consulta.
`--apply` requiere una base vacía y vuelve a comprobarla dentro de una transacción
con bloqueo. Inserta tablas en orden de dependencias, ajusta secuencias y valida
conteos antes de confirmar. Si hay datos, aborta sin sobrescribirlos.
No usarlo para fusionar otra base ni como migrador de esquemas.

La carga guardó el estado vacío previo en `.private/backup-before-demo-*.json`.
Todas las contraseñas públicas de la semilla se rotaron antes de escribir en la
nube. Las nuevas se encuentran únicamente en `.private/demo-credentials-*.json`.
No compartir esos archivos en evidencias, PDF ni commits. Los archivos tienen
permisos 0600 y `.private/` está excluido de Git. Producción mantiene
`SEED_DEMO_DATA=false`.

Para comprobar la demostración con sus credenciales locales:

```sh
python scripts/test-cloud-demo.py --credentials .private/demo-credentials-FECHA.json
```

Este operador requiere `httpx` además de las dependencias del backend. Comprueba
login/perfil de las tres cuentas, accesos denegados, búsqueda parametrizada y
creación/actualización/eliminación de un grupo y una sesión temporal. No imprime
tokens ni contraseñas; guarda solo resultados sanitizados en
`deployment-evidence/actualizacion/cloud-tests.json`. No sustituye pruebas de carga,
pruebas completas de UI ni restauración de respaldos.

En una base nueva, el esquema debe inicializarse explícitamente antes de cargar.
En Vercel, `INITIALIZE_DATABASE_AT_STARTUP` y `SEED_DEMO_DATA` son falsos por
defecto para evitar DDL y consultas de seed en cada arranque. Local conserva el
bootstrap existente. El siguiente paso es sustituirlo por migraciones versionadas.
