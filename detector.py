"""
Detector: lee la estructura de carpetas de estudiantes desde OneDrive local.
Retorna una lista de dicts {id_estudiante, archivos}.
"""

import os
import unicodedata

CARPETA_EXCLUIDA = "Plantillas"
ARCHIVOS_PLANTILLA_EXCLUIDOS = {
    "carga de documentos.pdf",
    "plan de formación y seguimientos uniminuto virtual .docx",
}

def leer_estudiantes(ruta_periodo: str) -> list[dict]:
    # ruta_periodo: ruta completa a la carpeta del periodo (ej. .../2026-18)
    resultado = []

    if not os.path.isdir(ruta_periodo):
        print(f"Ruta no encontrada: {ruta_periodo}")
        return resultado

    for id_estudiante in os.listdir(ruta_periodo):
        carpeta_estudiante = os.path.join(ruta_periodo, id_estudiante)

        if not os.path.isdir(carpeta_estudiante):
            continue  # ignora archivos sueltos en la raíz del periodo

        archivos = []
        for nombre in os.listdir(carpeta_estudiante):
            ruta_archivo = os.path.join(carpeta_estudiante, nombre)

            if nombre == CARPETA_EXCLUIDA:
                for nombre_plantilla in os.listdir(ruta_archivo):
                    clave = unicodedata.normalize("NFC", nombre_plantilla).lower()
                    if clave in ARCHIVOS_PLANTILLA_EXCLUIDOS:
                        continue  # ignora los archivos por defecto de Plantillas
                    archivos.append(nombre_plantilla)
                continue

            if not os.path.isdir(ruta_archivo):
                archivos.append(nombre)

        resultado.append({
            "id_estudiante": id_estudiante,
            "archivos": archivos
        })

    return resultado


if __name__ == "__main__":
    RUTA = (
        "/Users/Ailyn/Library/CloudStorage/"
        "OneDrive-uniminuto.edu/"
        "G-Practicas Profesionales Rectoria Virtual - ADMINISTRACION DE EMPRESAS/"
        "2026-18"
    )
    estudiantes = leer_estudiantes(RUTA)
    print(f"Estudiantes encontrados: {len(estudiantes)}")
    for e in estudiantes[:3]:
        print(f"\nID: {e['id_estudiante']}")
        print(f"Archivos: {e['archivos']}")