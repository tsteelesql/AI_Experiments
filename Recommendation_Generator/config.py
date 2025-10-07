# config.py
from __future__ import annotations

import os

# Ollama settings
OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_TIMEOUT_S: float = float(os.getenv("OLLAMA_TIMEOUT_S", "120"))

# Recommender specifics
RECOMMENDATION_COUNT: int = int(os.getenv("RECOMMENDATION_COUNT", "10"))
MAX_LIKES: int = int(os.getenv("MAX_LIKES", "50"))

# Request retry/backoff for synchronous calls
REQUESTS_RETRIES: int = int(os.getenv("REQUESTS_RETRIES", "2"))
REQUESTS_BACKOFF_S: float = float(os.getenv("REQUESTS_BACKOFF_S", "0.5"))

# Webserver defaults
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "5000"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
