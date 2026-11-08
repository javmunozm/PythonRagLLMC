# from collections.abc import Sequence

# from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
# from langchain_core.messages import AIMessage


# class FakeToolChatModel(GenericFakeChatModel):
#     def bind_tools(self, tool : Sequence, **kwargs):
#         return self

# def fake_llm(*respuestas: str | AIMessage) -> FakeToolChatModel:
#     msgs = [r if isinstance(r, AIMessage) else AIMessage(content=r) for r in respuestas]
#     return FakeToolChatModel(messages=iter(msgs))
"""Dobles de prueba: reemplazan todo lo que sale del proceso (modelo, red, archivos)."""
from collections.abc import Sequence
import httpx
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.domain.costs import Prices

# los de .env.example
PRICES = Prices(input_per_mtok=0.75, output_per_mtok=4.50)


class FakeToolChatModel(GenericFakeChatModel):
    """Modelo falso que acepta bind_tools (lo necesitan create_agent y la
    salida estructurada)."""

    def bind_tools(self, tools: Sequence, **kwargs):
        return self


def fake_llm(*respuestas: str | AIMessage) -> FakeToolChatModel:
    """Devuelve las respuestas en orden, una por cada llamada."""
    msgs = [r if isinstance(r, AIMessage) else AIMessage(content=r) for r in respuestas]
    return FakeToolChatModel(messages=iter(msgs))


def with_usage(text: str, tokens_in: int, tokens_out: int) -> AIMessage:
    """Respuesta falsa que además informa tokens, como hace un proveedor
    real."""
    usage = {
        "input_tokens": tokens_in,
        "output_tokens": tokens_out,
        "total_tokens": tokens_in + tokens_out,
    }
    return AIMessage(content=text, usage_metadata=usage, response_metadata={"model_name": "fake"})


def broken_llm(handler) -> ChatOpenAI:
    """Modelo real de LangChain conectado a una red falsa: sirve para simular
    429, cortes, etc."""
    transport = httpx.MockTransport(handler)
    return ChatOpenAI(
        model="gpt-5.4-mini",
        api_key="sk-test",
        max_retries=0,
        http_client=httpx.Client(transport=transport),
        http_async_client=httpx.AsyncClient(transport=transport),
    )


def broken_embeddings(handler) -> OpenAIEmbeddings:
    """Embeddings reales de LangChain conectados a una red falsa (los usa la
    búsqueda del RAG)."""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key="sk-test",
        max_retries=0,
        check_embedding_ctx_length=False,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def tiny_pdf(text: str) -> bytes:
    """PDF mínimo de una página con ese texto (ASCII), para no depender de
    archivos binarios."""
    stream = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf, offsets = b"%PDF-1.4\n", []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += b"%d 0 obj\n%s\nendobj\n" % (number, body)
    xref = len(pdf)
    pdf += b"xref\n0 6\n0000000000 65535 f \n"
    pdf += b"".join(b"%010d 00000 n \n" % offset for offset in offsets)
    return pdf + b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % xref