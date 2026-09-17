# Decisiones del proyecto

## 2026-09-16 — Uso de OneDrive local en vez de Microsoft Graph API

**Decisión:** Leer la estructura de carpetas de estudiantes directamente desde la carpeta sincronizada de OneDrive en el sistema de archivos local, en vez de consultar Microsoft Graph API.

**Razón:** El tenant institucional bloquea el acceso de aplicaciones a los sitios de SharePoint de equipo vía Graph API. Se registró una app con autenticación delegada, pero todas las variantes de permisos probadas devolvieron 403 o requerían aprobación de un administrador.
