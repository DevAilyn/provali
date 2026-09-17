from evaluator import evaluar_estudiante, filtrar_estudiantes

print("Caso 1: Aprendizaje, todo completo salvo ARL")
r = evaluar_estudiante("1001", {"doc_identidad", "afiliacion_salud", "hoja_vida"}, "aprendizaje")
for k, v in r.items():
    print(f"  {k}: {v}")

print("\nCaso 2: correccion manual pisa el resultado calculado")
r = evaluar_estudiante(
    "1006",
    {"doc_identidad", "afiliacion_salud", "hoja_vida"},
    "aprendizaje",
    correcciones={"afiliacion_salud": "rechazado_pendiente"},
)
assert r["afiliacion_salud"] == "rechazado_pendiente"
print("  ok, la correccion pisa el resultado")

print("\nCaso 3: filtro de inclusion")
estudiantes = [{"id_estudiante": "1001"}, {"id_estudiante": "1002"}]
assert len(filtrar_estudiantes(estudiantes, None)) == 2
assert len(filtrar_estudiantes(estudiantes, {"1001"})) == 1
print("  ok, filtro funciona con y sin lista")

print("\nTodo paso.")