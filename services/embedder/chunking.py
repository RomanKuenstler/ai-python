from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter


class Chunker:
    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3"), ("####", "h4")]
        )
        self.token_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
        )

    def split(self, file_path: Path, text: str) -> list[str]:
        semantic_docs = self._semantic_split(file_path, text)
        chunks = self.token_splitter.split_documents(semantic_docs)
        return [chunk.page_content.strip() for chunk in chunks if chunk.page_content.strip()]

    def _semantic_split(self, file_path: Path, text: str) -> list[Document]:
        if file_path.suffix.lower() == ".md":
            documents = self.markdown_splitter.split_text(text)
            return documents or [Document(page_content=text)]

        paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
        if not paragraphs:
            return [Document(page_content=text)]
        return [Document(page_content=paragraph) for paragraph in paragraphs]
