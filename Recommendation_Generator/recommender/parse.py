# recommender/parse.py
from __future__ import annotations

import re
from typing import Dict, List

from config import RECOMMENDATION_COUNT


def parse_recommendations(text: str, expected: int = RECOMMENDATION_COUNT) -> List[Dict[str, str]]:
    """
    Parse lines like:
      1. Title — Reason.
    into [{'title': ..., 'reason': ...}, ...]
    """
    if not text:
        return []

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    recs: List[Dict[str, str]] = []
    pattern = re.compile(r'^\s*(?:\d+[\.\)]\s*)?(?P<title>[^—–\-–\n\r]+?)\s*[-—–]\s*(?P<reason>.+)$')
    for ln in lines:
        m = pattern.match(ln)
        if m:
            title = m.group("title").strip(" \"' ")
            reason = m.group("reason").strip()
            if title and len(title) > 1:
                recs.append({"title": title, "reason": reason})
            continue
        m2 = re.match(r'^\s*(\d+)[\.\)]\s*(.+)$', ln)
        if m2:
            title = m2.group(2).strip(" \"' ")
            recs.append({"title": title, "reason": ""})
            continue
        m3 = re.match(r'^(?P<title>[^—–\-–]+)\s*[-—–]\s*(?P<reason>.+)$', ln)
        if m3:
            recs.append({"title": m3.group("title").strip(), "reason": m3.group("reason").strip()})
            continue
        if len(ln) < 60:
            recs.append({"title": ln.strip(" \"' "), "reason": ""})

    # Deduplicate while preserving order and truncate to expected
    seen = set()
    unique: List[Dict[str, str]] = []
    for r in recs:
        key = r["title"].lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
        if len(unique) >= expected:
            break

    return unique
