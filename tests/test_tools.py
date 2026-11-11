from src.services.tools import make_search_tool, make_weather_tool

def test_la_tool_del_clima_envuelve_el_caso_de_uso():
    clima = make_weather_tool(lambda lat, lon: 18.5)
    assert clima.name == "clima_actual"
    assert "Santiago" in clima.description # el docstring: lo que lee el modelo
    assert clima.invoke({"ciudad": "Santiago"}) == "18.5 °C en Santiago"

def test_busqueda_entrega_los_trozos_delimitados(repo):
    texto = make_search_tool(repo, k=2).invoke({"consulta": "vacaciones"})
    assert texto.startswith("<documentos>\n[1] rrhh.pdf p.") and "\n\n[2] rrhh.pdf p." in texto

def test_busqueda_sin_resultados_lo_dice(empty_repo):
    texto = make_search_tool(empty_repo).invoke({"consulta": "vacaciones"})
    assert texto == "No se encontraron documentos relevantes."