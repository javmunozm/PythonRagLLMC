"""Práctica capítulo 8: LangChain v1 (modelo, invoke/stream/batch, prompts,
LCEL, tools).
Usa el modelo configurado en .env a través de src/clients/llm.py. GASTA
TOKENS.
Ejecuta desde la raíz:
 python -m practica.p08_langchain
"""

from langchain.messages import (
    HumanMessage, 
    SystemMessage,
    )
from langchain.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    )
from langchain_core.runnables import (
    RunnableLambda, 
    RunnableParallel
    )

from src.clients.llm import get_chat_model
from src.services.tickets import TicketService

@tool
def sumar(a: int, b: int) -> int:
    """Suma dos enteros.""" #docstring que lee el llm
    return a + b


if __name__ == "__main__":
    llm = get_chat_model()

    print("=== invoke, stream y batch ===")
    r = llm.invoke("¿Que es un embedding? Una frase.")
    print(r.text) # lee .text, no el .content, (con gemini .content es una lista)
    print(r.usage_metadata)
    for chunk in llm.stream("Explica RAG en 2 frases"):
        print(chunk.text, end="", flush=True)
    print()
    print([m.text for m in llm.batch(["Di hola", "¿Que es Python? Una frase."])])
    print(llm.invoke([SystemMessage("Se breve"), HumanMessage("Hola")]).text)

    print("=== prompt reutilizable + LCEL ===")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Eres un experto en {tema}. Responde en maximo {n} frases."),
            MessagesPlaceholder("historial"),
            ("human", "{pregunta}"),
        ]
    )
    chain = prompt | llm | StrOutputParser() #prompt -> modelo -> texto plano
    print(chain.invoke({"tema": "python", "n": 2, "historial":[],
                        "pregunta": "¿Que es pip?"}))
    resumir = ChatPromptTemplate.from_template("Resume en una frase: {texto}") | llm
    traducir = ChatPromptTemplate.from_template("Traduce al ingles: {texto}") | llm
    resumir_y_traducir = (
        resumir | StrOutputParser() | RunnableLambda(lambda r: {"texto": r}) | traducir
    )
    print(resumir_y_traducir.invoke({"texto": "Python es un lenguaje facil de leer."}).text)
    ambos = RunnableParallel(resumen=resumir, traduccion=traducir)
    print({k: v.text for k, v in ambos.invoke({"texto": "langChain une modelos"}).items()})
    print("=== salida estructurada (TicketService del proyecto) ===")
    print(TicketService(llm).classify("No puedo entrar al sistema y hoy tengo cierre de mes"))

    print("=== tools ===")
    print(sumar.invoke({"a": 2, "b": 3}))
    print(llm.bind_tools([sumar]).invoke("¿Cuanto es 2 + 3?").tool_calls)