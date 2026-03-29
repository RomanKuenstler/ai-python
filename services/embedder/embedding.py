from __future__ import annotations

from langchain_openai import OpenAIEmbeddings


class EmbeddingClient:
    def __init__(self, *, model: str, base_url: str, api_key: str) -> None:
        self.client = OpenAIEmbeddings(model=model, base_url=base_url, api_key=api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.client.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self.client.embed_query(text)
