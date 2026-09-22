"""
Pruebas del Evaluador (test_evaluator.py)
"""

from process_validation.evaluator import evaluar_estudiante, filtrar_estudiantes, cargar_ids_incluir


def test_aprendizaje_completo_salvo_arl():
    r = evaluar_estudiante("1001", {"doc_identidad", "afiliacion_salud", "hoja_vida"}, "aprendizaje")
    assert r == {
        "doc_identidad": "cumplido",
        "afiliacion_salud": "cumplido",
        "afiliacion_arl": "faltante",
        "hoja_vida": "cumplido",
        "carta_presentacion": "no_verificable_por_programa",
        "carta_autorizacion": "no_aplica",
        "certificado_laboral": "no_aplica",
    }


def test_correccion_manual_pisa_el_resultado_calculado():
    r = evaluar_estudiante(
        "1006",
        {"doc_identidad", "afiliacion_salud", "hoja_vida"},
        "aprendizaje",
        correcciones={"afiliacion_salud"},
    )
    assert r["afiliacion_salud"] == "rechazado_pendiente"


def test_correccion_pisa_incluso_si_el_requisito_no_fue_detectado():
    r = evaluar_estudiante(
        "1007",
        set(),
        "aprendizaje",
        correcciones={"afiliacion_arl"},
    )
    assert r["afiliacion_arl"] == "rechazado_pendiente"


def test_requisito_condicional_cumplido_si_encontrado():
    r = evaluar_estudiante("1002", {"afiliacion_arl"}, "emprendimiento")
    assert r["afiliacion_arl"] == "cumplido"


def test_requisito_condicional_revisar_si_no_encontrado():
    r = evaluar_estudiante("1003", set(), "emprendimiento")
    assert r["afiliacion_arl"] == "revisar"


def test_requisito_externo_siempre_revisar():
    r = evaluar_estudiante("1004", {"carta_autorizacion"}, "emprendimiento")
    assert r["carta_autorizacion"] == "revisar"


def test_modalidad_no_reconocida_todo_a_revisar():
    r = evaluar_estudiante("1005", {"doc_identidad"}, "modalidad_inexistente")
    assert all(estado == "revisar" for estado in r.values())


def test_filtro_de_inclusion():
    estudiantes = [{"id_estudiante": "1001"}, {"id_estudiante": "1002"}]
    assert len(filtrar_estudiantes(estudiantes, None)) == 2
    assert len(filtrar_estudiantes(estudiantes, {"1001"})) == 1


def test_cargar_ids_incluir_desde_csv(tmp_path):
    ruta = tmp_path / "ids_revisar_hoy.csv"
    ruta.write_text("id_estudiante\n1001\n1002\n\n", encoding="utf-8")
    assert cargar_ids_incluir(str(ruta)) == {"1001", "1002"}


def test_requisito_marcado_para_corregir_da_rechazado_pendiente():
    r = evaluar_estudiante("1008", {"hoja_vida"}, "aprendizaje", correcciones={"hoja_vida"})
    assert r["hoja_vida"] == "rechazado_pendiente"


def test_en_extranjero_fuerza_no_aplica_en_afiliacion_arl():
    r = evaluar_estudiante("1009", {"afiliacion_arl"}, "aprendizaje", en_extranjero=True)
    assert r["afiliacion_arl"] == "no_aplica"