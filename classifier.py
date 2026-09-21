"""
Clasificador: convierte un nombre de archivo en un tipo de documento.
"""

import re
import unicodedata

# plantillas vacias que se descartan sin clasificar
ARCHIVOS_PLANTILLA_DEFAULT = {
    "cargadedocumentos.pdf",
    "formatodeseguimiento.pdf",
    "plandeformacionyseguimientosuniminutovirtual.docx",
}

# tipos que el Clasificador reconoce (solo los que son archivo_en_sharepoint)
TIPOS = [
    "doc_identidad",
    "afiliacion_salud",
    "afiliacion_arl",
    "hoja_vida",
    "carta_autorizacion",
    "certificado_laboral",
    "carta_presentacion",
]

# tipos que se cuentan pero no forman parte de la matriz de requisitos
TIPOS_INFORMATIVOS = [
    "aprobacion_emprendimiento",
    "carta_compromiso",
    "contrato_aprendizaje",
]


def normalizar(nombre: str) -> str:
    # quita tildes, pasa a minusculas, quita espacios/guiones para comparar
    sin_tildes = unicodedata.normalize("NFKD", nombre)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return re.sub(r"[\s_\-]+", "", sin_tildes.lower())


def _tokens(nombre_archivo: str) -> list[str]:
    # como normalizar, pero conserva los separadores como limites de palabra
    sin_tildes = unicodedata.normalize("NFKD", nombre_archivo)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return re.split(r"[\s_\-.]+", sin_tildes.lower())


def es_plantilla_default(nombre_archivo: str) -> bool:
    return normalizar(nombre_archivo) in ARCHIVOS_PLANTILLA_DEFAULT


def clasificar(nombre_archivo: str) -> str:
    if es_plantilla_default(nombre_archivo):
        return "plantilla_descartada"

    n = normalizar(nombre_archivo)
    tokens = _tokens(nombre_archivo)

    # pantallazo de aprobacion de emprendimiento (informativo, no es archivo_en_sharepoint)
    if ("resultado" in n and "postulacion" in n) or (
        "emprendimiento" in n and ("aprobacion" in n or "postulacion" in n or "resultado" in n)
    ):
        return "aprobacion_emprendimiento"

    # carta de compromiso de matricular el siguiente periodo (informativo, opcional)
    if "compromiso" in n:
        return "carta_compromiso"

        # contrato de aprendizaje firmado (informativo, documento complementario)
    if "contrato" in n and "aprendizaje" in n:
        return "contrato_aprendizaje"

    if "identidad" in n or "cedula" in n or "fotocopia" in n or "cc" in tokens:
        return "doc_identidad"
    if ("certific" in n or "certfic" in n or "carta" in n) and ("laboral" in n or "funciones" in n):
        return "certificado_laboral"
    if "autorizacion" in n or "memorando" in n or "aprobacion" in n or "aval" in n:
        return "carta_autorizacion"
    if "hoja" in n and "vida" in n:
        return "hoja_vida"
    if "arl" in n:
        return "afiliacion_arl"
    if "salud" in n or "eps" in n:
        return "afiliacion_salud"
    if "presentacion" in n:
        return "carta_presentacion"

    return "no_clasificado"


def clasificar_lista(archivos: list[str]) -> list[dict]:
    return [{"archivo": a, "tipo": clasificar(a)} for a in archivos]