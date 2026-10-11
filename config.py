"""API sağlayıcıları ve istemci oluşturma."""
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

PROVIDERS = {
    "Groq (ücretsiz)": {
        "env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "model": "openai/gpt-oss-120b",
    },
    "OpenAI": {
        "env": "OPENAI_API_KEY",
        "base_url": None,
        "model": "gpt-4o-mini",
    },
}


def has_key(provider):
    return bool(os.getenv(PROVIDERS[provider]["env"]))


def get_client(provider):
    p = PROVIDERS[provider]
    key = os.getenv(p["env"])
    if not key:
        raise RuntimeError(f".env dosyasında {p['env']} bulunamadı.")
    return OpenAI(api_key=key, base_url=p["base_url"])
