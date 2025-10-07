from recommender.parse import parse_recommendations

def test_parse_numbered_lines():
    text = """1. Some Show — Great ensemble and pacing.
2. Another Show — Similar tone and thoughtful drama.
3. ShortTitle — Compelling lead."""
    recs = parse_recommendations(text, expected=3)
    assert len(recs) == 3
    assert recs[0]["title"] == "Some Show"
    assert "ensemble" in recs[0]["reason"]

def test_parse_various_separators_and_dedup():
    text = """
Some Show - A reason.
2) Some Show - duplicate should be removed
3. Other Show — Different reason.
"""
    recs = parse_recommendations(text, expected=3)
    assert len(recs) >= 2
    titles = [r["title"].lower() for r in recs]
    assert titles.count("some show") == 1
    assert "other show" in titles

def test_parse_empty_text_returns_empty_list():
    assert parse_recommendations("", expected=5) == []
