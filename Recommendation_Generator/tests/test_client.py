import json
import requests
from types import SimpleNamespace

import pytest
from recommender.client import call_ollama_sync

# Use monkeypatch to avoid real HTTP calls and to assert payload shape and stream flag behavior.
class DummyResp:
    def __init__(self, status_code=200, json_data=None, text_data=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text_data

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json

def test_call_ollama_sync_prefers_text_field(monkeypatch):
    # Simulate Ollama returning {"text": "..."}
    def fake_post(url, json, headers, timeout):
        assert "model" in json
        assert "stream" in json and json["stream"] is False
        return DummyResp(json_data={"text": "final output"})
    monkeypatch.setattr(requests, "post", fake_post)
    out = call_ollama_sync("prompt")
    assert out == "final output"

def test_call_ollama_sync_handles_choices(monkeypatch):
    def fake_post(url, json, headers, timeout):
        return DummyResp(json_data={"choices":[{"text":"choice text"}]})
    monkeypatch.setattr(requests, "post", fake_post)
    out = call_ollama_sync("p")
    assert out == "choice text"

def test_call_ollama_sync_fallback_to_raw_text(monkeypatch):
    def fake_post(url, json, headers, timeout):
        return DummyResp(status_code=200, json_data=None, text_data="raw text")
    monkeypatch.setattr(requests, "post", fake_post)
    out = call_ollama_sync("p")
    assert out == "raw text"

def test_call_ollama_sync_non_200(monkeypatch):
    def fake_post(url, json, headers, timeout):
        return DummyResp(status_code=500, json_data=None, text_data="server err")
    monkeypatch.setattr(requests, "post", fake_post)
    with pytest.raises(RuntimeError):
        call_ollama_sync("p")
