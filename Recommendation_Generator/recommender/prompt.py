# recommender/prompt.py
from __future__ import annotations

from typing import List

from config import RECOMMENDATION_COUNT


def build_prompt(likes: List[str], n: int = RECOMMENDATION_COUNT) -> str:
    likes_block = "\n".join(f"- {s}" for s in likes)
    prompt = (
        "You are an expert anime TV and streaming show recommender.\n"
        "User provided a list of shows they like.\n"
        f"Produce exactly {n} distinct TV show or limited-series recommendations "
        "that are NOT in the user's list. For each recommendation output a single "
        "numbered line in the format:\n\n"
        "1. Title — One concise sentence (10–30 words) explaining why this is a good match.\n\n"
        "Avoid filler, do not list the user's input, prefer diverse genres and eras where appropriate.\n\n"
        "User likes:\n"
        f"{likes_block}\n\n"
        "Output exactly the numbered items and nothing else.\n" \
        "Recommendations should all be anime."
    )
    return prompt
