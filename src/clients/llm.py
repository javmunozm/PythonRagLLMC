"""Infraestructura: el unico archivo que sabee con que proveedor de IA se habla"""

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_openai import (
    ChatOpenAI,
    OpenAIEmbeddings,
)

from src.config import get_settings

def get_chat_model(temperature: float = 0.0) -> BaseChatModel:
    s = get_settings()
    if s.llm_provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=s.llm_model,
            api_key=s.gemini_api_key,
            temperature=temperature,
            timeout=60,
            max_retries=2
        )
    return ChatOpenAI(
        model=s.llm_model,
        api_key=s.openai_api_key,
        base_url=s.openai_base_url or None,
        temperature=temperature,
        timeout=60,
        max_retries=2,
        stream_usage=True,
    )

def get_embeddings() -> Embeddings:
    s = get_settings()
    if s.llm_provider == "gemini":
        return GoogleGenerativeAIEmbeddings(model=s.embedding_model, api_key=s.gemini_api_key)
    return OpenAIEmbeddings(
        model=s.embedding_model,
        api_key=s.openai_api_key,
        base_url=s.openai_base_url or None,
        check_embedding_ctx_length=False,
    )
