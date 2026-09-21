"""
Flujo integrado: Detector + Clasificador contra un periodo real.
Muestra solo conteos, nunca nombres de archivo ni de estudiantes.
"""

import os
from dotenv import load_dotenv

from process_validation.detector import leer_estudiantes
from process_validation.classifier import clasificar_lista, TIPOS, TIPOS_INFORMATIVOS
from process_validation.evaluator import cargar_correcciones_y_extranjero

load_dotenv()


def main():
    base = os.getenv("ONEDRIVE_BASE_PATH")
    if not base:
        print("Falta ONEDRIVE_BASE_PATH en el .env")
        return

    ruta_correcciones = os.getenv("CSV_CORRECCIONES_PATH")
    correcciones_por_id, ids_en_extranjero = {}, set()
    if ruta_correcciones and os.path.isfile(ruta_correcciones):
        correcciones_por_id, ids_en_extranjero = cargar_correcciones_y_extranjero(ruta_correcciones)

    periodo = input("Periodo a procesar (ej. 2026-18): ").strip()
    ruta = os.path.join(base, periodo)

    estudiantes = leer_estudiantes(ruta)
    if not estudiantes:
        return

    conteo_tipos = {tipo: 0 for tipo in TIPOS + TIPOS_INFORMATIVOS}
    conteo_tipos["plantilla_descartada"] = 0
    conteo_tipos["no_clasificado"] = 0

    vacias = 0
    con_error = 0
    total_archivos = 0

    for estudiante in estudiantes:
        if estudiante["error"]:
            con_error += 1
            continue
        if not estudiante["archivos"]:
            vacias += 1
            continue

        clasificados = clasificar_lista(estudiante["archivos"])
        total_archivos += len(clasificados)
        for item in clasificados:
            conteo_tipos[item["tipo"]] += 1

    print(f"\nEstudiantes encontrados: {len(estudiantes)}")
    print(f"Carpetas vacías: {vacias}")
    print(f"Carpetas con error de lectura: {con_error}")
    print(f"Archivos totales clasificados: {total_archivos}")
    print("\nConteo por tipo de documento:")
    for tipo, cantidad in conteo_tipos.items():
        print(f"  {tipo}: {cantidad}")

    if correcciones_por_id or ids_en_extranjero:
        print(f"\nCorrecciones cargadas: {len(correcciones_por_id)} estudiantes con al menos un requisito a corregir")
        print(f"Estudiantes marcados en el extranjero: {len(ids_en_extranjero)}")


if __name__ == "__main__":
    main()