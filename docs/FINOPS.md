# FinOps de StudyHub

Revisión: 13 de noviembre de 2026.

## Presupuesto y alcance

Se usa Vercel Hobby con Neon Free para una demostración académica. La base
mensual presupuestada es USD 0 si se cumplen las condiciones y cuotas gratuitas.
No se revisó una factura; no se incluyen trabajo humano, conexión ni equipo.
No es una garantía de gasto futuro ni de capacidad para producción comercial.
Vercel Hobby limita el uso a proyectos personales no comerciales.

Neon publica 100 CU-h por proyecto al mes y 1 GB de almacenamiento por proyecto
en Free. Vercel publica para Hobby límites como 4 horas de CPU activa y un millón
de invocaciones de funciones; otras cuotas también aplican. Exceder límites de
Hobby puede pausar el servicio hasta el restablecimiento de la cuota. No se
activaron alertas personalizadas de gasto exclusivas de planes pagos.

Fuentes oficiales consultadas en esa fecha:
[Neon Pricing](https://neon.com/pricing),
[Vercel Hobby](https://vercel.com/docs/plans/hobby) y
[Vercel Plans](https://vercel.com/docs/plans).

## Optimización y automatización implementadas

- En Vercel, el arranque ya no ejecuta `create_all` ni abre una sesión de seed.
  `/api/health` permite comprobar vida sin consultar PostgreSQL. `/api/ready`
  verifica realmente la base cuando se valida un despliegue. Esto evita trabajo
  y accesos innecesarios; no se atribuye un ahorro monetario sin medición.
- `SEED_DEMO_DATA=false` evita volver a cargar datos en cada arranque.
- `config/finops.json` versiona planes, presupuesto, cuotas, fuentes y umbral 80%.
- `scripts/finops-report.py` genera escenarios y tamaño local del build; puede
  incorporar la medición de `pg_database_size` del reporte de carga demo.
- Docker local conserva límites de recursos; Vercel/Neon usan su infraestructura
  administrada. Los límites Docker no se presentan como límites de Vercel.

Ejecutar: `python scripts/finops-report.py --database-report deployment-evidence/actualizacion/demo-load.json`.

## Evaluación y decisiones

| Escenario supuesto | Cálculo | CU-h/mes | Frente a 100 CU-h |
|---|---|---:|---:|
| Académico | 0.25 CU x 2 h x 22 días | 11 | 11% |
| Continuo | 0.25 CU x 24 h x 30 días | 180 | 180%, requiere revisión |

Son supuestos, no consumo observado en la cuenta ni predicción de factura.
El script marca revisión desde 80 CU-h; no cambia planes ni bloquea la cuenta.
El tamaño medido tras cargar datos fue 8,093,696 bytes (aprox. 7.72 MiB).
`pg_database_size` no equivale a almacenamiento facturado, historial o WAL.
El gzip local del build tampoco equivale a transferencia mensual real.

El responsable FinOps propuesto revisará semanalmente los paneles de uso y avisos
de cuota de ambos proveedores. Al llegar al 80%, debe investigar invocaciones,
consultas repetidas y recursos ociosos antes de solicitar un cambio de plan.
No hacer sondeos continuos de `/api/ready` que mantengan activa la base.
Las cuotas del proveedor y el consumo real deben verificarse antes de cada entrega.

Mejoras pendientes: capturar métricas reales CU-h/CPU/transferencia, establecer
costo por usuario activo y ejecutar prueba de carga con límite de tráfico. La
comparación sustituye estimaciones antiguas de DigitalOcean que no corresponden
al despliegue actual.
