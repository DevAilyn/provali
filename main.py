"""
Flujo integrado: Detector + Clasificador + Resolutor de modalidad + Evaluador.
Muestra solo conteos, nunca nombres de archivo ni de estudiantes.
"""

import os
from dotenv import load_dotenv

from process_validation.detector import leer_estudiantes
from process_validation.classifier import clasificar_lista, TIPOS, TIPOS_INFORMATIVOS

from process_validation.evaluator import (
    cargar_correcciones_y_extranjero,
    cargar_modalidades,
    cargar_verificaciones_forms,
    resolver_modalidad,
    evaluar_estudiante,
    cargar_ids_incluir,
    filtrar_estudiantes,
)
from process_validation.output import (
    construir_fila,
    fila_con_error,
    construir_resultados,
    escribir_json,
    escribir_excel,
)

load_dotenv()


def main():
    base = os.getenv("ONEDRIVE_BASE_PATH")
    if not base:
        print("Falta ONEDRIVE_BASE_PATH en el .env")
        return

    ruta_correcciones = os.getenv("CSV_CORRECCIONES_PATH")
    correcciones_por_id, ids_en_extranjero = {}, set()
    modalidades_por_id = {}
    verificaciones_forms_por_id = {}
    if ruta_correcciones and os.path.isfile(ruta_correcciones):
        correcciones_por_id, ids_en_extranjero = cargar_correcciones_y_extranjero(ruta_correcciones)
        modalidades_por_id = cargar_modalidades(ruta_correcciones)
        verificaciones_forms_por_id = cargar_verificaciones_forms(ruta_correcciones)

    periodo = input("Periodo a procesar (ej. 2026-18): ").strip()
    ruta = os.path.join(base, periodo)

    estudiantes = leer_estudiantes(ruta)
    if not estudiantes:
        return

    ruta_ids_revisar = os.getenv("CSV_IDS_REVISAR_HOY_PATH")
    if ruta_ids_revisar and os.path.isfile(ruta_ids_revisar):
        respuesta = input("¿Filtrar solo por los IDs de ids_revisar_hoy.csv? (si/no): ").strip().lower()
        if respuesta == "si":
            ids_incluir = cargar_ids_incluir(ruta_ids_revisar)
            estudiantes = filtrar_estudiantes(estudiantes, ids_incluir)
            print(f"Filtro activado: procesando solo {len(estudiantes)} estudiante(s) del CSV de revisión")

    conteo_tipos = {tipo: 0 for tipo in TIPOS + TIPOS_INFORMATIVOS}
    conteo_tipos["plantilla_descartada"] = 0
    conteo_tipos["no_clasificado"] = 0

    vacias = 0
    con_error = 0
    total_archivos = 0
    sin_modalidad = 0
    conteo_fuentes = {"csv_real": 0, "forms": 0, "documentos": 0}
    conteo_estados = {}

    filas = []

    for estudiante in estudiantes:
        id_estudiante = estudiante["id_estudiante"]
        verificaciones = verificaciones_forms_por_id.get(id_estudiante, {})
        preinscripcion = verificaciones.get("preinscripcion")
        induccion = verificaciones.get("induccion")

        if estudiante["error"]:
            con_error += 1
            filas.append(fila_con_error(id_estudiante, "OSError"))
            continue

        if not estudiante["archivos"]:
            vacias += 1
            filas.append(construir_fila(
                id_estudiante, 0, 0, None, "sin_resolver", None, False, {},
                preinscripcion=preinscripcion, induccion=induccion,
            ))
            continue

        clasificados = clasificar_lista(estudiante["archivos"])
        total_archivos += len(clasificados)
        for item in clasificados:
            conteo_tipos[item["tipo"]] += 1

        tipos_detectados = {item["tipo"] for item in clasificados}
        sin_clasificar = sum(1 for item in clasificados if item["tipo"] == "no_clasificado")

        modalidad, fuente, observacion = resolver_modalidad(
            tipos_detectados,
            modalidades_por_id.get(id_estudiante),
        )

        en_extranjero = id_estudiante in ids_en_extranjero

        if modalidad is None:
            sin_modalidad += 1
            filas.append(construir_fila(
                id_estudiante, len(clasificados), sin_clasificar,
                None, fuente, observacion, en_extranjero, {},
                preinscripcion=preinscripcion, induccion=induccion,
            ))
            continue

        conteo_fuentes[fuente] += 1
        resultado = evaluar_estudiante(
            id_estudiante,
            tipos_detectados,
            modalidad,
            correcciones_por_id.get(id_estudiante),
            en_extranjero,
        )
        for estado in resultado.values():
            conteo_estados[estado] = conteo_estados.get(estado, 0) + 1

        filas.append(construir_fila(
            id_estudiante, len(clasificados), sin_clasificar,
            modalidad, fuente, observacion, en_extranjero, resultado,
            preinscripcion=preinscripcion, induccion=induccion,
        ))

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

    if verificaciones_forms_por_id:
        for etiqueta, campo in (("Preinscripción", "preinscripcion"), ("Inducción", "induccion")):
            si = sum(1 for f in filas if f[campo] == "SI")
            no = sum(1 for f in filas if f[campo] == "NO")
            vacios = sum(1 for f in filas if f[campo] is None)
            print(f"\n{etiqueta} -> SI: {si}, NO: {no}, sin dato: {vacios}")

    print(f"\nEstudiantes sin modalidad resuelta: {sin_modalidad}")
    print("Modalidad resuelta por fuente:")
    for fuente, cantidad in conteo_fuentes.items():
        print(f"  {fuente}: {cantidad}")
    print("\nConteo por estado de requisito (todos los estudiantes con modalidad):")
    for estado, cantidad in sorted(conteo_estados.items()):
        print(f"  {estado}: {cantidad}")

    resultados = construir_resultados(periodo, filas)
    ruta_json = escribir_json(resultados, f"salidas/{periodo}/resultados.json")
    ruta_excel = escribir_excel(resultados, f"salidas/{periodo}/resultados.xlsx")
    print(f"\nResultados escritos en:\n  {ruta_json}\n  {ruta_excel}")


if __name__ == "__main__":
    main()