"""Llamar a un llm por http, sin sdk: la misma peticion de postman con reintentos"""

import logging 
import time
from collections.abc import Callable

import httpx

logger = logging.getLogger(__name__)
RETRYABLE = {408, 429, 500, 502, 503, 504} #errores con los que se reintenta


class LLMError(RuntimeError):
    """Fallo ya traducido a un mensaje claro: quien llama no necesita saber de HTTP"""

def post_json(
        client: httpx.Client,
        url: str,
        headers: dict[str, str],
        body: dict,
        attempts: int = 3,
        sleep: Callable[[float], None] = time.sleep,
) -> dict:
    """Post con reintentos y espera creciente ante errores de red, 429 y 5xx"""
    problem = "sin intentos"
    for attempt in range(1, attempts + 1):
        wait = float(2 ** (attempt -1)) # son segundos
        try:
            r = client.post(url, headers=headers, json=body)
        except httpx.TransportError as e: #timeout, DNS, deneid connection, proxy..
            problem = f"red: {type(e).__name__}"
        else:
            if r.status_code in (401, 403):
                raise LLMError("Credenciales rechazadas: revisa la clave y la URL en .env")
            if r.status_code not in RETRYABLE:
                if r.is_error:
                    raise LLMError(f"El proveedor respondio {r.status_code}:{r.text[:200]}")
                try:
                    return r.json()
                except ValueError as e:
                    raise LLMError("La respuesta no es JSON valida") from e
            problem = f"HTTP {r.status_code}"
            if r.headers.get("retry-after", "").isdigit():
                wait = float(r.headers["retry-after"]) #el provedor dice cuanto esperar
        if attempt < attempts:
            logger.warning("Intento %s fallo (%s); reintento en %s s", attempt, problem, wait)
            sleep(wait)
    raise LLMError(f"sin respuesta tras {attempts} intentos ({problem})")


def ask_openai(
    client: httpx.Client,
    prompt: str,
    api_key: str,
    model: str,
    base_url: str = "https://api.openai.com/v1",
) -> str:
    """OpenAI y Azure OpenAI (API v1): misma petición; en Azure cambia base_url."""
    if not prompt.strip():
        raise ValueError("La pregunta no puede estar vacía")

    data = post_json(
        client,
        f"{base_url.rstrip('/')}/responses",
        headers={"Authorization": f"Bearer {api_key}"},
        body={"model": model, "input": prompt},
    )

    try:
        messages = [
            item for item in data["output"] if item["type"] == "message"
        ]
        return "".join(
            c["text"]
            for m in messages
            for c in m["content"]
            if c["type"] == "output_text"
        )
    except (KeyError, TypeError) as e:
        raise LLMError("La respuesta no tiene la forma esperada") from e


def ask_gemini(client: httpx.Client, prompt: str, api_key: str, model: str) -> str:
    """Gemimni: otra url, otra cabecera y otra forma de respuesta"""
    if not prompt.strip():
        raise ValueError("la pregunta no puede estar vacia")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    data = post_json(
        client,
        url,
        headers={"x-goog-api-key": api_key},
        body={"contents": [{"parts": [{"text": prompt}]}]},
    )
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as e:
        raise LLMError("la respuesta no tiene la forma esperada") from e