# recommender/client.py
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import requests

from config import (
    OLLAMA_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT_S,
    REQUESTS_BACKOFF_S,
    REQUESTS_RETRIES,
)

logger = logging.getLogger("recommender.client")


def call_ollama_sync(prompt: str, model: str = OLLAMA_MODEL, timeout_s: float = OLLAMA_TIMEOUT_S) -> str:
    """
    Synchronously call Ollama /api/generate with stream=False and return the final text.
    Does simple retries for transient network errors and non-5xx responses.
    """
    url = f"{OLLAMA_URL}/api/generate"
    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        # No max_tokens field included by design
        "temperature": 0.8,
        "top_p": 0.95,
        "stream": False,  # request non-streaming behavior
    }
    headers = {"Content-Type": "application/json"}

    last_exc: Optional[Exception] = None
    for attempt in range(1, REQUESTS_RETRIES + 2):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=timeout_s)
        except requests.RequestException as exc:
            last_exc = exc
            logger.warning("Ollama request failed (attempt %d): %s", attempt, exc)
            if attempt <= REQUESTS_RETRIES:
                time.sleep(REQUESTS_BACKOFF_S * attempt)
            continue

        if resp.status_code != 200:
            last_exc = RuntimeError(f"Ollama returned status {resp.status_code}: {resp.text[:200]}")
            logger.error("Ollama HTTP error (status=%s) attempt %d", resp.status_code, attempt)
            # Do not retry on client errors
            if 400 <= resp.status_code < 500:
                break
            if attempt <= REQUESTS_RETRIES:
                time.sleep(REQUESTS_BACKOFF_S * attempt)
            continue

        try:
            data = resp.json()
        except ValueError:
            text = resp.text or ""
            if not text:
                raise ValueError("Empty response from Ollama")
            return text

        # Common shapes for non-streaming output
        if isinstance(data, dict):
            for key in ("text", "response", "generated", "output"):
                if key in data and isinstance(data[key], str):
                    return data[key]
            if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
                first = data["choices"][0]
                if isinstance(first, dict):
                    if "text" in first and isinstance(first["text"], str):
                        return first["text"]
                    if "message" in first and isinstance(first["message"], dict):
                        msg = first["message"]
                        if "content" in msg and isinstance(msg["content"], str):
                            return msg["content"]
        if isinstance(data, str):
            return data

        text = resp.text or ""
        if text:
            return text

        last_exc = RuntimeError("Could not extract text from Ollama response")
        logger.error("No usable field found in Ollama response JSON")

    raise RuntimeError(f"Failed to get response from Ollama after retries: {last_exc}")
