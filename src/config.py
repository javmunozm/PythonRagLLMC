"""Configuración tipada: lee .env y variables de entorno una sola vez (como IOptions<T>)."""
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    #"openai" sirve para gpt y azure (solo cambia la url);"gemini" para google
    llm_provider : Literal["openai", "gemini"] = "gemini"
    openai_base_url: str | None = None #Solo para azure, el str | none es tecnicamente str?
    gemini_api_key: SecretStr | None = None
    llm_model: str = "gemini-3.5-flash"
    embedding_model: str = "gemini-embedding-001"

    chroma_dir: str = "chroma_db"
    collection_name: str = "documentos"
    log_level: str = "INFO"
    max_upload_mb: int = 10


# USD por millón de tokens del modelo configurado (míralo en la página de precios)
    price_input_per_mtok: float =0.35
    price_output_per_mtok: float=.75

@lru_cache
def get_settings() -> Settings:
    return Settings()