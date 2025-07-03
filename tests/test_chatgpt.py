import os
import sys
import types
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import openai
from jarvis_core.chatgpt import ChatGPTModule


def test_ask_without_api_key(monkeypatch):
    monkeypatch.setattr(openai, "api_key", None)
    module = ChatGPTModule(api_key=None)
    reply = module.ask("Hello?")
    assert "Apologies" in reply
    assert module.conversation[-1]["role"] == "assistant"


def test_ask_with_api_key(monkeypatch):
    module = ChatGPTModule(api_key="key")

    class FakeResponse:
        choices = [types.SimpleNamespace(message={"content": "Hello"})]

    monkeypatch.setattr(
        openai.ChatCompletion,
        "create",
        lambda model, messages: FakeResponse(),
    )
    reply = module.ask("Hi")
    assert reply == "Hello"
    assert module.conversation[-1]["content"] == "Hello"

