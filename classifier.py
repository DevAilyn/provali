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


def normalizar(nombre: str) -> str:
    # quita tildes, pasa a minusculas, quita espacios/guiones para comparar
    sin_tildes = unicodedata.normalize("NFKD", nombre)
    sin_tildes = "".join(c for c in sin_tildes if not unicodedata.combining(c))
    return re.sub(r"[\s_\-]+", "", sin_tildes.lower())


def es_plantilla_default(nombre_archivo: str) -> bool:
    return normalizar(nombre_archivo) in ARCHIVOS_PLANTILLA_DEFAULT


def clasificar(nombre_archivo: str) -> str:
    if es_plantilla_default(nombre_archivo):
        return "plantilla_descartada"

    n = normalizar(nombre_archivo)

    if "identidad" in n or "cedula" in n:
        return "doc_identidad"
    if "certificado" in n and "laboral" in n:
        return "certificado_laboral"
    if "autorizacion" in n or "memorando" in n:
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