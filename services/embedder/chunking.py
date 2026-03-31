from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from services.embedder.processors.base_processor import ExtractionResult, SemanticBlock
from services.embedder.utils import compute_text_sha256


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

    def split(self, extraction: ExtractionResult, relative_path: str) -> list[dict]:
        semantic_docs = self._semantic_split(extraction)
        chunks = self.token_splitter.split_documents(semantic_docs)
        enriched_chunks: list[dict] = []
        for index, chunk in enumerate(chunks):
            text = chunk.page_content.strip()
            if not text:
                continue
            metadata = dict(chunk.metadata)
            title = metadata.get("title") or metadata.get("section") or metadata.get("chapter") or extraction.document_title
            chunk_id = f"{relative_path}:{index}"
            enriched_chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": text,
                    "title": title,
                    "chapter": metadata.get("chapter"),
                    "section": metadata.get("section"),
                    "heading_path": list(metadata.get("heading_path", [])),
                    "page_number": metadata.get("page_number"),
                    "extraction_method": metadata.get("extraction_method") or extraction.metadata.get("extraction_method"),
                    "content_type": metadata.get("content_type") or extraction.metadata.get("content_type"),
                    "quality_flags": list(extraction.quality.flags),
                    "metadata": {
                        **extraction.metadata,
                        **metadata,
                        "normalized_content_hash": compute_text_sha256(text),
                        "schema_version": extraction.metadata.get("schema_version"),
                        "processor_version": extraction.metadata.get("processor_version"),
                    },
                }
            )
        return enriched_chunks

    def _semantic_split(self, extraction: ExtractionResult) -> list[Document]:
        if extraction.metadata.get("extension") == ".md":
            documents = self.markdown_splitter.split_text(extraction.text)
            if documents:
                return documents

        blocks = extraction.semantic_blocks or [SemanticBlock(text=extraction.text, title=extraction.document_title)]
        documents = []
        for block in blocks:
            if not block.text.strip():
                continue
            documents.append(
                Document(
                    page_content=block.text,
                    metadata={
                        "title": block.title or extraction.document_title,
                        "chapter": block.chapter,
                        "section": block.section,
                        "heading_path": block.heading_path,
                        "page_number": block.page_number,
                        "extraction_method": block.extraction_method,
                        "content_type": block.content_type or extraction.metadata.get("content_type"),
                        **block.metadata,
                    },
                )
            )
        return documents or [Document(page_content=extraction.text, metadata={"title": extraction.document_title})]
