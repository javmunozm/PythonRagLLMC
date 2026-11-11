"""Práctica capítulo 10: el agente con memoria, sus pasos por dentro y el grafo LangGraph.
Necesita .env con clave y documentos ya indexados (python -m src.scripts.ingest data/docs).
GASTA TOKENS. Ejecuta desde la raíz:
 python -m practica.p10_agente
"""
from langchain.agents import create_agent
from src.container import get_agent_service, get_llm, get_repo
from src.services.graph import build_graph
from src.services.tools import make_search_tool

if __name__ == "__main__":
    print("=== agente con memoria ===")
    agent = get_agent_service()
    answer, usage = agent.chat(
        "¿Cuántos días de vacaciones tengo?", thread_id="usuario-42"
    )
    print(answer, "| costo USD:", usage.cost_usd)

    answer, usage = agent.chat(
        "¿Y con cuánta anticipación los pido?", thread_id="usuario-42"
    )
    print(answer)  # mismo thread_id: recuerda la pregunta anterior

    print("=== el bucle por dentro: model -> tools -> model ===")
    crudo = create_agent(model=get_llm(), tools=[make_search_tool(get_repo())])
    pregunta = {
        "messages": [
            {"role": "user", "content": "¿Cuántos días de vacaciones tengo?"}
        ]
    }

    for chunk in crudo.stream(pregunta, stream_mode="updates"):
        for nodo, update in chunk.items():
            # Nota: Si tu versión de LangChain usa .content en lugar de .text, cámbialo a update["messages"][-1].content[:120]
            msg = update["messages"][-1]
            contenido = getattr(msg, "text", getattr(msg, "content", str(msg)))
            print(nodo, "→", contenido[:120])

    print("=== grafo propio con LangGraph ===")
    graph = build_graph(get_llm(), get_repo())
    out = graph.invoke({"question": "¿Cuántos días de vacaciones tengo?"})
    print(out["route"], "→", out["answer"])
    print(graph.get_graph().draw_mermaid())  # diagrama para pegar en tu README