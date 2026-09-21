# Decisiones del proyecto

## 2026-09-16 — Uso de OneDrive local en vez de Microsoft Graph API

**Decisión:** Leer la estructura de carpetas de estudiantes directamente desde la carpeta sincronizada de OneDrive en el sistema de archivos local, en vez de consultar Microsoft Graph API.

**Razón:** El tenant institucional bloquea el acceso de aplicaciones a los sitios de SharePoint de equipo vía Graph API. Se registró una app con autenticación delegada, pero todas las variantes de permisos probadas devolvieron 403 o requerían aprobación de un administrador.

## 2026-09-21 — El ID de estudiante no se trata como dato sensible

**Decisión:** El ID de estudiante (asignado por la universidad) se considera seguro de mostrar en salidas de terminal, logs y conversaciones de trabajo. Nombres, números de cédula y correos institucionales siguen excluidos siempre.

**Razón:** El ID de estudiante no es un dato personal identificable como la cédula o el nombre, así que no requiere el mismo nivel de protección.

## 2026-09-21 — Ampliación de variantes de nombre de archivo en el Clasificador

**Decisión:** Se amplió classifier.py con variantes de nombre de archivo encontradas al probar contra datos reales del corte 2026-18: "fotocopia" y "cc" (como palabra completa) para doc_identidad; "certific", el typo "certfic" y "carta" combinado con "laboral" o "funciones" para certificado_laboral; "aprobacion" y "aval" para carta_autorizacion.

**Razón:** Los nombres de archivo reales de los estudiantes no coincidían con los patrones originales del clasificador, lo que generaba falsos negativos al probar contra datos del corte 2026-18.

## 2026-09-21 — Tipos de documento informativos fuera de la matriz de requisitos

**Decisión:** Se agregaron tres tipos de documento informativos que el Clasificador reconoce y main.py cuenta, pero que NO forman parte de la matriz de requisitos del Evaluador (no afectan ningún estado de cumplimiento): aprobacion_emprendimiento (pantallazos de resultados de postulación a emprendimiento, se valida por Excel externo), carta_compromiso (compromiso de matricular el siguiente periodo, documento opcional) y contrato_aprendizaje (contrato de aprendizaje firmado, documento complementario).

**Razón:** Estos documentos no determinan el cumplimiento de requisitos de un estudiante: uno se valida por una fuente externa (Excel), otro es opcional y el otro es complementario.

## 2026-09-21 — main.py conecta Detector → Clasificador, aún no el Evaluador

**Decisión:** El flujo integrado en main.py conecta Detector → Clasificador, y muestra solo conteos agregados por tipo de documento, nunca nombres de archivo. Todavía no conecta el Evaluador.

**Razón:** Falta la modalidad de cada estudiante, que resolverá US03 (resolutor de modalidad), que aún está pendiente.

## 2026-09-21 — ONEDRIVE_BASE_PATH desde .env, periodo por input()

**Decisión:** main.py lee ONEDRIVE_BASE_PATH desde el archivo .env (usando python-dotenv), en vez de tenerlo hardcodeado en el código. El periodo (ej. 2026-18) se sigue pidiendo por input() en cada corrida.

**Razón:** El repo es público, así que la ruta local de OneDrive no debe quedar expuesta en el código. El periodo no es un dato sensible y cambia cada corte, así que no vale la pena moverlo a configuración.
