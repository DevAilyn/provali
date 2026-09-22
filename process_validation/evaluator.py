"""
Evaluador: compara documentos detectados contra la matriz de requisitos
por modalidad y devuelve el estado de cada requisito.
"""

import csv
import re

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


# columna de la base real -> clave de requisito usada en MATRIZ
COLUMNAS_A_REQUISITO = {
    "HOJA VIDA": "hoja_vida",
    "DOC IDENTIDAD": "doc_identidad",
    "AFIL. SALUD": "afiliacion_salud",
    "AFIL. ARL": "afiliacion_arl",
    "CARTA O MEMORANDO DE AUTORIZACIÓN - APROBACIÓN": "carta_autorizacion",
    "CERTIFICADO LABORAL CON FUNCIONES": "certificado_laboral",
}

def _normalizar_encabezado(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


def _leer_filas_csv(ruta: str) -> list[dict]:
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        muestra = f.read(4096)
        f.seek(0)
        delimitador = ";" if muestra.count(";") > muestra.count(",") else ","
        lector = csv.DictReader(f, delimiter=delimitador)
        return [
            {_normalizar_encabezado(k): v for k, v in fila.items() if k and _normalizar_encabezado(k)}
            for fila in lector
        ]


def cargar_correcciones_y_extranjero(ruta: str) -> tuple[dict[str, set[str]], set[str]]:
    correcciones = {}
    en_extranjero = set()
    for fila in _leer_filas_csv(ruta):
            id_estudiante = fila["ID ESTUDIANTE"].strip()
            if not id_estudiante:
                continue
            if "extranjero" in fila.get("OBSERVACIONES", "").lower():
                en_extranjero.add(id_estudiante)
            requisitos_a_corregir = {
                requisito
                for columna, requisito in COLUMNAS_A_REQUISITO.items()
                if fila.get(columna, "").strip() == "Corregir"
            }
            if requisitos_a_corregir:
                correcciones[id_estudiante] = requisitos_a_corregir

    return correcciones, en_extranjero


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
    correcciones: set[str] | None = None,
    en_extranjero: bool = False,
) -> dict[str, str]:
    if modalidad not in MATRIZ:
        return {req: "revisar" for req in next(iter(MATRIZ.values()))}

    correcciones = correcciones or set()
    resultado = {}
    for requisito, tipo_regla in MATRIZ[modalidad].items():
        if requisito == "afiliacion_arl" and en_extranjero:
            resultado[requisito] = "no_aplica"
            continue
        if requisito in correcciones:
            resultado[requisito] = "rechazado_pendiente"
            continue
        encontrado = requisito in tipos_detectados
        resultado[requisito] = _evaluar_requisito(tipo_regla, encontrado)

    return resultado


def cargar_ids_incluir(ruta: str) -> set[str]:
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        return {fila["id_estudiante"].strip() for fila in lector if fila["id_estudiante"].strip()}


def filtrar_estudiantes(estudiantes: list[dict], ids_incluir: set[str] | None) -> list[dict]:
    if ids_incluir is None:
        return estudiantes
    return [e for e in estudiantes if e["id_estudiante"] in ids_incluir]
