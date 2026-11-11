"""El mismo caso de uso de preguntas, escrito como grafo: un router decide si
hace falta buscar."""

from typing import Literal, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, START, StateGraph

from src.domain.answers import data_block
from src.domain.documents import ChunkRepository
from src.services.ask import RAG_PROMPT

class State(TypedDict, total=False): # total = False: las claves se van lleando
    question: str
    route: Literal["documentos", "general"]
    context: str
    answer: str

ROUTER_PROMPT = ChatPromptTemplate.from_messages(
        [
            (
            "system",
                (
                "Clasifica la pregunta. Responde solo 'documentos' si trata de políticas o "
                "documentos internos de la empresa, o 'general' en otro caso."
                ),
            ),
            ("human", "{question}"),
        ]
    )

def build_graph(llm: BaseChatModel, repo: ChunkRepository, k: int = 4):
    def router(state: State) -> dict:
        label = (ROUTER_PROMPT | llm | StrOutputParser()).invoke({"question": state["question"]})
        return {"route": "documentos" if "documentos" in label.lower() else "general"}

    def retrieve(state: State) -> dict:
        return {"context": data_block(repo.search(state["question"], k))}

    def answer_rag(state: State) -> dict:
        chain = RAG_PROMPT | llm | StrOutputParser()
        answer = chain.invoke({"context": state["context"], "question": state["question"]})
        return {"answer": answer}

    def answer_general(state: State) -> dict:
        return {"answer": llm.invoke(state["question"]).text}

    g = StateGraph(State)
    g.add_node("router", router)
    g.add_node("retrieve", retrieve)
    g.add_node("answer_rag", answer_rag)
    g.add_node("answer_general", answer_general)

    g.add_edge(START, "router")
    g.add_conditional_edges(
        "router",
        lambda s: s["route"], # devuelve el nombre de la ruta
        {"documentos": "retrieve", "general": "answer_general"},
    )
    g.add_edge("retrieve", "answer_rag")
    g.add_edge("answer_rag", END)
    g.add_edge("answer_general", END)
    return g.compile()
