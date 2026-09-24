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

## ADR-003 — Excel de resultados: archivo nuevo, no copia del real

**Fecha:** 23 de septiembre de 2026
**Contexto:** US04 pedía "escribir sobre una copia del Excel de seguimiento".

**Decisión:** en vez de copiar el .xlsx real y llenar sus columnas, el programa
genera un archivo nuevo (`resultados.xlsx`) con una fila por estudiante y sus
propias columnas de estado.

**Por qué:**
- Copiar el real exigiría leer un .xlsx con encabezados sucios (espacios
  dobles, saltos de línea) y posibles celdas combinadas — mismo problema que
  ya resolvimos para el CSV en US03/US14, pero ahora con formato de Excel.
- El resultado del programa se mezclaría con lo que ya escribieron personas
  (columna "Corregir", OBSERVACIONES), dificultando comparar automático vs.
  manual — justo lo que necesitan US07 y US08.
- Un archivo nuevo nunca toca el archivo real, lo que reduce el riesgo sobre
  datos de estudiantes a prácticamente cero.
- La misma estructura sirve para el Excel y para resultados.json (ver
  process_validation/output.py), así que no hay dos fuentes de verdad.

**Trade-off aceptado:** el resultado no tiene el formato exacto que usa hoy
el área de prácticas. Si en el futuro se necesita ese formato exacto para
entregar, se puede agregar como paso adicional que traduzca resultados.json
a las columnas del Excel real — sin tocar el motor de evaluación.

## 2026-09-23 — US05/US06 se descartan como lectura de CSV de Forms; se leen columnas ya cruzadas en la base real

**Decisión:** el programa ya no lee los CSV exportados de Forms (preinscripción,
inducción) ni resuelve duplicados por fecha. En su lugar, lee dos columnas
adicionales de la misma base de seguimiento real que ya usa
cargar_correcciones_y_extranjero() (CSV_CORRECCIONES_PATH): PREINSCRIPCIÓN
e INDUCCIÓN (ambas Sí/No).

**Razón:** Graph sigue bloqueado para Forms (ver decisión del 22 sept), así que
la alternativa siempre fue exportar CSV manualmente. Al construir US05/US06 se
volvió evidente que el cruce entre Forms y la base real (por ID de estudiante)
había que hacerlo de todos modos para poder usarlo en el área de prácticas —
y ese cruce ya se hace directamente en Excel (BUSCARV/CONTAR.SI) antes de
exportar la base real a CSV. Programar en Python el parseo de encabezados
largos de Forms y la resolución de respuestas duplicadas por rango de fechas
duplicaba un trabajo que ya se resuelve una vez, a mano, en el mismo archivo
que el programa ya lee.

**Trade-off aceptado:** se pierde la automatización de V1 y V2 como
verificaciones independientes de Forms. A cambio, se elimina una fuente de
datos completa (dos CSV menos que mantener, sin lógica de fechas ni
duplicados en el código), y V1/V2 se resuelven exactamente igual de bien
porque dependen de que la usuaria mantenga el cruce actualizado en Excel,
que es el mismo lugar donde ya corrige documentos y modalidad manualmente.

**Riesgo a vigilar:** el cruce en Excel usa BUSCARV, que trae la primera
coincidencia del rango, no la más reciente. Si un estudiante respondió Forms
dos veces, hay que ordenar los datos de Forms por fecha de finalización
(más reciente primero) antes de pegarlos en la hoja de cruce, o BUSCARV podría
traer una respuesta vieja.
