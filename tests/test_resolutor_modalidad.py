from process_validation.evaluator import resolver_modalidad


def test_fuente_csv_real():
    resultado = resolver_modalidad(set(), "Contrato de Aprendizaje", None)
    assert resultado == ("aprendizaje", "csv_real", None)


def test_fuente_forms_cuando_no_hay_csv():
    resultado = resolver_modalidad(set(), None, "Emprendimiento")
    assert resultado == ("emprendimiento", "forms", None)


def test_fuente_documentos_certificado_laboral():
    resultado = resolver_modalidad({"certificado_laboral"}, None, None)
    assert resultado == ("laboral", "documentos", None)


def test_fuente_documentos_contrato_aprendizaje():
    resultado = resolver_modalidad({"contrato_aprendizaje"}, None, None)
    assert resultado == ("aprendizaje", "documentos", None)


def test_sin_resolver_sin_candidatas():
    modalidad, fuente, observacion = resolver_modalidad({"doc_identidad", "hoja_vida"}, None, None)
    assert modalidad is None
    assert fuente == "sin_resolver"
    assert "sin candidatas" in observacion


def test_sin_resolver_con_candidatas_ambiguas():
    tipos = {"certificado_laboral", "contrato_aprendizaje"}
    modalidad, fuente, observacion = resolver_modalidad(tipos, None, None)
    assert modalidad is None
    assert fuente == "sin_resolver"
    assert "aprendizaje" in observacion
    assert "laboral" in observacion


def test_csv_real_tiene_prioridad_sobre_forms_y_documentos():
    resultado = resolver_modalidad({"certificado_laboral"}, "Semillero de Investigación", "Aprendizaje")
    assert resultado == ("semillero", "csv_real", None)


def test_normaliza_mayusculas_y_tildes():
    resultado = resolver_modalidad(set(), "CONVENIO ESPECIAL", None)
    assert resultado == ("convenio_especial", "csv_real", None)

from process_validation.evaluator import cargar_modalidades


def test_cargar_modalidades_desde_csv(tmp_path):
    ruta = tmp_path / "base_real.csv"
    ruta.write_text(
        "ID ESTUDIANTE,MODALIDAD SELECCIONADA\n"
        "ST001,Contrato de Aprendizaje\n"
        "ST002,\n"
        "ST003,Laboral\n",
        encoding="utf-8",
    )
    resultado = cargar_modalidades(str(ruta))
    assert resultado == {
        "ST001": "Contrato de Aprendizaje",
        "ST003": "Laboral",
    }