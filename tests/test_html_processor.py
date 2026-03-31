from __future__ import annotations

from pathlib import Path

from services.common.config import Settings
from services.embedder.processors.html_processor import HtmlProcessor


def test_html_processor_removes_noise_and_preserves_structure(tmp_path: Path) -> None:
    html = """<!doctype html>
    <html>
      <head>
        <title>Install Guide</title>
        <style>.hidden { display: none; }</style>
      </head>
      <body>
        <nav>Navigation</nav>
        <main>
          <h1>Install Guide</h1>
          <p>Use Docker Compose for setup.</p>
          <ul><li>Pull image</li><li>Start service</li></ul>
          <blockquote>Keep volumes persistent.</blockquote>
          <pre>docker compose up</pre>
        </main>
      </body>
    </html>
    """
    path = tmp_path / "guide.html"
    path.write_text(html, encoding="utf-8")
    processor = HtmlProcessor(settings=Settings(data_dir=str(tmp_path)), data_dir=tmp_path)

    result = processor.process(file_path=path, relative_path="guide.html", tags=["docker"])

    assert "Navigation" not in result.text
    assert "# Install Guide" in result.text
    assert "- Pull image" in result.text
    assert "> Keep volumes persistent." in result.text
    assert "```" in result.text
    assert result.document_title == "Install Guide"
