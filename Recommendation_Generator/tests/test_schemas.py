import pytest
from recommender.schemas import LikesPayload
from pydantic import ValidationError

def test_validate_and_clean_likes_success():
    payload = {"likes": [" A ", "B", "a"]}
    obj = LikesPayload.model_validate(payload)
    # deduped case-insensitively, preserves order of first occurrence
    assert obj.likes == ["A", "B"]

def test_validate_and_clean_likes_errors():
    with pytest.raises(ValidationError):
        LikesPayload.model_validate({"likes": []})
    with pytest.raises(ValidationError):
        LikesPayload.model_validate({"likes": ["", "OK"]})
    with pytest.raises(ValidationError):
        LikesPayload.model_validate({"likes": [123]})
