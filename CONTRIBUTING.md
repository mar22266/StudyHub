# Colaboración en StudyHub

1. Crear una rama corta desde `main`: `feat/`, `fix/`, `docs/` o `chore/`.
2. Hacer commits pequeños con el formato `tipo: cambio concreto`.
3. Abrir un pull request hacia `main` y completar la plantilla.
4. Esperar a que CI y CodeQL terminen. Solicitar revisión de otra persona del equipo.
5. Integrar con squash para mantener un historial legible. No forzar pushes a `main`.
6. Si hay un incidente, revertir el commit o desplegar el commit anterior con el script local.

Las variables secretas permanecen en `.env` local, que Git ignora. El archivo `.env.example` documenta las claves sin contener credenciales de uso real.
