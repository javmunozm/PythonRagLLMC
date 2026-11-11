from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from src.services.agent import AgentService
from src.services.graph import build_graph
from src.services.tools import make_search_tool
from tests.fakes import PRICES, fake_llm, with_usage


def pide_tool(nombre: str, **args) -> AIMessage:
    """Lo que responde el modelo cuando decide usar una herramienta."""
    return AIMessage(
        content="",
        tool_calls=[{"name": nombre, "args": args, "id": "c1"}],
    )


def test_agente_usa_la_herramienta_y_recuerda_el_hilo(repo):
    llm = fake_llm(
        pide_tool("buscar_documentos", consulta="vacaciones"),
        with_usage("Tienes 15 días hábiles.", 900, 100),
        "Sí, hábiles.",
    )
    memory = InMemorySaver()
    service = AgentService(llm, [make_search_tool(repo)], memory, PRICES)

    answer, usage = service.chat("¿Cuántos días de vacaciones tengo?", thread_id="t1")
    assert answer == "Tienes 15 días hábiles."
    assert (usage.input_tokens, usage.cost_usd) == (900, 0.001125)

    service.chat("¿Hábiles?", thread_id="t1")

    messages = memory.get({"configurable": {"thread_id": "t1"}})["channel_values"]["messages"]
    
    assert [m.type for m in messages] == [
        "human",
        "ai",
        "tool",
        "ai",
        "human",
        "ai",
    ]
    # En LangChain estándar el texto de un mensaje está en `.content`
    assert messages[2].content.startswith("<documentos>")  # la tool entrega los trozos delimitados


def test_grafo_elige_la_ruta(repo):
    con_docs = build_graph(fake_llm("documentos", "15 días [1]"), repo)
    assert con_docs.invoke({"question": "¿Vacaciones?"})["answer"] == "15 días [1]"

    general = build_graph(fake_llm("general", "París"), repo)
    assert general.invoke({"question": "¿Capital de Francia?"})["route"] == "general"