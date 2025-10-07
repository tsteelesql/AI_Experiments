# app.py
from __future__ import annotations

import logging
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template_string, request

from config import HOST, PORT, LOG_LEVEL, RECOMMENDATION_COUNT
from recommender.client import call_ollama_sync
from recommender.parse import parse_recommendations
from recommender.prompt import build_prompt
from recommender.schemas import LikesPayload
from recommender.templates import HTML_TEMPLATE

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("recommender.app")

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    sample = "Breaking Bad\nThe Wire\nFleabag"
    return render_template_string(HTML_TEMPLATE, sample=sample)


@app.route("/recommend", methods=["POST"])
def recommend():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    try:
        payload_raw: Any = request.get_json()
    except Exception:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        payload = LikesPayload.model_validate(payload_raw)
    except Exception as exc:
        logger.debug("Validation error: %s", exc)
        # pydantic ValidationError has .errors() but keep concise
        return jsonify({"error": "Invalid input", "details": getattr(exc, "errors", lambda: str(exc))()}), 400

    likes: List[str] = payload.likes
    if not likes:
        return jsonify({"error": "likes must contain at least one show"}), 400

    prompt = build_prompt(likes, n=RECOMMENDATION_COUNT)

    try:
        raw_text = call_ollama_sync(prompt)
    except Exception as exc:
        logger.exception("Error calling Ollama: %s", exc)
        return jsonify({"error": "Failed to generate recommendations", "detail": str(exc)}), 502

    recs = parse_recommendations(raw_text, expected=RECOMMENDATION_COUNT)

    final: List[Dict[str, str]] = []
    for r in recs:
        title = (r.get("title") or "").strip()
        reason = (r.get("reason") or "").strip()
        if not title:
            continue
        if len(reason) > 400:
            reason = reason[:397].rstrip() + "..."
        final.append({"title": title, "reason": reason})
        if len(final) >= RECOMMENDATION_COUNT:
            break

    if not final:
        logger.warning("No parsable recommendations from Ollama; raw output length=%d", len(raw_text or ""))
        return jsonify({"error": "Model returned no valid recommendations"}), 502

    return jsonify({"recommendations": final}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
