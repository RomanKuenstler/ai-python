from __future__ import annotations

from langchain_openai import ChatOpenAI


class LlmClient:
    def __init__(self, *, model: str, base_url: str, api_key: str, timeout: float = 60.0) -> None:
        self.client = ChatOpenAI(model=model, base_url=base_url, api_key=api_key, temperature=0, timeout=timeout, max_retries=0)

    def invoke(self, messages: list[tuple[str, str]]) -> str:
        response = self.client.invoke(messages)
        return str(response.content)
