# recommender/schemas.py
from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel, Field, field_validator, ValidationError

from config import MAX_LIKES


class LikesPayload(BaseModel):
    likes: List[str] = Field(..., description="List of show titles the user enjoys")

    @field_validator("likes")
    @classmethod
    def validate_and_clean_likes(cls, v: List[Any]) -> List[str]:
        if not isinstance(v, list) or not v:
            raise ValueError("likes must be a non-empty list of strings")

        cleaned: List[str] = []
        for i, item in enumerate(v):
            if not isinstance(item, str):
                raise ValueError(f"likes[{i}] must be a string")
            s = item.strip()
            if not s:
                raise ValueError(f"likes[{i}] must not be empty or whitespace")
            cleaned.append(s)

        if len(cleaned) > MAX_LIKES:
            raise ValueError(f"likes list too large; maximum is {MAX_LIKES}")

        # Deduplicate while preserving order (case-insensitive)
        seen = set()
        deduped: List[str] = []
        for t in cleaned:
            key = t.lower()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(t)

        return deduped
