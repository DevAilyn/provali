import openpyxl
import pytest

from process_validation.base_reader import cargar_base_xlsx, normalizar_texto

ENCABEZADOS = [
    "NOMBRES Y APELLIDOS", "ID  ESTUDIANTE", "DOCUMENTO ",
    "MODALIDAD SELECCIONADA ", "DOC \nIDENTIDAD", "ESTADO", None, None,
]


def _crear_base(tmp_path, filas, hoja="2026-23"):
    libro = openpyxl.Workbook()
    ws = libro.active
    ws.title = hoja
    libro.create_sheet("Cruce Induccion")
    ws.append(ENCABEZADOS)
    for fila in filas:
        ws.append(fila)
    ruta = tmp_path / "base_ficticia.xlsx"
    libro.save(ruta)
    return ruta


def test_excluye_no_cumple_y_filas_sin_id(tmp_path):
    ruta = _crear_base(tmp_path, [
        ["Ana Prueba", "100", "OK", "CONTRATO LABORAL", "SI", None],
        ["Beto Prueba", "200", " no cumple ", None, None, None],
        [None, None, None, None, None, None],
    ])
    base = cargar_base_xlsx(ruta, "2026-23")
    assert list(base.filas) == ["100"]
    assert base.excluidos_no_cumple == 1


def test_encabezados_sucios_quedan_normalizados(tmp_path):
    ruta = _crear_base(tmp_path, [["Ana Prueba", "100", None, "EMPRENDIMIENTO", "SI", None]])
    base = cargar_base_xlsx(ruta, "2026-23")
    fila = base.filas["100"]
    assert fila["DOC IDENTIDAD"] == "SI"
    assert fila["MODALIDAD SELECCIONADA"] == "EMPRENDIMIENTO"


def test_conserva_encabezados_originales_sin_columnas_vacias_al_final(tmp_path):
    ruta = _crear_base(tmp_path, [["Ana Prueba", "100", None, None, None, None]])
    base = cargar_base_xlsx(ruta, "2026-23")
    assert base.encabezados[1] == "ID  ESTUDIANTE"
    assert base.encabezados[-1] == "ESTADO"


def test_id_numerico_se_vuelve_texto(tmp_path):
    ruta = _crear_base(tmp_path, [["Ana Prueba", 851049, None, None, None, None]])
    base = cargar_base_xlsx(ruta, "2026-23")
    assert "851049" in base.filas


def test_detecta_estado_ok(tmp_path):
    ruta = _crear_base(tmp_path, [
        ["Ana Prueba", "100", None, None, None, "OK"],
        ["Beto Prueba", "200", None, None, None, "REVISION"],
    ])
    base = cargar_base_xlsx(ruta, "2026-23")
    assert base.es_ok("100")
    assert not base.es_ok("200")


def test_ids_duplicados_se_reportan_y_gana_la_primera_fila(tmp_path):
    ruta = _crear_base(tmp_path, [
        ["Ana Prueba", "100", "primera", None, None, None],
        ["Ana Prueba", "100", "segunda", None, None, None],
    ])
    base = cargar_base_xlsx(ruta, "2026-23")
    assert base.filas["100"]["DOCUMENTO"] == "primera"
    assert base.ids_duplicados == ["100"]


def test_hoja_inexistente_da_error_claro(tmp_path):
    ruta = _crear_base(tmp_path, [])
    with pytest.raises(ValueError, match="Hojas disponibles"):
        cargar_base_xlsx(ruta, "2099-01")


def test_normalizar_texto():
    assert normalizar_texto("  DOC \nIDENTIDAD ") == "DOC IDENTIDAD"
    assert normalizar_texto("   ") is None
