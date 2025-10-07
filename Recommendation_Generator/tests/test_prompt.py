from recommender.prompt import build_prompt
from config import RECOMMENDATION_COUNT

def test_build_prompt_contains_likes_and_count():
    likes = ["Breaking Bad", "Fleabag"]
    prompt = build_prompt(likes, n=5)
    assert "Breaking Bad" in prompt
    assert "Fleabag" in prompt
    assert "Produce exactly 5" in prompt

def test_build_prompt_default_count():
    likes = ["The Wire"]
    prompt = build_prompt(likes)
    assert f"Produce exactly {RECOMMENDATION_COUNT}" in prompt
    assert "- The Wire" in prompt
