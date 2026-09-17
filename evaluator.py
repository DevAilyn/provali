"""
Evaluador: compara documentos detectados contra la matriz de requisitos
por modalidad y devuelve el estado de cada requisito.
"""

import csv

# tipo de regla por requisito, según modalidad
MATRIZ = {
    "aprendizaje": {
        "doc_identidad": "archivo",
        "afiliacion_salud": "archivo",
        "afiliacion_arl": "archivo",
        "hoja_vida": "archivo",
        "carta_presentacion": "forms",
        "carta_autorizacion": "no_aplica",
        "certificado_laboral": "no_aplica",
    },
    "emprendimiento": {
        "doc_identidad": "archivo",
        "afiliacion_salud": "archivo",
        "afiliacion_arl": "condicional",
        "hoja_vida": "archivo",
        "carta_presentacion": "no_aplica",
        "carta_autorizacion": "externo",
        "certificado_laboral": "no_aplica",
    },
    "laboral": {
        "doc_identidad": "archivo",
        "afiliacion_salud": "archivo",
        "afiliacion_arl": "archivo",
        "hoja_vida": "archivo",
        "carta_presentacion": "no_aplica",
        "carta_autorizacion": "archivo",
        "certificado_laboral": "archivo",
    },
    "internacional": {
        "doc_identidad": "archivo",
        "afiliacion_salud": "archivo",
        "afiliacion_arl": "no_aplica",
        "hoja_vida": "archivo",
        "carta_presentacion": "archivo",
        "carta_autorizacion": "no_aplica",
        "certificado_laboral": "no_aplica",
    },
    "semillero": {
        "doc_identidad": "archivo",
        "afiliacion_salud": "archivo",
        "afiliacion_arl": "condicional",
        "hoja_vida": "archivo",
        "carta_presentacion": "no_aplica",
        "carta_autorizacion": "archivo",
        "certificado_laboral": "no_aplica",
    },
    "convenio_especial": {
        "doc_identidad": "archivo",
        "afiliacion_salud": "archivo",
        "afiliacion_arl": "archivo",
        "hoja_vida": "archivo",
        "carta_presentacion": "forms",
        "carta_autorizacion": "no_aplica",
        "certificado_laboral": "no_aplica",
    },
}


def _evaluar_requisito(tipo_regla: str, encontrado: bool) -> str:
    if tipo_regla == "no_aplica":
        return "no_aplica"
    if tipo_regla == "forms":
        return "no_verificable_por_programa"
    if tipo_regla == "externo":
        return "revisar"
    if tipo_regla == "condicional":
        return "cumplido" if encontrado else "revisar"
    if tipo_regla == "archivo":
        return "cumplido" if encontrado else "faltante"
    return "revisar"  # tipo de regla desconocido, no debe pasar desapercibido


def evaluar_estudiante(
    id_estudiante: str,
    tipos_detectados: set[str],
    modalidad: str,
    correcciones: dict[str, str] | None = None,
) -> dict[str, str]:
    if modalidad not in MATRIZ:
        # modalidad vacia o no reconocida: todo queda para revision humana
        return {req: "revisar" for req in next(iter(MATRIZ.values()))}

    correcciones = correcciones or {}
    resultado = {}
    for requisito, tipo_regla in MATRIZ[modalidad].items():
        if requisito in correcciones:
            resultado[requisito] = correcciones[requisito]
            continue
        encontrado = requisito in tipos_detectados
        resultado[requisito] = _evaluar_requisito(tipo_regla, encontrado)

    return resultado


def cargar_ids_incluir(ruta: str) -> set[str]:
    with open(ruta, newline="", encoding="utf-8") as f:
        lector = csv.DictReader(f)
        return {fila["id_estudiante"].strip() for fila in lector if fila["id_estudiante"].strip()}


def filtrar_estudiantes(estudiantes: list[dict], ids_incluir: set[str] | None) -> list[dict]:
    if ids_incluir is None:
        return estudiantes
    return [e for e in estudiantes if e["id_estudiante"] in ids_incluir]
