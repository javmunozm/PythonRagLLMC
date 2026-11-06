"""Practica chapter 7: llamar al LLM por raw http con src/clients/llm_http.py.
Gasta tokens, y se ejecuta con 'py -m practica.p07_http_raw'"""

import httpx

from src.clients.llm_http import LLMError, ask_gemini, ask_openai
from src.config import get_settings

if __name__ == "__main__":
    s = get_settings()
    with httpx.Client(timeout=60) as client:
        try:
            if s.llm_provider == "gemini":
                key = s.gemini_api_key.get_secret_value() if s.gemini_api_key else ""
                texto = ask_gemini(client, "¿Que es un RAG? Una frase.", key, s.llm_model)
            else:
                key = s.openai_api_key.get_secret_value() if s.openai_api_key else ""
                base_url = s.openai_base_url or "https://api.openai.com/v1"
                texto = ask_openai(client, "¿Que es RAG? Una frase.", key, s.llm_model, base_url)
            print(texto)
        except LLMError as e:
            print(f"No se pudo completar la consulta: {e}")