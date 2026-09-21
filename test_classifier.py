"""
Pruebas del Clasificador (test_classifier.py)
"""

from classifier import normalizar, es_plantilla_default, clasificar, clasificar_lista


def test_normalizar_quita_tildes_y_mayusculas():
    assert normalizar("AFILIACIÓN") == "afiliacion"


def test_normalizar_quita_espacios_guiones_y_guion_bajo():
    assert normalizar("Hoja De Vida") == "hojadevida"
    assert normalizar("hoja_de_vida") == "hojadevida"
    assert normalizar("hoja-de-vida") == "hojadevida"


def test_variante_arl_con_espacio_y_sin_espacio():
    assert clasificar("1006959_JUAN_AFILIACION ARL_AEMV.pdf") == "afiliacion_arl"
    assert clasificar("1006959_JUAN_AFILIACIONARL_AEMV.pdf") == "afiliacion_arl"


def test_variante_hoja_vida_con_espacio_y_sin_espacio():
    assert clasificar("1006959_JUAN_HOJA DE VIDA_AEMV.pdf") == "hoja_vida"
    assert clasificar("1006959_JUAN_HOJADEVIDA_AEMV.pdf") == "hoja_vida"


def test_archivo_no_reconocido():
    assert clasificar("1006959_JUAN_ARCHIVO_RARO_AEMV.pdf") == "no_clasificado"


def test_plantillas_por_defecto_se_reconocen_con_variantes():
    assert es_plantilla_default("carga de documentos.pdf")
    assert es_plantilla_default("CARGA_DE_DOCUMENTOS.pdf")
    assert es_plantilla_default("formato de seguimiento.pdf")
    assert es_plantilla_default("Plan de formación y seguimientos UNIMINUTO Virtual .docx")


def test_clasificar_devuelve_plantilla_descartada():
    assert clasificar("carga de documentos.pdf") == "plantilla_descartada"


def test_imagenes_se_clasifican_igual_que_pdf():
    assert clasificar("1006959_JUAN_HOJADEVIDA_AEMV.jpg") == "hoja_vida"
    assert clasificar("1006959_JUAN_DOC IDENTIDAD_AEMV.png") == "doc_identidad"


def test_todos_los_tipos_reconocidos():
    casos = {
        "identidad.pdf": "doc_identidad",
        "cedula.pdf": "doc_identidad",
        "afiliacion salud.pdf": "afiliacion_salud",
        "eps.pdf": "afiliacion_salud",
        "afiliacion arl.pdf": "afiliacion_arl",
        "hoja de vida.pdf": "hoja_vida",
        "carta autorizacion.pdf": "carta_autorizacion",
        "memorando.pdf": "carta_autorizacion",
        "certificado laboral.pdf": "certificado_laboral",
        "carta presentacion.pdf": "carta_presentacion",
    }
    for archivo, tipo_esperado in casos.items():
        assert clasificar(archivo) == tipo_esperado


def test_clasificar_lista():
    archivos = ["identidad.pdf", "archivo_raro.pdf"]
    resultado = clasificar_lista(archivos)
    assert resultado == [
        {"archivo": "identidad.pdf", "tipo": "doc_identidad"},
        {"archivo": "archivo_raro.pdf", "tipo": "no_clasificado"},
    ]


# variantes agregadas tras revisar datos reales del corte 2026-18


def test_doc_identidad_variantes_fotocopia_y_cedula():
    assert clasificar("FOTOCOPIA CEDULA.pdf") == "doc_identidad"
    assert clasificar("1006959_JUAN_FOTOCOPIA_AEMV.pdf") == "doc_identidad"


def test_doc_identidad_cc_como_palabra_completa():
    assert clasificar("1006959_JUAN_CC_AEMV.pdf") == "doc_identidad"


def test_cc_no_activa_si_no_es_palabra_completa():
    # "cc" pegado dentro de otra palabra no debe disparar doc_identidad
    assert clasificar("1006959_MARCCELA_HOJADEVIDA_AEMV.pdf") == "hoja_vida"


def test_certificado_laboral_con_typo_certficado():
    assert clasificar("CERTFICADO LABORAL.pdf") == "certificado_laboral"


def test_certificado_laboral_variante_certificacion():
    assert clasificar("CERTIFICACION LABORAL CON FUNCIONES.pdf") == "certificado_laboral"


def test_certificado_laboral_variante_carta_laboral_funciones():
    assert clasificar("CARTA LABORAL FUNCIONES.pdf") == "certificado_laboral"


def test_carta_autorizacion_variante_aprobacion():
    assert clasificar("CARTA APROBACION PRACTICAS.pdf") == "carta_autorizacion"


def test_carta_autorizacion_variante_aval_semillero():
    assert clasificar("CARTA AVAL SEMILLERO.pdf") == "carta_autorizacion"


def test_aprobacion_emprendimiento_con_palabra_emprendimiento():
    assert clasificar("APROBACION EMPRENDIMIENTO.pdf") == "aprobacion_emprendimiento"
    assert clasificar("RESULTADOS POSTULACION EMPRENDIMIENTO.pdf") == "aprobacion_emprendimiento"


def test_aprobacion_emprendimiento_sin_palabra_emprendimiento():
    assert clasificar("RESULTADOS POSTULACION.pdf") == "aprobacion_emprendimiento"


def test_carta_compromiso():
    assert clasificar("CARTA COMPROMISO PRACTICA PROFESIONAL.pdf") == "carta_compromiso"


def test_contrato_aprendizaje():
    assert clasificar("CONTRATO DE APRENDIZAJE.pdf") == "contrato_aprendizaje"
    assert clasificar("CONTRATO APRENDIZAJE FIRMADO.pdf") == "contrato_aprendizaje"