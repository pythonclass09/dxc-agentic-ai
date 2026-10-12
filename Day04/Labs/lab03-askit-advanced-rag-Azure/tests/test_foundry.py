import pytest

from rag.llm import LLM


def test_foundry_uses_api_key_and_configured_endpoint(monkeypatch, tmp_path):
    import openai

    calls = []
    monkeypatch.setattr(openai, "OpenAI", lambda **kwargs: calls.append(kwargs) or object())

    llm = LLM(
        "foundry-key",
        chat_model="chat-deployment",
        embed_model="embedding-deployment",
        provider="foundry",
        base_url="https://example.services.ai.azure.com/models/",
        cache_dir=str(tmp_path),
    )

    assert calls == [{
        "api_key": "foundry-key",
        "base_url": "https://example.services.ai.azure.com/models",
    }]
    assert llm.chat_model == "chat-deployment"
    assert llm.embed_model == "embedding-deployment"
    assert llm._cache_path().startswith(str(tmp_path))


@pytest.mark.parametrize(
    ("api_key", "base_url"),
    [(None, "https://example.services.ai.azure.com/models"), ("foundry-key", None)],
)
def test_foundry_requires_key_and_endpoint(api_key, base_url, tmp_path):
    with pytest.raises(ValueError, match="API key and an OpenAI-compatible endpoint"):
        LLM(api_key, provider="foundry", base_url=base_url, cache_dir=str(tmp_path))


def test_foundry_embedding_cache_is_scoped_to_endpoint(tmp_path):
    first = LLM(
        "foundry-key",
        provider="foundry",
        base_url="https://one.services.ai.azure.com/models",
        cache_dir=str(tmp_path),
    )
    second = LLM(
        "foundry-key",
        provider="foundry",
        base_url="https://two.services.ai.azure.com/models",
        cache_dir=str(tmp_path),
    )

    assert first._cache_path() != second._cache_path()
