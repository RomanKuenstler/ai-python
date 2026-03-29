from __future__ import annotations

import logging

from langchain_openai import OpenAIEmbeddings
import tiktoken


LOGGER = logging.getLogger(__name__)


class EmbeddingClient:
    def __init__(self, *, model: str, base_url: str, api_key: str, max_input_tokens: int = 400) -> None:
        self.client = OpenAIEmbeddings(model=model, base_url=base_url, api_key=api_key)
        self.max_input_tokens = max_input_tokens
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        sanitized = [self._truncate_text(text) for text in texts]
        return self.client.embed_documents(sanitized)

    def embed_query(self, text: str) -> list[float]:
        return self.client.embed_query(self._truncate_text(text))

    def _truncate_text(self, text: str) -> str:
        tokens = self.encoding.encode(text)
        if len(tokens) <= self.max_input_tokens:
            return text

        LOGGER.warning(
            "Truncated embedding input to fit model limit",
            extra={"original_tokens": len(tokens), "max_input_tokens": self.max_input_tokens},
        )
        return self.encoding.decode(tokens[: self.max_input_tokens])
