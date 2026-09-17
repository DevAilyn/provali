# Decisiones del proyecto

## 2026-09-16 — Uso de OneDrive local en vez de Microsoft Graph API

**Decisión:** Leer la estructura de carpetas de estudiantes directamente desde la carpeta sincronizada de OneDrive en el sistema de archivos local, en vez de consultar Microsoft Graph API.

**Razón:** El tenant institucional de uniminuto.edu bloquea el acceso a Graph API, por lo que no es posible registrar una aplicación ni obtener permisos para consultar OneDrive/SharePoint por esa vía.
