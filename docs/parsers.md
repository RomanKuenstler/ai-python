# Parsers

## HTML / HTM

- Removes high-noise tags before extraction, including scripts, styles, navigation, forms, media, and hidden nodes.
- Prefers `<main>`, then `<article>`, then `[role="main"]`, then `<body>`.
- Preserves headings, paragraphs, lists, blockquotes, code blocks, and tables in markdown-like plain text.
- Drops duplicate consecutive blocks and trivial empty blocks.

## PDF

- Uses direct page-aware extraction first with PyMuPDF.
- Preserves page boundaries in semantic blocks and chunk metadata.
- Evaluates extraction quality before indexing.
- Falls back to OCR when configured and when direct extraction is weak or disabled.
- Supports configurable OCR preprocessing for grayscale, contrast, thresholding, and denoise.

## OCR Decision Flow

1. Extract direct text.
2. Score usefulness with character-count and text-quality heuristics.
3. If `PDF_OCR_MODE=fallback` and direct extraction is weak, try OCR.
4. If `PDF_OCR_MODE=ocr_only`, skip direct extraction output and rely on OCR.
5. If both paths are weak, store a failure state and do not index garbage text.

## EPUB

- Uses `ebooklib` and prefers spine order.
- Reuses the HTML extraction logic for XHTML content.
- Skips likely front matter based on spine position plus label/content markers.
- Removes repeated chrome that appears across many sections.
- Falls back to scanning document items directly if spine extraction yields nothing useful.

## Metadata

Depending on the file type, chunks may include:

- `title`
- `chapter`
- `section`
- `heading_path`
- `page_number`
- `extraction_method`
- `content_type`
- `normalized_content_hash`
- `document_title`
- `author`
- `tags`

## Chunking

- Semantic blocks are built first from file-type-specific structure.
- Oversized content is then split with token-aware chunking using the shared chunk size and overlap settings.
- Chunk titles are derived from the nearest semantic heading, chapter, section, or page label where possible.
