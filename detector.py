"""
Detector: lee la estructura de carpetas de estudiantes desde OneDrive local.
Retorna una lista de dicts {id_estudiante, archivos}.
"""

import os
import unicodedata

CARPETA_PLANTILLAS = "Plantillas"

# nombres ya normalizados (minúsculas, NFC)
ARCHIVOS_DEFAULT_PLANTILLAS = {
    "carga de documentos.pdf",
    "formato de seguimiento.pdf",
    "plan de formación y seguimientos uniminuto virtual .docx",
}


def nfc(nombre: str) -> str:
    # macOS puede separar las tildes (NFD); las unificamos
    return unicodedata.normalize("NFC", nombre)


def normalizar(nombre: str) -> str:
    return nfc(nombre).strip().lower()


def es_basura(nombre: str) -> bool:
    # ocultos del sistema y bloqueos de Office
    return nombre.startswith((".", "~$")) or nombre == "Icon\r"


def listar_archivos(carpeta: str, excluir: set[str] = frozenset()) -> list[str]:
    archivos = []
    for nombre in sorted(os.listdir(carpeta)):
        if es_basura(nombre) or normalizar(nombre) in excluir:
            continue
        if not os.path.isdir(os.path.join(carpeta, nombre)):
            archivos.append(nfc(nombre))
    return archivos


def leer_estudiantes(ruta_periodo: str) -> list[dict]:
    if not os.path.isdir(ruta_periodo):
        print(f"Ruta no encontrada: {ruta_periodo}")
        return []

    resultado = []
    for id_estudiante in sorted(os.listdir(ruta_periodo)):
        carpeta = os.path.join(ruta_periodo, id_estudiante)
        if es_basura(id_estudiante) or not os.path.isdir(carpeta):
            continue

        try:
            # listar_archivos ya ignora subcarpetas, incluida Plantillas
            archivos = listar_archivos(carpeta)

            # archivos que el estudiante subió dentro de Plantillas
            plantillas = os.path.join(carpeta, CARPETA_PLANTILLAS)
            if os.path.isdir(plantillas):
                archivos += listar_archivos(plantillas, ARCHIVOS_DEFAULT_PLANTILLAS)

            resultado.append({"id_estudiante": id_estudiante, "archivos": archivos, "error": False})
        except OSError as e:
            print(f"Error leyendo {id_estudiante}: {type(e).__name__}")
            resultado.append({"id_estudiante": id_estudiante, "archivos": [], "error": True})

    return resultado


if __name__ == "__main__":
    BASE = (
        "/Users/Ailyn/Library/CloudStorage/"
        "OneDrive-uniminuto.edu/"
        "G-Practicas Profesionales Rectoria Virtual - ADMINISTRACION DE EMPRESAS"
    )
    periodo = input("Periodo a procesar (ej. 2026-18): ").strip()
    ruta = os.path.join(BASE, periodo)

    estudiantes = leer_estudiantes(ruta)
    vacias = sum(1 for e in estudiantes if not e["archivos"] and not e["error"])
    con_error = sum(1 for e in estudiantes if e["error"])
    total_archivos = sum(len(e["archivos"]) for e in estudiantes)

    print(f"\nEstudiantes encontrados: {len(estudiantes)}")
    print(f"Carpetas vacías: {vacias}")
    print(f"Carpetas con error de lectura: {con_error}")
    print(f"Archivos totales: {total_archivos}")

