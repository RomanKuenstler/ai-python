from __future__ import annotations

from pathlib import Path

from ebooklib import epub

from services.common.config import Settings
from services.embedder.processors.epub_processor import EpubProcessor


def test_epub_processor_skips_front_matter_and_repeated_chrome(tmp_path: Path) -> None:
    book = epub.EpubBook()
    book.set_identifier("id123")
    book.set_title("Docker Book")
    book.add_author("Example Author")

    cover = epub.EpubHtml(title="Table of Contents", file_name="toc.xhtml", lang="en")
    cover.content = "<html><body><h1>Table of Contents</h1><p>Contents</p></body></html>"
    chapter = epub.EpubHtml(title="Chapter 1", file_name="chap1.xhtml", lang="en")
    chapter.content = (
        "<html><body><h1>Chapter 1</h1><p>Docker Book</p><p>Volumes keep data safe.</p></body></html>"
    )
    chapter2 = epub.EpubHtml(title="Chapter 2", file_name="chap2.xhtml", lang="en")
    chapter2.content = (
        "<html><body><h1>Chapter 2</h1><p>Docker Book</p><p>Networks isolate service traffic.</p></body></html>"
    )
    book.add_item(cover)
    book.add_item(chapter)
    book.add_item(chapter2)
    book.spine = ["nav", chapter, chapter2]
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    target = tmp_path / "docker.epub"
    epub.write_epub(str(target), book)

    processor = EpubProcessor(settings=Settings(data_dir=str(tmp_path)), data_dir=tmp_path)
    result = processor.process(file_path=target, relative_path="docker.epub", tags=["docker"])

    assert "Table of Contents" not in result.text
    assert result.document_title == "Docker Book"
    assert "Volumes keep data safe." in result.text
    assert "Networks isolate service traffic." in result.text
    assert result.text.count("Docker Book") <= 1
