"""SDK oficial de gmeini. google-genai"""
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()
client = genai.Client() #asi sapea el .env
MODELO = os.getenv("LLM_MODEL", "gemini-3.5-flash")
if not MODELO.startswith("gemini"):
    MODELO = "gemini-3.5-flash" 

class Contacto(BaseModel):
    nombre: str
    empresa: str
    intereses: list[str]

def clima_actual(ciudad: str) -> str:
    """Temperatura actual de una ciudad de chile"""

if __name__ == "__main__":
    print("=== primera llamada ===")
    r = client.models.generate_content(
        model=MODELO,
        contents="¿Que es RAG?",
        config=types.GenerateContentConfig(system_instruction="Responde en español, en 3 frases."),
    )
    print(r.text)
    print(r.usage_metadata)

    print("=== conversacion (el chat guarda el historial) ===")
    chat = client.chats.create(model=MODELO)
    chat.send_message("¿Que es una list comprehension? una frase.")
    print(chat.send_message("Dame un ejemplo comparado con LINQ").text)

    print("=== streaming ===")
    for chunk in client.models.generate_content_stream(model=MODELO,contents="Un chiste corto"):
        print(chunk.text or "", end="", flush=True)
    print()

    print("=== salida estructurada ===")
    r = client.models.generate_content(
        model=MODELO,
        contents="Hola, soy Ana perez de Acme y me interesa la IA y la automatizacion.",
        config=types.GenerateContentConfig(
            response_mime_type="application/json", response_schema=Contacto
        ),
    )
    print(r.parsed)

    print("=== tool calling (el SDK ejecuta la funcion) ===")
    chat = client.chats.create(
        model=MODELO, config=types.GenerateContentConfig(tools=[clima_actual])
    )
    print(chat.send_message("¿Que temperatura hace en santiago?").text)
    print("=== embeddings ===")
    r = client.models.embed_content(
        model="gemini-embedding-001", contents=["perro", "cachorro", "factura"]
    )
    print(len(r.embeddings), "vectores de", len(r.embeddings[0].values), "numeros")